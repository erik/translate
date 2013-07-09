#!/usr/bin/env bash

# This is a simple hacky way I update the docs. Not very useful if you're not me

set -e

cd ../translate/docs
make html
cp build/html/* -R ../../translate-docs/
