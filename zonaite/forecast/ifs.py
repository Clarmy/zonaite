"""ECMWF IFS (Integrated Forecasting System) Data Downloader

This module provides functionality to download specific elements from ECMWF's IFS
(Integrated Forecasting System) data. It supports efficient partial downloads by 
using idx files to locate and download only the required data elements.

Key Features:
    - Selective download of specific parameters and levels
    - Efficient byte-range requests for partial file downloads
    - Performance monitoring and logging
    - Object-oriented idx file parsing and querying
    - Type-safe data structures using dataclasses

Example:
    >>> from zonaite.forecast.ifs import download_ifs_data
    >>> elements = [
    ...     {"param": "t", "levtype": "sfc", "levelist": "2"},
    ...     {"param": "u", "levtype": "pl", "levelist": "10"}
    ... ]
    >>> result = download_ifs_data(
    ...     date_str="20250326",
    ...     cycle_str="00",
    ...     forecast_hour="000",
    ...     elements=elements,
    ...     output_path="ifs_data.grib"
    ... )
    >>> if result.success:
    ...     print(f"Downloaded {result.file_size_mb:.2f}MB")

Notes:
    - IFS data is available from ECMWF's data store
    - File naming format follows ECMWF conventions
    - Supported forecast cycles: 00, 12
    - Forecast hours range: 000-336
"""

import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

import boto3
from botocore import UNSIGNED
from botocore.config import Config
from loguru import logger
import json


@dataclass
class IFSDownloadResult:
    """Result of IFS data download operation

    Attributes:
        success (bool): Whether the download was successful
        date (str): The date of the IFS data in format "YYYYMMDD"
        cycle (str): The cycle hour in format "HH"
        forecast_hour (str): The forecast hour in format "HHH"
        elements (List[Dict]): List of downloaded elements with their levels
        file_format (str): Format of the downloaded file, defaults to "grib2"
        file_path (Optional[str]): Path where the file was saved
        file_size_mb (Optional[float]): Size of the downloaded file in MB
        download_time_s (Optional[float]): Total download time in seconds
        download_speed_mbs (Optional[float]): Average download speed in MB/s
        error_message (Optional[str]): Error message if download failed
    """

    success: bool
    date: str
    cycle: str
    forecast_hour: str
    elements: List[Dict]
    file_format: str = "grib2"
    file_path: Optional[str] = None
    file_size_mb: Optional[float] = None
    download_time_s: Optional[float] = None
    download_speed_mbs: Optional[float] = None
    error_message: Optional[str] = None


@dataclass
class GribElement:
    """Represents a single element in a GRIB file from IFS

    Attributes:
        param (str): Parameter name (e.g., "t", "u", "v")
        levtype (str): Level type (e.g., "pl", "sfc", "sol")
        levelist (Optional[str]): Level value if applicable
        start_byte (int): Start byte position in the grib file
        end_byte (int): End byte position in the grib file
    """
    param: str
    levtype: str
    levelist: Optional[str]
    start_byte: int
    end_byte: int

class GribIdx:
    """Parser and query interface for GRIB idx files

    This class provides functionality to parse IFS idx files and query specific
    elements within them. It maintains an internal mapping of parameters and levels
    to their byte ranges in the corresponding GRIB file.

    Attributes:
        elements (List[GribElement]): List of all elements found in the idx file
    """

    def __init__(self, idx_content: str):
        """Initialize GribIdx with idx file content

        Args:
            idx_content (str): Content of the idx file as string
        """
        self.elements = self._parse_idx_content(idx_content)

    def _parse_idx_content(self, idx_content: str) -> List[GribElement]:
        """Parse idx file content into GribElement objects

        Args:
            idx_content (str): Content of the idx file in JSON format

        Returns:
            List[GribElement]: List of parsed elements
        """
        elements = []
        lines = idx_content.strip().split("\n")

        for i, line in enumerate(lines):
            if not line.strip():
                continue

            entry = json.loads(line)
            start_byte = entry["_offset"]
            end_byte = start_byte + entry["_length"]

            elements.append(
                GribElement(
                    param=entry["param"],
                    levtype=entry["levtype"],
                    levelist=entry.get("levelist"),  # levelist 可能不存在
                    start_byte=start_byte,
                    end_byte=end_byte,
                )
            )

        return elements

    def find_elements(self, target_elements: List[Dict]) -> List[GribElement]:
        """Find specified elements in the idx file

        Args:
            target_elements (List[Dict]): List of elements to find, each containing:
                - param (str): Parameter name to find
                - levtype (str): Level type to find
                - levelist (Optional[str]): Level value to find if applicable

        Returns:
            List[GribElement]: List of matched elements with their byte ranges
        """
        result = []
        for target in target_elements:
            for elem in self.elements:
                if (elem.param == target["param"] and 
                    elem.levtype == target["levtype"] and
                    str(elem.levelist) == str(target.get("levelist"))):  # 确保类型一致
                    logger.info(f"Found match: {elem.param} @ {elem.levtype} level {elem.levelist}")
                    result.append(elem)
        return result

    def get_byte_ranges(self, target_elements: List[Dict]) -> List[Tuple[int, int]]:
        """Get byte ranges for specified elements

        Args:
            target_elements (List[Dict]): List of elements to find

        Returns:
            List[Tuple[int, int]]: List of (start_byte, end_byte) tuples
        """
        elements = self.find_elements(target_elements)
        return [(elem.start_byte, elem.end_byte) for elem in elements]


