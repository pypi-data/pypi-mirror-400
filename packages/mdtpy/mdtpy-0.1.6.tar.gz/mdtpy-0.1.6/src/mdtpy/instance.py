from __future__ import annotations

from typing import Any, Iterator, Generator, Optional
from abc import ABC, abstractmethod

import requests
from urllib.parse import quote

from .submodel import SubmodelService, SubmodelServiceCollection
from .reference import DefaultElementReference
from .descriptor import InstanceDescriptor, MDTParameterDescriptor, MDTSubmodelDescriptor, MDTOperationDescriptor, MDTAssetType, AssetKind, MDTInstanceStatus
from .parameter import MDTParameterCollection, MDTParameter
from .timeseries import TimeSeriesService
from .operation import OperationSubmodelService
from .http_client import parse_response, parse_list_response, parse_none_response
from .exceptions import InvalidResourceStateError

__mdt_endpoint:Optional[str] = None
mdt_manager:Optional[MDTInstanceManager] = None


def connect(endpoint: str) -> MDTInstanceManager:
  global __mdt_endpoint, mdt_manager
  __mdt_endpoint = endpoint
  mdt_manager = MDTInstanceManager(endpoint)
  return mdt_manager

class MDTInstanceManager:
  def __init__(self, endpoint: str):
    self.__endpoint = endpoint
    self.__instances = MDTInstanceCollection()

  @property
  def endpoint(self) -> str:
    return self.__endpoint

  @property
  def instances(self) -> MDTInstanceCollection:
    return self.__instances

  def resolve_reference(self, ref_string: str) -> DefaultElementReference:
    parts = ref_string.split(':')
    match parts[0]:
      case 'param':
        assert len(parts) == 3, f"Invalid parameter reference: {ref_string}"
        return self.instances[parts[1]].parameters[parts[2]]
      case 'oparg':
        assert len(parts) == 5, f"Invalid operation argument reference: {ref_string}"
        op = self.instances[parts[1]].operations[parts[2]]
        match parts[3]:
          case 'in':
            return op.input_arguments[parts[4]]
          case 'out':
            return op.output_arguments[parts[4]]
          case _:
            raise ValueError(f"Invalid operation argument reference: {ref_string}")
      case _:
        url = f"{self.__endpoint}/references/$url?ref={quote(ref_string)}"
        resp = requests.get(url)
        return DefaultElementReference(ref_string=ref_string, endpoint=parse_response(resp))


class MDTInstanceCollection:
  def __init__(self):
    assert __mdt_endpoint is not None, "MDTManager is not connected"
    self.__url_prefix = f"{__mdt_endpoint}/instances"

  def __bool__(self) -> bool:
    return len(self) > 0

  def __len__(self) -> int:
    resp = requests.get(self.__url_prefix)
    return len(parse_list_response(resp, InstanceDescriptor))
        
  def __iter__(self) -> Iterator[MDTInstance]:
      resp = requests.get(self.__url_prefix)
      inst_desc_list = parse_list_response(resp, InstanceDescriptor)
      return iter(MDTInstance(inst_desc) for inst_desc in inst_desc_list)
  
  def __contains__(self, key:str) -> bool:
      url = f'{self.__url_prefix}/{key}'
      resp = requests.get(url)
      return resp.status_code == 200
        
  def __getitem__(self, key:str) -> MDTInstance:
      url = f'{self.__url_prefix}/{key}'
      resp = requests.get(url)
      inst_desc: InstanceDescriptor = parse_response(resp, InstanceDescriptor)  # type: ignore
      return MDTInstance(inst_desc)
    
  def find(self, condition:str) -> Generator[MDTInstance, None, None]:
      resp = requests.get(self.__url_prefix, params={'filter': f"{condition}"})
      inst_desc_list = parse_list_response(resp, InstanceDescriptor)
      return (MDTInstance(inst_desc) for inst_desc in inst_desc_list)
    
  def add(self, id:str, port:int, inst_dir:str) -> MDTInstance:
    import shutil
    shutil.make_archive(inst_dir, 'zip', inst_dir)
    zipped_file = f'{inst_dir}.zip'
    
    from requests_toolbelt.multipart.encoder import MultipartEncoder
    m = MultipartEncoder(
      fields = {
        'id': id,
        'port': str(port),
        'bundle': ('filename', open(zipped_file, 'rb'), 'application/zip')
      }
    )
    resp = requests.post(self.__url_prefix, data=m, headers={'Content-Type': m.content_type}, verify=False)
    inst_desc: InstanceDescriptor = parse_response(resp, InstanceDescriptor)  # type: ignore 
    return MDTInstance(inst_desc)
    
  def __delitem__(self, key:str) -> None:
    url = f'{self.__url_prefix}/{key}'
    resp = requests.delete(url)
    parse_none_response(resp)

  def remove(self, id:str) -> None:
    url = f'{self.__url_prefix}/{id}'
    resp = requests.delete(url)
    return parse_none_response(resp)
        
  def remove_all(self) -> None:
    url = f"{self.__url_prefix}"
    resp = requests.delete(url)
    parse_none_response(resp)


