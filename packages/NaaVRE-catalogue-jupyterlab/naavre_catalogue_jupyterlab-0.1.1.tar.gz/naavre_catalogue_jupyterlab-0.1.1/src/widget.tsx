import React from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import { ThemeProvider } from '@mui/material/styles';

import { App } from './app';
import { ISettings, SettingsContext } from './settings';
import { theme } from './theme';
import { IJupyterContext, JupyterContext } from './contexts/JupyterContext';

export class CatalogueWidget extends ReactWidget {
  jupyterContext: IJupyterContext | null = null;
  settings: ISettings = {};

  constructor(
    jupyterContext: IJupyterContext | null,
    settings: Partial<ISettings>
  ) {
    super();
    this.jupyterContext = jupyterContext;
    this.settings = settings;
  }

  updateSettings(settings: Partial<ISettings>) {
    this.settings = { ...this.settings, ...settings };
    this.update();
  }

  render() {
    return (
      <JupyterContext.Provider value={this.jupyterContext}>
        <SettingsContext.Provider value={this.settings}>
          <ThemeProvider theme={theme}>
            <App />
          </ThemeProvider>
        </SettingsContext.Provider>
      </JupyterContext.Provider>
    );
  }
}
