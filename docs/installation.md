# 安装指南

## 系统要求

- Python >= 3.11
- 操作系统：Windows、macOS 或 Linux

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/Clarmy/zonaite.git
cd zonaite
```

### 2. 安装依赖

本项目使用 uv 作为包管理工具。安装步骤如下：

```bash
# 使用 uv 安装依赖
uv pip install .
```

### 3. 验证安装

安装完成后，您可以在 Python 中验证安装：

```python
import zonaite
print(zonaite.__version__)  # 显示版本号
```

## 开发环境设置

如果您想参与开发，需要安装开发依赖：

```bash
# 安装开发依赖
uv pip install -e ".[dev]"
```

开发依赖包括：
- black >= 25.1.0（代码格式化）
- flake8 >= 7.1.2（代码检查）
- ipython >= 9.0.2（交互式开发）
- isort >= 6.0.1（导入排序）

## 常见问题

### 1. 依赖安装失败

如果遇到依赖安装问题，请检查：
1. Python 版本是否 >= 3.11
2. 是否在正确的虚拟环境中
3. 尝试升级 uv：`pip install -U uv`

### 2. 权限问题

如果在 Linux 或 macOS 上遇到权限问题，可以尝试：
```bash
sudo pip install -U uv
```

## 更新

要更新到最新版本：
```bash
git pull
uv pip install -U .
``` 