#!/usr/bin/env bash

set -x

PYTHONPATH=. pytest -p no:labgrid -v tests
