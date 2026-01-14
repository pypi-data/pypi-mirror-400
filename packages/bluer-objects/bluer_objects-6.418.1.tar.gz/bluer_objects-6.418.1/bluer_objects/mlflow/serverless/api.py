from typing import Dict, Tuple

from blueness import module

from bluer_objects import NAME
from bluer_objects import file
from bluer_objects import objects
from bluer_objects import storage
from bluer_objects.logger import logger

NAME = module.name(__file__, NAME)


def write(
    object_name: str,
    filename: str,
    data: Dict,
    log: bool = False,
) -> bool:
    if log:
        logger.info(f"{NAME}.update({object_name}/{filename})")

    if not storage.download(
        object_name=object_name,
        filename=filename,
        log=log,
    ):
        return False

    full_filename = objects.path_of(
        object_name=object_name,
        filename=filename,
    )

    _, current_data = file.load_yaml(
        full_filename,
        ignore_error=True,
        default={},
    )
    if not isinstance(current_data, dict):
        logger.error(
            "dict expected, {} received".format(
                current_data.__class__.__name__,
            )
        )
        return False

    current_data.update(data)

    if not file.save_yaml(
        full_filename,
        current_data,
        log=log,
    ):
        return False

    if not storage.upload(
        object_name=object_name,
        filename=filename,
        log=log,
    ):
        return False

    return True


def read(
    object_name: str,
    filename: str,
    verbose: bool = False,
) -> Tuple[bool, Dict]:
    if not storage.download(
        object_name=object_name,
        filename=filename,
        log=verbose,
    ):
        return True, {}

    _, data = file.load_yaml(
        objects.path_of(
            object_name=object_name,
            filename=filename,
        ),
        ignore_error=True,
        default={},
    )

    return True, data
