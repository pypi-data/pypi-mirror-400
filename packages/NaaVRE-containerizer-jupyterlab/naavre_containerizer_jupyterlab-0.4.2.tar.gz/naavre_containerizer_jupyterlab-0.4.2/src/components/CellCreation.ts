import { Notification } from '@jupyterlab/apputils';
import pRetry, { AbortError } from 'p-retry';

import { NaaVRECatalogue } from '../naavre-common/types';
import { NaaVREExternalService } from '../naavre-common/handler';
import { IVREPanelSettings } from '../VREPanel';

declare type ContainerizeResponse = {
  workflow_id: string;
  dispatched_github_workflow: boolean;
  container_image: string;
  workflow_url: string;
  source_url: string;
};

declare type StatusResponse = {
  job: {
    html_url: string;
    status:
      | 'queued'
      | 'in_progress'
      | 'completed'
      | 'waiting'
      | 'requested'
      | 'pending';
    conclusion:
      | 'success'
      | 'failure'
      | 'neutral'
      | 'cancelled'
      | 'skipped'
      | 'timed_out'
      | 'action_required'
      | null;
  };
} | null;

declare type CatalogueResponseItem = {
  url: string;
} & NaaVRECatalogue.WorkflowCells.ICell;

declare type CatalogueResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: CatalogueResponseItem[];
};

async function callContainerizeAPI(
  cell: NaaVRECatalogue.WorkflowCells.ICell,
  forceContainerize: boolean,
  settings: IVREPanelSettings
) {
  const resp = await NaaVREExternalService(
    'POST',
    `${settings.containerizerServiceUrl}/containerize`,
    {},
    {
      virtual_lab: settings.virtualLab || undefined,
      cell: cell,
      force_containerize: forceContainerize
    }
  );
  if (resp.status_code !== 200) {
    throw `${resp.status_code} ${resp.reason}`;
  }
  return JSON.parse(resp.content) as ContainerizeResponse;
}

async function callStatusAPI(workflowId: string, settings: IVREPanelSettings) {
  const resp = await NaaVREExternalService(
    'GET',
    `${settings.containerizerServiceUrl}/status/${settings.virtualLab}/${workflowId}/`,
    {},
    {}
  );
  if (resp.status_code === 200) {
    return JSON.parse(resp.content) as StatusResponse;
  } else if (resp.status_code === 404) {
    return null;
  } else {
    throw `${resp.status_code} ${resp.reason}`;
  }
}

async function findCellInCatalogue({
  searchParams,
  settings
}: {
  searchParams: URLSearchParams;
  settings: IVREPanelSettings;
}): Promise<CatalogueResponse> {
  const resp = await NaaVREExternalService(
    'GET',
    `${settings.catalogueServiceUrl}/workflow-cells/?${searchParams}`
  );
  if (resp.status_code !== 200) {
    throw `${resp.status_code} ${resp.reason}`;
  }
  return JSON.parse(resp.content);
}

async function getLatestCellVersionFromCatalogue({
  cell,
  settings
}: {
  cell: NaaVRECatalogue.WorkflowCells.ICell;
  settings: IVREPanelSettings;
}): Promise<CatalogueResponseItem | null> {
  cell.virtual_lab = settings.virtualLab || undefined;
  if (settings.virtualLab === null) {
    throw 'Virtual lab is null, check @naavre/containerizer-jupyterlab settings';
  }
  const res = await findCellInCatalogue({
    searchParams: new URLSearchParams({
      title: cell.title,
      virtual_lab: settings.virtualLab
    }),
    settings
  });
  if (res.count === 0) {
    return null;
  }
  return res.results.reduce((max, item) =>
    item.version > max.version ? item : max
  );
}

async function addCellToCatalogue({
  cell,
  containerizeResponse,
  settings
}: {
  cell: NaaVRECatalogue.WorkflowCells.ICell;
  containerizeResponse: ContainerizeResponse;
  settings: IVREPanelSettings;
}): Promise<CatalogueResponseItem> {
  cell.container_image = containerizeResponse?.container_image || '';
  cell.source_url = containerizeResponse?.source_url || '';
  cell.description = cell.title;
  cell.virtual_lab = settings.virtualLab || undefined;

  const resp = await NaaVREExternalService(
    'POST',
    `${settings.catalogueServiceUrl}/workflow-cells/`,
    {},
    cell
  );
  if (resp.status_code !== 201) {
    throw `${resp.status_code} ${resp.reason}`;
  }
  return JSON.parse(resp.content);
}

async function patchCellInCatalogue({
  cellUrl,
  payload
}: {
  cellUrl: string;
  payload: object;
}): Promise<CatalogueResponseItem> {
  const resp = await NaaVREExternalService('PATCH', cellUrl, {}, payload);
  if (resp.status_code !== 200) {
    throw `${resp.status_code} ${resp.reason}`;
  }
  return JSON.parse(resp.content);
}

