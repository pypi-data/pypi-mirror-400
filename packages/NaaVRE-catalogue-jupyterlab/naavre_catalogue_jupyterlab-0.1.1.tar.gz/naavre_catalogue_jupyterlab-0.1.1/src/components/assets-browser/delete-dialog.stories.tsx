import type { Meta, StoryObj } from '@storybook/react-webpack5';

import { cells as mockCells } from '../../mocks/catalogue-service/workflow-cells';
import { DeleteDialog } from './delete-dialog';
import { assetKinds } from './asset-kinds';

const meta = {
  component: DeleteDialog
} satisfies Meta<typeof DeleteDialog>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    open: true,
    readonly: false,
    onClose: () => {},
    onUpdated: () => {},
    asset: mockCells[0],
    assetKind: assetKinds[1]
  }
};
