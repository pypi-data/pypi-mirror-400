import json
from datetime import datetime
import base64
import dbhydra.dbhydra_core as dh
import pandas as pd
from forloop_common_structures.core.job import JobStatusEnum
from forloop_modules.queries.db_model_templates import TriggerFrequencyEnum, TriggerType
from pydantic import ConfigDict, Field
from typing import Any

import forloop_modules.flog as flog


# FIXME: Dumbed down typehints to allow dbhydra to properly cast simple datatypes to mysql types
# E.g. Instead of using Optional[str] we use str and set default value to None
# This comment is applicable to every DB model here

# FIXME: All cast_*_types_to_* functions are a workaround for dbhydra not supporting proper data casts
# Ideally, when DBHydra gets updated, these functions can be simply removed from the codebase


class DBSession(dh.AbstractModel):
    auth0_session_id: str  # auth0 response - session_id
    version: str = None  # forloop platform version
    platform_type: str  # cloud or desktop
    ip: str = None  # only in desktop/execution core version
    mac_address: str = None  # only in desktop/execution core version
    hostname: str = None  # only in desktop/execution core version
    start_datetime_utc: datetime
    last_datetime_utc: datetime

    user_uid: int  # Foreign Key Many-to-1


class DBUser(dh.AbstractModel):
    email: str  # auth0 response - email
    auth0_subject_id: str  # auth0 response - auth_method_id
    stripe_id: str
    given_name: str = None  # auth0 response - given_name
    family_name: str = None  # auth0 response - family_name
    picture_url: str = None  # auth0 response - picture
    created_at: datetime


def cast_user_types_to_app(users_df: pd.DataFrame) -> pd.DataFrame:
    """Cast DB datatypes to in-app python datatypes."""
    users_df = gdtm.cast_types_to_app(users_df)
    return users_df


def cast_user_types_to_db(users_df: pd.DataFrame) -> pd.DataFrame:
    """Cast in-app python datatypes to DB datatypes."""
    users_df = users_df.drop("uid", axis=1)
    users_df = users_df.map(escape_if_string)
    return users_df


class DBProject(dh.AbstractModel):
    project_key: str
    project_name: str = "Untitled Project"

    owner_user_uid: int  # Foreign Key Many-to-1
    last_active_pipeline_uid: int = None  # Foreign Key 1-to-1


def cast_project_types_to_app(projects_df: pd.DataFrame) -> pd.DataFrame:
    """Cast DB datatypes to in-app python datatypes."""
    #projects_df = gdtm.cast_types_to_app(projects_df)  #doesnt work because of last_active_pipeline_uid
    projects_df = projects_df.astype(
        {"uid": str, "owner_user_uid": str}
    )

    # NULLable INT column 'last_active_pipeline_uid' is cast to DataFrame column of type float (NaN for NULL values)
    # I'm manually replacing NaN with None and floats with int to keep correct attribute types
    projects_df["last_active_pipeline_uid"] = projects_df["last_active_pipeline_uid"].apply(
        lambda x: (None if pd.isnull(x) else str(int(x)))
    )  # 1.0 -> '1', nan -> None
    return projects_df


def cast_project_types_to_db(projects_df: pd.DataFrame) -> pd.DataFrame:
    """Cast in-app python datatypes to DB datatypes."""
    projects_df = projects_df.drop("uid", axis=1)
    projects_df["last_active_pipeline_uid"] = projects_df["last_active_pipeline_uid"].apply(
        lambda x: (None if pd.isnull(x) else int(x))
    )
    projects_df = projects_df.map(escape_if_string)
    return projects_df







class DBPipeline(dh.AbstractModel):
    name: str
    # TODO: to be deprecated after introducing ExecCore for local execution
    active_nodes_uids: list = []
    # TODO: to be deprecated after introducing ExecCore for local execution
    remaining_nodes_uids: list = []
    # TODO: to be deprecated after introducing ExecCore for local execution
    start_node_uid: str = "0"
    # TODO: to be deprecated after introducing ExecCore for local execution
    is_active: bool = False

    project_uid: int  # Foreign Key Many-to-1
    system_reactivation_status: str = None


def cast_pipeline_types_to_app(pipelines_df: pd.DataFrame) -> pd.DataFrame:
    """Cast DB datatypes to in-app python datatypes."""
    pipelines_df = pipelines_df.astype(
        {"uid": str, "project_uid": str, "is_active": bool}
    )
    pipelines_df[["active_nodes_uids", "remaining_nodes_uids"]
                ] = pipelines_df[["active_nodes_uids", "remaining_nodes_uids"]].map(json.loads)
    return pipelines_df


