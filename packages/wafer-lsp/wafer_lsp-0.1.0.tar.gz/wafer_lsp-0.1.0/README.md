# Wafer LSP

Language Server Protocol server for CuTeDSL (Python GPU programming).

**Beta Feature**: Currently only available when Beta Mode is enabled in VS Code settings.

## Features

- **Hover Information**: Shows kernel and layout information with compiler analysis when hovering over CuTeDSL code

## Installation

```bash
pip install wafer-lsp
```

## Usage

### VS Code Extension

The LSP server is integrated into the `wevin-extension` VS Code extension. It starts automatically when Beta Mode is enabled.

### Standalone

For Neovim or other editors:

```bash
python -m wafer_lsp
```

## Supported Languages

- **CuTeDSL**: Python files with `@cute.kernel` decorators

## Architecture

The LSP server uses a modular language registry system. Currently supports CuTeDSL only. See `languages/README.md` for details on adding more languages.
