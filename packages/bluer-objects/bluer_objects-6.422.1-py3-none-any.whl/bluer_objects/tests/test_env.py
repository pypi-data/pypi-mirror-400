from bluer_ai.tests.test_env import test_bluer_ai_env

from bluer_objects import env
from bluer_objects.storage import (
    S3Interface,
    WebDAVInterface,
    WebDAVRequestInterface,
    WebDAVzipInterface,
)


def test_required_env():
    test_bluer_ai_env()


def test_bluer_objects_env():
    for var in [
        env.MLFLOW_IS_SERVERLESS,
    ]:
        assert var in (0, 1)

    for var in [
        env.ABCLI_MLFLOW_EXPERIMENT_PREFIX,
        env.BLUER_OBJECTS_DEFAULT_ASSETS_VOL,
        env.BLUER_OBJECTS_TEST_OBJECT,
        env.MLFLOW_DEPLOYMENT,
        env.S3_PUBLIC_STORAGE_BUCKET,
        env.S3_STORAGE_AWS_ACCESS_KEY_ID,
        env.S3_STORAGE_AWS_SECRET_ACCESS_KEY,
        env.S3_STORAGE_BUCKET,
        env.S3_STORAGE_ENDPOINT_URL,
        env.WEBDAV_HOSTNAME,
        env.WEBDAV_LOGIN,
        env.WEBDAV_PASSWORD,
    ]:
        assert isinstance(var, str)
        assert var

    for var in [
        env.MLFLOW_LOCK_WAIT_FOR_CLEARANCE,
        env.MLFLOW_LOCK_WAIT_FOR_EXCLUSIVITY,
    ]:
        assert isinstance(var, int)
        assert var > 0

    assert env.BLUER_OBJECTS_STORAGE_INTERFACE in [
        S3Interface.name,
        WebDAVInterface.name,
        WebDAVRequestInterface.name,
        WebDAVzipInterface.name,
    ]
