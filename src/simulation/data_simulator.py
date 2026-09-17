from __future__ import annotations
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd


def load_config(config_path: str | Path = "configs/default.yaml") -> dict[str, Any]:
    """
    读取 YAML 配置。

    参数
    ----
    config_path: 配置文件路径，默认 configs/default.yaml

    返回
    ----
    dict: 配置字典
    """
    # TODO: 使用 yaml.safe_load 读取配置
    with open(config_path, "r", encoding="utf-8") as f:
        import yaml

        config = yaml.safe_load(f)
    return config

def generate_time_index(
    start_date: str,
    days: int,
    hours_per_day: int,
    freq: str = "1s",
    day_start_time: str = "08:00:00",
) -> pd.DatetimeIndex:
    """
    生成时间索引。

    规则：
    - 每天只生成连续 hours_per_day 小时
    - 默认从每天 08:00:00 开始
    - 默认 1Hz，即 freq="1s"

    返回
    ----
    pd.DatetimeIndex
    """
    if days < 0 or hours_per_day < 0:
        raise ValueError("days and hours_per_day must be non-negative")

    if days == 0 or hours_per_day == 0:
        return pd.DatetimeIndex([], dtype="datetime64[ns]")

    first_day = pd.Timestamp(start_date).normalize()
    start_offset = pd.to_timedelta(day_start_time)
    daily_starts = pd.date_range(first_day, periods=days, freq="D") + start_offset

    daily_ranges = [
        pd.date_range(
            start=day_start,
            end=day_start + pd.Timedelta(hours=hours_per_day),
            freq=freq,
            inclusive="left",
        )
        for day_start in daily_starts
    ]
    return daily_ranges[0].append(daily_ranges[1:])


def generate_sensor_series(
    time_index: pd.DatetimeIndex,
    base_value: float,
    noise_std: float,
    drift_per_day: float,
    rng: np.random.Generator,
) -> pd.Series:
    """
    生成单个传感器序列。

    组成：
    - 基础值 base_value
    - 高斯噪声 noise_std
    - 线性漂移 drift_per_day

    返回
    ----
    pd.Series: 与 time_index 对齐的传感器值
    """
    if len(time_index) == 0:
        return pd.Series(index=time_index, dtype=float)

    elapsed_days = (
        (time_index - time_index[0]).total_seconds() / (24 * 60 * 60)
    )
    noise = rng.normal(loc=0.0, scale=noise_std, size=len(time_index))
    values = base_value + noise + drift_per_day * elapsed_days
    return pd.Series(values, index=time_index, dtype=float)


def simulate_device(
    device_config: dict[str, Any],
    global_config: dict[str, Any],
    rng: np.random.Generator,
) -> pd.DataFrame:
    """
    模拟单台设备。

    输出宽表字段建议：
    - timestamp
    - device_id
    - vibration
    - temperature
    - current

    返回
    ----
    pd.DataFrame
    """
    simulation_config = global_config.get("simulation", global_config)
    time_index = generate_time_index(
        start_date=simulation_config["start_date"],
        days=simulation_config["days"],
        hours_per_day=simulation_config["hours_per_day"],
        freq=simulation_config.get("sample_freq", "1s"),
        day_start_time=simulation_config.get("day_start_time", "08:00:00"),
    )

    data: dict[str, Any] = {
        "timestamp": time_index,
        "device_id": device_config["id"],
    }
    for sensor_name, sensor_config in device_config.get("sensors", {}).items():
        data[sensor_name] = generate_sensor_series(
            time_index=time_index,
            base_value=sensor_config["base_value"],
            noise_std=sensor_config["noise_std"],
            drift_per_day=sensor_config.get("drift_per_day", 0.0),
            rng=rng,
        ).to_numpy()

    return pd.DataFrame(data)


def inject_missing_values(
    df: pd.DataFrame,
    missing_rate: float,
    rng: np.random.Generator,
    sensor_columns: list[str] | None = None,
) -> pd.DataFrame:
    """
    注入缺失值。

    默认对传感器列随机置为 NaN，缺失比例由 missing_rate 控制。
    """
    if not 0 <= missing_rate <= 1:
        raise ValueError("missing_rate must be between 0 and 1")

    if sensor_columns is None:
        sensor_columns = [
            column
            for column in df.columns
            if column not in {"timestamp", "device_id"}
        ]
    missing = df.copy()
    total_cells = len(missing) * len(sensor_columns)
    missing_count = int(round(total_cells * missing_rate))

    if missing_count == 0:
        return missing

    selected = rng.choice(total_cells, size=missing_count, replace=False)
    row_positions = selected // len(sensor_columns)
    column_positions = selected % len(sensor_columns)
    for row_position, column_position in zip(row_positions, column_positions):
        missing.iat[row_position, missing.columns.get_loc(sensor_columns[column_position])] = np.nan

    return missing


