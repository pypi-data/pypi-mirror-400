#! /usr/bin/env bash
# Reset this var to be sure no addons_path is find
export ADDONS_GIT_CLOUD_MODULES="False"
git config --global --add safe.directory .
python --version
pip --version
pip install -U pip
pip install --no-input --disable-pip-version-check --no-python-version-warning --verbose  .
python -m unittest discover -s tests -t ./
