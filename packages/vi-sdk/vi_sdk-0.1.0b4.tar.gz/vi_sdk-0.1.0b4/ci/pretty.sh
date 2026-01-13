#!/bin/sh

ruff format vi tests examples
ruff check vi tests examples --fix
