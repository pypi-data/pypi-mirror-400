import React from 'react';
import {
  createFileRoute,
  Outlet,
  useNavigate,
  useRouterState
} from '@tanstack/react-router';
import { Button, Stack, ToggleButton, ToggleButtonGroup } from '@mui/material';
import { assetKinds } from '../../components/assets-browser/asset-kinds';

export const Route = createFileRoute('/assets')({
  component: RouteComponent
});

function RouteComponent() {
  const navigate = useNavigate();
  const state = useRouterState();
  return (
    <Stack spacing={4}>
      <Stack direction="row" spacing={2}>
        <Button variant="outlined" onClick={() => navigate({ to: '/' })}>
          Home
        </Button>
        <ToggleButtonGroup
          value={state.location.pathname}
          onChange={(e, href) => navigate({ to: href })}
          exclusive
          aria-label="Asset kind"
          color="primary"
        >
          {assetKinds.map(assetKind => (
            <ToggleButton
              key={assetKind.slug}
              value={`/assets/${assetKind.slug}`}
              aria-label="left aligned"
            >
              {assetKind.namePlural}
            </ToggleButton>
          ))}
        </ToggleButtonGroup>
      </Stack>
      <Outlet />
    </Stack>
  );
}
