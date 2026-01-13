

from __future__ import annotations

import json
from typing import Any, Dict, Optional, Sequence, Tuple

from le import _arg_types

from le import apifunction
from le import computedobject


class RestCall(computedobject.ComputedObject):
  """An object to represent an Earth Engine image."""

  _initialized = False

  def __init__(
      self
  ):
    """
    """
    self.initialize()


  @classmethod
  def initialize(cls) -> None:
    """Imports API functions to this class."""
    if not cls._initialized:
      apifunction.ApiFunction.importApi(cls, cls.name(), cls.name())
      cls._initialized = True

  @classmethod
  def reset(cls) -> None:
    """Removes imported API functions from this class."""
    apifunction.ApiFunction.clearApi(cls)
    cls._initialized = False

  @staticmethod
  def name() -> str:
    return 'RestCall'

  def post_lisflood(
      self,
      url: _arg_types.String,
      body: _arg_types.Dictionary,
  ) -> _arg_types.String:
    """
    """

    return apifunction.ApiFunction.call_(
        self.name() + '.post_lisflood',
        url,
        body
    )