def download_bytes(
    s3_client, bucket: str, key: str, start_byte: int, end_byte: int
) -> bytes:
    """Download data for specified byte range from S3

    This function downloads a specific byte range from an S3 object and logs the
    download performance metrics including size, time, and speed.

    Args:
        s3_client: Boto3 S3 client instance
        bucket (str): S3 bucket name
        key (str): S3 object key (path to the file in the bucket)
        start_byte (int): Starting byte position (inclusive)
        end_byte (int): Ending byte position (exclusive)

    Returns:
        bytes: The downloaded data within the specified byte range

    Raises:
        botocore.exceptions.ClientError: If there's an error accessing the S3 object
        ValueError: If start_byte is greater than or equal to end_byte

    Example:
        >>> s3_client = boto3.client('s3')
        >>> data = download_bytes(
        ...     s3_client,
        ...     'ecmwf-forecasts',
        ...     '20250326/00z/ifs/0p25/oper/20250326000000-000h-oper-fc.grib2',
        ...     1000,
        ...     2000
        ... )
        >>> len(data)  # Size of downloaded chunk
        1000
    """
    chunk_size = end_byte - start_byte
    start_time = time.time()

    response = s3_client.get_object(
        Bucket=bucket, Key=key, Range=f"bytes={start_byte}-{end_byte-1}"
    )
    data = response["Body"].read()

    end_time = time.time()
    duration = end_time - start_time
    speed_mbps = (chunk_size / 1024 / 1024) / duration if duration > 0 else 0

    logger.info(
        f"Download completed: {chunk_size/1024/1024:.2f}MB, Time: {duration:.2f}s, Speed: {speed_mbps:.2f}MB/s"
    )

    return data


