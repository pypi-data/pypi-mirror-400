import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { IMarkdownParser } from '@jupyterlab/rendermime';
import { ISettingRegistry } from '@jupyterlab/settingregistry';

// Import utility functions from separate module (allows testing without JupyterLab deps)
import { processAlerts, postProcessAlerts } from './utils';

// Re-export for backwards compatibility
export { processAlerts, postProcessAlerts } from './utils';

/**
 * Initialization data for the jupyterlab_github_markdown_alerts_extension extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab_github_markdown_alerts_extension:plugin',
  description:
    'Jupyterlab extension to render alerts tips like they are rendered in github in markdown',
  autoStart: true,
  requires: [IMarkdownParser],
  optional: [ISettingRegistry],
  activate: (
    app: JupyterFrontEnd,
    markdownParser: IMarkdownParser,
    settingRegistry: ISettingRegistry | null
  ) => {
    let showBackgrounds = false;

    // Load settings
    if (settingRegistry) {
      const loadSettings = () => {
        settingRegistry
          .load(plugin.id)
          .then(settings => {
            showBackgrounds = settings.get('showBackgrounds')
              .composite as boolean;
            settings.changed.connect(() => {
              showBackgrounds = settings.get('showBackgrounds')
                .composite as boolean;
            });
          })
          .catch(reason => {
            console.error(
              'Failed to load settings for jupyterlab_github_markdown_alerts_extension',
              reason
            );
          });
      };
      loadSettings();
    }

    const originalRender = markdownParser.render.bind(markdownParser);

    markdownParser.render = async (content: string): Promise<string> => {
      const processedContent = processAlerts(content);
      const renderedHtml = await originalRender(processedContent);
      return postProcessAlerts(renderedHtml, showBackgrounds);
    };

    console.log(
      'JupyterLab extension jupyterlab_github_markdown_alerts_extension is activated!'
    );
  }
};

export default plugin;
