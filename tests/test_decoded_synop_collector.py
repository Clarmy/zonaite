import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
import pandas as pd
from io import StringIO

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
    mock_response = {
        "temperature": {
            "unit": "°C",
            "description": "Air temperature"
        },
        "humidity": {
            "unit": "%",
            "description": "Relative humidity"
        }
    }
    
    with patch('requests.get') as mock_get:
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = mock_response
        
        result = collector.available_variables
        assert result == mock_response
        mock_get.assert_called_once_with(
            "https://open-data.skyviewor.org/obervations/meteo/decoded-synops/infos/available-variables.json",
            timeout=10
        )


def test_available_stations(collector):
    """测试 available_stations 属性"""
    mock_response = {
        "58370": {
            "name": "Test Station",
            "country": "CN",
            "latitude": 31.23,
            "longitude": 121.47,
            "elevation": 4.0
        }
    }
    
    with patch('requests.get') as mock_get:
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = mock_response
        
        result = collector.available_stations
        assert result == mock_response
        mock_get.assert_called_once_with(
            "https://open-data.skyviewor.org/obervations/meteo/decoded-synops/infos/available-stations.json",
            timeout=10
        )


def test_get_url(collector):
    """测试 _get_url 方法"""
    test_dt = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
    station_id = "58370"
    
    expected_url = "https://open-data.skyviewor.org/obervations/meteo/decoded-synops/2024/01/58370.csv"
    assert collector._get_url(test_dt, station_id) == expected_url


def test_fetch_success(collector):
    """测试成功获取数据的情况"""
    test_dt = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
    station_id = "58370"
    
    # 创建模拟的 CSV 数据
    csv_data = "timestamp,temperature,humidity\n2024-01-15 12:00:00,20.5,65"
    
    with patch('requests.get') as mock_get:
        mock_get.return_value.ok = True
        mock_get.return_value.text = csv_data
        
        df = collector.fetch(test_dt, test_dt, station_id)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert 'temperature' in df.columns
        assert 'humidity' in df.columns
        assert df['temperature'].iloc[0] == 20.5
        assert df['humidity'].iloc[0] == 65


def test_fetch_no_data(collector):
    """测试没有可用数据的情况"""
    test_dt = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
    station_id = "58370"
    
    with patch('requests.get') as mock_get:
        mock_get.return_value.ok = False
        mock_get.return_value.status_code = 404
        
        df = collector.fetch(test_dt, test_dt, station_id)
        assert df is None


def test_fetch_error(collector):
    """测试请求错误的情况"""
    test_dt = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
    station_id = "58370"
    
    with patch('requests.get') as mock_get:
        mock_get.return_value.ok = False
        mock_get.return_value.status_code = 500
        
        df = collector.fetch(test_dt, test_dt, station_id)
        assert df is None 