def cast_pipeline_types_to_db(pipelines_df: pd.DataFrame) -> pd.DataFrame:
    """Cast in-app python datatypes to DB datatypes."""
    pipelines_df = pipelines_df.drop("uid", axis=1)
    pipelines_df = pipelines_df.astype({"project_uid": int, "is_active": int})
    pipelines_df[["active_nodes_uids", "remaining_nodes_uids"]
                ] = pipelines_df[["active_nodes_uids", "remaining_nodes_uids"]].map(json.dumps)
    pipelines_df = pipelines_df.map(escape_if_string)
    return pipelines_df


class DBNode(dh.AbstractModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)  # due to dh.Jsonable

    pos: tuple[int, int]
    typ: str
    params: dh.Jsonable
    fields: dh.Jsonable
    visible: bool = True
    is_active: bool = False
    is_breakpoint_enabled: bool = False
    is_disabled: bool = False

    pipeline_uid: int  # Foreign Key Many-to-1
    project_uid: int  # Foreign Key Many-to-1


def cast_node_types_to_app(nodes_df: pd.DataFrame) -> pd.DataFrame:
    """Cast DB datatypes to in-app python datatypes."""
    nodes_df = nodes_df.astype(
        {
            "uid": str,
            "pipeline_uid": str,
            "project_uid": str,
            "visible": bool,
            "is_active": bool,
            "is_breakpoint_enabled": bool,
            "is_disabled": bool,
        }
    )
    nodes_df[["pos", "params", "fields"]] = nodes_df[["pos", "params", "fields"]].map(json.loads)
    return nodes_df


def cast_node_types_to_db(nodes_df: pd.DataFrame) -> pd.DataFrame:
    """Cast in-app python datatypes to DB datatypes."""
    nodes_df = nodes_df.drop("uid", axis=1)
    nodes_df = nodes_df.astype(
        {
            "visible": int,
            "is_active": int,
            "is_breakpoint_enabled": int,
            "is_disabled": int,
        }
    )
    nodes_df[["pos", "params", "fields"]] = nodes_df[["pos", "params", "fields"]].map(json.dumps)
    nodes_df = nodes_df.map(escape_if_string)
    return nodes_df


class DBEdge(dh.AbstractModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)  # due to dh.Jsonable

    from_node_uid: int
    to_node_uid: int
    channel: dh.Jsonable = None
    visible: bool = True

    pipeline_uid: int  # Foreign Key Many-to-1
    project_uid: int  # Foreign Key Many-to-1


def cast_edge_types_to_app(edges_df: pd.DataFrame) -> pd.DataFrame:
    """Cast DB datatypes to in-app python datatypes."""
    edges_df = edges_df.astype(
        {
            "uid": str,
            "from_node_uid": str,
            "to_node_uid": str,
            "pipeline_uid": str,
            "project_uid": str,
            "visible": bool,
        }
    )
    # NULLable INT column 'channel' is cast to DataFrame column of type float (NaN for NULL values)
    # I'm manually replacing NaN with None and floats with int to keep correct attribute types
    edges_df["channel"] = edges_df["channel"].apply(
        lambda x: (None if pd.isnull(x) else json.loads(x))
    )  # 1.0 -> '1', nan -> None

    return edges_df


def cast_edge_types_to_db(edges_df: pd.DataFrame) -> pd.DataFrame:
    """Cast in-app python datatypes to DB datatypes."""
    edges_df = edges_df.drop("uid", axis=1)
    edges_df = edges_df.astype(
        {
            "from_node_uid": int,
            "to_node_uid": int,
            "pipeline_uid": int,
            "project_uid": int,
            "visible": int,
        }
    )
    edges_df["channel"] = edges_df["channel"].apply(
        lambda x: (None if x is None else json.dumps(x))
    )  # Cast channel to NULL if it holds None
    edges_df = edges_df.map(escape_if_string)
    return edges_df


class DBVariable(dh.AbstractModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)  # due to dh.Jsonable

    name: str  # Check constraint on name/pipeline_uid
    value: dh.Jsonable
    type: str = None
    size: dh.Jsonable = None
    is_result: bool = False

    pipeline_job_uid: str  # Foreign Key Many-to-1
    project_uid: int  # Foreign Key Many-to-1


