# Zonaite 文档

欢迎使用 Zonaite 文档！Zonaite 是一个用于气象数据处理的 Python 工具包，提供了天气预报数据下载和观测数据解码的功能。

## 快速开始

- [安装指南](installation.md)
- [使用教程](tutorials/index.md)
- [API 参考](api/index.md)

## 主要功能

### GFS 数据下载
- 支持从 NOAA 的 GFS（全球预报系统）公共 S3 存储桶中选择性下载特定变量和层次的数据
- 支持通过 idx 文件进行高效的部分下载
- 提供性能监控和日志记录
- 使用数据类进行类型安全的数据结构处理

### SYNOP 观测数据解码
- 支持从 Skyviewor 开放数据平台获取和解码 SYNOP 格式的气象观测数据
- 提供 WMO 国际交换气象站点信息查询（目前数据仅包括中国大陆地区）
- 支持查询可用的气象要素信息
- 支持按时间范围和站点批量获取数据

## 示例代码

### GFS 数据下载示例

```python
from zonaite.forecast import download_gfs_data

# 定义要下载的气象要素
elements = [
    {"name": "TMP", "level": "2 m above ground"},
    {"name": "UGRD", "level": "10 m above ground"}
]

# 下载数据
result = download_gfs_data(
    date=datetime(2025, 3, 26, tzinfo=timezone.utc),
    cycle=0,
    forecast_hour=0,
    elements=elements,
    output_path="gfs_data.grib2"
)

# 检查下载结果
if result.success:
    print(f"Downloaded {result.file_size_mb:.2f}MB")
```

### SYNOP 观测数据解码示例

```python
from datetime import datetime, timezone
from zonaite.obser import get_decoded_synop_data

# 设置时间范围和站点
start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
end_date = datetime(2024, 3, 31, tzinfo=timezone.utc)
station_id = "54511"

# 获取观测数据
df = get_decoded_synop_data(start_date, end_date, station_id)

# 查看数据
if df is not None:
    print("Data preview:")
    print(df)
```

## 获取帮助

如果您在使用过程中遇到任何问题，或有任何建议，欢迎：
1. 提交 [Issue](https://github.com/Clarmy/zonaite/issues)
2. 发送邮件至 [您的邮箱] 