def inject_duplicates(
    df: pd.DataFrame,
    duplicate_rate: float,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """
    注入重复值。

    随机抽取部分行复制并追加，模拟重复采集。
    """
    if not 0 <= duplicate_rate <= 1:
        raise ValueError("duplicate_rate must be between 0 and 1")

    duplicate_count = int(round(len(df) * duplicate_rate))
    if duplicate_count == 0 or df.empty:
        return df.copy()

    selected = rng.choice(len(df), size=duplicate_count, replace=False)
    duplicates = df.iloc[selected].copy()
    return pd.concat([df.copy(), duplicates], ignore_index=True)


def inject_linear_drift(
    df: pd.DataFrame,
    drift_per_day: float,
    sensor_columns: list[str] | None = None,
) -> pd.DataFrame:
    """
    注入线性漂移。

    按天对传感器值叠加线性漂移，例如每天增加 drift_per_day 比例。
    """
    if sensor_columns is None:
        sensor_columns = [
            column
            for column in df.columns
            if column not in {"timestamp", "device_id"}
        ]

    drifted = df.copy()
    if drifted.empty or not sensor_columns:
        return drifted

    timestamps = pd.to_datetime(drifted["timestamp"])
    elapsed_days = (
        (timestamps - timestamps.iloc[0]).dt.total_seconds() / (24 * 60 * 60)
    )
    drift_factor = 1 + drift_per_day * elapsed_days
    drifted[sensor_columns] = drifted[sensor_columns].mul(drift_factor, axis=0)
    return drifted


def simulate_all_devices(config: dict[str, Any]) -> pd.DataFrame:
    """
    遍历配置中的所有设备，生成并合并数据。

    返回
    ----
    pd.DataFrame: 所有设备的原始模拟数据
    """
    simulation_config = config.get("simulation", {})
    devices = simulation_config.get("devices", [])
    if not devices:
        return pd.DataFrame(columns=["timestamp", "device_id"])

    project_config = config.get("project", {})
    seed = project_config.get("random_seed", config.get("random_seed", 42))
    rng = np.random.default_rng(seed)
    device_frames = [
        simulate_device(device_config, config, rng)
        for device_config in devices
    ]
    return pd.concat(device_frames, ignore_index=True)


def save_raw_csv(
    df: pd.DataFrame,
    output_path: str | Path = "data/raw/raw_sensor_data.csv",
) -> None:
    """
    保存原始模拟 CSV。

    默认输出到 data/raw/raw_sensor_data.csv。
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)


def main() -> None:
    """
    命令行入口。

    流程：
    1. 读取配置
    2. 模拟所有设备
    3. 注入缺失值、重复值、线性漂移
    4. 保存原始 CSV
    """
    config = load_config()
    df = simulate_all_devices(config)

    simulation_config = config.get("simulation", {})
    injection_config = simulation_config.get("injection", {})
    project_config = config.get("project", {})
    seed = project_config.get("random_seed", config.get("random_seed", 42))
    rng = np.random.default_rng(seed)

    df = inject_missing_values(
        df,
        missing_rate=injection_config.get("missing_rate", 0.0),
        rng=rng,
    )
    df = inject_duplicates(
        df,
        duplicate_rate=injection_config.get("duplicate_rate", 0.0),
        rng=rng,
    )

    drift_config = injection_config.get("linear_drift", {})
    if drift_config.get("enabled", False):
        df = inject_linear_drift(
            df,
            drift_per_day=drift_config.get("per_day", 0.0),
        )

    paths_config = config.get("paths", {})
    output_config = simulation_config.get("output", {})
    output_path = Path(paths_config.get("raw_dir", "data/raw")) / output_config.get(
        "filename", "raw_sensor_data.csv"
    )
    save_raw_csv(df, output_path)



if __name__ == "__main__":
    main()