def cast_variable_types_to_app(variables_df: pd.DataFrame) -> pd.DataFrame:
    """Cast DB datatypes to in-app python datatypes."""
    ##### TODO for Jakub: check variables here:
    # print(variables_df) #returns this: Columns: [uid, name, value, type, size, pipeline_uid, project_uid] (doesnt match row below)
    variables_df = variables_df.astype(
        {"uid": str, "value": str, "project_uid": str, "pipeline_job_uid": str, "is_result": bool}
    )
    non_df_variables = variables_df["type"] != "DataFrame"
    variables_df["size"] = variables_df["size"].map(json.loads)
    variables_df.loc[non_df_variables, "value"] = variables_df.loc[non_df_variables, "value"].map(
        json.loads
    )
    return variables_df


def cast_variable_types_to_db(variables_df: pd.DataFrame) -> pd.DataFrame:
    """Cast in-app python datatypes to DB datatypes."""
    variables_df = variables_df.drop("uid", axis=1)
    variables_df = variables_df.astype({"project_uid": int, "pipeline_job_uid": int})
    variables_df[["value", "size"]] = variables_df[["value", "size"]].applymap(json.dumps)
    variables_df = variables_df.map(escape_if_string)
    return variables_df


class DBInitialVariable(dh.AbstractModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)  # due to dh.Jsonable

    name: str  # Check constraint on name/pipeline_uid
    value: dh.Jsonable
    is_result: bool = False
    type: str = None
    size: dh.Jsonable = None
    is_result: bool = False

    pipeline_uid: int  # Foreign Key Many-to-1
    project_uid: int  # Foreign Key Many-to-1


def cast_initial_variable_types_to_app(initial_variables_df: pd.DataFrame) -> pd.DataFrame:
    """Cast DB datatypes to in-app python datatypes."""
    initial_variables_df = initial_variables_df.astype(
        {"uid": str, "value": str, "pipeline_uid": str, "project_uid": str, "is_result": bool}
    )
    non_df_variables = initial_variables_df["type"] != "DataFrame"
    initial_variables_df["size"] = initial_variables_df["size"].map(json.loads)
    initial_variables_df.loc[non_df_variables, "value"] = initial_variables_df.loc[
        non_df_variables, "value"
    ].map(json.loads)
    return initial_variables_df


def cast_initial_variable_types_to_db(initial_variables_df: pd.DataFrame) -> pd.DataFrame:
    """Cast in-app python datatypes to DB datatypes."""
    initial_variables_df = initial_variables_df.drop("uid", axis=1)
    initial_variables_df = initial_variables_df.astype({"pipeline_uid": int, "project_uid": int})
    initial_variables_df[["value", "size"]] = initial_variables_df[["value", "size"]].applymap(
        json.dumps
    )
    initial_variables_df = initial_variables_df.map(escape_if_string)
    return initial_variables_df


class DBNodeJob(dh.AbstractModel):
    machine_uid: str = None
    status: str = JobStatusEnum.QUEUED  # Enum - saved as a string as DBHydra does not support them
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: datetime = None
    completed_at: datetime = None
    message: str = None
    node: dh.Jsonable

    pipeline_uid: int  # Foreign Key Many-to-1
    pipeline_job_uid: int = None  # Foreign Key Many-to-1


def cast_node_job_types_to_app(node_jobs_df: pd.DataFrame) -> pd.DataFrame:
    """Cast DB datatypes to in-app python datatypes."""
    node_jobs_df=gdtm.cast_types_to_app(node_jobs_df)
    #node_jobs_df = node_jobs_df.astype({"uid": str, "pipeline_job_uid": str, "pipeline_uid": str})
    node_jobs_df[["created_at", "started_at",
                  "completed_at"]] = node_jobs_df[["created_at", "started_at", "completed_at"
                                                  ]].astype(object).replace(pd.NaT, None)
    node_jobs_df["node"] = node_jobs_df["node"].map(json.loads)
    node_jobs_df["status"] = node_jobs_df["status"].map(lambda x: JobStatusEnum(x))
    return node_jobs_df


def cast_node_job_types_to_db(node_jobs_df: pd.DataFrame) -> pd.DataFrame:
    """Cast in-app python datatypes to DB datatypes."""
    node_jobs_df = node_jobs_df.drop("uid", axis=1)
    node_jobs_df = node_jobs_df.astype({"pipeline_uid": int})
    node_jobs_df[["created_at", "started_at",
                  "completed_at"]] = node_jobs_df[["created_at", "started_at", "completed_at"
                                                  ]].astype(object).replace(pd.NaT, None)
    node_jobs_df["pipeline_job_uid"] = node_jobs_df["pipeline_job_uid"].map(
        lambda x: int(x) if x is not None else None
    )  # Replacement for astype(), but can handle NULLable columns
    node_jobs_df["node"] = node_jobs_df["node"].map(json.dumps)
    node_jobs_df["status"] = node_jobs_df["status"].map(lambda x: x.value)
    node_jobs_df = node_jobs_df.map(escape_if_string)
    return node_jobs_df


