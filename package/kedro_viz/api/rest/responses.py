"""`kedro_viz.api.rest.responses` defines REST response types."""
# pylint: disable=missing-class-docstring,too-few-public-methods,invalid-name
import abc
from typing import Any, Dict, List, Optional, Union

import orjson
from fastapi._compat import PYDANTIC_V2
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel, ConfigDict

from kedro_viz.data_access import data_access_manager


class APIErrorMessage(BaseModel):
    message: str


class BaseAPIResponse(BaseModel, abc.ABC):
    if PYDANTIC_V2:
        model_config = ConfigDict(from_attributes=True)
    else:

        class Config:
            orm_mode = True


class BaseGraphNodeAPIResponse(BaseAPIResponse):
    id: str
    name: str
    tags: List[str]
    pipelines: List[str]
    type: str

    # If a node is a ModularPipeline node, this value will be None, hence Optional.
    modular_pipelines: Optional[List[str]] = None


task_node_api_response_example = {
    "example": {
        "id": "6ab908b8",
        "name": "split_data_node",
        "tags": [],
        "pipelines": ["__default__", "ds"],
        "modular_pipelines": [],
        "type": "task",
        "parameters": {
            "test_size": 0.2,
            "random_state": 3,
            "features": [
                "engines",
                "passenger_capacity",
                "crew",
                "d_check_complete",
                "moon_clearance_complete",
                "iata_approved",
                "company_rating",
                "review_scores_rating",
            ],
        },
    }
}


class TaskNodeAPIResponse(BaseGraphNodeAPIResponse):
    parameters: Dict
    if PYDANTIC_V2:
        model_config = ConfigDict(json_schema_extra=task_node_api_response_example)
    else:

        class Config:
            schema_extra = task_node_api_response_example


data_node_api_response_example = {
    "example": {
        "id": "d7b83b05",
        "name": "master_table",
        "tags": [],
        "pipelines": ["__default__", "dp", "ds"],
        "modular_pipelines": [],
        "type": "data",
        "layer": "primary",
        "dataset_type": "kedro.extras.datasets.pandas.csv_dataset.CSVDataSet",
        "stats": {"rows": 10, "columns": 2, "file_size": 2300},
    }
}


class DataNodeAPIResponse(BaseGraphNodeAPIResponse):
    layer: Optional[str] = None
    dataset_type: Optional[str] = None
    stats: Optional[Dict] = None
    if PYDANTIC_V2:
        model_config = ConfigDict(json_schema_extra=data_node_api_response_example)
    else:

        class Config:
            schema_extra = data_node_api_response_example


NodeAPIResponse = Union[
    TaskNodeAPIResponse,
    DataNodeAPIResponse,
]


task_node_metadata_api_example = {
    "example": {
        "code": "def split_data(data: pd.DataFrame, parameters: Dict) -> Tuple:",
        "filepath": "proj/src/new_kedro_project/pipelines/data_science/nodes.py",
        "parameters": {"test_size": 0.2},
        "inputs": ["params:input1", "input2"],
        "outputs": ["output1"],
        "run_command": "kedro run --to-nodes=split_data",
    }
}


class TaskNodeMetadataAPIResponse(BaseAPIResponse):
    code: Optional[str] = None
    filepath: Optional[str] = None
    parameters: Optional[Dict] = None
    inputs: List[str]
    outputs: List[str]
    run_command: Optional[str] = None
    if PYDANTIC_V2:
        model_config = ConfigDict(json_schema_extra=task_node_metadata_api_example)
    else:

        class Config:
            schema_extra = task_node_metadata_api_example


data_node_metadata_api_example = {
    "example": {
        "filepath": "/my-kedro-project/data/03_primary/master_table.csv",
        "type": "pandas.csv_dataset.CSVDataSet",
        "run_command": "kedro run --to-outputs=master_table",
    }
}


class DataNodeMetadataAPIResponse(BaseAPIResponse):
    filepath: Optional[str] = None
    type: str
    plot: Optional[Dict] = None
    image: Optional[str] = None
    tracking_data: Optional[Dict] = None
    run_command: Optional[str] = None
    preview: Optional[Dict] = None
    stats: Optional[Dict] = None
    if PYDANTIC_V2:
        model_config = ConfigDict(json_schema_extra=data_node_metadata_api_example)
    else:

        class Config:
            schema_extra = data_node_metadata_api_example


class TranscodedDataNodeMetadataAPIReponse(BaseAPIResponse):
    filepath: str
    original_type: str
    transcoded_types: List[str]
    run_command: Optional[str] = None
    stats: Optional[Dict] = None


