import pytest
import os
from datetime import datetime, timezone, timedelta

from zonaite.forecast import download_gfs_data


@pytest.fixture
def test_elements():
    """测试用的气象要素列表"""
    return [
        {"name": "TMP", "level": "2 m above ground"},
        {"name": "UGRD", "level": "10 m above ground"},
        {"name": "VGRD", "level": "10 m above ground"},
    ]


@pytest.fixture
def test_output_dir(tmp_path):
    """创建临时输出目录"""
    output_dir = os.path.join(tmp_path, "gfs_data")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def test_download_success(test_elements, test_output_dir):
    """测试成功下载数据的情况"""
    # 使用固定的时间进行测试
    start_dt = datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)
    forecast_hour = 0
    output_path = os.path.join(
        test_output_dir,
        f"gfs_{start_dt.strftime('%Y%m%d')}_{start_dt.strftime('%H')}_{forecast_hour:03d}.grib2",
    )

    result = download_gfs_data(
        init_dt=start_dt,
        forecast_hour=forecast_hour,
        elements=test_elements,
        output_path=output_path,
    )

    # 检查下载结果
    assert result.success
    assert result.date == start_dt.strftime("%Y%m%d")
    assert result.cycle == start_dt.strftime("%H")
    assert result.forecast_hour == forecast_hour
    assert result.file_path == output_path
    assert result.file_size_mb is not None and result.file_size_mb > 0
    assert result.download_time_s is not None and result.download_time_s > 0
    assert result.download_speed_mbs is not None and result.download_speed_mbs > 0

    # 检查文件是否存在
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0


def test_download_invalid_elements(test_output_dir):
    """测试无效的气象要素"""
    invalid_elements = [
        {"name": "INVALID", "level": "2 m above ground"},
    ]

    end_dt = datetime.now(timezone.utc) - timedelta(days=1)
    start_dt = end_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    forecast_hour = 0
    output_path = os.path.join(test_output_dir, "gfs_invalid.grib2")

    result = download_gfs_data(
        init_dt=start_dt,
        forecast_hour=forecast_hour,
        elements=invalid_elements,
        output_path=output_path,
        quiet=True,
    )

    # 检查下载结果
    assert not result.success
    assert result.error_message is not None
    assert "Specified elements not found" in result.error_message


def test_download_future_data(test_elements, test_output_dir):
    """测试下载未来数据的情况"""
    future_dt = datetime.now(timezone.utc) + timedelta(days=365)
    forecast_hour = 0
    output_path = os.path.join(test_output_dir, "gfs_future.grib2")

    result = download_gfs_data(
        init_dt=future_dt,
        forecast_hour=forecast_hour,
        elements=test_elements,
        output_path=output_path,
        quiet=True,
    )

    # 检查下载结果
    assert not result.success
    assert result.error_message is not None


def test_download_invalid_forecast_hour(test_elements, test_output_dir):
    """测试无效的预报时效"""
    end_dt = datetime.now(timezone.utc) - timedelta(days=1)
    start_dt = end_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    invalid_forecast_hour = 999  # 超出有效范围
    output_path = os.path.join(test_output_dir, "gfs_invalid_hour.grib2")

    result = download_gfs_data(
        init_dt=start_dt,
        forecast_hour=invalid_forecast_hour,
        elements=test_elements,
        output_path=output_path,
        quiet=True,
    )

    # 检查下载结果
    assert not result.success
    assert result.error_message is not None


def test_download_multiple_elements(test_output_dir):
    """测试下载多个气象要素"""
    elements = [
        {"name": "TMP", "level": "2 m above ground"},
        {"name": "UGRD", "level": "10 m above ground"},
        {"name": "VGRD", "level": "10 m above ground"},
        {"name": "APCP", "level": "surface"},
        {"name": "RH", "level": "2 m above ground"},
    ]

    end_dt = datetime.now(timezone.utc) - timedelta(days=1)
    start_dt = end_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    forecast_hour = 0
    output_path = os.path.join(test_output_dir, "gfs_multiple.grib2")

    result = download_gfs_data(
        init_dt=start_dt,
        forecast_hour=forecast_hour,
        elements=elements,
        output_path=output_path,
        quiet=True,
    )

    # 检查下载结果
    assert result.success
    assert result.date == start_dt.strftime("%Y%m%d")
    assert result.cycle == start_dt.strftime("%H")
    assert result.forecast_hour == forecast_hour
    assert result.file_path == output_path
    assert result.file_size_mb is not None and result.file_size_mb > 0

    # 检查文件是否存在
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0


def test_download_performance(test_elements, test_output_dir):
    """测试下载性能"""
    end_dt = datetime.now(timezone.utc) - timedelta(days=1)
    start_dt = end_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    forecast_hour = 0
    output_path = os.path.join(test_output_dir, "gfs_performance.grib2")

    result = download_gfs_data(
        init_dt=start_dt,
        forecast_hour=forecast_hour,
        elements=test_elements,
        output_path=output_path,
        quiet=True,
    )

    # 检查性能指标
    assert result.success
    assert result.download_time_s is not None and result.download_time_s > 0
    assert result.download_speed_mbs is not None and result.download_speed_mbs > 0

    # 检查下载速度是否合理（假设最小速度为 0.1 MB/s）
    assert result.download_speed_mbs >= 0.1


def test_download_custom_bucket_and_region(test_elements, test_output_dir):
    """测试使用自定义的 S3 存储桶和区域"""
    end_dt = datetime.now(timezone.utc) - timedelta(days=1)
    start_dt = end_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    forecast_hour = 0
    output_path = os.path.join(test_output_dir, "gfs_custom_bucket.grib2")

    result = download_gfs_data(
        init_dt=start_dt,
        forecast_hour=forecast_hour,
        elements=test_elements,
        output_path=output_path,
        bucket="noaa-gfs-bdp-pds",
        region="us-east-1",
        quiet=True,
    )

    # 检查下载结果
    assert result.success
    assert result.file_path == output_path
    assert result.file_size_mb is not None and result.file_size_mb > 0
