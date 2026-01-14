import React, { ReactNode } from 'react';
import Alert from '@mui/material/Alert';
import Stack from '@mui/material/Stack';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';

import { ListItem, LoadingListItem } from './list-item';
import { Asset, AssetKind } from './asset-kinds';

export function AssetsList({
  assets,
  assetKind,
  fetchAssetsListResponse,
  pageNav
}: {
  assets: Array<Asset>;
  assetKind: AssetKind;
  fetchAssetsListResponse: () => void;
  pageNav?: ReactNode;
}) {
  if (!assets.length) {
    return <Alert severity="info">No {assetKind.namePlural} to display.</Alert>;
  }

  return (
    <Stack spacing={3}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Title</TableCell>
            {'version' in assets[0] && <TableCell>Version</TableCell>}
            <TableCell>Owner</TableCell>
            <TableCell></TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {assets.map(asset => (
            <ListItem
              key={asset.url}
              asset={asset}
              assetKind={assetKind}
              fetchAssetsListResponse={fetchAssetsListResponse}
            />
          ))}
        </TableBody>
      </Table>
      {pageNav && pageNav}
    </Stack>
  );
}

export function LoadingAssetsList() {
  return (
    <Stack sx={{ marginTop: '56px' }}>
      <LoadingListItem />
      <LoadingListItem />
      <LoadingListItem />
    </Stack>
  );
}
