# Industrial Data Cleaning Pipeline

工业时序数据清洗管道：模拟 → 清洗 → 异常标注 → 存储。

项目地址：https://github.com/zwb0630/Industrial-Data-Cleaning-Pipeline

## 项目背景

面向工业设备（振动、温度、电流）时序数据，构建一套可复用的清洗与异常检测流程。  
当前阶段重点：数据模拟、时间序列清洗、异常标注、Parquet / MySQL 存储。

## 技术栈

- Python 3.10+
- NumPy / Pandas / SciPy
- Matplotlib / Seaborn
- PyOD
- Parquet (pyarrow) / MySQL
- pytest / mypy / pytest-cov
- DuckDB（后续预习）

## 安装步骤

```bash
git clone https://github.com/zwb0630/Industrial-Data-Cleaning-Pipeline.git
cd Industrial-Data-Cleaning-Pipeline

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
快速开始
当前已完成 2026.09 数据模拟模块，可生成 3 台设备的振动 / 温度 / 电流时间序列。

bash
python -m src.simulation.data_simulator
默认行为：

生成 3 台设备

采样频率：1Hz

每天 8 小时

注入 5% 缺失值、重复值、线性漂移

输出原始 CSV 到 data/raw/raw_sensor_data.csv

配置文件位于：

text
configs/default.yaml
目录结构
text
Industrial-Data-Cleaning-Pipeline/
│
├── .gitignore                    # 忽略 __pycache__/、.venv/、*.pyc、.env、数据文件等
├── .env.example                  # 环境变量模板（MySQL 连接信息等）
├── LICENSE                       # 2027.03 添加，MIT 或 Apache 2.0
├── README.md                     # 项目说明
├── requirements.txt              # 依赖列表
│
├── src/                          # 源代码根目录
│   ├── __init__.py
│   │
│   ├── simulation/               # 【2026.09】数据模拟模块
│   │   ├── __init__.py
│   │   └── data_simulator.py     # 生成设备时序数据，注入缺失、重复、漂移
│   │
│   ├── cleaning/                 # 【2026.10～12】清洗管道模块
│   │   ├── __init__.py
│   │   ├── cleaner.py            # 基础清洗：时间戳对齐 → 线性插补 → 3σ 去极值
│   │   ├── pipeline.py           # 函数管道封装
│   │   ├── outlier.py            # 3σ / 滚动窗口标准差
│   │   └── interpolate.py        # 线性插补 + 样条插补
│   │
│   ├── anomaly/                  # 【2027.02】异常检测模块
│   │   ├── __init__.py
│   │   └── pyod_audit.py         # PyOD IsolationForest 集成
│   │
│   ├── storage/                  # 【2026.12】存储模块
│   │   ├── __init__.py
│   │   ├── parquet_writer.py     # 输出 Parquet
│   │   └── db_writer.py          # 写入 MySQL 宽表
│   │
│   ├── viz/                      # 【2026.10～12】可视化模块
│   │   ├── __init__.py
│   │   └── plot_utils.py         # 清洗前后对比图、3σ 阈值可视化
│   │
│   └── utils/                    # 通用工具
│       ├── __init__.py
│       ├── logger.py             # logging 配置
│       └── io_utils.py           # CSV / Parquet 读写封装
│
├── data/                         # 数据目录
│   ├── raw/                      # 原始模拟数据 CSV
│   ├── intermediate/             # 中间清洗结果
│   ├── processed/                # 最终干净 Parquet
│   └── .gitkeep
│
├── tests/                        # 【2027.02】pytest 单元测试
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_data_simulator.py
│   ├── test_cleaner.py
│   ├── test_pipeline.py
│   └── test_pyod_audit.py
│
├── notebooks/                    # 探索性分析
│   └── .gitkeep
│
├── docs/                         # 文档
│   ├── architecture.md
│   └── blog_outline.md
│
├── configs/                      # 配置文件
│   └── default.yaml              # 设备列表、采样频率、3σ 阈值、MySQL 表名等
│
└── run.py                        # 【2027.02】一键执行全流程入口
当前进度
☑ 2026.09 项目骨架初始化
☑ 2026.09 GitHub 仓库配置 + README 初始化
☑ 2026.09 数据模拟模块：3 台设备振动 / 温度 / 电流，1Hz，8h/天
☑ 2026.09 注入缺失值 5%、重复值、线性漂移
□ 2026.10 基础清洗：时间戳对齐、线性插补、3σ 去极值
□ 2026.11 管道封装 + 日志 + 样条插补对比
□ 2026.12 Parquet + MySQL + 可视化
□ 2027.02 PyOD 异常检测 + pytest 单元测试
□ 2027.03 开源发布 + 博客大纲 + LICENSE
□ 2027.04 项目交付 + 博客终稿 + mypy 类型检查
□ 2027.05 软考冲刺 + 项目维护
□ 2027.06 测试覆盖率 + 演示视频 + DuckDB 预习
□ 2027.07 最终交付 + 软考成绩查询 + 暑假衔接