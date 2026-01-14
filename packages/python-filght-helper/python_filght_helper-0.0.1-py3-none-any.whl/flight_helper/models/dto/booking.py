# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  python-flight-helper
# FileName:     booking.py
# Description:  预订航班转换对象
# Author:       ASUS
# CreateDate:   2026/01/08
# Copyright ©2011-2026. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
from typing import Optional
from flight_helper.validator.type_validator import parse_to_date_str
from pydantic import BaseModel, model_validator, PositiveInt, PositiveFloat, NonNegativeFloat, Field, field_validator


class OneWayBookingDTO(BaseModel):
    # 平台信息
    pl_domain: Optional[str] = Field(default=None, description="平台域名，例如：www.ceair.com")
    pl_protocol: Optional[str] = Field(default=None, description="平台协议，例如：https")

    # 航班信息
    dep_city: str = Field(..., description="起飞城市（中文）")
    arr_city: str = Field(..., description="抵达城市（中文）")
    dep_code: Optional[str] = Field(default=None, description="起飞城市（三字码）")
    arr_code: Optional[str] = Field(default=None, description="抵达城市（三字码）")
    dep_date: str = Field(...,
                          description="起飞日期，格式必须为其中之一：YYYY-MM-DD、YYYY-MM-DD HH:MM、YYYY-MM-DD HH:MM:SS")
    flight_no: str = Field(..., description="航班编号，如 CA1831")
    cabin: Optional[str] = Field(default=None, description="舱位代码，如 Y, C, F 或具体名称")

    # 乘机人信息
    adult: PositiveInt = Field(..., description="成人数量（≥1）")
    children: Optional[PositiveInt] = Field(default=None, description="儿童数量（如提供，必须 ≥1；未提供则视为无儿童）")
    infant: Optional[PositiveInt] = Field(default=None, description="婴儿数量（如提供，必须 ≥1；未提供则视为无婴儿）")

    # 产品与价格
    product_type: str = Field(..., description="产品类型，如：经济舱、超级经济舱等")
    product_name: Optional[str] = Field(default=None, description="产品名称，如：C919特惠，老年特惠")
    sale_price: Optional[PositiveFloat] = Field(default=None, description="预期销售价")
    standard_price: PositiveFloat = Field(..., description="预期票面价（应 ≥ sale_price）")
    sale_increase_threshold: Optional[NonNegativeFloat] = Field(
        default=0.00, description="涨价上限（相对于 sale_price 的绝对值或百分比？按业务定）"
    )
    sale_reduction_threshold: Optional[NonNegativeFloat] = Field(
        default=0.00, description="降价上限（相对于 sale_price 的绝对值或百分比？按业务定）"
    )
    standard_increase_threshold: Optional[NonNegativeFloat] = Field(
        default=0.00, description="涨价上限（相对于 standard_price 的绝对值或百分比？按业务定）"
    )
    standard_reduction_threshold: Optional[NonNegativeFloat] = Field(
        default=0.00, description="降价上限（相对于 standard_price 的绝对值或百分比？按业务定）"
    )

    # 服务联系人
    specialist_name: Optional[str] = Field(default=None, description="退改联系人姓名")
    specialist_mobile: Optional[str] = Field(default=None, description="电话")
    specialist_email: Optional[str] = Field(default=None, description="邮箱")

    @field_validator("dep_date")
    @classmethod
    def validator_dep_date(cls, v: str) -> str:
        return parse_to_date_str(v)

    # 模型级校验（推荐用于跨字段逻辑）
    @model_validator(mode='after')
    def validate_prices(self) -> 'OneWayBookingDTO':
        if self.sale_price is not None and self.sale_price > self.standard_price:
            raise ValueError("预期销售价不能高于预期票面价")
        return self
