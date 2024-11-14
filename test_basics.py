import pytest
from main import funcTestFunc

def test_sample():
    assert funcTestFunc("CUEs/Schumann - Test - FLAC.cue") == dict