class DBPipelineJob(dh.AbstractModel):
    machine_uid: str = None
    status: str = JobStatusEnum.QUEUED  # Enum - saved as a string as DBHydra does not support them
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: datetime = None
    completed_at: datetime = None
    message: str = None
    pipeline_elements: dh.Jsonable  # to replace 3 above columns
    trigger_mode: str
    created_by: dh.Jsonable  # {"trigger_type": "USER/PIPELINE/TRIGGER", "uid": user_uid/pipeline_uid/trigger_uid}

    pipeline_uid: str  # Foreign Key Many-to-1


def cast_pipeline_job_types_to_app(pipeline_jobs_df: pd.DataFrame) -> pd.DataFrame:
    """Cast DB datatypes to in-app python datatypes."""
    pipeline_jobs_df = gdtm.cast_types_to_app(pipeline_jobs_df)
    pipeline_jobs_df[["created_at", "started_at", "completed_at"]
                    ] = pipeline_jobs_df[["created_at", "started_at",
                                          "completed_at"]].astype(object).replace(pd.NaT, None)
    pipeline_jobs_df[["created_by"]] = pipeline_jobs_df[["created_by"]].map(json.loads)
    if "pipeline_elements" in pipeline_jobs_df.columns: #this can be potentially omitted - due to performance issues
        pipeline_jobs_df[["pipeline_elements"]] = pipeline_jobs_df[["pipeline_elements"]].map(json.loads)
    pipeline_jobs_df["status"] = pipeline_jobs_df["status"].map(lambda x: JobStatusEnum(x))
    return pipeline_jobs_df


def cast_pipeline_job_types_to_db(pipeline_jobs_df: pd.DataFrame) -> pd.DataFrame:
    """Cast in-app python datatypes to DB datatypes."""
    pipeline_jobs_df = pipeline_jobs_df.drop("uid", axis=1)
    pipeline_jobs_df = pipeline_jobs_df.astype({"pipeline_uid": int})
    pipeline_jobs_df[["created_at", "started_at", "completed_at"]
                    ] = pipeline_jobs_df[["created_at", "started_at",
                                          "completed_at"]].astype(object).replace(pd.NaT, None)
    pipeline_jobs_df[["pipeline_elements",
                      "created_by"]] = pipeline_jobs_df[["pipeline_elements",
                                                           "created_by"]].map(json.dumps)
    pipeline_jobs_df["status"] = pipeline_jobs_df["status"].map(lambda x: x.value)
    pipeline_jobs_df = pipeline_jobs_df.map(escape_if_string)
    return pipeline_jobs_df


class DBOperationJob(dh.AbstractModel):
    status: str = JobStatusEnum.QUEUED  # Enum - saved as a string as DBHydra does not support them
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: datetime = None
    completed_at: datetime = None
    message: str = None
    node: dh.Jsonable

    prototype_job_uid: int  # Foreign Key Many-to-1


def cast_operation_job_types_to_app(operation_jobs_df: pd.DataFrame) -> pd.DataFrame:
    """Cast DB datatypes to in-app python datatypes."""
    operation_jobs_df=gdtm.cast_types_to_app(operation_jobs_df)
    #operation_jobs_df = operation_jobs_df.astype({"uid": str, "pipeline_job_uid": str, "pipeline_uid": str})
    operation_jobs_df[["created_at", "started_at",
                  "completed_at"]] = operation_jobs_df[["created_at", "started_at", "completed_at"
                                                  ]].astype(object).replace(pd.NaT, None)
    operation_jobs_df["node"] = operation_jobs_df["node"].map(json.loads)
    operation_jobs_df["status"] = operation_jobs_df["status"].map(lambda x: JobStatusEnum(x))
    return operation_jobs_df


def cast_operation_job_types_to_db(operation_jobs_df: pd.DataFrame) -> pd.DataFrame:
    """Cast in-app python datatypes to DB datatypes."""
    operation_jobs_df = operation_jobs_df.drop("uid", axis=1)
    operation_jobs_df = operation_jobs_df.astype({"prototype_job_uid": int})
    operation_jobs_df[["created_at", "started_at",
                  "completed_at"]] = operation_jobs_df[["created_at", "started_at", "completed_at"
                                                  ]].astype(object).replace(pd.NaT, None)
    operation_jobs_df["node"] = operation_jobs_df["node"].map(json.dumps)
    operation_jobs_df["status"] = operation_jobs_df["status"].map(lambda x: x.value)
    operation_jobs_df = operation_jobs_df.map(escape_if_string)
    return operation_jobs_df


