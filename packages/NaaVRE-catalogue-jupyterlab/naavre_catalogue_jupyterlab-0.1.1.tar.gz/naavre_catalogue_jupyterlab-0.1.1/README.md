# NaaVRE_catalogue_jupyterlab

[![Github Actions Status](https://github.com/NaaVRE/NaaVRE-catalogue-jupyterlab/workflows/Build/badge.svg)](https://github.com/NaaVRE/NaaVRE-catalogue-jupyterlab/actions/workflows/build.yml)

NaaVRE assets catalogue frontend on Jupyter Lab

## Requirements

- JupyterLab >= 4.0.0

## Install

To install the extension, execute:

```bash
pip install NaaVRE_catalogue_jupyterlab
```

## Uninstall

To remove the extension, execute:

```bash
pip uninstall NaaVRE_catalogue_jupyterlab
```

## Contributing

### Development install

Note: You will need NodeJS to build the extension package.

The `jlpm` command is JupyterLab's pinned version of
[yarn](https://yarnpkg.com/) that is installed with JupyterLab. You may use
`yarn` or `npm` in lieu of `jlpm` below.

```bash
# Clone the repo to your local environment
# Change directory to the NaaVRE_catalogue_jupyterlab directory

# Set up a virtual environment and install package in development mode
python -m venv venv
source venv/bin/activate

# Install jupyterlab and refresh the virtual environment
pip install 'jupyterlab>=4.0.0,<5'
. venv/bin/activate

# Install package in development mode
pip install --editable "."

# Link your development version of the extension with JupyterLab
jupyter labextension develop . --overwrite

# Rebuild extension Typescript source after making changes
# IMPORTANT: Unlike the steps above which are performed only once, do this step
# every time you make a change.
jlpm build
```

This extension communicates with external NaaVRE services. During development, you can run a local version of those services with Docker compose. Initial setup:

1. Copy the Jupyter Lab configuration
   ```bash
   mkdir venv/share/jupyter/lab/settings/
   cp dev/overrides.json venv/share/jupyter/lab/settings/
   ```
2. Start docker compose
   ```bash
   docker compose -f dev/docker-compose.yaml up
   ```

You can watch the source directory and run JupyterLab at the same time in different terminals to watch for changes in the extension's source and automatically rebuild the extension.

```bash
# Watch the source directory in one terminal, automatically rebuilding when needed
jlpm watch
# Run JupyterLab in another terminal
export $(xargs < dev/jupyterlab.env && jupyter lab --notebook-dir ./notebook-dir
```

With the watch command running, every saved change will immediately be built locally and available in your running JupyterLab. Refresh JupyterLab to load the change in your browser (you may need to wait several seconds for the extension to be rebuilt).

By default, the `jlpm build` command generates the source maps for this extension to make it easier to debug using the browser dev tools. To also generate source maps for the JupyterLab core extensions, you can run the following command:

```bash
jupyter lab build --minimize=False
```

### Development uninstall

```bash
pip uninstall NaaVRE_catalogue_jupyterlab
```

In development mode, you will also need to remove the symlink created by `jupyter labextension develop`
command. To find its location, you can run `jupyter labextension list` to figure out where the `labextensions`
folder is located. Then you can remove the symlink named `@naavre/catalogue-jupyterlab` within that folder.

### Isolated component development

Rebuilding the extension and refreshing JupyterLab to see changes in the browser takes several seconds. This makes it hard to quickly iterate on presentation aspects such as layout.

To get a quick preview of some components, we use [Storybook](https://storybook.js.org/):

```shell
jlpm run storybook
```

Note that in Storybook, components don’t get the full context from Jupyter Lab and rely on some mocking. To access all interaction features, you still need to run it in JupyterLab.

### Testing the extension

#### Frontend tests

This extension is using [Jest](https://jestjs.io/) for JavaScript code testing.

To execute them, execute:

```sh
jlpm
jlpm test
```

#### Integration tests

This extension uses [Playwright](https://playwright.dev/docs/intro) for the integration tests (aka user level tests).
More precisely, the JupyterLab helper [Galata](https://github.com/jupyterlab/jupyterlab/tree/master/galata) is used to handle testing the extension in JupyterLab.

More information are provided within the [ui-tests](./ui-tests/README.md) README.

### Packaging the extension

See [RELEASE](RELEASE.md)
