export interface ISharingScope {
  url: string;
  title: string;
  label: 'virtual_lab' | 'community';
  show_in_virtual_labs: string[];
  check_in_virtual_labs: string[];
}

export interface IUser {
  username: string;
  name: string;
}

export interface IVersioningMixin {
  version?: number;
  next_version?: string | null;
}

export interface IBaseAsset {
  url: string;
  title: string;
  description?: string;
  created?: string;
  modified?: string;
  owner?: string;
  virtual_lab?: string | null;
  shared_with_scopes?: string[]; // ISharingScope slug
  shared_with_users?: string[]; // User slug
}

export interface IFileAsset extends IBaseAsset {
  file: string;
}

export interface IWorkflowCell extends IBaseAsset, IVersioningMixin {}

export interface INotebookFile extends IFileAsset, IVersioningMixin {}

export interface IWorkflowFile extends IFileAsset, IVersioningMixin {}