async function addCellToCatalogueAndLinkPreviousVersion(
  cell: NaaVRECatalogue.WorkflowCells.ICell,
  containerizeResponse: ContainerizeResponse,
  settings: IVREPanelSettings
): Promise<'added' | 'updated'> {
  const previousCell = await getLatestCellVersionFromCatalogue({
    cell: cell,
    settings: settings
  });
  cell.version = previousCell !== null ? previousCell.version + 1 : 1;
  const newCell = await addCellToCatalogue({
    cell,
    containerizeResponse: containerizeResponse,
    settings
  });
  if (previousCell !== null) {
    await patchCellInCatalogue({
      cellUrl: previousCell.url,
      payload: { next_version: newCell.url }
    });
    return 'updated';
  } else {
    return 'added';
  }
}

export async function createCell(
  cell: NaaVRECatalogue.WorkflowCells.ICell,
  settings: IVREPanelSettings,
  forceContainerize: boolean
) {
  const notificationId = Notification.emit(
    `Containerizing ${cell.title}: submitting cell`,
    'in-progress',
    { autoClose: false }
  );
  let containerizeResponse: ContainerizeResponse;
  try {
    containerizeResponse = await callContainerizeAPI(
      cell,
      forceContainerize,
      settings
    );
    console.debug('containerizeResponse', containerizeResponse);
  } catch {
    Notification.update({
      id: notificationId,
      type: 'error',
      message: `Failed to containerize ${cell.title}: cannot submit cell`,
      autoClose: 5000
    });
    return;
  }
  if (!containerizeResponse.dispatched_github_workflow) {
    Notification.update({
      id: notificationId,
      type: 'warning',
      message: `Cell ${cell.title} is already containerized`,
      autoClose: 5000
    });
    return;
  }

  await new Promise(r => setTimeout(r, 5000));

  Notification.update({
    id: notificationId,
    message: `Containerizing ${cell.title}: starting build job`
  });
  let statusResponse: StatusResponse;
  try {
    statusResponse = await pRetry(
      async () => {
        const res = await callStatusAPI(
          containerizeResponse.workflow_id,
          settings
        );
        console.debug(res);
        if (res === null) {
          throw Error('job not found');
        }
        return res;
      },
      {
        retries: 5,
        factor: 2,
        minTimeout: 3000
      }
    );
    console.debug('statusResponse', statusResponse);
  } catch {
    Notification.update({
      id: notificationId,
      type: 'error',
      message: `Failed to containerize ${cell.title}: could not start build job`,
      autoClose: 5000
    });
    return;
  }

  Notification.update({
    id: notificationId,
    message: `Containerizing ${cell.title}: building image (this can take up to several minutes)`,
    actions: [
      {
        label: 'See progress on GitHub',
        callback: event => {
          event.preventDefault();
          window.open(statusResponse?.job.html_url);
        }
      }
    ]
  });
  try {
    statusResponse = await pRetry(
      async () => {
        const res = await callStatusAPI(
          containerizeResponse.workflow_id,
          settings
        );
        if (res === null) {
          throw Error('job not found');
        }
        console.debug(res.job);
        if (res.job.status !== 'completed') {
          throw Error('job not complete');
        }
        if (
          res.job.conclusion === null ||
          [
            'action_required',
            'cancelled',
            'failure',
            'stale',
            'timed_out'
          ].includes(res.job.conclusion)
        ) {
          throw new AbortError('job was not successful');
        }
        return res;
      },
      {
        retries: 180,
        factor: 1,
        minTimeout: 20000
      }
    );
    console.debug('statusResponse', statusResponse);
  } catch {
    Notification.update({
      id: notificationId,
      type: 'error',
      message: `Failed to containerize ${cell.title}: could not run build job`,
      actions: [
        {
          label: 'See status on GitHub',
          callback: event => {
            event.preventDefault();
            window.open(statusResponse?.job.html_url);
          }
        }
      ],
      autoClose: 5000
    });
    return;
  }

  Notification.update({
    id: notificationId,
    message: `Containerizing ${cell.title}: saving to the catalogue`,
    actions: []
  });
  try {
    const catalogueResponse = await addCellToCatalogueAndLinkPreviousVersion(
      cell,
      containerizeResponse,
      settings
    );
    console.debug('catalogueResponse', catalogueResponse);
  } catch {
    Notification.update({
      id: notificationId,
      type: 'error',
      message: `Failed to containerize ${cell.title}: save to the catalogue`,
      autoClose: 5000
    });
    return;
  }

  Notification.update({
    id: notificationId,
    type: 'success',
    message: `Containerized ${cell.title}`,
    autoClose: 5000
  });
}
