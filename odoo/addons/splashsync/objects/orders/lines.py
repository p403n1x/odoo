# -*- coding: utf-8 -*-
#
#  This file is part of SplashSync Project.
#
#  Copyright (C) 2015-2019 Splash Sync  <www.splashsync.com>
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  For the full copyright and license information, please view the LICENSE
#  file that was distributed with this source code.
#

from collections import OrderedDict

from odoo.addons.splashsync.helpers import CurrencyHelper, TaxHelper, SettingsManager, M2MHelper
from splashpy import const, Framework
from splashpy.componants import FieldFactory
from splashpy.helpers import ListHelper, PricesHelper, ObjectsHelper


class Orderline:
    """
    Access to Order line Fields
    """

    def buildLinesFields(self):
        # ==================================================================== #
        # Order line child fields
        # ==================================================================== #
        FieldFactory.create(ObjectsHelper.encode("Product", const.__SPL_T_ID__), "product_id", "Product ID")
        FieldFactory.inlist("Orderlines")
        FieldFactory.microData("http://schema.org/OrderItem", "orderedItem")
        # ==================================================================== #
        FieldFactory.create(ObjectsHelper.encode("Order", const.__SPL_T_ID__), "order_id", "Order ID")
        FieldFactory.inlist("Orderlines")
        FieldFactory.microData("http://schema.org/OrderItem", "orderID")
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_VARCHAR__, "state", "Line Status")
        FieldFactory.inlist("Orderlines")
        FieldFactory.microData("http://schema.org/OrderItem", "LineStatus")
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_VARCHAR__, "ref", "Product Ref.")
        FieldFactory.inlist("Orderlines")
        FieldFactory.microData("http://schema.org/Product", "ref")
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_VARCHAR__, "desc", "Product Desc.")
        FieldFactory.inlist("Orderlines")
        FieldFactory.microData("http://schema.org/Product", "description")
        FieldFactory.isRequired()
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_DOUBLE__, "ord_qty", "Ordered Qty")
        FieldFactory.inlist("Orderlines")
        FieldFactory.microData("http://schema.org/OrderItem", "orderQuantity")
        FieldFactory.isRequired()
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_DOUBLE__, "delv_qty", "Delivered Qty")
        FieldFactory.inlist("Orderlines")
        FieldFactory.microData("http://schema.org/OrderItem", "orderDelivery")
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_DOUBLE__, "inv_qty", "Invoiced Qty")
        FieldFactory.inlist("Orderlines")
        FieldFactory.microData("http://schema.org/OrderItem", "orderQuantity")
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_PRICE__, "ut_price", "Unit Price")
        FieldFactory.inlist("Orderlines")
        FieldFactory.microData("http://schema.org/UnitPriceSpecification", "price")
        FieldFactory.isRequired()
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_DOUBLE__, "lead_time", "Customer LeadTime")
        FieldFactory.inlist("Orderlines")
        FieldFactory.microData("http://schema.org/Offer", "deliveryLeadTime")
        FieldFactory.isRequired()
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_VARCHAR__, "tax_name", "Taxes")
        FieldFactory.inlist("Orderlines")
        FieldFactory.microData("http://schema.org/Product", "priceTaxNames")

    def getLinesFields(self, index, field_id):
        """
        Get Order Lines List
        :param index: str
        :param field_id: str
        :return: None
        """
        # ==================================================================== #
        # Init Lines List...
        lines_list = ListHelper.initOutput(self._out, "Orderlines", field_id)
        # ==================================================================== #
        # Safety Check
        if lines_list is None:
            return
        # ==================================================================== #
        # List Order Lines Ids
        for line in self.object.order_line:
            # ==================================================================== #
            # Read Lines Data
            lines_values = self._get_lines_values(lines_list)
            for pos in range(len(lines_values)):
                ListHelper.insert(self._out, "Orderlines", field_id, "line-" + str(pos), lines_values[pos])
        # ==================================================================== #
        # Force Lines Ordering
        self._out["Orderlines"] = OrderedDict(sorted(self._out["Orderlines"].items()))

        self._in.__delitem__(index)

    def _get_lines_values(self, value_id):
        """
        Get List of Lines Values for given Field
        :param value_id: str
        :return: dict
        """
        values = []
        # ====================================================================#
        # Walk on Product Attributes Values
        for orderline_field in self.object.order_line:
            # Collect Values
            if value_id == "product_id":
                values += [ObjectsHelper.encode("Product", str(orderline_field.product_id[0].id))]
            if value_id == "order_id":
                values += [ObjectsHelper.encode("Order", str(orderline_field.order_id[0].id))]
            if value_id == "ref":
                values += [orderline_field.product_id[0].default_code]
            if value_id == "state":
                values += [orderline_field.state]
            if value_id == "desc":
                values += [orderline_field.name]
            if value_id == "ord_qty":
                values += [orderline_field.product_uom_qty]
            if value_id == "delv_qty":
                values += [orderline_field.qty_delivered]
            if value_id == "inv_qty":
                values += [orderline_field.qty_invoiced]
            if value_id == "ut_price":
                values += [PricesHelper.encode(
                    float(orderline_field.price_unit),
                    TaxHelper.get_tax_rate(orderline_field.tax_id,
                                           'sale') if not SettingsManager.is_prd_adv_taxes() else float(0),
                    None,
                    CurrencyHelper.get_main_currency_code()
                )]
            if value_id == "tax_name":
                values += [M2MHelper.get_names(orderline_field, "tax_id")]
            if value_id == "lead_time":
                values += [orderline_field.customer_lead]

        return values

    #######################################

    def setLinesFields(self, field_id, field_data):
        """
        Set Orderlines List
        :param field_id: str
        :param field_data: hash
        :return: None
        """
        # ==================================================================== #
        # Safety Check - field_id is an Orderlines List
        if field_id != "Orderlines":
            return
        # ==================================================================== #
        # Safety Check
        if not isinstance(field_data, dict):
            return
        # # ==================================================================== #
        # Force Orderlines Ordering
        # field_data = OrderedDict(sorted(field_data.items()))
        # ==================================================================== #
        # Init List
        new_orderlines = []
        # ==================================================================== #
        # Walk on Lines Field...
        for pos, line in field_data.items():
            for line_to_set in self.object.order_line.sorted(key=lambda r: r.sequence):
                # for line_to_set in self.object.order_line.filtered(lambda r: r.sequence == ...):
                Framework.log().dump(line.items(), "line.items(")
                # if int(line_to_set.sequence) == ...):
                self._set_lines_values(line, line_to_set)
                # else:
                #     new_orderlines.append(self._set_lines_values(line, line_to_set))
                #     setattr(self.object, "order_line", new_orderlines)
        self._in.__delitem__(field_id)

    def _set_lines_values(self, line, line_to_set):
        for key, value in line.items():
            if key == "product_id":
                setattr(line_to_set, "product_id", int(ObjectsHelper.id(value)))
            if key == "order_id":
                setattr(line_to_set, "order_id", int(ObjectsHelper.id(value)))
            if key == "ref":
                setattr(line_to_set, "product_id[0].default_code", value)
            if key == "desc":
                setattr(line_to_set, "name", value)
            if key == "state":
                setattr(line_to_set, "state", value)
            if key == "ord_qty":
                setattr(line_to_set, "product_uom_qty", float(value))
            if key == "delv_qty":
                setattr(line_to_set, "qty_delivered", float(value))
            if key == "inv_qty":
                setattr(line_to_set, "qty_invoiced", float(value))
            if key == "ut_price":
                Framework.log().dump(PricesHelper.taxExcluded(value), "PricesHelper.taxExcluded(value)")
                setattr(line_to_set, "price_unit", PricesHelper.taxExcluded(value))
            if key == "tax_name" and value is not None:
                # TODO: A revoir
                setattr(line_to_set, "tax_id", TaxHelper.find_by_rate(PricesHelper.extract(value, "vat"), 'sale'))
                # tax_rate = PricesHelper.taxPercent(field_data)
                # if tax_rate is not None and tax_rate > 0:
                #     tax = TaxHelper.find_by_rate(tax_rate, 'sale')
                #     if tax is None:
                #         return Framework.log().error("Unable to Identify Tax ID for Rate "+str(tax_rate))
                #     else:
                #         self.object.taxes_id = [(6, 0, [tax.id])]
                # else:
                #     self.object.taxes_id = [(6, 0, [])]
            if key == "lead_time":
                setattr(line_to_set, "customer_lead", float(value))

    @staticmethod
    def line_exist(field_data):
        field_data.items()
