import {
  INotebookFile,
  IWorkflowCell,
  IWorkflowFile
} from '../../types/NaaVRECatalogue/assets';

export type Asset = INotebookFile | IWorkflowCell | IWorkflowFile;

export type AssetKind = {
  name: string;
  namePlural: string;
  slug: string;
  cataloguePath: string;
};

export const assetKinds: AssetKind[] = [
  {
    name: 'notebook file',
    namePlural: 'notebook file',
    slug: 'notebook-files',
    cataloguePath: 'notebook-files'
  },
  {
    name: 'workflow component',
    namePlural: 'workflow component',
    slug: 'workflow-cells',
    cataloguePath: 'workflow-cells'
  },
  {
    name: 'workflow file',
    namePlural: 'workflow file',
    slug: 'workflow-files',
    cataloguePath: 'workflow-files'
  }
];
