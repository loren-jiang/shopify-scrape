import pytest
import os
import shutil

@pytest.fixture(scope='module')
def logs_dir():
    os.makedirs('logs', exist_ok=True)
    

@pytest.fixture(scope='module')
def products_dir(tmp_path_factory):
    path = tmp_path_factory.mktemp("products_temp")
    yield path
    shutil.rmtree(path)

@pytest.fixture(scope='module')
def good_shop_domain():
    return 'bombas.com'
