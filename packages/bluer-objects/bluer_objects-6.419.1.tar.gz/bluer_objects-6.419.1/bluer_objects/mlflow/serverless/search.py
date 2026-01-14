from typing import List, Tuple, Union

from bluer_options.options import Options

from bluer_objects.mlflow.serverless import api
from bluer_objects.logger import logger


def search(
    filter_string: Union[str, dict],
    log: bool = False,
) -> Tuple[bool, List[str]]:
    query = Options(filter_string)

    output: Union[List[str], None] = None
    for key, value in query.items():
        success, dict_of_objects = api.read(
            object_name="_serverless_keys",
            filename=f"{key}.yaml",
            verbose=log,
        )
        if not success:
            return False, []

        output = [
            object_name
            for object_name in (dict_of_objects if output is None else output)
            if dict_of_objects.get(
                object_name,
                False if isinstance(value, bool) else None,
            )
            == value
        ]

    return True, [] if output is None else output
