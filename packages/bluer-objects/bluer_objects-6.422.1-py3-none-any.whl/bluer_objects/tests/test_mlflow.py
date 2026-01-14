import pytest

from bluer_options import string
from bluer_options.options import Options
from bluer_options.testing import is_list_of_str

from bluer_objects import env
from bluer_objects.objects import unique_object
from bluer_objects.mlflow import cache
from bluer_objects.mlflow import create_server_style_filter_string
from bluer_objects.mlflow import objects
from bluer_objects.mlflow import tags
from bluer_objects.mlflow import testing


def test_from_and_to_experiment_name():
    object_name = unique_object("test_from_and_to_experiment_name")

    assert (
        objects.to_object_name(objects.to_experiment_name(object_name)) == object_name
    )


def test_mlflow_testing():
    MLFLOW_IS_SERVERLESS = env.MLFLOW_IS_SERVERLESS
    env.MLFLOW_IS_SERVERLESS = False

    assert testing.test()

    env.MLFLOW_IS_SERVERLESS = MLFLOW_IS_SERVERLESS


@pytest.mark.parametrize(
    ["tags_str"],
    [["x=1,y=2,z=3"]],
)
@pytest.mark.parametrize(
    ["serverless"],
    [
        [False],
        [True],
    ],
)
def test_mlflow_tags_set_get(
    tags_str: str,
    serverless: bool,
):
    MLFLOW_IS_SERVERLESS = env.MLFLOW_IS_SERVERLESS
    env.MLFLOW_IS_SERVERLESS = serverless

    object_name = unique_object("test_mlflow_tag_set_get")

    assert tags.set_tags(
        object_name,
        tags_str,
        log=False,
    )

    success, tags_read = tags.get_tags(object_name)
    assert success

    tags_option = Options(tags_str)
    for keyword, value in tags_option.items():
        assert tags_read[keyword] == value

    env.MLFLOW_IS_SERVERLESS = MLFLOW_IS_SERVERLESS


@pytest.mark.parametrize(
    [
        "filter_string",
        "server_style",
        "serverless",
        "success_expected",
    ],
    [
        [
            "this=that,what,~who",
            False,
            True,
            True,
        ],
        [
            "this=that,what,~who",
            False,
            False,
            True,
        ],
        [
            'tags."this" = "that" and tags."what" = "True" and tags."who" = "False"',
            True,
            True,
            False,
        ],
        [
            'tags."this" = "that" and tags."what" = "True" and tags."who" = "False"',
            True,
            False,
            True,
        ],
    ],
)
def test_mlflow_tags_search(
    filter_string: str,
    server_style: bool,
    serverless: bool,
    success_expected: bool,
):
    MLFLOW_IS_SERVERLESS = env.MLFLOW_IS_SERVERLESS
    env.MLFLOW_IS_SERVERLESS = serverless

    success, list_of_objects = tags.search(
        filter_string,
        server_style=server_style,
    )

    assert success == success_expected
    assert is_list_of_str(list_of_objects)

    env.MLFLOW_IS_SERVERLESS = MLFLOW_IS_SERVERLESS


@pytest.mark.parametrize(
    ["keyword", "value"],
    [
        [
            f"test_mlflow_cache_read_write-keyword-{string.random()}",
            string.random(),
        ]
    ],
)
@pytest.mark.parametrize(
    ["serverless"],
    [
        [True],
        [False],
    ],
)
def test_mlflow_cache_read_write(
    keyword: str,
    value: str,
    serverless: bool,
):
    MLFLOW_IS_SERVERLESS = env.MLFLOW_IS_SERVERLESS
    env.MLFLOW_IS_SERVERLESS = serverless

    assert cache.write(keyword, value)

    success, value_read = cache.read(keyword)
    assert success
    assert value_read == value

    env.MLFLOW_IS_SERVERLESS = MLFLOW_IS_SERVERLESS


@pytest.mark.parametrize(
    ["filter_string", "expected_output"],
    [
        [
            "this=that,what,~who",
            'tags."this" = "that" and tags."what" = "True" and tags."who" = "False"',
        ]
    ],
)
def test_create_server_style_filter_string(
    filter_string: str,
    expected_output: str,
):
    assert create_server_style_filter_string(filter_string) == expected_output
