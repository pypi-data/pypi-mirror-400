# 地理编码工具 (geocoding-cli)

> 将 Excel 文件中指定工作表的某一列地址批量转换为经纬度坐标。
> 使用百度地图api

## 功能概述

本工具支持从命令行调用，读取 Excel 文件（`.xlsx` 格式），对指定工作表（sheet）中某一列的地址文本进行地理编码（Geocoding），并自动将经纬度结果写回原文件的新列中。

## 打包

```bash
pip install build
python -m build

...
Successfully built geocoding_cli-1.0.0.tar.gz and geocoding_cli-1.0.0-py3-none-any.whl

# 上传到 PyPI
pip install twine
twine upload dist/*
# 输入pypi token

```

## 安装

```bash
pip install geocoding-cli
```

> 注意：本工具依赖于网络请求调用地理编码 API（如高德、百度、Google 等），需提供有效的 API 密钥。

## 使用方法

### 命令行语法

```bash
geocoding-cli --key <API_KEY> --sheet <SHEET_INDEX> --column <COLUMN_INDEX> <INPUT_FILE.xlsx>
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `--key` 或 `-k` | 地理编码服务的 API 密钥（例如高德地图 API Key） |
| `--sheet` 或 `-s` | 工作表索引（从 1 开始计数，即第一个 sheet 为 1） |
| `--column` 或 `-c` | 地址所在列的列号（从 1 开始计数，即 A 列为 1） |
| `<INPUT_FILE.xlsx>` | 输入的 Excel 文件路径（必须为 `.xlsx` 格式） |

### 示例

```bash
geocoding-cli --key your_amap_api_key --sheet 1 --column 5 addresses.xlsx
```

该命令将：
- 读取 `addresses.xlsx` 文件；
- 选择第一个工作表（Sheet1）；
- 读取第 5 列（E 列）中的地址文本；
- 调用地理编码 API 获取经纬度；
- 在原文件中新增两列（默认为“经度”和“纬度”）写入结果。

> ⚠️ **注意**：工具会输出结果到到**原文件名_已加入经纬度.xlsx**，建议操作前备份 Excel 文件。

## 输出格式

工具会在原 Excel 文件中追加两列：
- **经度（Longitude）**
- **纬度（Latitude）**

若某地址无法解析，对应单元格将留空或标记为 `N/A`。

## 支持的地理编码服务

当前默认使用 **高德地图地理编码 API**。如需支持其他服务（如百度地图、Google Maps），请在 `--service` 参数中指定（未来版本支持）。

## 依赖

- Python 3.10+
- `openpyxl`
- `requests`

## 许可证

MIT License

---

© 2026 zzhoo8
