import {
  ILayoutRestorer,
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { INotebookTracker } from '@jupyterlab/notebook';
import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { VREPanelWidget } from './widget';
import { IVREPanelSettings } from './VREPanel';
import { extensionIcon } from './icons';

/**
 * Initialization data for the @naavre/containerizer-jupyterlab extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: '@naavre/containerizer-jupyterlab:plugin',
  description: 'NaaVRE cells containerizer frontend on Jupyter Lab',
  autoStart: true,
  requires: [ILayoutRestorer, INotebookTracker],
  optional: [ISettingRegistry],
  activate: (
    app: JupyterFrontEnd,
    restorer: ILayoutRestorer,
    tracker: INotebookTracker,
    settingRegistry: ISettingRegistry | null
  ) => {
    console.log(
      'JupyterLab extension @naavre/containerizer-jupyterlab is activated!'
    );

    let widget: VREPanelWidget;

    if (settingRegistry) {
      const loadSettings = settingRegistry.load(plugin.id);

      Promise.all([loadSettings, app.restored])
        .then(([settings]) => {
          function onSettingsChanged(
            settings: ISettingRegistry.ISettings
          ): void {
            widget.updateSettings(
              settings.composite as Partial<IVREPanelSettings>
            );
          }
          settings.changed.connect(onSettingsChanged);
          onSettingsChanged(settings);
        })
        .catch(reason => {
          console.error(
            'Failed to load settings for @naavre/containerizer-jupyterlab.',
            reason
          );
        });
    }

    app.started.then(() => {
      widget = new VREPanelWidget(tracker);
      widget.id = 'NaaVRE-containerizer-jupyterlab';
      widget.title.icon = extensionIcon;
      widget.title.caption = 'NaaVRE containerizer';
      restorer.add(widget, widget.id);
    });

    app.restored.then(() => {
      if (!widget.isAttached) {
        app.shell.add(widget, 'left');
      }
    });
  }
};

export default plugin;
