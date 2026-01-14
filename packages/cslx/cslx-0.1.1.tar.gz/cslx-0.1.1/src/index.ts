import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ICommandPalette, MainAreaWidget } from '@jupyterlab/apputils';
//import { MainAreaWidget } from '@jupyterlab/apputils';
import { ILauncher } from '@jupyterlab/launcher';
import { INotebookTracker } from '@jupyterlab/notebook';
import { CyberShuttlePanel } from './CyberShuttlePanel';
/**
 * Initialization data for the cslx extension.
 */

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'cslx:plugin',
  description: 'A JupyterLab extension for Cybershuttle',
  autoStart: true,
  requires: [ICommandPalette],
  optional: [ILauncher, INotebookTracker],
  activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    launcher: ILauncher | null,
    tracker: INotebookTracker | null
  ) => {
    console.log('JupyterLab extension cslx is activated!');

    if (!tracker) {
      console.warn('INotebookTracker is not available.');
      return;
    }

  const panel = new CyberShuttlePanel(app);
    const panelWidget = new MainAreaWidget({ content: panel });
    app.shell.add(panelWidget, 'right', { rank: 200 });
    app.shell.activateById(panelWidget.id);
  }
};

export default plugin;
