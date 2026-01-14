import { LabIcon } from '@jupyterlab/ui-components';

import addFileToCatSvgStr from '../style/icons/add-file-to-cat.svg';
import launcherIconSvgStr from '../style/icons/launcher-icon.svg';
import tabIconSvgStr from '../style/icons/tab-icon.svg';

export const launcherIcon = new LabIcon({
  name: 'launcher-icon',
  svgstr: launcherIconSvgStr
});

export const tabIcon = new LabIcon({
  name: 'tab-icon',
  svgstr: tabIconSvgStr
});

export const addFileToCatIcon = new LabIcon({
  name: 'add-to-cat-icon',
  svgstr: addFileToCatSvgStr
});
