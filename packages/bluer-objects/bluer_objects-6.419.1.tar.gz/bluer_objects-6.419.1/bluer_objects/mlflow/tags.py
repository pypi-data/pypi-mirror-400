from typing import Tuple, Dict, List, Union
from mlflow.tracking import MlflowClient
from mlflow.entities import ViewType

from blueness import module
from bluer_options.options import Options
from bluer_options.logger import crash_report

from bluer_objects import NAME
from bluer_objects import env
from bluer_objects.mlflow import serverless
from bluer_objects.mlflow.objects import to_experiment_name, to_object_name
from bluer_objects.logger import logger

NAME = module.name(__file__, NAME)


def create_server_style_filter_string(
    tags: Union[str, dict],
) -> str:
    tags_options = Options(tags)

    # https://www.mlflow.org/docs/latest/search-experiments.html
    return " and ".join(
        [f'tags."{keyword}" = "{value}"' for keyword, value in tags_options.items()]
    )


def get_tags(
    object_name: str,
    exclude_system_tags: bool = True,
    verbose: bool = False,
) -> Tuple[bool, Dict[str, str]]:
    if env.MLFLOW_IS_SERVERLESS:
        return serverless.get_tags(
            object_name,
            verbose=verbose,
        )

    experiment_name = to_experiment_name(object_name)

    try:
        client = MlflowClient()
        experiment = client.get_experiment_by_name(experiment_name)

        if experiment is None:
            return True, {}

        tags = {
            keyword: value
            for keyword, value in experiment.tags.items()
            if not keyword.startswith("mlflow.") or not exclude_system_tags
        }

        return True, tags
    except:
        crash_report(f"{NAME}.get_tags({object_name})")
        return False, {}


# https://www.mlflow.org/docs/latest/search-experiments.html
def search(
    filter_string: Union[str, dict],
    server_style: bool = False,
    verbose: bool = False,
) -> Tuple[bool, List[str]]:
    if server_style and env.MLFLOW_IS_SERVERLESS:
        logger.error("server_style search is not supported when mlflow is serverless.")
        return False, []

    if filter_string == "-":
        filter_string = ""

    if env.MLFLOW_IS_SERVERLESS:
        return serverless.search(
            filter_string=filter_string,
            log=verbose,
        )

    if not server_style:
        filter_string = create_server_style_filter_string(filter_string)

    client = MlflowClient()

    success = False
    output = []

    try:
        output = [
            to_object_name(experiment.name)
            for experiment in client.search_experiments(
                filter_string=filter_string,
                view_type=ViewType.ALL,
            )
        ]
        success = True
    except Exception as e:
        logger.error(e)

    return success, output


def set_tags(
    object_name: str,
    tags: Union[str, Dict[str, str]],
    log: bool = True,
    icon="#️⃣ ",
    verbose: bool = False,
) -> bool:
    if env.MLFLOW_IS_SERVERLESS:
        return serverless.set_tags(
            object_name,
            tags=tags,
            log=log,
            verbose=verbose,
            icon=icon,
        )

    experiment_name = to_experiment_name(object_name)

    try:
        tags = Options(tags)

        client = MlflowClient()

        experiment = client.get_experiment_by_name(experiment_name)
        if experiment is None:
            client.create_experiment(name=experiment_name)
            experiment = client.get_experiment_by_name(experiment_name)

        for key, value in tags.items():
            client.set_experiment_tag(experiment.experiment_id, key, value)
            if log:
                logger.info("{} {}.{}={}".format(icon, object_name, key, value))

    except:
        crash_report(f"{NAME}.set_tags({object_name})")
        return False

    return True
