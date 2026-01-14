import React, { useEffect, useState } from 'react';
import IconButton from '@mui/material/IconButton';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import SwapVertIcon from '@mui/icons-material/SwapVert';
import Tooltip from '@mui/material/Tooltip';
import { updateSearchParams } from './list-filters';

const orderingOptions = [
  { value: 'created', title: 'First created' },
  { value: '-created', title: 'Last created' },
  { value: 'title', title: 'A-Z' },
  { value: '-name', title: 'Z-A' }
];

export function ListFiltersOrdering({
  setUrl,
  setReady
}: {
  setUrl: React.Dispatch<React.SetStateAction<string | null>>;
  setReady: (ready: boolean) => void;
}) {
  const [ordering, setOrdering] = useState<string | null>('-created');

  useEffect(() => {
    setUrl((url: string | null) =>
      updateSearchParams(url, {
        ordering: ordering,
        page: null
      })
    );
    setReady(true);
  }, [ordering]);

  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  return (
    <>
      <Tooltip title="Order">
        <IconButton
          id="ordering-button"
          aria-label="Order"
          aria-controls={open ? 'ordering-menu' : undefined}
          aria-expanded={open ? 'true' : undefined}
          aria-haspopup="true"
          style={{
            borderRadius: '100%'
          }}
          onClick={e => setAnchorEl(e.currentTarget)}
        >
          <SwapVertIcon />
        </IconButton>
      </Tooltip>
      <Menu
        id="ordering-menu"
        anchorEl={anchorEl}
        open={open}
        onClose={() => setAnchorEl(null)}
        slotProps={{
          list: {
            'aria-labelledby': 'ordering-button'
          }
        }}
      >
        {orderingOptions.map(option => (
          <MenuItem
            key={option.value}
            selected={option.value === ordering}
            onClick={() => {
              setOrdering(option.value);
              setAnchorEl(null);
            }}
          >
            {option.title}
          </MenuItem>
        ))}
      </Menu>
    </>
  );
}
