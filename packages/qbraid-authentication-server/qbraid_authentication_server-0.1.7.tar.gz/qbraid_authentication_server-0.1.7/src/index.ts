import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import Cookies from 'universal-cookie';

import { requestAPI } from './handler';

const cookies = new Cookies();
/**
 * Initialization data for the @qbraid/authentication-server extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: '@qbraid/authentication-server:plugin',
  description:
    'A JupyterLab extension. used to get the user credentials from qbraidrc file, with the support of qbraid-core module.',
  autoStart: true,
  activate: async (app: JupyterFrontEnd) => {
    console.log(
      'JupyterLab extension @qbraid/authentication-server is activated!'
    );
    try {
      const email = cookies.get('EMAIL');
      const refreshToken = cookies.get('REFRESH');
      if (email && refreshToken) {
        await requestAPI('qbraid-config', {
          method: 'POST',
          body: JSON.stringify({
            email: email,
            refreshToken: refreshToken
          })
        });
        console.log('qBraid configuration successfully set from cookies.');
      } else {
        console.warn(
          'qBraid configuration not set: EMAIL or REFRESH token not found in cookies.'
        );
      }
    } catch (error) {
      console.error(
        'Error activating @qbraid/authentication-server extension:',
        error
      );
    }
  }
};

export default plugin;
