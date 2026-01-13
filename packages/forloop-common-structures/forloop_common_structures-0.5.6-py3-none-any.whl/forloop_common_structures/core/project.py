from dataclasses import dataclass
from typing import Optional


@dataclass
class Project:
    owner_user_uid: str
    project_key: str  #will be used as URL extension e.g. app.forloop.ai/jh45FsR45xyE
    project_name: str = "Untitled Project"
    last_active_pipeline_uid: Optional[str] = None
    # TODO: Jakub: I'm not sure if property 'last_active_pipeline_uid' is a correct approach
    # In case pipeline is deleted from the DB, 'last_active_pipeline_uid' will point to a non-existing pipeline
    # Normally this would be taken care of by ORM/DB schema, but we dont have this functionality
    # This introduces a lot of shenanigans and edge cases to handle
    # Maybe 'last_saved' datetime column on pipelines could be a solution, to filter the last-used pipeline
    uid: Optional[str] = None

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():

            if key in vars(self).keys():
                setattr(self, key, value)
            else:
                raise AttributeError(f"Attribute '{key}' cannot be updated, as it does not exist")