class DBPrototypeJob(dh.AbstractModel):
    machine_uid: str = None # CHECK constraint: not (machine_uid is not None & status == 'QUEUED')
    status: str = JobStatusEnum.QUEUED  # Enum - saved as a string as DBHydra does not support them
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: datetime = None
    completed_at: datetime = None

    pipeline_uid: str  # Foreign Key Many-to-1
    trigger_mode: str


def cast_prototype_job_types_to_app(prototype_jobs_df: pd.DataFrame) -> pd.DataFrame:
    """Cast DB datatypes to in-app python datatypes."""
    prototype_jobs_df=gdtm.cast_types_to_app(prototype_jobs_df)

    #prototype_jobs_df = prototype_jobs_df.astype({"uid": str, "prototype_uid": str})
    prototype_jobs_df[["created_at", "started_at", "completed_at"]
                    ] = prototype_jobs_df[["created_at", "started_at",
                                          "completed_at"]].astype(object).replace(pd.NaT, None)
    prototype_jobs_df["status"] = prototype_jobs_df["status"].map(lambda x: JobStatusEnum(x))
    return prototype_jobs_df


def cast_prototype_job_types_to_db(prototype_jobs_df: pd.DataFrame) -> pd.DataFrame:
    """Cast in-app python datatypes to DB datatypes."""
    prototype_jobs_df = prototype_jobs_df.drop("uid", axis=1)
    prototype_jobs_df = prototype_jobs_df.astype({"pipeline_uid": int})
    prototype_jobs_df[["created_at", "started_at", "completed_at"]
                    ] = prototype_jobs_df[["created_at", "started_at",
                                          "completed_at"]].astype(object).replace(pd.NaT, None)
    prototype_jobs_df["status"] = prototype_jobs_df["status"].map(lambda x: x.value)
    prototype_jobs_df = prototype_jobs_df.map(escape_if_string)
    return prototype_jobs_df


class DBUserLog(dh.AbstractModel):
    message: str
    severity: str
    datetime_utc: datetime = datetime.utcnow()

    project_uid: int  # Foreign Key Many-to-1

def cast_user_log_types_to_app(user_logs_df: pd.DataFrame) -> pd.DataFrame:
    """Cast DB datatypes to in-app python datatypes."""
    user_logs_df=gdtm.cast_types_to_app(user_logs_df)
    
    # user_logs_df = user_logs_df.astype(
    #     {"uid": str, "project_uid": str}
    # )
    user_logs_df["datetime_utc"] = user_logs_df["datetime_utc"].astype(object).replace(pd.NaT, None)
    
    return user_logs_df


def cast_user_log_types_to_db(user_logs_df: pd.DataFrame) -> pd.DataFrame:
    """Cast in-app python datatypes to DB datatypes."""
    
    user_logs_df = user_logs_df.astype({"project_uid": int})
    user_logs_df["datetime_utc"] = user_logs_df["datetime_utc"].astype(object).replace(pd.NaT, None)
    user_logs_df = user_logs_df.map(escape_if_string)
    
    #user_logs_df=gdtm.cast_types_to_db(user_logs_df) #raised an error because its not equivalent to other casting functions (missing uid)
    return user_logs_df


class DBUserFlowStep(dh.AbstractModel):
    user_uid: int # Foreign Key Many-to-1
    step_identifier: str
    step_data: str
    timestamp_utc: str
    
    
class DBUserAET(dh.AbstractModel):
    user_uid: int # Foreign Key Many-to-1
    last_active_project_uid: str # Foreign Key Many-to-1
    last_active_pipeline_uid: str # Foreign Key Many-to-1
    last_active_script_uid: str # Foreign Key Many-to-1
    last_active_dataframe_node_uid: str # Foreign Key Many-to-1
    last_active_subscription_plan_uid: str # Foreign Key Many-to-1


class DBUserSubscriptionPlan(dh.AbstractModel):
    start_datetime_utc: datetime
    end_datetime_utc: datetime
    consumed_credits: int
    status: str # UserSubscriptionPlanStatusEnum - saved as a string as DBHydra does not support them

    user_uid: str # Foreign Key Many-to-1
    subscription_plan_uid: str # Foreign Key Many-to-1


