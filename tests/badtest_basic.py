import pytest
from proyectocc.main import funcTestFunc

def test_sample():
    assert funcTestFunc("project/CUEs/Schumann - Test - FLAC.cue") == dict