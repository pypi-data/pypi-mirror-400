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
WuttaPOS - data model
"""

from wuttjamaican.db.model import *

from .stores import Store
from .terminals import Terminal
from .tenders import Tender
from .taxes import Tax
from .employees import Employee
from .customers import Customer
from .departments import Department
from .products import (
    Product,
    ProductInventory,
    InventoryAdjustmentType,
    InventoryAdjustment,
)

from .batch.pos import POSBatch, POSBatchRow