class DBUserResources(dh.AbstractModel):
    # TODO: probably split into User > UserResources < Resources if there will be more fields for Resource

    user_uid: int   # Foreign Key Many-to-1
    resource_type: str      # TODO: enum
    resource_name: str
    created_at: datetime
    removed_at: datetime


def cast_user_resource_types_to_app(user_resources_df: pd.DataFrame) -> pd.DataFrame:
    """Cast DB datatypes to in-app python datatypes."""
    user_resources_df = gdtm.cast_types_to_app(user_resources_df)

    user_resources_df['user_uid'] = user_resources_df['user_uid'].astype(str)
    user_resources_df[["removed_at", "created_at"]] = user_resources_df[["removed_at", "created_at"]].astype(object).replace(pd.NaT, None)

    return user_resources_df


def cast_user_resource_types_to_db(user_resources_df: pd.DataFrame) -> pd.DataFrame:
    """Cast in-app python datatypes to DB datatypes."""
    user_resources_df = user_resources_df.astype({"user_uid": str})
    user_resources_df = user_resources_df.drop("uid", axis=1)
    user_resources_df[["removed_at", "created_at"]] = user_resources_df[["removed_at", "created_at"]].astype(object).replace(pd.NaT, None)
    user_resources_df = user_resources_df.map(escape_if_string)

    return user_resources_df


def cast_user_subscription_plan_types_to_app(user_subscription_plans_df: pd.DataFrame) -> pd.DataFrame:
    """Cast DB datatypes to in-app python datatypes."""
    user_subscription_plans_df=gdtm.cast_types_to_app(user_subscription_plans_df)
    return user_subscription_plans_df


def cast_user_subscription_plan_types_to_db(user_subscription_plans_df: pd.DataFrame) -> pd.DataFrame:
    """Cast in-app python datatypes to DB datatypes."""
    user_subscription_plans_df=gdtm.cast_types_to_db(user_subscription_plans_df)
    return user_subscription_plans_df


class DBSubscriptionPlan(dh.AbstractModel):
    name: str
    stripe_id: str
    lookup_key: str
    price: float
    total_credits: int
    max_concurrent_pipelines: int
    max_collaborators: int
    is_active: bool
    description: str

def cast_subscription_plan_types_to_app(subscription_plans_df: pd.DataFrame) -> pd.DataFrame:
    """Cast DB datatypes to in-app python datatypes."""
    subscription_plans_df=gdtm.cast_types_to_app(subscription_plans_df)
    subscription_plans_df = subscription_plans_df.astype({"is_active": bool})
    return subscription_plans_df

def cast_subscription_plan_types_to_db(subscription_plans_df: pd.DataFrame) -> pd.DataFrame:
    """Cast in-app python datatypes to DB datatypes."""
    subscription_plans_df=gdtm.cast_types_to_db(subscription_plans_df)
    return subscription_plans_df


class DBUserProjectLink(dh.AbstractModel):
    user_uid: int # Foreign Key Many-to-1
    project_uid: int # Foreign Key Many-to-1
    

class DBTemplatePipelineMapping(dh.AbstractModel):
    template_name: str
    pipeline_uid: int
    owner_user_uid: int
    screenshot: dh.Blob = None


def cast_template_mappings_types_to_app(temp_mappings_df: pd.DataFrame) -> pd.DataFrame:
    """Cast DB datatypes to in-app python datatypes."""
    temp_mappings_df = gdtm.cast_types_to_app(temp_mappings_df)
    temp_mappings_df["screenshot"] = temp_mappings_df["screenshot"].apply(
        lambda x: base64.b64encode(x) if x is not None else None
    )
    return temp_mappings_df


def cast_template_mappings_types_to_db(temp_mappings_df: pd.DataFrame) -> pd.DataFrame:
    """Cast in-app python datatypes to DB datatypes."""
    temp_mappings_df = gdtm.cast_types_to_db(temp_mappings_df)
    temp_mappings_df["screenshot"] = temp_mappings_df["screenshot"].apply(
        lambda x: base64.b64decode(x) if x is not None else None
    )
    temp_mappings_df = temp_mappings_df.map(escape_if_string)
    return temp_mappings_df


class DBTrigger(dh.AbstractModel):
    name: str
    type: str
    params: dh.Jsonable
    last_run_date: datetime = None

    pipeline_uid: int  # Foreign Key Many-to-1
    project_uid: int  # Foreign Key Many-to-1


