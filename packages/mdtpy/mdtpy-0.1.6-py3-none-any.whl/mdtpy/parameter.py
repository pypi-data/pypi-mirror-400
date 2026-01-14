from __future__ import annotations

from typing import cast, Optional, Mapping, Iterator

from .descriptor import MDTParameterDescriptor
from .reference import DefaultElementReference


class MDTParameter(DefaultElementReference):
  def __init__(self, descriptor: MDTParameterDescriptor):
    super().__init__(ref_string=descriptor.reference, endpoint=cast(str, descriptor.endpoint)) 
    self.descriptor = descriptor

  @property
  def id(self) -> str:
    """
    파라미터 식별자를 반환한다.

    Returns:
      str: 파라미터 식별자.
    """
    return self.descriptor.id

  @property
  def name(self) -> Optional[str]:
    """
    파라미터 이름을 반환한다.

    Returns:
      Optional[str]: 파라미터 이름.
    """
    return self.descriptor.name


class MDTParameterCollection(Mapping[str, MDTParameter]):
  def __init__(self, parameters: list[MDTParameter]):
    self.__param_dict = { param.id:param for param in parameters }

  def __len__(self) -> int:
    return len(self.__param_dict)

  def __iter__(self) -> Iterator[str]:
    return iter(self.__param_dict.keys())

  def __contains__(self, key: str) -> bool:
    return key in self.__param_dict

  def __getitem__(self, key: str) -> MDTParameter:
    return self.__param_dict[key]