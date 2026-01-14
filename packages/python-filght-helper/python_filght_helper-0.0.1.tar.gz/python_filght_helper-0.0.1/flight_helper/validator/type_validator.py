# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  python-flight-helper
# FileName:     type_validator.py
# Description:  类型校验模块
# Author:       ASUS
# CreateDate:   2026/01/08
# Copyright ©2011-2026. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
from typing import List
from datetime import datetime

# 支持的输入格式（用于解析）
_INPUT_FORMATS: List[str] = [
    "%Y-%m-%d",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d %H:%M:%S"
]


def parse_to_date_str(value: str, formatter: str = _INPUT_FORMATS[0]) -> str:
    for fmt in _INPUT_FORMATS:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.strftime(formatter)  # 标准化输出
        except ValueError:
            continue

    raise ValueError(
        "起飞日期格式必须为其中之一："
        "YYYY-MM-DD、YYYY-MM-DD HH:MM、YYYY-MM-DD HH:MM:SS"
    )
