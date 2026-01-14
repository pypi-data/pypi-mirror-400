from abc import ABC, abstractmethod
from typing import Generic, TypeVar
import xarray

from sorcerer_forecasts.entity.geo import Point4
from sorcerer_forecasts.entity.forecast import ForecastData


T = TypeVar("T", bound=ForecastData)


class ForecastSource(Generic[T], ABC):
  @abstractmethod
  def fetch(self, location: Point4) -> xarray.Dataset:
    pass

  @abstractmethod
  def forecast_id(self, location: Point4) -> str:
    pass
