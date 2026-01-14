import { createContext } from 'react';

import { ISharingScope } from '../types/NaaVRECatalogue/assets';

export const SharingScopesContext = createContext<ISharingScope[] | null>(null);
