# vtx-protocol

**Official WIT interface definitions for VTX Project.**

This package serves as a carrier for the VTX WIT (WebAssembly Interface Type) definitions. It provides Python tooling access to the official protocol contract.

> **Building a Plugin?** Please use the **VTX SDK** for Python. This package is a low-level dependency used to locate the interface definitions.

## Installation

```bash
pip install vtx-protocol

```

## Usage

```python
import vtx_protocol

# Get the absolute path to the bundled vtx.wit file
wit_path = vtx_protocol.get_wit_path()

print(f"Loading WIT from: {wit_path}")

```