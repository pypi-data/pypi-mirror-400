import os
import xarray
import logging
from typing import Generic, TypeVar

from sorcerer_forecasts.entity.geo import Point4

from sorcerer_forecasts.entity.forecast import Forecast, ForecastData, ForecastRegion

from sorcerer_forecasts.sources import ForecastSource

T = TypeVar('T', bound=ForecastData)


class ForecastService(Generic[T]):
  _logger = logging.getLogger(__name__)

  def __init__(self, source: ForecastSource[T], cache_dir: str | None = None):
    self.cache_dir = cache_dir
    self.source: ForecastSource[T] = source

    # Create cache directory if it doesn't exist
    if self.cache_dir:
      os.makedirs(self.cache_dir, exist_ok=True)

    self.forecasts: dict[str, Forecast] = {}

  def get(self, location: Point4) -> T | None:
    forecast_id = self.source.forecast_id(location)
    forecast_path = os.path.join(self.cache_dir, forecast_id + ".nc") if self.cache_dir else None

    if forecast_id in self.forecasts:
      return self.forecasts[forecast_id].get(location)

    if forecast_path and os.path.exists(forecast_path):
      dataset = xarray.load_dataset(forecast_path)
      self.forecasts[forecast_id] = Forecast[T](dataset)
      return self.forecasts[forecast_id].get(location)

    dataset = self.source.fetch(location)

    if forecast_path:
      # Clean up stale encoding referencing old dimension names (e.g., 'Time')
      dataset.encoding.pop('unlimited_dims', None)
      dataset.to_netcdf(forecast_path)

    self.forecasts[forecast_id] = Forecast(dataset)
    return self.forecasts[forecast_id].get(location)

  def get_region(self, location: Point4) -> ForecastRegion | None:
    forecast_id = self.source.forecast_id(location)
    forecast_path = os.path.join(self.cache_dir, forecast_id + ".nc") if self.cache_dir else None

    if forecast_path and os.path.exists(forecast_path):
      return {'forecast_id': forecast_id, 'dataset': xarray.load_dataset(forecast_path)}

    dataset = self.source.fetch(location)

    if dataset is None:
      return None

    dataset.encoding.pop('unlimited_dims', None)

    if forecast_path:
      dataset.to_netcdf(forecast_path)

    return {'forecast_id': forecast_id, 'dataset': dataset}
