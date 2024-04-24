import pytest
import os
from main import Invoice


def test_create_invoice():
    path_to_file = "testfile.txt"
    assert not os.path.exists(path_to_file)
    Invoice(path_to_file)
    assert os.path.exists(path_to_file)
    os.remove(path_to_file)