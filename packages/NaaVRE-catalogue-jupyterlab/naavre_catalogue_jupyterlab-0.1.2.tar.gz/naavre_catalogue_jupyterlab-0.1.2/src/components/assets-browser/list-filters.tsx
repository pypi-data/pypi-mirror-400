import React, { ReactElement, useEffect, useState } from 'react';

import { ListFiltersSearch } from './list-filters-search';
import { ListFiltersOrdering } from './list-filters-ordering';
import { ListFiltersCheckboxes } from './list-filters-checkboxes';

export function updateSearchParams(
  url: string | null,
  params: { [key: string]: string | null }
): string | null {
  if (url === null) {
    return null;
  }
  const newUrl = new URL(url);
  for (const [key, value] of Object.entries(params)) {
    if (value === null || value === '') {
      newUrl.searchParams.delete(key);
    } else {
      newUrl.searchParams.set(key, value);
    }
  }
  return newUrl.toString();
}

interface IListFilter {
  setUrl: React.Dispatch<React.SetStateAction<string | null>>;
  setReady: (ready: boolean) => void;
}

const initialListfilters: {
  [key: string]: {
    Component: ({ setUrl, setReady }: IListFilter) => ReactElement;
    ready: boolean;
  };
} = {
  search: {
    Component: ListFiltersSearch,
    ready: false
  },
  checkboxes: {
    Component: ListFiltersCheckboxes,
    ready: false
  },
  ordering: {
    Component: ListFiltersOrdering,
    ready: false
  }
};

export function ListFilters({
  setUrl,
  setPaused
}: {
  setUrl: React.Dispatch<React.SetStateAction<string | null>>;
  setPaused: React.Dispatch<React.SetStateAction<boolean>>;
}) {
  const [listFilters, setListFilters] = useState(initialListfilters);

  const setReady = (key: string, ready: boolean) => {
    setListFilters(listFilters => {
      listFilters[key].ready = ready;
      return listFilters;
    });
  };

  const allReady: boolean = Object.values(listFilters).every(lf => lf.ready);

  useEffect(() => {
    setPaused(!allReady);
  }, [allReady]);

  return (
    <>
      {Object.entries(listFilters).map(([key, lf]) => (
        <lf.Component
          key={key}
          setUrl={setUrl}
          setReady={ready => setReady(key, ready)}
        />
      ))}
    </>
  );
}
