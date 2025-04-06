import os
from datetime import datetime, timedelta, timezone

import pytest

from zonaite.forecast import download_ifs_data


@pytest.fixture
def test_elements():
    """测试用的气象要素列表"""
    return [
        {"param": "2t", "levtype": "sfc"},  # 2米温度
        {"param": "10u", "levtype": "sfc"},  # 10米U风
        {"param": "10v", "levtype": "sfc"},  # 10米V风
    ]


@pytest.fixture
def test_output_dir(tmp_path):
    """创建临时输出目录"""
    output_dir = os.path.join(tmp_path, "ifs_data")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def test_download_success(test_elements, test_output_dir):
    """测试成功下载数据的情况"""
    # 使用当前日期减去一天进行测试
    end_dt = datetime.now(timezone.utc) - timedelta(days=1)
    start_dt = end_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    forecast_hour = 0
    output_path = os.path.join(
        test_output_dir,
        f"ifs_{start_dt.strftime('%Y%m%d')}_{start_dt.strftime('%H')}_{forecast_hour:03d}.grib2",
    )

    result = download_ifs_data(
        dt=start_dt,
        forecast_hour=forecast_hour,
        elements=test_elements,
        output_path=output_path,
    )

    # 检查下载结果
    assert result.success
    assert result.date == start_dt.strftime("%Y%m%d")
    assert result.cycle == start_dt.strftime("%H")
    assert result.forecast_hour == str(forecast_hour)
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
        {"param": "INVALID", "levtype": "sfc"},
    ]

    end_dt = datetime.now(timezone.utc) - timedelta(days=1)
    start_dt = end_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    forecast_hour = 0
    output_path = os.path.join(test_output_dir, "ifs_invalid.grib2")

    result = download_ifs_data(
        dt=start_dt,
        forecast_hour=forecast_hour,
        elements=invalid_elements,
        output_path=output_path,
    )

    # 检查下载结果
    assert not result.success
    assert result.error_message is not None
    assert "Specified elements not found" in result.error_message


def test_download_future_data(test_elements, test_output_dir):
    """测试下载未来数据的情况"""
    future_dt = datetime.now(timezone.utc) + timedelta(days=365)
    forecast_hour = 0
    output_path = os.path.join(test_output_dir, "ifs_future.grib2")

    result = download_ifs_data(
        dt=future_dt,
        forecast_hour=forecast_hour,
        elements=test_elements,
        output_path=output_path,
    )

    # 检查下载结果
    assert not result.success
    assert result.error_message is not None


def test_download_invalid_forecast_hour(test_elements, test_output_dir):
    """测试无效的预报时效"""
    end_dt = datetime.now(timezone.utc) - timedelta(days=1)
    start_dt = end_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    invalid_forecast_hour = 999  # 超出有效范围（IFS 通常使用 0-336 小时）
    output_path = os.path.join(test_output_dir, "ifs_invalid_hour.grib2")

    result = download_ifs_data(
        dt=start_dt,
        forecast_hour=invalid_forecast_hour,
        elements=test_elements,
        output_path=output_path,
    )

    # 检查下载结果
    assert not result.success
    assert result.error_message is not None


def test_download_multiple_elements(test_output_dir):
    """测试下载多个气象要素"""
    elements = [
        {"param": "2t", "levtype": "sfc"},  # 2米温度
        {"param": "10u", "levtype": "sfc"},  # 10米U风
        {"param": "10v", "levtype": "sfc"},  # 10米V风
        {"param": "tp", "levtype": "sfc"},  # 总降水量
        {"param": "msl", "levtype": "sfc"},  # 平均海平面气压
    ]

    end_dt = datetime.now(timezone.utc) - timedelta(days=1)
    start_dt = end_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    forecast_hour = 0
    output_path = os.path.join(test_output_dir, "ifs_multiple.grib2")

    result = download_ifs_data(
        dt=start_dt,
        forecast_hour=forecast_hour,
        elements=elements,
        output_path=output_path,
    )

    # 检查下载结果
    assert result.success
    assert result.date == start_dt.strftime("%Y%m%d")
    assert result.cycle == start_dt.strftime("%H")
    assert result.forecast_hour == str(forecast_hour)
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
    output_path = os.path.join(test_output_dir, "ifs_performance.grib2")

    result = download_ifs_data(
        dt=start_dt,
        forecast_hour=forecast_hour,
        elements=test_elements,
        output_path=output_path,
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
    output_path = os.path.join(test_output_dir, "ifs_custom_bucket.grib2")

    result = download_ifs_data(
        dt=start_dt,
        forecast_hour=forecast_hour,
        elements=test_elements,
        output_path=output_path,
        bucket="ecmwf-forecasts",
        region="eu-central-1",
    )

    # 检查下载结果
    assert result.success
    assert result.date == start_dt.strftime("%Y%m%d")
    assert result.cycle == start_dt.strftime("%H")
    assert result.forecast_hour == str(forecast_hour)
    assert result.file_path == output_path
    assert result.file_size_mb is not None and result.file_size_mb > 0

    # 检查文件是否存在
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0 