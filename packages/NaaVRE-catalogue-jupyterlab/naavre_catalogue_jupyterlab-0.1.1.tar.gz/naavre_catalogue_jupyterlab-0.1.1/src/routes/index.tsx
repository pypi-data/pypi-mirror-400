import React from 'react';
import { Button, Stack, Typography } from '@mui/material';
import { createFileRoute, useNavigate } from '@tanstack/react-router';

import {
  AssetKind,
  assetKinds
} from '../components/assets-browser/asset-kinds';

export const Route = createFileRoute('/')({
  component: Launcher
});
function LauncherItem({ assetKind }: { assetKind: AssetKind }) {
  const navigate = useNavigate();
  return (
    <Button
      variant="outlined"
      onClick={() => navigate({ to: `/assets/${assetKind.slug}` })}
    >
      {assetKind.namePlural}
    </Button>
  );
}

export function Launcher() {
  return (
    <Stack direction="column" spacing={3}>
      <Typography variant="h4">Assets catalogue</Typography>
      <Stack direction="row" spacing={2}>
        {assetKinds.map(assetKind => (
          <LauncherItem key={assetKind.slug} assetKind={assetKind} />
        ))}
      </Stack>
    </Stack>
  );
}
