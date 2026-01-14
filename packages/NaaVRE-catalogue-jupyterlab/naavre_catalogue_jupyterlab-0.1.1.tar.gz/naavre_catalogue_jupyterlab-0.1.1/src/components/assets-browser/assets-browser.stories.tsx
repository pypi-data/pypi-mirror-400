import type { Meta, StoryObj } from '@storybook/react-webpack5';

import { AssetsBrowser } from './assets-browser';
import { assetKinds } from './asset-kinds';

const meta = {
  component: AssetsBrowser
} satisfies Meta<typeof AssetsBrowser>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    assetKind: assetKinds[0]
  }
};
