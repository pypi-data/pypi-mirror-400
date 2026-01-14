import React, { useContext } from 'react';
import Alert from '@mui/material/Alert';
import IconButton from '@mui/material/IconButton';
import RefreshIcon from '@mui/icons-material/Refresh';
import Stack from '@mui/material/Stack';
import Tooltip from '@mui/material/Tooltip';

import { Asset, AssetKind } from './asset-kinds';
import { AssetsList, LoadingAssetsList } from './assets-list';
import { ISharingScope } from '../../types/NaaVRECatalogue/assets';
import { ListFilters } from './list-filters';
import { PageNav } from './page-nav';
import { SettingsContext } from '../../settings';
import { SharingScopesContext } from '../../contexts/SharingScopesContext';
import { UserInfoContext } from '../../contexts/UserInfoContext';
import { useCatalogueList } from '../../hooks/use-catalogue-list';
import { useUserInfo } from '../../hooks/use-user-info';

function RefreshButton({ onClick }: { onClick: () => void }) {
  return (
    <Tooltip title="Refresh">
      <IconButton
        aria-label="Refresh"
        style={{ borderRadius: '100%' }}
        onClick={onClick}
      >
        <RefreshIcon />
      </IconButton>
    </Tooltip>
  );
}

export function AssetsBrowser({ assetKind }: { assetKind: AssetKind }) {
  const settings = useContext(SettingsContext);
  const {
    setUrl: setAssetsListUrl,
    loading,
    errorMessage,
    setPaused: setAssetsListPaused,
    fetchResponse: fetchAssetsListResponse,
    response: assetsListResponse
  } = useCatalogueList<Asset>({
    catalogueServiceUrl: settings.catalogueServiceUrl,
    path: assetKind.cataloguePath,
    initialSearchParams: '?ordering=-created',
    startPaused: true
  });

  const { response: sharingScopesResponse } = useCatalogueList<ISharingScope>({
    catalogueServiceUrl: settings.catalogueServiceUrl,
    path: 'sharing-scopes',
    initialSearchParams: '?page_size=100',
    getAllPages: true
  });

  const userInfo = useUserInfo();

  return (
    <SharingScopesContext.Provider
      value={sharingScopesResponse?.results || null}
    >
      <UserInfoContext.Provider value={userInfo}>
        <Stack spacing={3}>
          <Stack
            direction="row"
            spacing={1}
            sx={{
              justifyContent: 'start',
              alignItems: 'center',
              padding: '10px'
            }}
          >
            <ListFilters
              setUrl={setAssetsListUrl}
              setPaused={setAssetsListPaused}
            />
            <RefreshButton onClick={() => fetchAssetsListResponse()} />
          </Stack>
          {loading ? (
            <LoadingAssetsList />
          ) : errorMessage ? (
            <Alert severity="error">{errorMessage}</Alert>
          ) : assetsListResponse === null ? (
            <Alert severity="error">
              Could not load {assetKind.namePlural}.
            </Alert>
          ) : (
            <AssetsList
              assets={assetsListResponse.results}
              assetKind={assetKind}
              fetchAssetsListResponse={fetchAssetsListResponse}
              pageNav={
                <PageNav
                  listResponse={assetsListResponse}
                  setUrl={setAssetsListUrl}
                />
              }
            />
          )}
        </Stack>
      </UserInfoContext.Provider>
    </SharingScopesContext.Provider>
  );
}
