from __future__ import annotations

from typing import Any, Optional
from abc import ABC, abstractmethod

import logging
from functools import cached_property

from airflow.sdk import Variable, get_current_context
from airflow.models import TaskInstance

from ..instance import MDTInstanceManager, connect
from ..operation import OperationSubmodelService
from ..reference import ElementReference, ElementValueType
from ..value import ElementValueDict
from ..exceptions import ResourceNotFoundError


def task_output(task_id:str, argument:str) -> TaskOutputArgument:
  return TaskOutputArgument(task_id, argument)

def reference(ref_string:str) -> ElementReferenceArgument:
  return ElementReferenceArgument(ref_string)

def value(value:ElementValueType) -> ValueArgument:
  return ValueArgument(value)


class DagContext:
  def __init__(self) -> None:
    self.mdt_endpoint = Variable.get("mdt_endpoint")
    self.mdt_manager = connect(self.mdt_endpoint)

  @property
  def task_id(self) -> str:
    return self.task_instance['task_id']

  def get_operation_submodel(self, instance:str, submodel:str) -> OperationSubmodelService:
    return self.mdt_manager.instances[instance].operations[submodel]

  def resolve_reference(self, ref_string:str) -> ElementReference:
    return self.mdt_manager.resolve_reference(ref_string)

  @cached_property
  def task_instance(self) -> TaskInstance:
    ctx = get_current_context()
    assert ctx is not None, "Airflow context is not available"
    return ctx['ti']

  def get_task_output_argument(self, task_id:str, argument:str) -> ElementValueDict:
    ti = self.task_instance
    logging.info(f'taskInstance: {ti}, task_id: {task_id}, argument: {argument}')

    output_args = ti.xcom_pull(task_ids=task_id, key='task_output')
    assert output_args is not None, f"Task output for {task_id} is not found"

    logging.info(f"Fetching task output for {task_id}[{argument}] from {output_args}")
    return output_args[argument]

  def set_task_output(self, task_id:str, output:ElementValueDict) -> None:
    ti = self.task_instance
    logging.info(f"Setting task output for {task_id}: {output}")
    ti.xcom_push(key='task_output', value=output)


class TaskArgument(ABC):
  @abstractmethod
  def get(self, context:DagContext) -> ElementReference|Optional[ElementValueType]: ...

class TaskOutputArgument(TaskArgument):
  def __init__(self, task_id:str, argument:str) -> None:
    self.task_id = task_id
    self.argument = argument

  def get(self, context:DagContext) -> ElementReference|Optional[ElementValueType]:
    return context.get_task_output_argument(self.task_id, self.argument)

  def __repr__(self) -> str:
    return f"task_output({self.task_id}[{self.argument}])"

class ElementReferenceArgument(TaskArgument):
  def __init__(self, ref_string:str) -> None:
    self.ref_string = ref_string

  def get(self, context:DagContext) -> ElementReference|Optional[ElementValueType]:
    return context.resolve_reference(self.ref_string)

  def __repr__(self) -> str:
    return f"reference({self.ref_string})"

class ValueArgument(TaskArgument):
  def __init__(self, value:ElementValueType) -> None:
    self.value = value

  def get(self, context:DagContext) -> ElementReference|Optional[ElementValueType]:
    return self.value

  def __repr__(self) -> str:
    return f"value({self.value})"


class OperationSubmodelInvocation:
  def __init__(self, instance: str, submodel: str, arguments: dict[str, TaskArgument] ) -> None:
    self.instance = instance
    self.submodel = submodel
    self.arguments = arguments

  def run(self) -> None:
    context = DagContext()
    op_submodel = context.get_operation_submodel(self.instance, self.submodel)
    args:dict[str, ElementReference|Optional[ElementValueType]] = {}
    for arg_id, arg in self.arguments.items():
      args[arg_id] = arg.get(context)
    out_args = op_submodel.invoke(**args)
    context.set_task_output(context.task_id, out_args)

  def __repr__(self) -> str:
    return f"OperationSubmodelInvocation(task={self.instance}:{self.submodel}, arguments={self.arguments})"