def cast_trigger_types_to_app(triggers_df: pd.DataFrame) -> pd.DataFrame:
    """Cast DB datatypes to in-app python datatypes."""
    def parse_trigger_params(series: pd.Series):
        if series["type"] != TriggerType.TIME:
            return series
        else:
            series['params'] = {
                **series['params'],
                'first_run_date': datetime.fromisoformat(series["params"]['first_run_date']),
                'frequency': TriggerFrequencyEnum(series["params"]['frequency']),
            }
            return series

    triggers_df = gdtm.cast_types_to_app(triggers_df)
    triggers_df["type"] = triggers_df["type"].map(lambda x: TriggerType(x))
    triggers_df['params'] = triggers_df['params'].map(json.loads)
    triggers_df = triggers_df.apply(parse_trigger_params, axis=1)

    triggers_df["last_run_date"] = triggers_df["last_run_date"].astype(object).replace(pd.NaT, None)
    return triggers_df


def cast_trigger_types_to_db(triggers_df: pd.DataFrame) -> pd.DataFrame:
    """Cast in-app python datatypes to DB datatypes."""
    def serialize_trigger_params(series: pd.Series):
        if series["type"] != TriggerType.TIME:
            return series
        else:
            series["params"] = {
                **series["params"],
                'first_run_date': series['params']['first_run_date'].isoformat(),
                'frequency': series['params']['frequency'].value,
            }
            return series

    #triggers_df = triggers_df.drop("uid", axis=1)
    #triggers_df = triggers_df.astype({"pipeline_uid": int, "project_uid": int})
    triggers_df = triggers_df.apply(serialize_trigger_params, axis=1)
    triggers_df["params"] = triggers_df['params'].map(json.dumps)
   
    #triggers_df = triggers_df.map(escape_if_string)
    
    triggers_df=gdtm.cast_types_to_db(triggers_df)
    return triggers_df


class DBScript(dh.AbstractModel):
    script_name: str
    text: str
    project_uid: str


def cast_script_types_to_app(scripts_df: pd.DataFrame) -> pd.DataFrame:
    """Cast DB datatypes to in-app python datatypes."""
    scripts_df = gdtm.cast_types_to_app(scripts_df)
    return scripts_df


def cast_script_types_to_db(scripts_df: pd.DataFrame) -> pd.DataFrame:
    """Cast in-app python datatypes to DB datatypes."""
    scripts_df = gdtm.cast_types_to_db(scripts_df)
    return scripts_df


class DBDeployment(dh.AbstractModel):
    pipeline_uid: str
    port: int
    host: str = "0.0.0.0"
    module_app: str = "user_api_sample:app"
    subprocess_id: int = None
    status: str = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = None


def cast_deployment_types_to_app(deployments_df: pd.DataFrame) -> pd.DataFrame:
    """Cast DB datatypes to in-app python datatypes."""
    deployments_df = gdtm.cast_types_to_app(deployments_df)
    deployments_df[["created_at", "updated_at"]] = deployments_df[["created_at", "updated_at"]].astype(object).replace(pd.NaT, None)
    return deployments_df


def cast_deployment_types_to_db(deployments_df: pd.DataFrame) -> pd.DataFrame:
    """Cast in-app python datatypes to DB datatypes."""
    deployments_df = gdtm.cast_types_to_db(deployments_df)
    deployments_df[["created_at", "updated_at"]] = deployments_df[["created_at", "updated_at"]].astype(object).replace(pd.NaT, None)
    deployments_df = deployments_df.map(escape_if_string)
    return deployments_df


class DBDatabase(dh.AbstractModel):
    database_name: str
    server: str
    port: int
    database: str
    username: str
    password: str
    dialect: str
    new: bool
    project_uid: str # Foreign Key Many-to-1

def cast_database_types_to_app(databases_df: pd.DataFrame) -> pd.DataFrame:
    """Cast DB datatypes to in-app python datatypes."""
    databases_df=gdtm.cast_types_to_app(databases_df)
    return databases_df


def cast_database_types_to_db(databases_df: pd.DataFrame) -> pd.DataFrame:
    """Cast in-app python datatypes to DB datatypes."""
    databases_df=gdtm.cast_types_to_db(databases_df)
    return databases_df


class DBScreenshot(dh.AbstractModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)  # due to dh.Jsonable

    url: str
    screenshot: dh.Blob

    prototype_job_uid: int  # Foreign Key Many-to-1


