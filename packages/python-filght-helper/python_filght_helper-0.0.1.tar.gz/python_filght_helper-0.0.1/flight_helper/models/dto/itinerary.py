# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  python-flight-helper
# FileName:     itinerary.py
# Description:  订单票号数据转换对象
# Author:       ASUS
# CreateDate:   2026/01/08
# Copyright ©2011-2026. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
from typing import Optional, List
from pydantic import BaseModel, NonNegativeFloat, Field, field_validator


class ItineraryInfoDTO(BaseModel):
    # 平台信息
    passenger_name: str = Field(..., description="乘客名")
    order_itinerary: str = Field(..., description="行程单号")
    id_no: str = Field(..., description="证件号码")
    pre_order_no: str = Field(..., description="采购平台订单号")


class OrderItineraryInfoDTO(BaseModel):
    # 平台信息
    pl_domain: Optional[str] = Field(default=None, description="平台域名，例如：www.ceair.com")
    pl_protocol: Optional[str] = Field(default=None, description="平台协议，例如：https")
    order_no: Optional[str] = Field(default=None, description="业务平台订单号")
    pre_order_no: str = Field(..., description="采购平台订单号")
    order_status: Optional[str] = Field(default=None, description="采购平台订单状态")
    order_amount: Optional[NonNegativeFloat] = Field(default=None, description="采购平台订单金额")
    cash_unit: Optional[str] = Field(default=None, description="采购金额的币种")
    itinerary_info: List[ItineraryInfoDTO] = Field(..., description="乘客行程单信息")

    @field_validator("itinerary_info")
    @classmethod
    def validate_non_empty(cls, info, v: List[ItineraryInfoDTO]):
        if len(v) == 0:
            raise ValueError("至少需要一个乘客行程")
        # 获取外层的 pre_order_no
        outer_pre_order = info.data.get("pre_order_no")
        for item in v:
            if item.pre_order_no != outer_pre_order:
                raise ValueError("行程中的 pre_order_no 必须与订单一致")
        return v  # 必须返回值！
