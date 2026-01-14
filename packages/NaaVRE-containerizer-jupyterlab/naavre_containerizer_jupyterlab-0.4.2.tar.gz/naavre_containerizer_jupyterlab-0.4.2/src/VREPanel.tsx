import React, { useEffect, useState } from 'react';
import { theme } from './Theme';
import { ThemeProvider } from '@material-ui/core/styles';
import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';
import { CellTracker } from './components/CellTracker';
import { Slot } from '@lumino/signaling';
import { Divider } from '@material-ui/core';

export interface IVREPanelSettings {
  virtualLab: string | null;
  containerizerServiceUrl: string | null;
  catalogueServiceUrl: string | null;
}

export const DefaultVREPanelSettings: IVREPanelSettings = {
  virtualLab: null,
  containerizerServiceUrl: null,
  catalogueServiceUrl: null
};

export const VREPanelComponent = ({
  tracker,
  settings
}: {
  tracker: INotebookTracker;
  settings: IVREPanelSettings;
}): React.ReactElement => {
  const [notebookPath, setNotebookPath] = useState('');

  useEffect(() => {
    tracker.currentChanged.connect(handleNotebookChanged, this);
    if (tracker.currentWidget instanceof NotebookPanel) {
      setNotebookPath(tracker.currentWidget.context.path);
    }
  }, [tracker]);

  const handleNotebookChanged: Slot<INotebookTracker, NotebookPanel | null> = (
    tracker,
    notebook
  ) => {
    if (notebook) {
      setNotebookPath(notebook.context.path);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <div
        style={{
          flexDirection: 'column',
          minWidth: 'var(--jp-sidebar-min-width)',
          color: 'var(--jp-ui-font-color1)',
          background: 'var(--jp-layout-color1)',
          fontSize: 'var(--jp-ui-font-size1)',
          overflow: 'auto',
          height: '100%',
          display: 'flex'
        }}
      >
        <div
          style={{
            minWidth: 'var(--jp-sidebar-min-width)',
            overflow: 'auto'
          }}
        >
          <div>
            <p
              style={{
                fontSize: 'var(--jp-ui-font-size3)',
                padding: '10px',
                fontWeight: '800',
                letterSpacing: '0.5px'
              }}
            >
              Component containerizer
            </p>
            <Divider />
            <div>
              <p
                style={{
                  fontSize: 'var(--jp-ui-font-size2)',
                  padding: '10px',
                  color: 'cornflowerblue',
                  fontWeight: '700'
                }}
              >
                {notebookPath}
              </p>
            </div>
            <Divider />
          </div>
          <div style={{ marginTop: 5 }}>
            <CellTracker notebook={tracker.currentWidget} settings={settings} />
          </div>
        </div>
      </div>
    </ThemeProvider>
  );
};
