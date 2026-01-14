import {
  ILayoutRestorer,
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import {
  ICommandPalette,
  IThemeManager,
  MainAreaWidget,
  WidgetTracker
} from '@jupyterlab/apputils';
import { IStateDB } from '@jupyterlab/statedb';
import { ILauncher } from '@jupyterlab/launcher';
import { requestAPI } from './handler';
import { JupyterIGVWidget } from './widget';
import { igvIcon } from './icon';

export const PLUGIN_NAME = 'climb-jupyter-igv';
export const PLUGIN_NAMESPACE = `@${PLUGIN_NAME}`;
const PLUGIN_ID = `${PLUGIN_NAMESPACE}:plugin`;

// Command IDs and categories
const igvCommandID = 'climb_jupyter_igv';
const category = 'CLIMB-TRE';

const tracker = new WidgetTracker<MainAreaWidget<JupyterIGVWidget>>({
  namespace: PLUGIN_NAMESPACE
});

/**
 * Initialization data for the climb-jupyter-igv extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: PLUGIN_ID,
  description: 'JupyterLab Extension for IGV (Integrative Genomics Viewer).',
  autoStart: true,
  requires: [ICommandPalette, IStateDB, IThemeManager],
  optional: [ILauncher, ILayoutRestorer],
  activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    stateDB: IStateDB,
    themeManager: IThemeManager,
    launcher: ILauncher | null,
    restorer: ILayoutRestorer | null
  ) => {
    console.log(`JupyterLab extension ${PLUGIN_NAMESPACE} is activated!`);

    // Retrieve extension version and log to the console
    let version = '';
    requestAPI<any>('version')
      .then(data => {
        version = data['version'];
        console.log(
          `JupyterLab extension ${PLUGIN_NAMESPACE} version: ${version}`
        );
      })
      .catch(error =>
        console.error(`Failed to fetch ${PLUGIN_NAMESPACE} version: ${error}`)
      );

    // Function to create new JupyterIGV widgets
    const createJupyterIGVWidget = async (
      name?: string
    ): Promise<MainAreaWidget<JupyterIGVWidget>> => {
      // Generate a unique name if not provided
      if (!name) {
        name = Date.now().toString();
      }

      // Prefix shared by all state keys for this widget
      const stateKeyPrefix = `${PLUGIN_ID}:${name}`;

      // Load any initial state before widget creation
      const initialState = new Map<string, any>();
      const pluginStateKeys = await stateDB.list(PLUGIN_NAMESPACE);

      pluginStateKeys.ids.forEach((stateKey, index) => {
        if (stateKey.startsWith(stateKeyPrefix)) {
          initialState.set(stateKey, pluginStateKeys.values[index]);
        }
      });

      // Create the JupyterIGVWidget instance
      const content = new JupyterIGVWidget(
        themeManager,
        version,
        name,
        stateDB,
        stateKeyPrefix,
        initialState
      );

      // Define the MainAreaWidget with the JupyterIGVWidget content
      const widget = new MainAreaWidget({ content });
      widget.id = `jupyter-igv-widget-${name}`;
      widget.title.label = 'IGV';
      widget.title.icon = igvIcon;
      widget.title.closable = true;

      return widget;
    };

    // Add commands to the command registry
    // Command to launch IGV
    app.commands.addCommand(igvCommandID, {
      label: 'IGV',
      caption: 'IGV | Integrative Genomics Viewer',
      icon: igvIcon,
      execute: async args => {
        const name = args['name'] as string;
        let widget: MainAreaWidget<JupyterIGVWidget>;

        if (name) {
          // Restore existing widget
          const existingWidget = tracker.find(w => w.content.name === name);
          if (existingWidget) {
            widget = existingWidget;
          } else {
            widget = await createJupyterIGVWidget(name);
          }
        } else {
          // Create new widget
          widget = await createJupyterIGVWidget();
        }

        // Add the widget to the tracker if it's not there
        if (!tracker.has(widget)) {
          tracker.add(widget);
        }

        // Attach the widget to the main work area if it's not there
        if (!widget.isAttached) {
          app.shell.add(widget, 'main');
        }

        // Activate and return the widget
        app.shell.activateById(widget.id);
        return widget;
      }
    });

    // Add commands to the command palette
    palette.addItem({ command: igvCommandID, category: category });

    // Add commands to the launcher
    if (launcher) {
      launcher.add({
        command: igvCommandID,
        category: category
      });
    }

    // Handle layout restoration
    if (restorer) {
      void restorer.restore(tracker, {
        command: igvCommandID,
        args: widget => ({ name: widget.content.name }),
        name: widget => widget.content.name
      });
    }

    // Update widget theme on change
    themeManager.themeChanged.connect(theme => {
      tracker.forEach(w => w.content.updateTheme(theme.theme));
    });
  }
};

export default plugin;
