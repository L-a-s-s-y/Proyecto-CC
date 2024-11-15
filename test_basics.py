import pytest
from main import funcTestFunc

def test_sample():
    assert funcTestFunc("tests/Three Samples_ASCII.cue") == dict