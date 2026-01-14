import { useCallback, useEffect, useState } from 'react';
import {
  fetchListFromCatalogue,
  ICatalogueListResponse
} from '../utils/catalog';

function getUrl(
  catalogueServiceUrl: string | undefined,
  path: string,
  initialSearchParams: string
) {
  return catalogueServiceUrl
    ? `${catalogueServiceUrl}/${path}/${initialSearchParams}`
    : null;
}

export function useCatalogueList<T>({
  catalogueServiceUrl,
  path,
  initialSearchParams,
  startPaused = false,
  getAllPages
}: {
  catalogueServiceUrl: string | undefined;
  path: string;
  initialSearchParams: string;
  startPaused?: boolean;
  getAllPages?: boolean;
}) {
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [paused, setPaused] = useState(startPaused);

  const [url, setUrl] = useState<string | null>(
    getUrl(catalogueServiceUrl, path, initialSearchParams)
  );

  useEffect(() => {
    setUrl(url =>
      url !== null
        ? getUrl(catalogueServiceUrl, path, new URL(url).search)
        : catalogueServiceUrl
          ? getUrl(catalogueServiceUrl, path, initialSearchParams)
          : null
    );
  }, [catalogueServiceUrl, path, initialSearchParams]);

  const [response, setResponse] = useState<ICatalogueListResponse<T> | null>(
    null
  );

  const fetchResponse = useCallback(() => {
    setErrorMessage && setErrorMessage(null);
    setLoading && setLoading(true);
    if (url) {
      fetchListFromCatalogue<T>(url, getAllPages)
        .then(resp => {
          setResponse(resp);
        })
        .catch(error => {
          const msg = `Error listing items: ${String(error)}`;
          console.error(msg);
          setErrorMessage && setErrorMessage(msg);
          setResponse(null);
        })
        .finally(() => {
          setLoading && setLoading(false);
        });
    }
  }, [url]);

  useEffect(() => {
    if (!paused) {
      fetchResponse();
    }
  }, [paused, fetchResponse]);

  return {
    url,
    setUrl,
    loading,
    setLoading,
    errorMessage,
    setErrorMessage,
    paused,
    setPaused,
    fetchResponse,
    response
  };
}
