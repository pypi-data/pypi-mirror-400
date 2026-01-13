from dataclasses import dataclass, field
from typing import ClassVar, Any, Dict, List, Optional
    
from forloop_modules.node_detail_form import NodeDetailForm, NodeParams

from forloop_modules.globals.local_variable_handler import LocalVariable
from forloop_modules.globals.variable_handler import variable_handler
from forloop_modules.pipeline_function_handlers import (
    pipeline_function_handler_dict,  #TODO: Refactor out -> disable dependency for server (Temporary)
)

# from src.function_handlers.codeview_handler import codeview_handler

# if platform != "linux" and platform != "linux2":
#     # linux
#     from forloop_modules.pipeline_function_handlers import pipeline_function_handler_dict #TODO: Refactor out -> disable dependency for server (Temporary)
# else:
#     from forloop_modules.function_handlers.control_flow_handlers import control_flow_handlers_dict as pipeline_function_handler_dict


@dataclass
class Node:
    pos: list[int]  # Should be a tuple[int, int] but dbhydra doesn't support tuples
    typ: str
    params: dict[str, dict] = field(compare=False, repr=False) #yapf: disable this is actually NodeParams dict
    fields: list = field(default_factory=list)
    is_active: bool = False
    pipeline_uid: str = "0"
    project_uid: str = "0"
    visible: bool = True
    is_breakpoint_enabled: bool = False
    is_disabled: bool = False
    uid: Optional[str] = None
# <<<<<<< HEAD
#     instance_counter: ClassVar[int] = 0

#     def __post_init__(self):
#         if self.uid is None:
#             self.__class__.instance_counter += 1
#             self.uid = str(self.instance_counter)
#         self.node_detail_form.node_uid = self.uid
    
# =======

# >>>>>>> origin/jakub_redis_pipelines

    @property
    def params(self):  #Danger zone - don't change functionality
        params_dict = self.node_detail_form.node_params.params_dict_repr()
        return params_dict

    @params.setter
    def params(self,params): #Danger zone - don't change functionality
        node_params=NodeParams({**params}) #Copy params changes in NodeParams object
        if hasattr(self,"node_detail_form"):
            self.node_detail_form.node_params=node_params
        else: #runs when params are initialized -> i.e. before __post_init__()
            self.node_detail_form = NodeDetailForm(node_params=node_params,typ=self.typ, pos=self.pos)
            
    @property
    def fields(self):
        node_fields = self.node_detail_form.fields
        return node_fields

    @fields.setter
    def fields(self, fields):
        if hasattr(self,"node_detail_form"):
            self.node_detail_form.fields = fields
            
    def __post_init__(self):
        self.node_detail_form.node_uid = self.uid

    def __hash__(self):
        return hash((self.typ, self.uid))

    def __str__(self):
        params = ' '.join(map(str, self.get_params().values()))
        return f'{self.typ}({params})' if params else self.typ

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if key in dir(self):  # vars() does not see 'params' attribute, as it is a property
                setattr(self, key, value)
            else:
                raise AttributeError(f"Attribute '{key}' cannot be updated, as it does not exist")

    def execute(self, is_executed_as_prototype_job=False):
        """Execute the node's pipeline function handler.

        Args:
            is_executed_as_prototype_job (bool, optional): Flag indicating if the execution is
                done as a prototype job. If set to True or the handler hasn't got a `direct_execute` method, `execute` 
                is called, else `direct_execute` is called. Defaults to False.

        Returns:
            Any: The result of executing the pipeline function handler.
        Raises:
            NotImplementedError: If the node type is not implemented yet.
        """
    
        try:
            handler = pipeline_function_handler_dict[self.typ]
        except KeyError as e:
            raise NotImplementedError(f'Node type {self.typ} is not implemented yet.') from e

        params = self.get_params()
        if is_executed_as_prototype_job or not hasattr(handler, "direct_execute"):
            result = handler.execute(self.node_detail_form)
        else:
            result = handler.direct_execute(**params)

        return result

    # TODO: NOT PROPERLY DEFINED, ONLY TEMPORARY IMPLEMENTATION FOR TESTING
    def export_code(self):  #Not critical # Tomas part
        try:
            pipeline_function_handler_dict[self.typ]
        except KeyError as e:
            raise NotImplementedError(f'Node type {self.typ} is not implemented yet.') from e

        node_params = NodeParams()
        node_params.update(self.params)
        # image = FakeImage(self.typ, node_params)
        # code, imports = codeview_handler.get_image_code_and_imports(image, pipeline_function_handler_dict)
        # code = codeview_handler.remove_blank_lines_and_indent_from_code(code)
        code = ""
        imports = []

        return code, imports

    def get_params(self):  #Original implementation in node.py - don't deprecate
        kwargs = {}

        for key, values in self.node_detail_form.node_params.items():
            variable = values.get('variable')
            if variable is None:
                var_value = values.get('value')
            else:
                var_value = variable_handler.variables.get(variable)
                # if var_value is None:
                #     logger.warning(f'Variable {variable} is not stored or has a value of "None"')
                var_value = var_value.value if isinstance(var_value,
                                                          LocalVariable) else values.get('value')
            kwargs[key] = var_value
        # return list(kwargs.values())
        return kwargs
