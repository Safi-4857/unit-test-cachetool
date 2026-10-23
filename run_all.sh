#!/bin/bash
# Runs the test groups in a fixed order. Each group runs in parallel (-n auto)
# except smoke, which runs serially so its pytest.mark.order sequence holds.
set -e
pytest -m smoke
pytest -n auto -m unit
pytest -n auto -m module
pytest -n auto -m data_driven
