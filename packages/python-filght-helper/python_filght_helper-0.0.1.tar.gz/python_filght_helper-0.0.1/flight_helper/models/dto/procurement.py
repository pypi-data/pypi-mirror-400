# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  python-flight-helper
# FileName:     procurement.py
# Description:  采购信息数据转换对象
# Author:       ASUS
# CreateDate:   2026/01/08
# Copyright ©2011-2026. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
from typing import Optional
from pydantic import BaseModel, PositiveInt, NegativeFloat, Field


class ProcurementDTO(BaseModel):
    # 平台信息
    pl_domain: Optional[str] = Field(default=None, description="平台域名，例如：www.ceair.com")
    pl_protocol: Optional[str] = Field(default=None, description="平台协议，例如：https")
    order_no: PositiveInt = Field(..., description="订单号")
    out_ticket_platform_type: str = Field(..., description="出票平台类型")
    out_ticket_platform: str = Field(..., description="出票平台")
    out_ticket_account: str = Field(..., description="出票账号")
    purchase_account_type: str = Field(..., description="采购账号类型")
    purchase_account: str = Field(..., description="采购账号")
    purchase_amount: NegativeFloat = Field(..., description="采购金额")
    remark: str = Field(..., description="备注，一般是由采购平台账号 + 账号密码拼接而成")
    out_ticket_mobile: str = Field(..., description="出票手机，退改业务需要根据此手机号码来进行操作")
    pay_transaction: str = Field(..., description="支付流水")
    pre_order_no: str = Field(..., description="采购平台订单号")
