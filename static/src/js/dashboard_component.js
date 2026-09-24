/** @odoo-module **/

import { Component, useState, onWillStart, useEffect, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";

export class CustomDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        
        // Refs for Chart.js canvases
        this.monthlyTrendCanvas = useRef("monthlyTrendCanvas");
        this.categoryCanvas = useRef("categoryCanvas");
        this.poStatusCanvas = useRef("poStatusCanvas");

        this.state = useState({
            data: {
                total_revenue: 0,
                sale_orders_count: 0,
                inventory_value: 0,
                monthly_trend: { labels: [], data: [] },
                sales_by_category: { labels: [], data: [] },
                po_status: { labels: [], data: [] },
                top_products: [],
            }
        });

        onWillStart(async () => {
            // Load Chart.js from Odoo's standard web libs
            await loadJS("/web/static/lib/Chart/Chart.js");
            // Fetch backend data
            this.state.data = await this.orm.call(
                "custom.dashboard.provider",
                "get_dashboard_data",
                []
            );
        });

        useEffect(() => {
            this.renderCharts();
        });
    }

    formatCurrency(value) {
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value || 0);
    }

    renderCharts() {
        if (!window.Chart) return;

        // 1. Monthly Sales Trend (Line Chart)
        if (this.monthlyTrendCanvas.el) {
            new Chart(this.monthlyTrendCanvas.el, {
                type: 'line',
                data: {
                    labels: this.state.data.monthly_trend.labels,
                    datasets: [{
                        label: 'Revenue',
                        data: this.state.data.monthly_trend.data,
                        borderColor: '#4A90E2',
                        backgroundColor: 'rgba(74, 144, 226, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.3
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }

        // 2. Sales by Category (Doughnut Chart)
        if (this.categoryCanvas.el) {
            new Chart(this.categoryCanvas.el, {
                type: 'doughnut',
                data: {
                    labels: this.state.data.sales_by_category.labels,
                    datasets: [{
                        data: this.state.data.sales_by_category.data,
                        backgroundColor: ['#4A90E2', '#50E3C2', '#F5A623', '#D0021B', '#BD10E0'],
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }

        // 3. PO Status Overview (Bar Chart)
        if (this.poStatusCanvas.el) {
            new Chart(this.poStatusCanvas.el, {
                type: 'bar',
                data: {
                    labels: this.state.data.po_status.labels,
                    datasets: [{
                        label: 'Purchase Orders',
                        data: this.state.data.po_status.data,
                        backgroundColor: ['#4A90E2', '#50E3C2', '#F5A623', '#D0021B', '#BD10E0'],
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: { y: { beginAtZero: true } }
                }
            });
        }
    }
}

CustomDashboard.template = "custom_dashboard.MainTemplate";

registry.category("actions").add("custom_dashboard.main", CustomDashboard);