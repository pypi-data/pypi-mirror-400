# ipycobe

[![JupyterLite](https://jupyterlite.rtfd.io/en/latest/_static/badge-launch.svg)](https://jtpio.github.io/ipycobe/)

A Jupyter Widget for rendering an interactive globe, based on [cobe](https://cobe.vercel.app/) and built with [anywidget](https://anywidget.dev/).

![screenshot of ipycobe in a Jupyter notebook](screenshot.png)

## Installation

```sh
pip install ipycobe
```

or with [uv](https://github.com/astral-sh/uv):

```sh
uv add ipycobe
```

## Development

We recommend using [uv](https://github.com/astral-sh/uv) for development.
It will automatically manage virtual environments and dependencies for you.

```sh
uv run jupyter lab example.ipynb
```

Alternatively, create and manage your own virtual environment:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
jupyter lab example.ipynb
```

The widget front-end code bundles its JavaScript dependencies. After setting up Python,
make sure to install these dependencies locally:

```sh
pnpm install
```

While developing, you can run the following in a separate terminal to automatically
rebuild JavaScript as you make changes:

```sh
pnpm dev
```

Open `example.ipynb` in JupyterLab, VS Code, or your favorite editor
to start developing. Changes made in `js/` will be reflected
in the notebook.
