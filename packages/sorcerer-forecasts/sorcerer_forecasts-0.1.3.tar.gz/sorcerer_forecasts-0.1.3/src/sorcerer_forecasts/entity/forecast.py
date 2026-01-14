import xarray
import numpy
import logging
from datetime import datetime, timezone
from typing import Generic, TypeVar, TypedDict, cast

from sorcerer_forecasts.entity.geo import Point2, Point4, Region


class ForecastRegion(TypedDict):
  forecast_id: str
  dataset: xarray.Dataset


class ForecastData(TypedDict):
  """Base type for forecast data mappings used by services and sources."""
  pass


T = TypeVar('T', bound=ForecastData)


class Forecast(Generic[T]):
  _logger = logging.getLogger(__name__)

  def __init__(self, dataset: xarray.Dataset):
    """
    Forecast region.

    Parameters:
    - dataset: xarray.Dataset with time, level, latitude, longitude dimensions and resolution attribute. Dims must be in that order.
    """

    # Extract coordinates and levels from dataset
    self.times: list[datetime] = [datetime.fromtimestamp(time.astype('datetime64[s]').astype(int), tz=timezone.utc) for time in dataset.time.values]
    self.latitudes: numpy.ndarray = dataset.latitude.values
    self.longitudes: numpy.ndarray = dataset.longitude.values
    self.levels: numpy.ndarray = dataset.level.values
    self.vars: list[str] = list(dataset.data_vars)
    self.resolution = float(dataset.attrs['resolution'])

    # Create region
    lat_min, lat_max = self.latitudes.min(), self.latitudes.max() + self.resolution
    lon_min, lon_max = self.longitudes.min(), self.longitudes.max() + self.resolution
    self.region = Region(bottom_left=Point2(latitude=lat_min, longitude=lon_min), top_right=Point2(latitude=lat_max, longitude=lon_max))

    # Get temporal resolution by looking at the time dimension
    self.temporal_resolution = self.times[1] - self.times[0]
    self.temporal_resolution_seconds = self.temporal_resolution.total_seconds()

    # Extract levels for each variable into a dictionary
    self.data: list[dict[str, numpy.ndarray]] = []
    for i, _ in enumerate(self.times):
      time_data = {}
      for var in self.vars:
        time_data[var] = dataset.isel(time=i)[var].values

      self.data.append(time_data)

  def contains(self, time: datetime, latitude: float, longitude: float) -> bool:
    # Check if location is in region
    if not self.region.contains(Point2(latitude=latitude, longitude=longitude)):
      self._logger.debug(f"FAILED REGION CONTAINS: ({latitude}, {longitude})")
      return False

    # Check if time is in times
    if time not in self.times:
      self._logger.debug(f"FAILED TIME CONTAINS: {time}")
      return False

    return True

  def get(self, location: Point4) -> T | None:
    # Floor time to temporal resolution
    timestamp = location['time'].timestamp()
    floored_time = datetime.fromtimestamp(timestamp - (timestamp % self.temporal_resolution_seconds), tz=timezone.utc)

    if not self.contains(floored_time, location['latitude'], location['longitude']):
      self._logger.debug(f"FAILED CONTAINS")
      return None

    # Get time index
    time_index = self.times.index(floored_time)

    # Get latitude and longitude index
    lat_index, lon_index = self._get_latlon_index(location)

    # Get level index
    level_index = self._get_level_index(time_index, lat_index, lon_index, location['altitude'])

    data = {}
    for var in self.vars:
      data[var] = self.data[time_index][var][level_index, lat_index, lon_index]

    return cast(T, data)

  def _get_latlon_index(self, location: Point4) -> tuple[int, int]:
    bottom_left = self.region.bottom_left

    latitude_index = (location['latitude'] - bottom_left['latitude']) / self.resolution
    longitude_index = (location['longitude'] - bottom_left['longitude']) / self.resolution

    return int(latitude_index), int(longitude_index)

  def _get_level_index(self, time_index: int, lat_index: int, lon_index: int, altitude: float) -> int | None:
    time_data = self.data[time_index]

    if 'h' in time_data:
      level = time_data['h'][:, lat_index, lon_index]

      # Find closest level
      level_index = numpy.argmin(numpy.abs(level - altitude))

      return int(level_index)

    return None
