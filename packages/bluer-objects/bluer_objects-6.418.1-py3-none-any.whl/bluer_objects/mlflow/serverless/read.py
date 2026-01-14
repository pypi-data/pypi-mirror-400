from typing import Tuple, Dict

from blueness import module

from bluer_objects import NAME
from bluer_objects.mlflow.serverless import api

NAME = module.name(__file__, NAME)


def get_tags(
    object_name: str,
    verbose: bool = False,
) -> Tuple[bool, Dict[str, str]]:
    return api.read(
        object_name="_serverless_objects",
        filename=f"{object_name}.yaml",
        verbose=verbose,
    )
