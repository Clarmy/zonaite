# Zonaite

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

Zonaite 是一个用于气象数据处理的 Python 工具包，提供了天气预报数据下载和观测数据解码的功能。

## 功能特点

- **GFS 数据下载**：支持从 NOAA 的 GFS（全球预报系统）公共 S3 存储桶中选择性下载特定变量和层次的数据
  - 支持通过 idx 文件进行高效的部分下载
  - 提供性能监控和日志记录
  - 使用数据类进行类型安全的数据结构处理

- **SYNOP 观测数据解码**：支持从 Skyviewor 开放数据平台获取和解码 SYNOP 格式的气象观测数据
  - 提供 WMO 国际交换气象站点信息查询（目前数据仅包括中国大陆地区）
  - 支持查询可用的气象要素信息
  - 支持按时间范围和站点批量获取数据

## 安装

本项目使用 uv 作为包管理工具。安装步骤如下：

```bash
# 克隆仓库
git clone https://github.com/Clarmy/zonaite.git
cd zonaite

# 使用 uv 安装依赖
uv pip install .
```

## 使用示例

### GFS 数据下载

更多 GFS 变量要素的代码和含义请参考：[Inventory of File gfs.t00z.pgrb2.0p25.f003](https://www.nco.ncep.noaa.gov/pmb/products/gfs/gfs.t00z.pgrb2.0p25.f003.shtml)

本项目使用的 GFS 数据源来自 AWS 的 Open-Data 项目的 GFS 存储桶，具体参考：https://registry.opendata.aws/noaa-gfs-bdp-pds/
本项目支持有限的历史 GFS 数据检索查询，具体支持的时间区间请从数据源那里查询。

```python
from datetime import datetime, timezone
from zonaite.forecast import download_gfs_data

# 定义要下载的气象要素
elements = [
    {"name": "TMP", "level": "2 m above ground"},  # 2米温度
    {"name": "UGRD", "level": "10 m above ground"},  # 10米U风
    {"name": "VGRD", "level": "10 m above ground"}   # 10米V风
]

# 设置时间参数（使用 UTC 时间）
dt = datetime(2024, 4, 1, tzinfo=timezone.utc)  # UTC时间
forecast_hour = 3  # 预报时效（小时）

# 设置输出路径
output_path = "gfs_data.grib2"

# 下载数据
result = download_gfs_data(
    init_dt=dt,
    forecast_hour=forecast_hour,
    elements=elements,
    output_path=output_path,
    quiet=False  # 显示下载进度
)

# 检查下载结果
if result.success:
    print(f"下载成功！文件大小：{result.file_size_mb:.2f}MB")
    print(f"下载速度：{result.download_speed_mbs:.2f}MB/s")
    print(f"下载时间：{result.download_time_s:.2f}秒")
else:
    print(f"下载失败：{result.error_message}")
```

### SYNOP 观测数据解码

本项目的 SYNOP 观测数据源来自于 [ogimet.com](https://www.ogimet.com/)，经过了一些整理和处理。

```python
from datetime import datetime, timezone
from zonaite.obser import get_decoded_synop_data

# 设置时间范围和站点
start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
end_date = datetime(2024, 1, 31, tzinfo=timezone.utc)
station_id = "54511"  # 北京站

# 获取观测数据
df = get_decoded_synop_data(start_date, end_date, station_id)

# 查看数据
if df is not None:
    print("数据预览：")
    print(df.head())
    print("\n数据信息：")
    print(df.info())
```

目前仅支持中国大陆的 290+ 个观测站，如果想要查看支持哪些站点和要素，可以使用下面的代码：

```python
from zonaite.obser import DecodedSynopCollector

collector = DecodedSynopCollector()

print("Available variables:")
print(collector.available_variables)

print("Available stations:")
print(collector.available_stations)
```

## Star 历史

[![Star History Chart](https://api.star-history.com/svg?repos=Clarmy/zonaite&type=Date)](https://star-history.com/#Clarmy/zonaite&Date)
