import { INaaVREExternalServiceResponse } from '@naavre/communicator-jupyterlab';

import {
  IFileAsset,
  IVersioningMixin
} from '../../types/NaaVRECatalogue/assets';

// FIXME: make it realistic
export const notebooks: (IFileAsset & IVersioningMixin)[] = [
  {
    url: 'http://localhost:8000/notebook-files/cbd0bc89-7418-4536-a8c4-6eb3bb6bf2e6/',
    owner: 'fixture-user-1',
    virtual_lab: 'test-virtual-lab-1',
    shared_with_scopes: ['test-community-1'],
    shared_with_users: [],
    title: 'nb-shared-with-community.ipynb',
    description: 'Description of nb-shared-with-community',
    created: '2025-09-19T18:48:23.397000Z',
    modified: '2025-09-19T18:48:23.397000Z',
    version: 1,
    next_version: null,
    file: ''
  },
  {
    url: 'http://localhost:8000/notebook-files/d7fa87ca-79a3-43eb-993a-83afec93f1e4/',
    owner: 'fixture-user-1',
    virtual_lab: 'test-virtual-lab-1',
    shared_with_scopes: ['test-virtual-lab-1'],
    shared_with_users: [],
    title: 'nb-shared-with-vl-1.ipynb',
    description: 'Description of nb-shared-with-vl-1',
    created: '2025-09-19T18:48:23.397000Z',
    modified: '2025-09-19T18:48:23.397000Z',
    version: 1,
    next_version: null,
    file: ''
  },
  {
    url: 'http://localhost:8000/notebook-files/77e49ffb-7688-40c5-8287-6693ae3d096a/',
    owner: 'fixture-user-1',
    virtual_lab: 'test-virtual-lab-2',
    shared_with_scopes: ['test-virtual-lab-2'],
    shared_with_users: [],
    title: 'nb-shared-with-vl-2.ipynb',
    description: 'Description of nb-shared-with-vl-2',
    created: '2025-09-19T18:48:23.397000Z',
    modified: '2025-09-19T18:48:23.397000Z',
    version: 1,
    next_version: null,
    file: ''
  },
  {
    url: 'http://localhost:8000/notebook-files/a9ad6181-e78c-45b0-83c1-69385b9f9404/',
    owner: 'fixture-user-1',
    virtual_lab: 'test-virtual-lab-1',
    shared_with_scopes: [],
    shared_with_users: ['test-user-2'],
    title: 'nb-shared-with-user.ipynb',
    description: 'Description of nb-shared-with-user',
    created: '2025-09-19T18:48:23.397000Z',
    modified: '2025-09-19T18:48:23.397000Z',
    version: 1,
    next_version: null,
    file: ''
  },
  {
    url: 'http://localhost:8000/notebook-files/3995b067-95fd-4706-9325-2b89339afb2c/',
    owner: 'test-user-2',
    virtual_lab: 'test-virtual-lab-2',
    shared_with_scopes: [],
    shared_with_users: [],
    title: 'other-vl-nb-1-test-user-2.ipynb',
    description: 'Description of other-vl-nb-1-test-user-2',
    created: '2025-01-19T21:40:23.503000Z',
    modified: '2025-01-19T21:40:23.503000Z',
    version: 1,
    next_version: null,
    file: ''
  },
  {
    url: 'http://localhost:8000/notebook-files/57c32902-cd0b-4c59-8307-08456e4bfe30/',
    owner: 'test-user-2',
    virtual_lab: 'test-virtual-lab-1',
    shared_with_scopes: ['test-virtual-lab-1'],
    shared_with_users: [],
    title: 'test-nb-3-test-user-2.ipynb',
    description: 'Description of test-nb-3-test-user-2',
    created: '2025-01-19T21:37:23.503000Z',
    modified: '2025-01-19T21:37:23.503000Z',
    version: 1,
    next_version: null,
    file: ''
  },
  {
    url: 'http://localhost:8000/notebook-files/b6923c9e-eeb6-49fe-81f2-3df7003f8332/',
    owner: 'test-user-2',
    virtual_lab: 'test-virtual-lab-1',
    shared_with_scopes: [],
    shared_with_users: [],
    title: 'test-nb-2-with-a-looooooooooooooong-name-test-user-2.ipynb',
    description:
      'Description of test-nb-2-with-a-looooooooooooooong-name-test-user-2',
    created: '2025-01-19T21:39:53.924000Z',
    modified: '2025-01-19T21:39:53.924000Z',
    version: 1,
    next_version: null,
    file: ''
  },
  {
    url: 'http://localhost:8000/notebook-files/d1d41322-1101-489c-82a1-8038ea999416/',
    owner: 'test-user-2',
    virtual_lab: 'test-virtual-lab-1',
    shared_with_scopes: [],
    shared_with_users: [],
    title: 'test-nb-1-test-user-2.ipynb',
    description: 'Description of test-nb-1-test-user-2',
    created: '2025-01-19T21:37:23.503000Z',
    modified: '2025-01-19T21:37:23.503000Z',
    version: 1,
    next_version: null,
    file: ''
  },
  {
    url: 'http://localhost:8000/notebook-files/b58c627a-1843-421c-a897-89461ddc581a/',
    owner: 'test-user-2',
    virtual_lab: 'test-virtual-lab-1',
    shared_with_scopes: [],
    shared_with_users: [],
    title: 'test-nb-1-test-user-2.ipynb',
    description: 'Description of test-nb-1-test-user-2',
    created: '2025-01-19T21:38:23.503000Z',
    modified: '2025-01-19T21:37:23.503000Z',
    version: 1,
    next_version: null,
    file: ''
  }
];

export async function getNotebooksList(
  request: Request
): Promise<INaaVREExternalServiceResponse> {
  return {
    status_code: 200,
    reason: 'OK',
    headers: {
      'content-type': 'application/json'
    },
    content: JSON.stringify({
      count: notebooks.length,
      next: null,
      previous: null,
      results: notebooks
    })
  };
}

export async function patchNotebook(
  request: Request
): Promise<INaaVREExternalServiceResponse> {
  return {
    status_code: 200,
    reason: 'OK',
    headers: {
      'content-type': 'application/json'
    },
    content: JSON.stringify(notebooks[0])
  };
}

export async function deleteNotebook(
  request: Request
): Promise<INaaVREExternalServiceResponse> {
  return {
    status_code: 204,
    reason: 'OK',
    headers: {
      'content-type': 'application/json'
    },
    content: JSON.stringify({})
  };
}