def cast_screenshot_types_to_app(screenshots_df: pd.DataFrame) -> pd.DataFrame:
    """Cast DB datatypes to in-app python datatypes."""
    screenshots_df = screenshots_df.astype({"prototype_job_uid": str})
    screenshots_df["screenshot"] = screenshots_df["screenshot"].apply(base64.b64encode)
    return screenshots_df


def cast_screenshot_types_to_db(screenshots_df: pd.DataFrame) -> pd.DataFrame:
    """Cast in-app python datatypes to DB datatypes."""
    screenshots_df = screenshots_df.drop("uid", axis=1)
    screenshots_df = screenshots_df.astype({"prototype_job_uid": int})
    screenshots_df["screenshot"] = screenshots_df["screenshot"].apply(base64.b64decode)
    screenshots_df = screenshots_df.map(escape_if_string)
    return screenshots_df


class DBScannedElements(dh.AbstractModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)  # due to dh.Jsonable

    elements: dh.Jsonable

    prototype_job_uid: int  # Foreign Key Many-to-1


class DBSelectedElements(dh.AbstractModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)  # due to dh.Jsonable

    elements: dh.Jsonable

    prototype_job_uid: int  # Foreign Key Many-to-1


class DBSimilarElements(dh.AbstractModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)  # due to dh.Jsonable

    elements: dh.Jsonable

    prototype_job_uid: int  # Foreign Key Many-to-1


def cast_elements_types_to_app(elements_df: pd.DataFrame) -> pd.DataFrame:
    """Cast DB datatypes to in-app python datatypes."""
    elements_df = elements_df.astype({"prototype_job_uid": str})
    elements_df["elements"] = elements_df["elements"].apply(json.loads)
    return elements_df


def cast_elements_types_to_db(elements_df: pd.DataFrame) -> pd.DataFrame:
    """Cast in-app python datatypes to DB datatypes."""
    elements_df = elements_df.drop("uid", axis=1)
    elements_df = elements_df.astype({"prototype_job_uid": int})
    elements_df["elements"] = elements_df["elements"].apply(json.dumps)
    elements_df = elements_df.map(escape_if_string)
    return elements_df


class GenericDbTypeMapper:
    def __init__(self):
        pass
    
    def cast_types_to_app(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cast DB datatypes to in-app python datatypes."""
        
        for i,column in enumerate(df.columns):
            if "uid" == column[-3:]: #matches uid, pipeline_uid, project_uid etc.
                df = df.astype({column: str})
        
        
        #triggers_df = triggers_df.astype({"uid": str, "pipeline_uid": str, "project_uid": str}) #if "uid" contained use it - DONE
        #triggers_df["frequency"] = triggers_df["frequency"].map(lambda x: TriggerFrequencyEnum(x)) - not DONE
        #triggers_df["first_run_date"] = triggers_df["first_run_date"].astype(object).replace(pd.NaT, None) #datetime transformation
        #node_jobs_df[["created_at", "started_at",
        #              "completed_at"]] = node_jobs_df[["created_at", "started_at", "completed_at"                                             ]].astype(object).replace(pd.NaT, None)
        #node_jobs_df["node"] = node_jobs_df["node"].map(json.loads)
        #node_jobs_df["status"] = node_jobs_df["status"].map(lambda x: JobStatusEnum(x))
        
        
        return df
    
    
    def cast_types_to_db(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cast in-app python datatypes to DB datatypes."""
        if "uid" in df.columns:
            df = df.drop("uid", axis=1)

        for i,column in enumerate(df.columns):
            if "uid" == column[-3:]: #matches uid, pipeline_uid, project_uid etc.
                df = df.astype({column: int})
        
        df=df.map(escape_if_string)
        
        return df
    

gdtm=GenericDbTypeMapper()


def escape_if_string(variable: Any) -> Any:
    """Escape a variable if it's a string.

    Replaces single-quotes with single-quote pairs, backlashes with double-backlashes and escapes
    double-quotes.

    Note:
        Old implementation using db connector was moved to a new function
        'escape_if_string_database_dependent'.
    """
    if isinstance(variable, str):
        return variable.replace("\\","\\\\").replace("'", "\\'").replace('"', '\\"')
    #if isinstance(db1, dh.MysqlDb) and isinstance(variable, str):
    #    return db1.connection.escape_string(variable)
    return variable


def escape_if_string_database_dependent(variable: Any, db1) -> Any:
    """Original implementation - to be deprecated if the new version of escape if string works fine.
    Escape a variable if it's a string."""
    if isinstance(db1, dh.MysqlDb) and isinstance(variable, str):
        return db1.connection.escape_string(variable)
    return variable


