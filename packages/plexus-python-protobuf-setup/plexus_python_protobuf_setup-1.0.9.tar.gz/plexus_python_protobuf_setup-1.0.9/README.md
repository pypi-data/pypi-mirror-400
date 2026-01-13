# Plexus Python Protocol Buffer Setup Module

[![codecov](https://codecov.io/gh/ruyangshou/plexus-python-protobuf-setup/graph/badge.svg?token=J4rQVKXeRx)](
https://codecov.io/gh/ruyangshou/plexus-python-protobuf-setup)

## Usage

1. **Modify the `pyproject.toml` file** as follows:
    ```toml
    [build-system]
    requires = [
        "setuptools>=80.0",
        "setuptools-scm>=9.0",
        "plexus-python-protobuf-setup>=1.0"  # This is required
    ]
    ```
2. **Use this tool in your `setup.py` script**:
    ```python
    import os
    from setuptools import setup
    from plexus.protobuf.setup import compile_protos
   
    # Call this code generation before setup
    compile_protos(out_dir,
                   proto_dirs,
                   include_dirs,
                   descriptor_path=os.path.join(out_dir, "descriptor.proto"))
    setup()
    ```
