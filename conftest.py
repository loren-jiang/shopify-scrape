import pytest
import os
import shutil

@pytest.fixture(scope='module')
def products_dir(tmp_path_factory):
    path = tmp_path_factory.mktemp("products_temp")
    yield path
    shutil.rmtree(path.getbasetemp())

