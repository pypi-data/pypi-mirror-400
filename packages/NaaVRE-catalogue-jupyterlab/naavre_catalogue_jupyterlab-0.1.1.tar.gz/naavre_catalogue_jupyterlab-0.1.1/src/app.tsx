import React, { StrictMode } from 'react';
import {
  createHashHistory,
  createRouter,
  RouterProvider
} from '@tanstack/react-router';
import { routeTree } from './routeTree.gen';

const router = createRouter({
  routeTree,
  history: createHashHistory(),
  basepath: 'naavre-catalogue'
});

// Register the router instance for type safety
declare module '@tanstack/react-router' {
  // Tanstack router requires `Register` interface, which differs from Jupyter
  // lab's naming rule. We ignore the rule here to avoid lint errors.
  // eslint-disable-next-line @typescript-eslint/naming-convention
  interface Register {
    router: typeof router;
  }
}

export function App() {
  return (
    <StrictMode>
      <RouterProvider router={router} />
    </StrictMode>
  );
}
