# Industrial Data Cleaning Pipeline

工业时序数据清洗管道：模拟 → 清洗 → 异常标注 → 存储。

## 项目背景

面向工业设备（振动、温度、电流）时序数据，构建一套可复用的清洗与异常检测流程。

## 技术栈

- Python 3.10+
- NumPy / Pandas / SciPy
- Matplotlib / Seaborn
- PyOD
- Parquet (pyarrow) / MySQL
- pytest

## 目录结构

src/
├── simulation/ # 数据模拟
├── cleaning/ # 清洗管道
├── anomaly/ # 异常检测
├── storage/ # Parquet / MySQL
├── viz/ # 可视化
└── utils/ # 通用工具


## 当前进度

- [x] 2026.09 项目骨架初始化
- [ ] 2026.09 数据模拟模块
- [ ] 2026.10 基础清洗
- [ ] 2026.11 管道封装
- [ ] 2026.12 Parquet + MySQL
- [ ] 2027.02 PyOD 异常检测