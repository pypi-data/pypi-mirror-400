from __future__ import annotations

from typing import Any, Optional

from ..instance import MDTInstanceManager, connect
from ..reference import ElementReference, ElementValueType
from ..value import ElementValueDict
from ..exceptions import ResourceNotFoundError


def task_output(task_id:str, argument:str) -> LazyTaskOutput:
  return LazyTaskOutput(task_id, argument)


class DagContext:
  def __init__(self, mdt_endpoint:str, task_outputs:dict[str, ElementValueDict]={}) -> None:
    self.mdt_endpoint = mdt_endpoint
    self.__task_output_dict:dict[str, ElementValueDict] = task_outputs

  def connect_mdt(self) -> MDTInstanceManager:
    return connect(self.mdt_endpoint)

  def get_task_output(self, task_id:str) -> ElementValueDict:
    assert task_id in self.__task_output_dict, f"Task has not been run: id= {task_id}"
    return self.__task_output_dict[task_id]

  def set_task_output(self, task_id:str, output:ElementValueDict) -> None:
    self.__task_output_dict[task_id] = output

  def to_dict(self) -> dict[str, Any]:
    return { 'mdt_endpoint': self.mdt_endpoint, 'task_outputs': self.__task_output_dict }

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> DagContext:
    return cls(data['mdt_endpoint'], data['task_outputs'])

  def __repr__(self) -> str:
    import json
    return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


class OperationSubmodelInvocation:
  def __init__(self, instance: str, submodel: str,
                arguments: dict[str, ElementReference|LazyTaskOutput|Optional[ElementValueType]],
                task_id: Optional[str]=None) -> None:
    self._task_id = task_id if task_id else f"{instance}:{submodel}"
    self.instance = instance
    self.submodel = submodel
    self.arguments = arguments

  @property
  def id(self) -> str:
    return self._task_id

  def run(self, context:DagContext, **kwargs: Any) -> ElementValueDict:
    from ..instance import mdt_manager
    assert mdt_manager is not None, "MDT Manager is not connected"

    op_submodel = mdt_manager.instances[self.instance].operations[self.submodel]

    arg_values:dict[str, Optional[ElementValueType]] = {}
    for arg_id, arg in self.arguments.items():
      if isinstance(arg, LazyTaskOutput):
        arg_values[arg_id] = arg.get(context)
      elif isinstance(arg, ElementReference):
        arg_values[arg_id] = arg.read_value()
      else:
        arg_values[arg_id] = arg
    output = op_submodel.invoke(**arg_values)
    context.set_task_output(self.id, output)
    return output


class LazyTaskOutput:
  def __init__(self, task_id:str, argument:str) -> None:
    self.task_id = task_id
    self.argument = argument

  def get(self, context:DagContext) -> Optional[ElementValueType]:
    outputs = context.get_task_output(self.task_id)
    try:
      return outputs[self.argument]
    except KeyError:
      raise ResourceNotFoundError.create("TaskOutput", f"task_id={self.task_id}, argument={self.argument}")