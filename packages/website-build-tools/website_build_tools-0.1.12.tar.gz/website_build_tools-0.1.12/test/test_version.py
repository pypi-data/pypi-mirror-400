"""Test documentation."""

import os

import pytest
import webtools


def test_vesion_numbers():
    if not os.path.isfile(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "../pyproject.toml")
    ):
        pytest.skip("Not running in source directory")
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../pyproject.toml")) as f:
        version = f.read().split('version = "')[1].split('"')[0]

    assert webtools.__version__ == version
