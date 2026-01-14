import { createContext } from 'react';

export interface ISettings {
  virtualLab?: string;
  catalogueServiceUrl?: string;
}

export const SettingsContext = createContext<ISettings>({});
