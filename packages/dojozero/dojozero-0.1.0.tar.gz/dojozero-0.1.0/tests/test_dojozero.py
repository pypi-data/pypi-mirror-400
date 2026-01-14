import pytest
import dojozero


def test_version():
    assert dojozero.__version__ == "0.1.0"


def test_import():
    # Basic import test
    assert dojozero is not None
