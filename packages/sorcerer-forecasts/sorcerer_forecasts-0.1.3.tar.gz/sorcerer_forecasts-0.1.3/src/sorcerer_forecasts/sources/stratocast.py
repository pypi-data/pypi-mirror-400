import xarray
import s3fs
import jwt
import logging
import numpy as np
from datetime import timedelta, timezone


from sorcerer_forecasts.sources import ForecastSource

from sorcerer_forecasts.utils.region import get_region

from sorcerer_forecasts.entity.forecast import ForecastData
from sorcerer_forecasts.entity.geo import Point4

NUM_LEVELS = 80
RESOLUTION = 0.25

REGION_DIR_MAP = {
    'conus': 'oper'
}


class StratocastData(ForecastData):
  pres: float
  u: float
  v: float
  h: float


class Stratocast(ForecastSource[StratocastData]):
  _logger = logging.getLogger(__name__)

  def __init__(self, api_key: str):
    # Decode the API key
    payload = jwt.decode(api_key, options={"verify_signature": False})

    aws_access_key_id = payload['aws_access_key_id']
    aws_secret_access_key = payload['aws_secret_access_key']

    if aws_access_key_id is None or aws_secret_access_key is None:
      raise ValueError("Invalid API key")

    self.demo_user: str | None = payload['demo_user'] if 'demo_user' in payload else None

    self.s3 = s3fs.S3FileSystem(client_kwargs={'aws_access_key_id': aws_access_key_id, 'aws_secret_access_key': aws_secret_access_key})

  def fetch(self, location: Point4):
    for attempt in range(3):
      # Determine the forecast time and reference time
      forecast_time = location['time'].replace(minute=0, second=0, microsecond=0)

      ref_time = forecast_time.replace(hour=(forecast_time.hour // 6) * 6)
      ref_time = ref_time - (attempt * timedelta(hours=6))

      # Create the forecast ID
      forecast_id = self.forecast_id(location)

      self._logger.debug(f"{forecast_id} - FETCH START")

      try:
        region = get_region(location)
        region_dir = self.demo_user or REGION_DIR_MAP.get(region.name, region.name)
        path = f'stratocast/{region_dir}/{ref_time.strftime("%Y%m%d")}/{ref_time.strftime("%H")}'
        forecast_file = f'{forecast_time.strftime("%Y%m%d")}.t{forecast_time.strftime("%H")}z.stratocast.{str(RESOLUTION).replace(".", "p")}.ml{NUM_LEVELS}.wind.{region.name}.nc'

        # Open the dataset
        file = self.s3.open(f"s3://sorcerer-forecasts/{path}/{forecast_file}")

        contents = xarray.open_dataset(file, engine='h5netcdf')

        # Rename Time dimension to time,
        contents = contents.rename({'Time': 'time'})

        # Add time coordinates with explicit dtype; ensure tz-naive UTC to avoid warnings
        base_time = forecast_time.astimezone(timezone.utc).replace(tzinfo=None) if forecast_time.tzinfo is not None else forecast_time
        times = [base_time + timedelta(minutes=15 * i) for i in range(len(contents.time.values))]
        contents = contents.assign_coords(time=np.array(times, dtype='datetime64[ns]'))

        # Set resolution attribute
        contents.attrs['resolution'] = RESOLUTION

        self._logger.debug(f"{forecast_id} - FETCH SUCCESS")
        return contents

      except Exception as error:
        self._logger.error(f"{forecast_id} - FETCH FAILED: {error}")

    raise RuntimeError("Failed to fetch forecast for all reference times.")

  def forecast_id(self, location: Point4) -> str:
    forecast_time = location['time'].replace(minute=0, second=0, microsecond=0)
    region = get_region(location)
    return f'{forecast_time.strftime("%Y%m%d")}.t{forecast_time.strftime("%H")}z.stratocast.{str(RESOLUTION).replace(".", "p")}.ml{NUM_LEVELS}.wind.{region.name}'