parameters_node_metaxata_api_example = {
    "example": {
        "parameters": {
            "test_size": 0.2,
            "random_state": 3,
            "features": [
                "engines",
                "passenger_capacity",
                "crew",
                "d_check_complete",
                "moon_clearance_complete",
                "iata_approved",
                "company_rating",
                "review_scores_rating",
            ],
        }
    }
}


class ParametersNodeMetadataAPIResponse(BaseAPIResponse):
    parameters: Dict
    if PYDANTIC_V2:
        model_config = ConfigDict(
            json_schema_extra=parameters_node_metaxata_api_example
        )
    else:

        class Config:
            schema_extra = parameters_node_metaxata_api_example


NodeMetadataAPIResponse = Union[
    TaskNodeMetadataAPIResponse,
    DataNodeMetadataAPIResponse,
    TranscodedDataNodeMetadataAPIReponse,
    ParametersNodeMetadataAPIResponse,
]


class GraphEdgeAPIResponse(BaseAPIResponse):
    source: str
    target: str


class NamedEntityAPIResponse(BaseAPIResponse):
    """Model an API field that has an ID and a name.
    For example, used for representing modular pipelines and pipelines in the API response.
    """

    id: str
    name: Optional[str] = None


class ModularPipelineChildAPIResponse(BaseAPIResponse):
    """Model a child in a modular pipeline's children field in the API response."""

    id: str
    type: str


class ModularPipelinesTreeNodeAPIResponse(BaseAPIResponse):
    """Model a node in the tree representation of modular pipelines in the API response."""

    id: str
    name: str
    inputs: List[str]
    outputs: List[str]
    children: List[ModularPipelineChildAPIResponse]


# Represent the modular pipelines in the API response as a tree.
# The root node is always designated with the __root__ key.
# Example:
# {
#     "__root__": {
#            "id": "__root__",
#            "name": "Root",
#            "inputs": [],
#            "outputs": [],
#            "children": [
#                {"id": "d577578a", "type": "parameters"},
#                {"id": "data_science", "type": "modularPipeline"},
#                {"id": "f1f1425b", "type": "parameters"},
#                {"id": "data_engineering", "type": "modularPipeline"},
#            ],
#        },
#        "data_engineering": {
#            "id": "data_engineering",
#            "name": "Data Engineering",
#            "inputs": ["d577578a"],
#            "outputs": [],
#            "children": [],
#        },
#        "data_science": {
#            "id": "data_science",
#            "name": "Data Science",
#            "inputs": ["f1f1425b"],
#            "outputs": [],
#            "children": [],
#        },
#    }
# }
ModularPipelinesTreeAPIResponse = Dict[str, ModularPipelinesTreeNodeAPIResponse]


class GraphAPIResponse(BaseAPIResponse):
    nodes: List[NodeAPIResponse]
    edges: List[GraphEdgeAPIResponse]
    layers: List[str]
    tags: List[NamedEntityAPIResponse]
    pipelines: List[NamedEntityAPIResponse]
    modular_pipelines: ModularPipelinesTreeAPIResponse
    selected_pipeline: str


def get_default_response() -> GraphAPIResponse:
    """Default response for `/api/main`."""
    default_selected_pipeline_id = (
        data_access_manager.get_default_selected_pipeline().id
    )

    modular_pipelines_tree = (
        data_access_manager.create_modular_pipelines_tree_for_registered_pipeline(
            default_selected_pipeline_id
        )
    )

    return GraphAPIResponse(
        nodes=data_access_manager.get_nodes_for_registered_pipeline(  # type: ignore
            default_selected_pipeline_id
        ),
        edges=data_access_manager.get_edges_for_registered_pipeline(  # type: ignore
            default_selected_pipeline_id
        ),
        tags=data_access_manager.tags.as_list(),
        layers=data_access_manager.get_sorted_layers_for_registered_pipeline(
            default_selected_pipeline_id
        ),
        pipelines=data_access_manager.registered_pipelines.as_list(),
        modular_pipelines=modular_pipelines_tree,  # type: ignore
        selected_pipeline=default_selected_pipeline_id,
    )


class EnhancedORJSONResponse(ORJSONResponse):
    @staticmethod
    def encode_to_human_readable(content: Any) -> bytes:
        """A method to encode the given content to JSON, with the
        proper formatting to write a human-readable file.

        Returns:
            A bytes object containing the JSON to write.

        """
        return orjson.dumps(
            content,
            option=orjson.OPT_INDENT_2
            | orjson.OPT_NON_STR_KEYS
            | orjson.OPT_SERIALIZE_NUMPY,
        )
