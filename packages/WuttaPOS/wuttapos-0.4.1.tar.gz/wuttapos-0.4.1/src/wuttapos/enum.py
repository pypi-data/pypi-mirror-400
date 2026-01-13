# -*- coding: utf-8; -*-
################################################################################
#
#  WuttaPOS -- Point of Sale system based on Wutta Framework
#  Copyright © 2026 Lance Edgar
#
#  This file is part of WuttaPOS.
#
#  WuttaPOS is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  WuttaPOS is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  WuttaPOS.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
WuttaPOS enum values
"""

from collections import OrderedDict

from wuttjamaican.enum import *


########################################
# POS Batch Row Type
########################################

POS_ROW_TYPE_SET_CUSTOMER = "set_customer"
POS_ROW_TYPE_SWAP_CUSTOMER = "swap_customer"
POS_ROW_TYPE_DEL_CUSTOMER = "del_customer"
POS_ROW_TYPE_SELL = "sell"
POS_ROW_TYPE_OPEN_RING = "openring"
POS_ROW_TYPE_BADSCAN = "badscan"
POS_ROW_TYPE_BADPRICE = "badprice"
POS_ROW_TYPE_ADJUST_PRICE = "adjust_price"
POS_ROW_TYPE_VOID_LINE = "void_line"
POS_ROW_TYPE_VOID_TXN = "void_txn"
POS_ROW_TYPE_SUSPEND = "suspend"
POS_ROW_TYPE_RESUME = "resume"
POS_ROW_TYPE_TENDER = "tender"
POS_ROW_TYPE_CHANGE_BACK = "change_back"

POS_ROW_TYPE = OrderedDict(
    [
        (POS_ROW_TYPE_SET_CUSTOMER, "set customer"),
        (POS_ROW_TYPE_SWAP_CUSTOMER, "swap customer"),
        (POS_ROW_TYPE_DEL_CUSTOMER, "del customer"),
        (POS_ROW_TYPE_SELL, "sell"),
        (POS_ROW_TYPE_OPEN_RING, "open ring"),
        (POS_ROW_TYPE_BADSCAN, "bad scan"),
        (POS_ROW_TYPE_BADPRICE, "bad price"),
        (POS_ROW_TYPE_ADJUST_PRICE, "adjust price"),
        (POS_ROW_TYPE_VOID_LINE, "void line"),
        (POS_ROW_TYPE_VOID_TXN, "void txn"),
        (POS_ROW_TYPE_SUSPEND, "suspend"),
        (POS_ROW_TYPE_RESUME, "resume"),
        (POS_ROW_TYPE_TENDER, "tender"),
        (POS_ROW_TYPE_CHANGE_BACK, "change back"),
    ]
)
