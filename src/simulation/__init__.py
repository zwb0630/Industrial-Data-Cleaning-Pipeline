"""
数据模拟模块。

负责生成工业设备时序数据，并注入缺失值、重复值、线性漂移等。
"""

from .data_simulator import (
    load_config,
    generate_time_index,
    generate_sensor_series,
    simulate_device,
    inject_missing_values,
    inject_duplicates,
    inject_linear_drift,
    simulate_all_devices,
    save_raw_csv,
    main,
)

__all__ = [
    "load_config",
    "generate_time_index",
    "generate_sensor_series",
    "simulate_device",
    "inject_missing_values",
    "inject_duplicates",
    "inject_linear_drift",
    "simulate_all_devices",
    "save_raw_csv",
    "main",
]