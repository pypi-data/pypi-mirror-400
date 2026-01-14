import { createContext } from 'react';
import { IDocumentManager } from '@jupyterlab/docmanager';

export interface IJupyterContext {
  docManager: IDocumentManager;
}

export const JupyterContext = createContext<IJupyterContext | null>(null);
