import { LabIcon } from '@jupyterlab/ui-components';

import extensionIconSvgStr from '../style/icons/extension-icon.svg';

export const extensionIcon = new LabIcon({
  name: 'extension-icon',
  svgstr: extensionIconSvgStr
});
