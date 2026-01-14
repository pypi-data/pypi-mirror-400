import { ReactWidget } from '@jupyterlab/ui-components';

import React from 'react';

import {
  VREPanelComponent,
  IVREPanelSettings,
  DefaultVREPanelSettings
} from './VREPanel';
import { INotebookTracker } from '@jupyterlab/notebook';

export class VREPanelWidget extends ReactWidget {
  tracker: INotebookTracker;
  settings: IVREPanelSettings = DefaultVREPanelSettings;

  constructor(tracker: INotebookTracker) {
    super();
    this.tracker = tracker;
  }

  updateSettings(settings: Partial<IVREPanelSettings>) {
    this.settings = { ...this.settings, ...settings };
    this.update();
  }

  render() {
    return (
      <VREPanelComponent tracker={this.tracker} settings={this.settings} />
    );
  }
}
