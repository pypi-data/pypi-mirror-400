# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  python-flight-helper
# FileName:     passenger.py
# Description:  乘客
# Author:       ASUS
# CreateDate:   2026/01/08
# Copyright ©2011-2026. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field


class PassengerDTO(BaseModel):
    # 乘客基本信息
    passenger_type: Literal["成人", "儿童", "婴儿"] = Field(
        ..., description="乘客类型，必须是：成人、儿童 或 婴儿"
    )
    passenger_name: str = Field(
        ..., description="乘客法定姓名（按证件填写），如：Zhang San 或 张三"
    )
    passenger_alias: Optional[str] = Field(
        default=None,
        description="乘客中文常用名（仅外国人使用），如：汤姆（对应 Tom）"
    )

    # 性别与证件
    gender: Literal["男", "女"] = Field(..., description='性别，只能是"男"或"女"')
    id_type: Literal["身份证", "港澳通行证", "护照", "军官证", "回乡证"] = Field(
        ..., description='证件类型'
    )
    id_number: str = Field(..., description="证件号码（按证件如实填写）")
