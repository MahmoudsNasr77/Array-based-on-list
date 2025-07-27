# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class SaleOrderReport(models.AbstractModel):
    """
    Abstract model for Sales Report customizations
    """
    _name = 'report.mg_account.report_sales_template'
    _description = 'Sales Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        """
        Override to add custom data processing for the sales report
        """
        docs = self.env['sale.order'].browse(docids)
        
        # Add any custom processing here
        processed_docs = []
        
        for doc in docs:
            # Calculate totals and additional data
            doc_data = {
                'doc': doc,
                'total_cost': 0.0,
                'total_sale': 0.0,
                'total_profit': 0.0,
                'lines_with_profit': [],
            }
            
            for line in doc.order_line:
                if line.product_id:
                    # Get cost price from purchase order or product standard price
                    cost_price = self._get_cost_price(doc, line)
                    sale_price = line.price_unit
                    line_profit = (sale_price - cost_price) * line.product_uom_qty
                    
                    line_data = {
                        'line': line,
                        'cost_price': cost_price,
                        'sale_price': sale_price,
                        'profit': line_profit,
                        'profit_margin': (line_profit / (sale_price * line.product_uom_qty) * 100) if sale_price > 0 else 0,
                    }
                    
                    doc_data['lines_with_profit'].append(line_data)
                    doc_data['total_cost'] += cost_price * line.product_uom_qty
                    doc_data['total_sale'] += sale_price * line.product_uom_qty
                    doc_data['total_profit'] += line_profit
            
            processed_docs.append(doc_data)
        
        return {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'docs': docs,
            'processed_docs': processed_docs,
            'data': data,
            'company': self.env.company,
            'user': self.env.user,
            'context_today': fields.Date.context_today(self),
        }
    
    def _get_cost_price(self, sale_order, order_line):
        """
        Get the cost price for a product from purchase order or standard cost
        """
        cost_price = 0.0
        
        # Try to get from related purchase order lines
        if hasattr(sale_order, 'po_line_ids'):
            for po_line in sale_order.po_line_ids:
                if po_line.product_id.id == order_line.product_id.id:
                    cost_price = po_line.price_unit
                    break
        
        # Fallback to product standard price
        if not cost_price:
            cost_price = order_line.product_id.standard_price
        
        return cost_price


class SaleOrder(models.Model):
    """
    Extend Sale Order with report-related functionality
    """
    _inherit = 'sale.order'
    
    def action_print_sales_report(self):
        """
        Action to print the sales report
        """
        return self.env.ref('mg_account.action_sales_report').report_action(self)
    
    @api.model
    def get_sales_report_data(self, date_from=None, date_to=None, partner_ids=None, product_ids=None):
        """
        Get filtered data for sales report with additional filters
        """
        domain = [('state', 'in', ['sale', 'done'])]
        
        if date_from:
            domain.append(('date_order', '>=', date_from))
        if date_to:
            domain.append(('date_order', '<=', date_to))
        if partner_ids:
            domain.append(('partner_id', 'in', partner_ids))
        if product_ids:
            domain.append(('order_line.product_id', 'in', product_ids))
        
        orders = self.search(domain, order='date_order desc')
        
        # Calculate summary statistics
        summary = {
            'total_orders': len(orders),
            'total_revenue': sum(order.amount_total for order in orders),
            'total_cost': 0.0,
            'total_profit': 0.0,
        }
        
        for order in orders:
            for line in order.order_line:
                if line.product_id:
                    cost_price = self.env['report.mg_account.report_sales_template']._get_cost_price(order, line)
                    summary['total_cost'] += cost_price * line.product_uom_qty
                    summary['total_profit'] += (line.price_unit - cost_price) * line.product_uom_qty
        
        return {
            'orders': orders,
            'summary': summary,
        }


class ReportSalesWizard(models.TransientModel):
    """
    Wizard for generating sales reports with filters
    """
    _name = 'report.sales.wizard'
    _description = 'Sales Report Wizard'
    
    date_from = fields.Date(
        string='From Date',
        required=True,
        default=fields.Date.context_today
    )
    date_to = fields.Date(
        string='To Date',
        required=True,
        default=fields.Date.context_today
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Customers',
        domain=[('customer_rank', '>', 0)]
    )
    product_ids = fields.Many2many(
        'product.product',
        string='Products'
    )
    report_type = fields.Selection([
        ('detailed', 'Detailed Report'),
        ('summary', 'Summary Report'),
    ], string='Report Type', default='detailed', required=True)
    
    def action_generate_report(self):
        """
        Generate the sales report based on filters
        """
        data = self.get_sales_report_data(
            date_from=self.date_from,
            date_to=self.date_to,
            partner_ids=self.partner_ids.ids if self.partner_ids else None,
            product_ids=self.product_ids.ids if self.product_ids else None
        )
        
        if not data['orders']:
            raise ValidationError(_('No sales orders found for the selected criteria.'))
        
        # Choose template based on report type
        if self.report_type == 'detailed':
            template = 'mg_account.report_sales_template'
        else:
            template = 'mg_account.report_sales_template_multi'
        
        return {
            'type': 'ir.actions.report',
            'report_name': template,
            'report_type': 'qweb-html',
            'data': {
                'date_from': self.date_from,
                'date_to': self.date_to,
                'summary': data['summary'],
            },
            'context': self.env.context,
            'docids': data['orders'].ids,
        }