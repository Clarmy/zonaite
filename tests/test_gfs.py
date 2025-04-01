import os
import pytest
from datetime import datetime, timezone
from zonaite.forecast.gfs import download_gfs_data

def test_gfs_download():
    """测试 GFS 数据下载功能"""
    # 设置测试参数
    test_elements = [
        {"name": "TMP", "level": "2 m above ground"},
        {"name": "UGRD", "level": "10 m above ground"},
        {"name": "VGRD", "level": "10 m above ground"},
    ]
    
    # 使用昨天的 UTC 时间
    utc_now = datetime.now(timezone.utc)
    test_time = datetime(
        utc_now.year,
        utc_now.month,
        utc_now.day,
        0,  # 使用 00 时次
        0,
        tzinfo=timezone.utc
    )
    
    # 设置输出路径
    output_dir = "test_data"
    output_path = os.path.join(
        output_dir,
        f"gfs_{test_time.strftime('%Y%m%d')}_{test_time.strftime('%H')}_003.grib2"
    )
    
    # 执行下载
    result = download_gfs_data(
        dt=test_time,
        forecast_hour=3,
        elements=test_elements,
        output_path=output_path,
        quiet=True
    )
    
    # 验证结果
    assert result.success, f"下载失败: {result.error_message}"
    assert os.path.exists(output_path), "输出文件不存在"
    assert result.file_size_mb > 0, "下载的文件大小为 0"
    
    # 清理测试文件
    if os.path.exists(output_path):
        os.remove(output_path)
    if os.path.exists(output_dir):
        os.rmdir(output_dir) 