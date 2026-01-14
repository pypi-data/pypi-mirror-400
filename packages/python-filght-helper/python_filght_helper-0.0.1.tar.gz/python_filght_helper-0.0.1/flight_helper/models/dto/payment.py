# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  python-flight-helper
# FileName:     payment.py
# Description:  支付数据转成对象
# Author:       ASUS
# CreateDate:   2026/01/08
# Copyright ©2011-2026. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
from typing import Literal, Optional, Union, Annotated
from pydantic import BaseModel, Field, TypeAdapter, NonNegativeFloat

SupportedChannels = Literal["微信", "支付宝", "汇付天下", "易宝支付"]


class __BasePayment(BaseModel):
    channel_name: SupportedChannels = Field(
        ..., description=f'支付渠道，只能是其中之一：{SupportedChannels}'
    )
    payment_type: str = Field(..., description="支付方式")
    account: Optional[str] = Field(default=None, description="支付账号")
    password: Optional[str] = Field(default=None, description="账号密码")
    pay_transaction: Optional[str] = Field(default=None, description="支付流水")
    pay_amount: Optional[NonNegativeFloat] = Field(default=None, description="支付金额")


class YBAccountPaymentDTO(__BasePayment):
    """易宝支付-账号支付"""
    channel_name: Literal["易宝支付"] = Field(..., description="支付渠道")
    payment_type: Literal["账户支付"] = Field(..., description="支付方式")
    account: str = Field(..., description="易宝账号")
    password: str = Field(..., description="账号密码")


class WeChatPaymentDTO(__BasePayment):
    channel_name: Literal["微信"] = Field(..., description="支付渠道")
    payment_type: Literal["二维码识别"] = Field(..., description="支付方式")


class AlipayPaymentDTO(__BasePayment):
    channel_name: Literal["支付宝"] = Field(..., description="支付渠道")
    payment_type: Literal["二维码识别"] = Field(..., description="支付方式")


class HFPaidAccountPaymentDTO(__BasePayment):
    """汇付天下-付款账户支付"""
    channel_name: Literal["汇付天下"] = Field(..., description="支付渠道")
    payment_type: Literal["付款账户支付"] = Field(..., description="支付方式")
    account: str = Field(..., description="操作员号")
    password: str = Field(..., description="操作员交易密码")


# 3. 创建联合类型，并指定 discriminator
PaymentDTO = Annotated[
    Union[
        YBAccountPaymentDTO,
        WeChatPaymentDTO,
        AlipayPaymentDTO,
        HFPaidAccountPaymentDTO,
        # TODO ... 其他支付方式
    ],
    Field(discriminator='channel_name')  # 或者用 'payment_type'，看业务
]

if __name__ == '__main__':
    # 创建适配器
    adapter = TypeAdapter(PaymentDTO)

    # 测试 1: 易宝支付
    yb_data = {
        "channel_name": "易宝支付",
        "payment_type": "账户支付",
        "account": "yb123",
        "password": "pass123"
    }
    yb = YBAccountPaymentDTO(**yb_data)
    yb.pay_transaction = "112312"
    print(yb)
    yb_payment = adapter.validate_python(yb_data)
    yb_payment.pay_transaction = "123123123"
    print(yb_payment)
    print(type(yb_payment))  # <class '__main__.YBAccountPayment'>

    # 测试 2: 微信支付
    wx_data = {
        "channel_name": "微信",
        "payment_type": "二维码识别",
        # account/password 可省略（Optional）
    }
    wx_payment = adapter.validate_python(wx_data)
    print(wx_payment)
    print(type(wx_payment))  # <class '__main__.WeChatPayment'>