def download_ifs_data(
    dt: datetime,
    forecast_hour: int,
    elements: List[Dict],
    output_path: str,
    bucket: str = "ecmwf-forecasts",
    region: str = "eu-central-1",
) -> IFSDownloadResult:
    """Download IFS data for specified time and elements

    This function downloads selected elements from ECMWF's IFS (Integrated Forecasting System)
    data stored in a public S3 bucket. It first downloads an idx file to locate the
    byte ranges for requested elements, then downloads only the needed parts of the
    grib2 file. The function supports partial downloads of specific variables at
    specific levels, making it efficient for cases where only certain elements are needed.

    Args:
        dt (datetime): Datetime object for the forecast initialization time
        forecast_hour (int): Forecast hour (e.g., 0, 3, 336)
        elements (List[Dict]): List of elements to download, each containing:
            - param (str): Parameter name (e.g., "t", "u", "v")
            - levtype (str): Level type (e.g., "pl", "sfc", "sol")
            - levelist (Optional[str]): Level value if applicable
        output_path (str): Path where to save the downloaded grib2 file
        bucket (str, optional): S3 bucket name. Defaults to 'ecmwf-forecasts'
        region (str, optional): AWS region. Defaults to 'eu-central-1'

    Returns:
        IFSDownloadResult: Download result containing:
            - success (bool): Whether the download was successful
            - date (str): The requested date
            - cycle (str): The requested cycle
            - forecast_hour (str): The requested forecast hour
            - elements (List[Dict]): The requested elements
            - file_format (str): Format of the downloaded file ("grib2")
            - file_path (str): Path where the file was saved
            - file_size_mb (float): Size of the downloaded file in MB
            - download_time_s (float): Total download time in seconds
            - download_speed_mbs (float): Average download speed in MB/s
            - error_message (str): Error message if download failed

    Raises:
        Exception: If there's an error during download, parsing, or file writing

    Example:
        >>> elements = [
        ...     {"param": "2t", "levtype": "sfc"},  # 2m temperature
        ...     {"param": "10u", "levtype": "sfc"},  # 10m U wind component
        ...     {"param": "10v", "levtype": "sfc"}   # 10m V wind component
        ... ]
        >>> result = download_ifs_data(
        ...     dt=datetime.now(timezone.utc),
        ...     forecast_hour=0,
        ...     elements=elements,
        ...     output_path="ifs_data.grib2"
        ... )
        >>> if result.success:
        ...     print(f"Downloaded {result.file_size_mb:.2f}MB in {result.download_time_s:.2f}s")
        ...     print(f"Average speed: {result.download_speed_mbs:.2f}MB/s")
        ... else:
        ...     print(f"Download failed: {result.error_message}")
    """
    total_start_time = time.time()
    total_bytes = 0

    # Ensure datetime has timezone information
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        # Convert to UTC for consistency
        dt = dt.astimezone(timezone.utc)

    # Extract date and cycle from datetime
    date_str = dt.strftime("%Y%m%d")
    cycle_str = dt.strftime("%H")

    result = IFSDownloadResult(
        success=False,
        date=date_str,
        cycle=cycle_str,
        forecast_hour=str(forecast_hour),
        elements=elements,
        file_path=output_path,
    )
    # https://ecmwf-forecasts.s3.amazonaws.com/20250404/00z/ifs/0p25/oper/20250404000000-354h-oper-fc.index

    try:
        # Build file path
        grib_key = f"{date_str}/{cycle_str}z/ifs/0p25/oper/{date_str}{cycle_str}0000-{forecast_hour}h-oper-fc.grib2"
        idx_key = grib_key.replace(".grib2", ".index")

        # Create S3 client with anonymous access
        s3_client = boto3.client(
            "s3",
            region_name=region,
            config=Config(signature_version=UNSIGNED, s3={"addressing_style": "path"}),
        )

        # Download and parse idx file
        logger.info(f"Downloading idx file: {idx_key}")
        response = s3_client.get_object(Bucket=bucket, Key=idx_key)
        idx_content = response["Body"].read().decode("utf-8")

        # Parse idx file and find elements
        grib_idx = GribIdx(idx_content)
        selected_elements = grib_idx.find_elements(elements)

        if not selected_elements:
            result.error_message = f"Specified elements not found: {elements}"
            logger.warning(result.error_message)
            return result

        # Download and merge data
        logger.info(f"Starting data download: {grib_key}")
        merged_data = bytearray()

        for elem in selected_elements:
            logger.info(f"Downloading element {elem.param} at {elem.levtype} level {elem.levelist}")
            chunk = download_bytes(
                s3_client, bucket, grib_key, elem.start_byte, elem.end_byte
            )
            merged_data.extend(chunk)
            total_bytes += len(chunk)

        # Save data
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(merged_data)

        total_time = time.time() - total_start_time
        avg_speed_mbps = (
            (total_bytes / 1024 / 1024) / total_time if total_time > 0 else 0
        )

        # Update result with success and metadata
        result.success = True
        result.file_size_mb = total_bytes / 1024 / 1024
        result.download_time_s = total_time
        result.download_speed_mbs = avg_speed_mbps

        logger.success(
            f"Data saved to: {output_path}\n"
            f"Total size: {result.file_size_mb:.2f}MB\n"
            f"Total time: {result.download_time_s:.2f}s\n"
            f"Average speed: {result.download_speed_mbs:.2f}MB/s"
        )
        return result

    except Exception as e:
        error_msg = f"Error downloading data: {str(e)}"
        result.error_message = error_msg
        logger.error(error_msg)
        return result


if __name__ == "__main__":
    # Example usage for IFS data
    elements = [
        {"param": "2t", "levtype": "sfc"},  # 2m 温度
        {"param": "10u", "levtype": "sfc"},  # 10层风速 U 分量
        {"param": "10v", "levtype": "sfc"},  # 10层风速 V 分量
    ]

    # Get previous day's UTC time
    utc_now = datetime.now(timezone.utc) - timedelta(days=1)
    # Set time to 00:00 UTC
    forecast_time = datetime(
        utc_now.year, utc_now.month, utc_now.day, 0, 0, tzinfo=timezone.utc
    )

    # Use fixed forecast hour
    forecast_hour = 3  # IFS 通常使用 0-336 小时的预报

    output_path = f"data/ifs_{forecast_time.strftime('%Y%m%d')}_{forecast_time.strftime('%H')}_{forecast_hour}.grib"
    logger.info(
        f"Starting IFS data download: {forecast_time.strftime('%Y%m%d')}_{forecast_time.strftime('%H')}z"
    )
    result = download_ifs_data(forecast_time, forecast_hour, elements, output_path)

    if result.success:
        logger.success(f"Download successful! File size: {result.file_size_mb:.2f}MB")
    else:
        logger.error(f"Download failed: {result.error_message}")