class MDTInstance:
  def __init__(self, descriptor:InstanceDescriptor) -> None:
    self.__descriptor = descriptor
    assert __mdt_endpoint is not None, "MDTManager is not connected"
    self.__instanceUrl = f"{__mdt_endpoint}/instances/{descriptor.id}"
    self.__submodel_descriptors = None

  @property
  def id(self) -> str:
    return self.__descriptor.id

  @property
  def aas_id(self) -> str:
    return self.__descriptor.aas_id

  @property
  def aas_id_short(self) -> str|None:
    return self.__descriptor.aas_id_short

  @property
  def global_asset_id(self) -> str|None:
    return self.__descriptor.global_asset_id

  @property
  def asset_type(self) -> MDTAssetType|None:
    return self.__descriptor.asset_type

  @property
  def asset_kind(self) -> AssetKind|None:
    return self.__descriptor.asset_kind

  @property
  def status(self) -> MDTInstanceStatus:
    return self.__descriptor.status

  @property
  def base_endpoint(self) -> str|None:
    return self.__descriptor.base_endpoint

  def is_running(self) -> bool:
    return self.status == MDTInstanceStatus.RUNNING

  @property
  def parameters(self) -> MDTParameterCollection:
    if not self.is_running():
      raise InvalidResourceStateError.create("MDTInstance", f"id={self.id}", self.status)

    url = f"{self.__instanceUrl}/model/parameters"
    resp = requests.get(url)
    desc_list = parse_list_response(resp, MDTParameterDescriptor)
    return MDTParameterCollection([MDTParameter(desc) for desc in desc_list])

  @property
  def submodel_descriptors(self) -> dict[str, MDTSubmodelDescriptor]:
    if not self.is_running():
      raise InvalidResourceStateError.create("MDTInstance", f"id={self.id}", self.status)

    url = f"{self.__instanceUrl}/model/submodels"
    resp = requests.get(url)
    return { desc.id_short:desc for desc in parse_list_response(resp, MDTSubmodelDescriptor) }

  @property
  def operation_descriptors(self) -> dict[str, MDTOperationDescriptor]:
    if not self.is_running():
      raise InvalidResourceStateError.create("MDTInstance", f"id={self.id}", self.status)

    url = f"{self.__instanceUrl}/model/operations"
    resp = requests.get(url)
    return { desc.id:desc for desc in parse_list_response(resp, MDTOperationDescriptor) }

  @property
  def submodel_services(self) -> SubmodelServiceCollection:
    return SubmodelServiceCollection[SubmodelService](self, self.submodel_descriptors)

  @property
  def operations(self) -> SubmodelServiceCollection[OperationSubmodelService]:
    op_sm_desc_dict = { id:sm_desc for id, sm_desc in self.submodel_descriptors.items() \
                                        if sm_desc.is_simulation() or sm_desc.is_ai() }
    return SubmodelServiceCollection[OperationSubmodelService](self, op_sm_desc_dict)

  @property
  def timeseries(self) -> SubmodelServiceCollection[TimeSeriesService]:
    ts_sm_desc_dict = { id:sm_desc for id, sm_desc in self.submodel_descriptors.items() if sm_desc.is_time_series() }
    return SubmodelServiceCollection[TimeSeriesService](self, ts_sm_desc_dict)

  def start(self, nowait=False) -> None:
    url = f"{self.__instanceUrl}/start"
    resp = requests.put(url, data="")

    self.reload_descriptor()
    if nowait:
      if self.__descriptor.status != MDTInstanceStatus.STARTING and MDTInstanceStatus.RUNNING:
        raise InvalidResourceStateError.create("MDTInstance", f"id={self.id}", self.__descriptor.status)
    else:
      poller = InstanceStartPoller(f"{self.__instanceUrl}", init_desc=self.__descriptor)
      poller.wait_for_done()
      self.__descriptor = poller.desc
      if self.__descriptor.status != MDTInstanceStatus.RUNNING:
        raise InvalidResourceStateError.create("MDTInstance", f"id={self.id}", self.__descriptor.status)
  
  def stop(self, nowait=False) -> None:
    url = f"{self.__instanceUrl}/stop"
    resp = requests.put(url, data="")
    parse_none_response(resp)

    self.reload_descriptor()
    if nowait:
      if self.__descriptor.status != MDTInstanceStatus.STOPPING and MDTInstanceStatus.STOPPED:
        raise InvalidResourceStateError.create("MDTInstance", f"id={self.id}", self.__descriptor.status)
    else:
      poller = InstanceStopPoller(f"{self.__instanceUrl}", init_desc=self.__descriptor)
      poller.wait_for_done()
      self.__descriptor = poller.desc
      if self.__descriptor.status != MDTInstanceStatus.STOPPED:
        raise InvalidResourceStateError.create("MDTInstance", f"id={self.id}", self.__descriptor.status)
    
  def reload_descriptor(self) -> InstanceDescriptor:
    resp = requests.get(self.__instanceUrl)
    self.__descriptor: InstanceDescriptor = parse_response(resp, InstanceDescriptor)  # type: ignore
    return self.__descriptor

  def __str__(self) -> str:
    return f"HttpMDTInstance({self.__descriptor})"

  def __repr__(self) -> str:
    return self.__str__()


