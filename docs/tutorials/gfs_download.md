# GFS 数据下载教程

本教程将指导您如何使用 Zonaite 下载 GFS（全球预报系统）数据。

## 基础用法

### 1. 导入必要的模块

```python
from datetime import datetime, timezone
from zonaite.forecast import download_gfs_data
```

### 2. 设置下载参数

```python
# 设置要下载的气象要素
elements = [
    {"name": "TMP", "level": "2 m above ground"},  # 2米温度
    {"name": "UGRD", "level": "10 m above ground"},  # 10米U风
    {"name": "VGRD", "level": "10 m above ground"}   # 10米V风
]

# 设置时间参数
date = datetime(2024, 4, 1, tzinfo=timezone.utc)  # UTC时间
cycle = 0  # 预报起报时次
forecast_hour = 3  # 预报时效（小时）

# 设置输出路径
output_path = "gfs_data.grib2"
```

### 3. 执行下载

```python
# 下载数据
result = download_gfs_data(
    date=date,
    cycle=cycle,
    forecast_hour=forecast_hour,
    elements=elements,
    output_path=output_path
)

# 检查下载结果
if result.success:
    print(f"下载成功！文件大小：{result.file_size_mb:.2f}MB")
else:
    print(f"下载失败：{result.error_message}")
```

## 高级用法

### 1. 使用 idx 文件加速下载

```python
# 设置 idx 文件路径
idx_path = "gfs.idx"

# 下载数据（使用 idx 文件）
result = download_gfs_data(
    date=date,
    cycle=cycle,
    forecast_hour=forecast_hour,
    elements=elements,
    output_path=output_path,
    idx_path=idx_path  # 使用 idx 文件
)
```

### 2. 批量下载多个时效

```python
# 设置多个预报时效
forecast_hours = [0, 3, 6, 9, 12]

# 批量下载
for hour in forecast_hours:
    output_path = f"gfs_data_{hour:03d}.grib2"
    result = download_gfs_data(
        date=date,
        cycle=cycle,
        forecast_hour=hour,
        elements=elements,
        output_path=output_path
    )
    if result.success:
        print(f"下载成功 {hour} 小时预报！")
```

### 3. 使用进度条

```python
# 显示下载进度
result = download_gfs_data(
    date=date,
    cycle=cycle,
    forecast_hour=forecast_hour,
    elements=elements,
    output_path=output_path,
    show_progress=True  # 显示进度条
)
```

## 常见问题

### 1. 下载失败

如果下载失败，请检查：
1. 网络连接是否正常
2. 时间参数是否有效（GFS 数据通常保留 10 天）
3. 气象要素名称是否正确
4. 是否有足够的磁盘空间

### 2. 性能优化

为提高下载性能，您可以：
1. 使用 idx 文件进行选择性下载
2. 减少下载的气象要素数量
3. 使用代理服务器（如果需要）

### 3. 内存使用

对于大型数据下载：
1. 使用 `show_progress=True` 监控下载进度
2. 确保系统有足够的内存
3. 考虑分批下载

## 最佳实践

1. 总是检查下载结果
2. 使用有意义的文件名
3. 保存下载日志
4. 定期清理临时文件
5. 使用异常处理

```python
try:
    result = download_gfs_data(...)
    if result.success:
        print("下载成功！")
    else:
        print(f"下载失败：{result.error_message}")
except Exception as e:
    print(f"发生错误：{str(e)}") 