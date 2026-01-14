from __future__ import annotations

    
class MDTException(Exception):
  def __init__(self, details:str) -> None:
    self.details = details
    super().__init__(details)
    
  def __str__(self) -> str:
    return repr(self)


class InternalError(MDTException):
  def __init__(self, details:str) -> None:
    super().__init__(details)


class TimeoutError(MDTException):
  def __init__(self, details:str) -> None:
    super().__init__(details)


class CancellationError(MDTException):
  def __init__(self, details:str) -> None:
    super().__init__(details)


class OperationError(MDTException):
  def __init__(self, details:str) -> None:
    super().__init__(details)


class RemoteError(MDTException):
  def __init__(self, details:str) -> None:
    super().__init__(details)

import requests
class MDTInstanceConnectionError(MDTException):
  def __init__(self, details:str, cause:requests.exceptions.ConnectionError) -> None:
    super().__init__(details)
    self.cause = cause

  def __repr__(self) -> str:
    return f"{self.__class__.__name__}(details={self.details}, cause={self.cause})"

   
class ResourceAlreadyExistsError(MDTException):
  def __init__(self, details:str) -> None:
    super().__init__(details)
      
  @classmethod
  def create(cls, resource_type:str, id_spec:str):
    return ResourceAlreadyExistsError(f"Resource(type={resource_type}, {id_spec})")
    
    
class ResourceNotFoundError(MDTException):
  def __init__(self, details:str) -> None:
    super().__init__(details)
      
  @classmethod
  def create(cls, resource_type:str, id_spec:str):
    return ResourceNotFoundError(f"Resource(type={resource_type}, {id_spec})")
        
    
class InvalidResourceStateError(MDTException):
  def __init__(self, details:str) -> None:
    super().__init__(details)
      
  @classmethod
  def create(cls, resource_type:str, id_spec:str, status):
    return InvalidResourceStateError(f"Resource(type={resource_type}, {id_spec}), status={status}")