from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

from zonaite.obser import DecodedSynopCollector


@pytest.fixture
def collector():
    return DecodedSynopCollector()


def test_init(collector):
    """测试 DecodedSynopCollector 的初始化"""
    assert collector.base_url == "https://open-data.skyviewor.org"
    assert collector.sub_url == "obervations/meteo/decoded-synops"


def test_available_variables(collector):
    """测试 available_variables 属性"""
    result = collector.available_variables
    assert isinstance(result, dict)

    # 检查必要的变量是否存在
    expected_variables = {
        "temperature",
        "dew_point",
        "relative_humidity",
        "wind_direction",
        "wind_speed",
        "wind_gust",
        "station_pressure",
        "sea_level_pressure",
        "visibility",
        "weather_phenomena",
        "precipitation_6h",
        "precipitation_24h",
    }
    assert set(result.keys()) == expected_variables

    # 检查变量信息的结构
    for var_name, var_info in result.items():
        assert "variable_name" in var_info
        assert "unit" in var_info
        assert "description" in var_info


def test_available_stations(collector):
    """测试 available_stations 属性"""
    result = collector.available_stations
    assert isinstance(result, list)
    assert len(result) > 0

    # 检查站点信息的结构
    station = result[0]
    expected_fields = {
        "wmo_id",
        "name",
        "country",
        "latitude",
        "longitude",
        "elevation",
        "established",
        "closed",
    }
    assert set(station.keys()) == expected_fields

    # 检查是否有中国站点
    china_stations = [s for s in result if s["country"] == "China"]
    assert len(china_stations) > 0

    # 检查一些基本属性
    for station in china_stations[:5]:  # 只检查前5个中国站点
        assert isinstance(station["wmo_id"], str)
        assert isinstance(station["name"], str)
        assert isinstance(station["latitude"], (int, float))
        assert isinstance(station["longitude"], (int, float))
        assert isinstance(station["elevation"], (int, float))
        assert station["latitude"] >= -90 and station["latitude"] <= 90
        assert station["longitude"] >= -180 and station["longitude"] <= 180
        assert station["elevation"] >= -500  # 考虑到死海等低于海平面的地方


def test_get_url(collector):
    """测试 _get_url 方法"""
    test_dt = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
    station_id = "54511"

    expected_url = "https://open-data.skyviewor.org/obervations/meteo/decoded-synops/2024/01/54511.csv"
    assert collector._get_url(test_dt, station_id) == expected_url


def test_fetch_success(collector):
    """测试成功获取数据的情况"""
    # 使用过去的数据进行测试，以确保数据存在
    end_dt = datetime(2024, 3, 31, tzinfo=timezone.utc)  # 使用固定的日期
    start_dt = end_dt - timedelta(days=1)
    station_id = "50136"  # 漠河站，使用已知存在的站点

    df = collector.fetch(start_dt, end_dt, station_id)

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0

    # 检查必要的列是否存在
    expected_columns = {
        "datetime",
        "temperature",
        "relative_humidity",
        "wind_direction",
        "wind_speed",
        "station_pressure",
        "sea_level_pressure",
        "visibility",
    }
    assert expected_columns.issubset(set(df.columns))

    # 检查数据类型
    assert pd.api.types.is_datetime64_any_dtype(df["datetime"])
    numeric_columns = [
        "temperature",
        "relative_humidity",
        "wind_speed",
        "station_pressure",
        "sea_level_pressure",
        "visibility",
    ]
    for col in numeric_columns:
        if col in df.columns and not df[col].isna().all():
            assert pd.api.types.is_numeric_dtype(df[col])

    # 检查数值范围（只检查非空值）
    if "temperature" in df.columns and not df["temperature"].isna().all():
        assert df["temperature"].dropna().between(-50, 50).all()  # 温度范围检查
    if "relative_humidity" in df.columns and not df["relative_humidity"].isna().all():
        assert df["relative_humidity"].dropna().between(0, 100).all()  # 湿度范围检查
    if "station_pressure" in df.columns and not df["station_pressure"].isna().all():
        assert df["station_pressure"].dropna().between(800, 1100).all()  # 气压范围检查
    if "wind_speed" in df.columns and not df["wind_speed"].isna().all():
        assert df["wind_speed"].dropna().between(0, 100).all()  # 风速范围检查


def test_fetch_no_data(collector):
    """测试没有可用数据的情况"""
    # 使用未来的日期测试
    future_dt = datetime.now(timezone.utc) + timedelta(days=365)
    station_id = "50136"  # 使用已知存在的站点

    df = collector.fetch(future_dt, future_dt, station_id)
    assert df is None


def test_fetch_error(collector):
    """测试请求错误的情况"""
    # 使用无效的站点ID测试
    test_dt = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
    invalid_station_id = "00000"  # 无效的站点ID

    df = collector.fetch(test_dt, test_dt, invalid_station_id)
    assert df is None
