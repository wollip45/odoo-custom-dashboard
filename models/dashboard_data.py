from odoo import models, api, fields
from datetime import date
from dateutil.relativedelta import relativedelta

class CustomDashboardProvider(models.AbstractModel):
    _name = 'custom.dashboard.provider'
    _description = 'Data Provider for Custom Dashboard'

    @api.model
    def get_dashboard_data(self):
        today = fields.Date.context_today(self)
        ytd_start = today.replace(month=1, day=1)
        
        # 1. Total Revenue & Sales Orders Count (YTD - Confirmed Sales)
        sales_domain = [
            ('state', 'in', ['sale', 'done']),
            ('date_order', '>=', ytd_start),
            ('date_order', '<=', today)
        ]
        sales = self.env['sale.order'].search_read(sales_domain, ['amount_untaxed'])
        total_revenue = sum(s['amount_untaxed'] for s in sales)
        sale_orders_count = len(sales)

        # 2. Inventory Value (Current Asset Value - All Time)
        stock_layers = self.env['stock.valuation.layer'].search_read([], ['value'])
        inventory_value = sum(layer['value'] for layer in stock_layers)

        # 3. Monthly Sales Trend (YTD)
        monthly_sales_query = self.env['sale.order']._read_group(
            domain=sales_domain,
            groupby=['date_order:month'],
            aggregates=['amount_untaxed:sum']
        )
        monthly_trend = {
            'labels': [group[0].strftime('%b') for group in monthly_sales_query],
            'data': [group[1] for group in monthly_sales_query]
        }

        # 4. Sales by Category (YTD)
        # Using sale.order.line to join with products/categories accurately
        sol_domain = [
            ('order_id.state', 'in', ['sale', 'done']),
            ('order_id.date_order', '>=', ytd_start),
            ('order_id.date_order', '<=', today)
        ]
        category_sales_query = self.env['sale.order.line']._read_group(
            domain=sol_domain,
            groupby=['product_id'],
            aggregates=['price_subtotal:sum']
        )
        
        category_totals = {}
        for product, subtotal in category_sales_query:
            if product:
                cat_name = product.categ_id.name
                category_totals[cat_name] = category_totals.get(cat_name, 0) + subtotal

        sales_by_category = {
            'labels': list(category_totals.keys()),
            'data': list(category_totals.values())
        }

        # 5. PO Status Overview (YTD)
        po_domain = [
            ('date_order', '>=', ytd_start),
            ('date_order', '<=', today)
        ]
        po_status_query = self.env['purchase.order']._read_group(
            domain=po_domain,
            groupby=['state'],
            aggregates=['__count']
        )
        
        state_mapping = {
            'draft': 'Draft',
            'sent': 'Sent',
            'to approve': 'To Approve',
            'purchase': 'Purchase Order',
            'done': 'Locked',
            'cancel': 'Cancelled'
        }
        
        po_status = {
            'labels': [state_mapping.get(group[0], group[0].capitalize()) for group in po_status_query],
            'data': [group[1] for group in po_status_query]
        }

        # 6. Top Selling Products Table (YTD)
        top_products_query = self.env['sale.order.line']._read_group(
            domain=sol_domain,
            groupby=['product_id'],
            aggregates=['product_uom_qty:sum', 'price_subtotal:sum']
        )
        
        top_products = []
        for product, qty_sum, subtotal_sum in top_products_query:
            if product and qty_sum > 0:
                avg_price = subtotal_sum / qty_sum
                top_products.append({
                    'name': product.name,
                    'qty': qty_sum,
                    'avg_price': avg_price,
                    'total': subtotal_sum
                })
        
        # Sort by total revenue descending and take top 6 (as shown in layout)
        top_products.sort(key=lambda x: x['total'], reverse=True)
        top_products = top_products[:6]

        return {
            'total_revenue': total_revenue,
            'sale_orders_count': sale_orders_count,
            'inventory_value': inventory_value,
            'monthly_trend': monthly_trend,
            'sales_by_category': sales_by_category,
            'po_status': po_status,
            'top_products': top_products,
        }