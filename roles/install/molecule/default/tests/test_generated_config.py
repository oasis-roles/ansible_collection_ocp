import pytest


@pytest.fixture(scope='module')
def expected_config(request):
    tests_dir = request.fspath.dirpath()
    install_config = tests_dir.join('data').join('install-config.yaml')
    return install_config.read()


def test_install_config_contents(host, expected_config):
    generated = host.file('/ocp_install/install-config.yaml').content_string
    assert generated.strip() == expected_config.strip()
