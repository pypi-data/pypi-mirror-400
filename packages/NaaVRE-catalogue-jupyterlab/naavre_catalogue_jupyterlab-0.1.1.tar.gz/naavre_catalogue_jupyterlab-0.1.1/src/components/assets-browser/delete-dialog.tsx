import React, { useCallback, useState } from 'react';
import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import LinearProgress from '@mui/material/LinearProgress';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import { NaaVREExternalService } from '@naavre/communicator-jupyterlab';

import { Asset, AssetKind } from './asset-kinds';

function ShredWithWarning({
  sharedWithList,
  label
}: {
  sharedWithList?: string[];
  label: string;
}) {
  if (!(sharedWithList && sharedWithList.length > 0)) {
    return <></>;
  }
  return (
    <Stack spacing={1}>
      <DialogContentText>
        The following {label} will lose access:
      </DialogContentText>
      <DialogContentText component="ul">
        {sharedWithList.map(sharedWith => (
          <DialogContentText key={sharedWith} component="li">
            {sharedWith}
          </DialogContentText>
        ))}
      </DialogContentText>
    </Stack>
  );
}

export function DeleteDialog({
  open,
  onClose,
  onUpdated,
  asset,
  assetKind,
  readonly
}: {
  open: boolean;
  onClose: () => void;
  onUpdated: () => void;
  asset: Asset;
  assetKind: AssetKind;
  readonly: boolean;
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirmText, setConfirmText] = useState('');

  const deleteAsset = useCallback(async () => {
    const resp = await NaaVREExternalService('DELETE', asset.url, {
      accept: 'application/json'
    });
    if (resp.status_code !== 204) {
      throw `${resp.status_code} ${resp.reason}`;
    }
  }, [asset]);

  return (
    <Dialog onClose={onClose} open={open}>
      <DialogTitle>Delete {asset.title}</DialogTitle>
      <DialogContent>
        {readonly ? (
          <Alert severity="info" sx={{ mb: 2 }}>
            You cannot delete this asset because it belongs to another user.
          </Alert>
        ) : (
          <Stack spacing={2}>
            <DialogContentText>
              You are about to delete the following {assetKind.name}:
            </DialogContentText>
            <DialogContentText
              style={{ fontWeight: 'bold', marginLeft: '1.5rem' }}
            >
              {asset.title}
            </DialogContentText>
            <ShredWithWarning
              label="users"
              sharedWithList={asset.shared_with_users}
            />
            <ShredWithWarning
              label="virtual labs or communities"
              sharedWithList={asset.shared_with_scopes}
            />
            <DialogContentText>
              To confirm, type "
              <span style={{ fontWeight: 'bold' }}>{asset.title}</span>" in the
              box below
            </DialogContentText>
            <TextField
              value={confirmText}
              sx={{
                '& .MuiOutlinedInput-root': {
                  '& .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'error.main'
                  },
                  '&:hover .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'error.main'
                  },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'error.main'
                  }
                }
              }}
              onChange={event => setConfirmText(event.currentTarget.value)}
            />
          </Stack>
        )}
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            Cannot delete asset: {error}
          </Alert>
        )}
        {loading && <LinearProgress sx={{ mt: 2 }} />}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          color="error"
          disabled={readonly || confirmText !== asset.title}
          onClick={async () => {
            setError(null);
            setLoading(true);
            deleteAsset()
              .then(onClose)
              .then(onUpdated)
              .catch(e => setError(`${e}`))
              .finally(() => setLoading(false));
          }}
        >
          Delete this {assetKind.name}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
