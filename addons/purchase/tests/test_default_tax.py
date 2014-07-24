# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Muschang Anthony
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import openerp.tests.common as common
import logging
import datetime

_logger = logging.getLogger(__name__)

DB = common.DB
ADMIN_USER_ID = common.ADMIN_USER_ID


class test_default_tax(common.TransactionCase):

    def test_default_tax_expense(self):
        """
            Test obtaining the purchase taxes from account.accout default tax
        """

        account_model = self.registry('account.account')
        product_category_model = self.registry('product.category')
        product_model = self.registry('product.product')
        purchase_model = self.registry('purchase.order')
        order_line_model = self.registry('purchase.order.line')
        partner_model = self.registry('res.partner')

        id_product_category_a = self.ref("product.product_category_1")

        #add a tax id to the product category
        product_category = product_category_model.browse(self.cr, self.uid, id_product_category_a)
        id_account = product_category.property_account_expense_categ.id

        account_model.write(self.cr, ADMIN_USER_ID, id_account, {
            'tax_ids': [(0, 0, {'name': 'Tax A'})],
        })

        self.assertEquals(product_category.property_account_expense_categ.tax_ids[0].name, "Tax A", "there must be a default tax on the product category")

        id_product = product_model.create(self.cr, ADMIN_USER_ID, {
            'name': 'Product A',
            'categ_id': id_product_category_a,
        })

        id_partner = partner_model.create(self.cr, ADMIN_USER_ID, {
            'name': 'Partner A',
        })

        id_pricelist = self.ref("product.list0")

        id_purchase = purchase_model.create(self.cr, ADMIN_USER_ID, {
            'partner_id': id_partner,
            'location_id': self.ref("stock.stock_location_3"),
            'pricelist_id': id_pricelist,
        })

        purchase_model.write(self.cr, ADMIN_USER_ID, id_purchase, {
            'order_line': [(0, 0, {'name': 'Order line A',
                                   'order_id': id_purchase,
                                   'price_unit': 0.0,
                                   'date_planned': datetime.date(2012, 12, 12)})],
        })

        purchase = purchase_model.browse(self.cr, self.uid, id_purchase)
        values_to_update = order_line_model.product_id_change(self.cr, self.uid, purchase.order_line[0].id, id_pricelist, id_product, qty=1, uom_id=False, partner_id=id_partner)['value']
        self.assertEqual(product_category.property_account_expense_categ.tax_ids[0].id, values_to_update['taxes_id'][0])

        """Set an purchase account in the product, the default tax should be ignored"""

        product_model.write(self.cr, ADMIN_USER_ID, id_product, {
            'supplier_taxes_id': [(0, 0, {'name': 'Tax B'})],
        })

        product = product_model.browse(self.cr, self.uid, id_product)
        self.assertEquals(product_category.property_account_expense_categ.tax_ids[0].name, "Tax A", "the default tax on the product category must not have change")
        self.assertEquals(product.supplier_taxes_id[0].name, "Tax B", "the default tax on the product category must not have change")

        values_to_update = order_line_model.product_id_change(self.cr, self.uid, purchase.order_line[0].id, id_pricelist, id_product, qty=1, uom_id=False, partner_id=id_partner)['value']
        self.assertEqual(product.supplier_taxes_id[0].id, values_to_update['taxes_id'][0])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
