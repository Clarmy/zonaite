from datetime import datetime, timezone
from io import StringIO

import pandas as pd
import requests
from tqdm import tqdm


class DecodedSynopCollector:
    """A collector class for retrieving decoded SYNOP meteorological data.

    This class provides functionality to fetch decoded SYNOP meteorological data
    from the Skyviewor open data platform. It supports retrieving various meteorological
    parameters such as temperature, humidity, and wind speed.

    Note:
        All datetime objects passed to methods must include timezone information.
        If timezone is not provided, the system will assume UTC.
    """

    def __init__(self):
        """Initialize the DecodedSynopCollector instance.

        Sets up the base URL and sub-path for constructing data request URLs.
        """
        self.base_url = "https://open-data.skyviewor.org"
        self.sub_url = "obervations/meteo/decoded-synops"

    @property
    def available_variables(self):
        """Get information about available meteorological variables.

        Returns:
            dict: A dictionary containing information about all available meteorological
                 variables, including variable names, units, and descriptions.
        """
        url = f"{self.base_url}/{self.sub_url}/infos/available-variables.json"
        response = requests.get(url, timeout=10)
        if response.ok:
            result = response.json()

        return result

    @property
    def available_stations(self):
        """Get information about available meteorological stations.

        Returns:
            dict: A dictionary containing information about all available meteorological
                 stations, including station IDs, names, countries, latitudes, longitudes, elevations, established dates, and closed dates.
        """
        url = f"{self.base_url}/{self.sub_url}/infos/available-stations.json"
        response = requests.get(url, timeout=10)
        if response.ok:
            result = response.json()

        return result

    def _get_url(self, dt: datetime, station_id: str):
        """Construct the data request URL based on date and station ID.

        Args:
            dt (datetime): Target date and time (must include timezone information)
            station_id (str): Meteorological station ID

        Returns:
            str: Constructed data request URL

        Note:
            The datetime object will be converted to UTC internally.
        """
        search_dt = dt.astimezone(timezone.utc)
        return f"{self.base_url}/{self.sub_url}/{search_dt.year}/{search_dt.month:02d}/{station_id}.csv"

    def fetch(self, start_dt: datetime, end_dt: datetime, station_id: str):
        """Fetch meteorological data for a specified time range.

        Args:
            start_dt (datetime): Start date and time (must include timezone information)
            end_dt (datetime): End date and time (must include timezone information)
            station_id (str): Meteorological station ID

        Returns:
            pandas.DataFrame: DataFrame containing all meteorological data for the
                            requested time range, or None if no data is available

        Note:
            Both start_dt and end_dt will be converted to UTC internally.
            The time range is processed month by month to handle large date ranges efficiently.
        """
        dfs = []
        date_range = pd.date_range(start=start_dt, end=end_dt, freq="31D")
        for dt in tqdm(
            date_range, desc=f"Fetching data for {station_id} from {start_dt} to {end_dt}"
        ):
            url = self._get_url(dt, station_id)
            response = requests.get(url, timeout=10)
            if response.ok:
                df = pd.read_csv(StringIO(response.text))
                dfs.append(df)
            else:
                status_code = response.status_code
                if status_code == 404:
                    print(
                        f"No data available for {dt.date()} of station {station_id}"
                    )
                else:
                    print(f"Error fetching data from {url}: {status_code}")

        if dfs:
            return pd.concat(dfs, ignore_index=True)
        return None


def get_decoded_synop_data(start_dt: datetime, end_dt: datetime, station_id: str):
    """Get decoded SYNOP meteorological data for a specified time range and station ID.

    Args:
        start_dt (datetime): Start date and time (must include timezone information)
        end_dt (datetime): End date and time (must include timezone information)
        station_id (str): Meteorological station ID
    """
    collector = DecodedSynopCollector()
    return collector.fetch(start_dt, end_dt, station_id)


if __name__ == "__main__":
    collector = DecodedSynopCollector()

    print("Available variables:")
    print(collector.available_variables)

    print("Available stations:")
    print(collector.available_stations)
    from datetime import timezone

    start_date = datetime(2000, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2015, 3, 31, tzinfo=timezone.utc)
    station_id = "54511"

    print(
        f"\nFetching data for station {station_id} from {start_date.date()} to {end_date.date()}"
    )
    df = collector.fetch(start_date, end_date, station_id)

    if df is not None:
        print("\nData preview:")
        print(df)
        print("\nData info:")
        print(df.info())
    else:
        print("No data available for the specified period.")
