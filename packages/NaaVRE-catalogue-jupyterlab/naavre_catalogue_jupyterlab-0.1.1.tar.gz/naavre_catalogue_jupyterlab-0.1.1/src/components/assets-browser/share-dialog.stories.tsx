import React from 'react';
import type { Meta, StoryObj } from '@storybook/react-webpack5';

import { cells as mockCells } from '../../mocks/catalogue-service/workflow-cells';
import { sharingScopes as mockSharingScopes } from '../../mocks/catalogue-service/sharing-scopes';
import { ShareDialog } from './share-dialog';
import { SharingScopesContext } from '../../contexts/SharingScopesContext';

const meta = {
  component: ShareDialog
} satisfies Meta<typeof ShareDialog>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    open: true,
    readonly: false,
    onClose: () => {},
    onUpdated: () => {},
    asset: mockCells[0]
  },
  decorators: [
    (Story, { parameters }) => {
      return (
        <SharingScopesContext.Provider value={mockSharingScopes}>
          <Story />
        </SharingScopesContext.Provider>
      );
    }
  ]
};
