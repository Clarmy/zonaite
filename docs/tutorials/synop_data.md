# SYNOP 观测数据教程

本教程将指导您如何使用 Zonaite 获取和解码 SYNOP 格式的气象观测数据。

## 基础用法

### 1. 导入必要的模块

```python
from datetime import datetime, timezone
from zonaite.obser import get_decoded_synop_data
```

### 2. 设置查询参数

```python
# 设置时间范围
start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
end_date = datetime(2024, 1, 31, tzinfo=timezone.utc)

# 设置站点 ID（例如：54511 代表北京站）
station_id = "54511"
```

### 3. 获取数据

```python
# 获取观测数据
df = get_decoded_synop_data(start_date, end_date, station_id)

# 检查数据
if df is not None:
    print("数据预览：")
    print(df.head())
    print("\n数据信息：")
    print(df.info())
```

## 高级用法

### 1. 获取站点信息

```python
from zonaite.obser import get_station_info

# 获取站点信息
station_info = get_station_info(station_id)
print(f"站点名称：{station_info.name}")
print(f"站点位置：{station_info.latitude}°N, {station_info.longitude}°E")
print(f"站点海拔：{station_info.elevation}米")
```

### 2. 查询可用气象要素

```python
from zonaite.obser import get_available_elements

# 获取可用的气象要素列表
elements = get_available_elements()
print("可用的气象要素：")
for element in elements:
    print(f"- {element.name}: {element.description}")
```

### 3. 批量获取多个站点数据

```python
# 设置多个站点
station_ids = ["54511", "54527", "54534"]  # 北京、天津、石家庄

# 批量获取数据
for station_id in station_ids:
    df = get_decoded_synop_data(start_date, end_date, station_id)
    if df is not None:
        print(f"\n{station_id} 站点数据：")
        print(df.head())
```

## 数据处理

### 1. 数据筛选

```python
# 按时间筛选
df_filtered = df[df.index >= datetime(2024, 1, 15, tzinfo=timezone.utc)]

# 按气象要素筛选
df_temp = df[['temperature', 'humidity']]

# 按条件筛选
df_cold = df[df['temperature'] < 0]
```

### 2. 数据统计

```python
# 基本统计信息
print(df.describe())

# 计算平均值
print("\n温度平均值：", df['temperature'].mean())

# 计算最大值
print("温度最大值：", df['temperature'].max())
```

### 3. 数据可视化

```python
import matplotlib.pyplot as plt

# 绘制温度时间序列
plt.figure(figsize=(12, 6))
df['temperature'].plot()
plt.title('温度变化趋势')
plt.xlabel('时间')
plt.ylabel('温度 (°C)')
plt.grid(True)
plt.show()
```

## 常见问题

### 1. 数据获取失败

如果数据获取失败，请检查：
1. 站点 ID 是否正确
2. 时间范围是否有效
3. 网络连接是否正常
4. 是否有足够的权限

### 2. 数据质量问题

处理数据质量问题：
1. 检查缺失值
2. 处理异常值
3. 数据插值
4. 数据平滑

### 3. 性能优化

提高性能的建议：
1. 减少时间范围
2. 减少站点数量
3. 使用数据缓存
4. 并行处理

## 最佳实践

1. 数据验证
```python
# 检查数据完整性
if df.isnull().any().any():
    print("数据存在缺失值")
    print(df.isnull().sum())

# 检查数据范围
print("\n数据范围：")
print(df.describe())
```

2. 错误处理
```python
try:
    df = get_decoded_synop_data(start_date, end_date, station_id)
    if df is not None:
        print("数据获取成功！")
    else:
        print("未获取到数据")
except Exception as e:
    print(f"发生错误：{str(e)}")
```

3. 数据保存
```python
# 保存为 CSV 文件
df.to_csv(f"synop_data_{station_id}.csv")

# 保存为 Excel 文件
df.to_excel(f"synop_data_{station_id}.xlsx")
``` 