import time
class StatusPoller(ABC):
  """
  Abstract base class for polling the status of an operation.
  Attributes:
    poll_interval (float): The interval in seconds between each poll.
    timeout (Optional[float]): The maximum time in seconds to wait for the operation to complete. If None, wait indefinitely.
  Methods:
    is_done() -> bool:
        Abstract method to check if the operation is done. Must be implemented by subclasses.
    wait_for_done() -> None:
      Waits for the operation to complete by repeatedly calling `check_done` at intervals specified by `poll_interval`.
      Raises:
        TimeoutError: If the operation does not complete within the specified timeout.
  """
  def __init__(self, poll_interval:float, timeout:float|None=None):
      self.poll_interval = poll_interval
      self.timeout = timeout
      
  @abstractmethod
  def is_done(self) -> bool: pass
  
  def wait_for_done(self) -> None:
      # 타임아웃 (self.timeout)이 있는 경우 최종 제한 시간을 계산하고,    
      # 타임아웃이 없는 경우 due를 None으로 설정하여 무제한 대기하도록 한다.
      started = time.time()
      due = started + self.timeout if self.timeout else None
      # 다음 폴링 시간을 계산한다.
      next_wakeup = started + self.poll_interval
      
      while not self.is_done():
          now = time.time()
          
          # 타임 아웃까지 남은 시간이 일정 시간 이내인 경우에는 TimeoutError를 발생시킨다.
          # 그렇지 않은 경우는 다음 폴링 시간까지 대기한다.
          if due and (due - now) < 0.01:
              raise TimeoutError(f'timeout={self.timeout}')
          
          # 다음 폴링 시간까지 남은 시간이 짧으면 대기하지 않고 바로 다음 폴링 시도한다.
          sleep_time = next_wakeup - now
          if sleep_time > 0.001:
              time.sleep(sleep_time)
          next_wakeup += self.poll_interval

class InstanceStartPoller(StatusPoller):
    def __init__(self, status_url:str, init_desc:InstanceDescriptor|None=None,
                 poll_interval:float=1.0, timeout:float|None=None) -> None:
        super().__init__(poll_interval=poll_interval, timeout=timeout)
        self.status_url = status_url
        self.desc = init_desc
        
    def is_done(self) -> bool:
        if self.desc.status == MDTInstanceStatus.STARTING:
            resp = requests.get(self.status_url)
            self.desc: InstanceDescriptor = parse_response(resp, InstanceDescriptor)  # type: ignore
            return self.desc.status != MDTInstanceStatus.STARTING
        else:
            return True
    
class InstanceStopPoller(StatusPoller):
  def __init__(self, status_url:str, init_desc:InstanceDescriptor|None=None,
                poll_interval:float=1.0, timeout:float|None=None) -> None:
    super().__init__(poll_interval=poll_interval, timeout=timeout)
    self.status_url = status_url
    self.desc = init_desc
        
  def is_done(self) -> bool:
    resp = requests.get(self.status_url)
    self.desc: InstanceDescriptor = parse_response(resp, InstanceDescriptor)  # type: ignore
    return self.desc.status == MDTInstanceStatus.STOPPED