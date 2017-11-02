
import os

def from_test_dir(filename):
    return os.path.join(os.path.dirname(__file__), filename)
