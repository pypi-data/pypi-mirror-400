# H2O Secure Store

H2O Secure Store Python client.
This Python client implements interaction with the Secure Store REST API server.

## Local development

This python project is managed by [hatch](https://github.com/pypa/hatch) (environment management, version management,
dependency management, building, publishing, etc.).

You're free to use any tools for local development for managing python environments that you're comfortable with.

## Usage

### Run using hatch

You can run H2O Secure Store Python client using Hatch.
Hatch will automatically create an environment and install all required dependencies:

```shell
hatch run python local/example.py
```

You can also switch to hatch's environment and run commands in it:

```shell
hatch shell
python local/example.py
```

### Run in custom env

If you want to use your own environment for running the client (global, virtual env, etc.), you can do so.
For example to build, install and run H2O Secure Store Python client in the current python env:

```shell
hatch build
pip install dist/h2o_secure_store-*.whl
python local/example.py
```
