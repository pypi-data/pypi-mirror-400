from typing import Dict, Union

from blueness import module
from bluer_options.options import Options

from bluer_objects import NAME
from bluer_objects.mlflow.serverless import api
from bluer_objects.logger import logger

NAME = module.name(__file__, NAME)


def set_tags(
    object_name: str,
    tags: Union[str, Dict[str, str]],
    log: bool = True,
    verbose: bool = False,
    icon="#️⃣ ",
) -> bool:
    tags = Options(tags)

    if not api.write(
        object_name="_serverless_objects",
        filename=f"{object_name}.yaml",
        data=tags,
        log=verbose,
    ):
        return False

    for key, value in tags.items():
        if not api.write(
            object_name="_serverless_keys",
            filename=f"{key}.yaml",
            data={object_name: value},
            log=verbose,
        ):
            return False

        if log:
            logger.info("{} {}.{}={}".format(icon, object_name, key, value))

    return True
