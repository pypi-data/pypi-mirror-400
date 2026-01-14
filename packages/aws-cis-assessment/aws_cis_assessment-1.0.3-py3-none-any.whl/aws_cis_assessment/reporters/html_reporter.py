"""HTML Reporter for CIS Controls compliance assessment reports."""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import base64
from datetime import datetime

from aws_cis_assessment.reporters.base_reporter import ReportGenerator
from aws_cis_assessment.core.models import (
    AssessmentResult, ComplianceSummary, RemediationGuidance,
    IGScore, ControlScore, ComplianceResult
)

logger = logging.getLogger(__name__)


class HTMLReporter(ReportGenerator):
    """HTML format reporter for compliance assessment results.
    
    Generates interactive web-based reports with executive dashboard,
    compliance summaries, charts, detailed drill-down capabilities,
    and responsive design for mobile and desktop viewing.
    """
    
    def __init__(self, template_dir: Optional[str] = None, include_charts: bool = True):
        """Initialize HTML reporter.
        
        Args:
            template_dir: Optional path to custom report templates
            include_charts: Whether to include interactive charts (default: True)
        """
        super().__init__(template_dir)
        self.include_charts = include_charts
        logger.info(f"Initialized HTMLReporter with charts={include_charts}")
    
    def generate_report(self, assessment_result: AssessmentResult, 
                       compliance_summary: ComplianceSummary,
                       output_path: Optional[str] = None) -> str:
        """Generate HTML format compliance assessment report.
        
        Args:
            assessment_result: Complete assessment result data
            compliance_summary: Executive summary of compliance status
            output_path: Optional path to save the HTML report
            
        Returns:
            HTML formatted report content as string
        """
        # Handle None inputs
        if assessment_result is None or compliance_summary is None:
            logger.error("Assessment result or compliance summary is None")
            return ""
            
        logger.info(f"Generating HTML report for account {assessment_result.account_id}")
        
        # Validate input data
        if not self.validate_assessment_data(assessment_result, compliance_summary):
            logger.error("Assessment data validation failed")
            return ""
        
        # Prepare structured report data
        report_data = self._prepare_report_data(assessment_result, compliance_summary)
        
        # Validate prepared data
        if not self._validate_report_data(report_data):
            logger.error("Report data validation failed")
            return ""
        
        # Enhance HTML-specific data structure
        html_report_data = self._enhance_html_structure(report_data)
        
        try:
            # Generate HTML content
            html_content = self._generate_html_content(html_report_data)
            
            logger.info(f"Generated HTML report with {len(html_content)} characters")
            
            # Save to file if path provided
            if output_path:
                if self._save_report_to_file(html_content, output_path):
                    logger.info(f"HTML report saved to {output_path}")
                else:
                    logger.error(f"Failed to save HTML report to {output_path}")
            
            return html_content
            
        except Exception as e:
            logger.error(f"Failed to generate HTML report: {e}")
            return ""
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported output formats.
        
        Returns:
            List containing 'html' format
        """
        return ['html']
    
    def _enhance_html_structure(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance report data structure for HTML-specific requirements.
        
        Args:
            report_data: Base report data from parent class
            
        Returns:
            Enhanced data structure optimized for HTML output
        """
        # Create enhanced HTML structure
        html_data = {
            "report_format": "html",
            "report_version": "1.0",
            "include_charts": self.include_charts,
            **report_data
        }
        
        # Add HTML-specific metadata
        html_data["metadata"]["report_format"] = "html"
        html_data["metadata"]["interactive"] = True
        html_data["metadata"]["responsive_design"] = True
        
        # Enhance executive summary with visual indicators
        exec_summary = html_data["executive_summary"]
        exec_summary["compliance_grade"] = self._calculate_compliance_grade(
            exec_summary["overall_compliance_percentage"]
        )
        exec_summary["risk_level"] = self._calculate_risk_level(
            exec_summary["overall_compliance_percentage"]
        )
        exec_summary["status_color"] = self._get_status_color(
            exec_summary["overall_compliance_percentage"]
        )
        
        # Add chart data for Implementation Groups
        html_data["chart_data"] = self._prepare_chart_data(html_data)
        
        # Enhance Implementation Group data with visual elements
        for ig_name, ig_data in html_data["implementation_groups"].items():
            ig_data["status_color"] = self._get_status_color(ig_data["compliance_percentage"])
            ig_data["progress_width"] = ig_data["compliance_percentage"]
            
            # Enhance control data with visual indicators
            for control_id, control_data in ig_data["controls"].items():
                control_data["status_color"] = self._get_status_color(
                    control_data["compliance_percentage"]
                )
                control_data["progress_width"] = control_data["compliance_percentage"]
                control_data["severity_badge"] = self._get_severity_badge(control_data)
                
                # Process findings for display
                control_data["display_findings"] = self._prepare_findings_for_display(
                    control_data.get("non_compliant_findings", [])
                )
        
        # Enhance remediation priorities with visual elements
        for remediation in html_data["remediation_priorities"]:
            remediation["priority_badge"] = self._get_priority_badge(remediation["priority"])
            remediation["effort_badge"] = self._get_effort_badge(remediation["estimated_effort"])
        
        # Add navigation structure
        html_data["navigation"] = self._build_navigation_structure(html_data)
        
        return html_data
    
    def _generate_html_content(self, html_data: Dict[str, Any]) -> str:
        """Generate complete HTML content from data.
        
        Args:
            html_data: Enhanced HTML report data
            
        Returns:
            Complete HTML document as string
        """
        # Build HTML document sections
        html_head = self._generate_html_head(html_data)
        html_body = self._generate_html_body(html_data)
        
        # Combine into complete document
        html_content = f"""<!DOCTYPE html>
<html lang="en">
{html_head}
{html_body}
</html>"""
        
        return html_content
    
    def _generate_html_head(self, html_data: Dict[str, Any]) -> str:
        """Generate HTML head section with styles and scripts.
        
        Args:
            html_data: Enhanced HTML report data
            
        Returns:
            HTML head section as string
        """
        metadata = html_data["metadata"]
        exec_summary = html_data["executive_summary"]
        
        # Include Chart.js if charts are enabled
        chart_script = ""
        if self.include_charts:
            chart_script = '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>'
        
        head_content = f"""<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CIS Controls Compliance Report - {metadata.get('account_id', 'Unknown')}</title>
    <meta name="description" content="AWS CIS Controls compliance assessment report">
    <meta name="author" content="AWS CIS Assessment Tool">
    <meta name="report-date" content="{metadata.get('report_generated_at', '')}">
    
    {chart_script}
    
    <style>
        {self._get_css_styles()}
    </style>
    
    <script>
        {self._get_javascript_code(html_data)}
    </script>
</head>"""
        
        return head_content
    
    def _generate_html_body(self, html_data: Dict[str, Any]) -> str:
        """Generate HTML body section with content.
        
        Args:
            html_data: Enhanced HTML report data
            
        Returns:
            HTML body section as string
        """
        # Generate main content sections
        header = self._generate_header(html_data)
        navigation = self._generate_navigation(html_data)
        executive_dashboard = self._generate_executive_dashboard(html_data)
        implementation_groups = self._generate_implementation_groups_section(html_data)
        detailed_findings = self._generate_detailed_findings_section(html_data)
        resource_details = self._generate_resource_details_section(html_data)
        remediation_section = self._generate_remediation_section(html_data)
        footer = self._generate_footer(html_data)
        
        body_content = f"""<body>
    <div class="container">
        {header}
        {navigation}
        {executive_dashboard}
        {implementation_groups}
        {detailed_findings}
        {resource_details}
        {remediation_section}
        {footer}
    </div>
    
    <script>
        // Initialize interactive features after DOM load
        document.addEventListener('DOMContentLoaded', function() {{
            initializeCharts();
            initializeInteractivity();
        }});
    </script>
</body>"""
        
        return body_content
    
    def _get_css_styles(self) -> str:
        """Get CSS styles for the HTML report.
        
        Returns:
            CSS styles as string
        """
        return """
        /* Reset and base styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            min-height: 100vh;
        }
        
        /* Header styles */
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }
        
        .header .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        /* Navigation styles */
        .navigation {
            background-color: #2c3e50;
            border-radius: 8px;
            margin-bottom: 30px;
            overflow: hidden;
        }
        
        .nav-list {
            display: flex;
            list-style: none;
            flex-wrap: wrap;
        }
        
        .nav-item {
            flex: 1;
            min-width: 150px;
        }
        
        .nav-link {
            display: block;
            padding: 15px 20px;
            color: white;
            text-decoration: none;
            text-align: center;
            transition: background-color 0.3s;
            border-right: 1px solid #34495e;
        }
        
        .nav-link:hover, .nav-link.active {
            background-color: #3498db;
        }
        
        /* Dashboard styles */
        .dashboard {
            margin-bottom: 40px;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-left: 4px solid #3498db;
            transition: transform 0.2s;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
        }
        
        .metric-card.excellent { border-left-color: #27ae60; }
        .metric-card.good { border-left-color: #2ecc71; }
        .metric-card.fair { border-left-color: #f39c12; }
        .metric-card.poor { border-left-color: #e67e22; }
        .metric-card.critical { border-left-color: #e74c3c; }
        
        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .metric-label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .metric-trend {
            font-size: 0.8em;
            margin-top: 10px;
            padding: 5px 10px;
            border-radius: 15px;
            display: inline-block;
        }
        
        .trend-up { background-color: #d5f4e6; color: #27ae60; }
        .trend-down { background-color: #ffeaa7; color: #e17055; }
        .trend-stable { background-color: #e3f2fd; color: #2196f3; }
        
        /* Progress bars */
        .progress-container {
            background-color: #ecf0f1;
            border-radius: 10px;
            height: 20px;
            margin: 10px 0;
            overflow: hidden;
        }
        
        .progress-bar {
            height: 100%;
            border-radius: 10px;
            transition: width 0.8s ease-in-out;
            position: relative;
        }
        
        .progress-bar.excellent { background-color: #27ae60; }
        .progress-bar.good { background-color: #2ecc71; }
        .progress-bar.fair { background-color: #f39c12; }
        .progress-bar.poor { background-color: #e67e22; }
        .progress-bar.critical { background-color: #e74c3c; }
        
        .progress-text {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            color: white;
            font-weight: bold;
            font-size: 0.8em;
        }
        
        /* Implementation Groups */
        .ig-section {
            margin-bottom: 40px;
        }
        
        .ig-header {
            background: linear-gradient(90deg, #74b9ff 0%, #0984e3 100%);
            color: white;
            padding: 20px;
            border-radius: 10px 10px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .ig-title {
            font-size: 1.5em;
            font-weight: 600;
        }
        
        .ig-score {
            font-size: 2em;
            font-weight: bold;
        }
        
        .ig-content {
            background: white;
            border: 1px solid #ddd;
            border-top: none;
            border-radius: 0 0 10px 10px;
            padding: 20px;
        }
        
        .controls-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .control-card {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            background: #fafafa;
            transition: box-shadow 0.2s;
        }
        
        .control-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .control-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .control-id {
            font-weight: bold;
            color: #2c3e50;
        }
        
        .control-title {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
        }
        
        /* Badges */
        .badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.75em;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .badge.high { background-color: #e74c3c; color: white; }
        .badge.medium { background-color: #f39c12; color: white; }
        .badge.low { background-color: #27ae60; color: white; }
        
        .badge.effort-minimal { background-color: #2ecc71; color: white; }
        .badge.effort-moderate { background-color: #f39c12; color: white; }
        .badge.effort-significant { background-color: #e67e22; color: white; }
        .badge.effort-extensive { background-color: #e74c3c; color: white; }
        
        .badge.compliant { background-color: #27ae60; color: white; }
        .badge.non_compliant { background-color: #e74c3c; color: white; }
        
        /* Inheritance indicators */
        .inheritance-note {
            color: #666;
            font-style: italic;
            display: block;
            margin-top: 5px;
        }
        
        .ig-explanation {
            background-color: #e8f4fd;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin-bottom: 30px;
            border-radius: 5px;
        }
        
        .ig-scope {
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }
        
        /* Resource Details Section */
        .resource-details {
            margin-bottom: 40px;
        }
        
        .resource-summary {
            margin-bottom: 30px;
        }
        
        .resource-stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .resource-stat-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #3498db;
        }
        
        .resource-stat-card.compliant {
            border-left-color: #27ae60;
        }
        
        .resource-stat-card.non-compliant {
            border-left-color: #e74c3c;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .resource-type-breakdown {
            margin-bottom: 30px;
        }
        
        .resource-type-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .resource-type-stat {
            background: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .resource-type-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .resource-type-name {
            font-weight: 600;
            color: #2c3e50;
        }
        
        .resource-type-count {
            font-size: 0.9em;
            color: #666;
        }
        
        .resource-table-container {
            margin-bottom: 20px;
        }
        
        .resource-filters {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .search-input, .filter-select {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        
        .search-input {
            flex: 1;
            min-width: 200px;
        }
        
        .filter-select {
            min-width: 150px;
        }
        
        .resource-table {
            font-size: 0.9em;
        }
        
        .resource-table th {
            cursor: pointer;
            user-select: none;
        }
        
        .resource-table th:hover {
            background-color: #2c3e50;
        }
        
        .resource-row.compliant {
            background-color: #f8fff8;
        }
        
        .resource-row.non_compliant {
            background-color: #fff8f8;
        }
        
        .evaluation-reason {
            max-width: 300px;
            word-wrap: break-word;
            font-size: 0.85em;
        }
        
        .resource-export {
            text-align: center;
            margin-top: 20px;
        }
        
        .export-btn {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 0 10px;
            font-size: 14px;
            transition: background-color 0.3s;
        }
        
        .export-btn:hover {
            background-color: #2980b9;
        }
        
        /* Tables */
        .findings-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .findings-table th {
            background-color: #34495e;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }
        
        .findings-table td {
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }
        
        .findings-table tr:hover {
            background-color: #f8f9fa;
        }
        
        /* Collapsible sections */
        .collapsible {
            cursor: pointer;
            padding: 15px;
            background-color: #f1f2f6;
            border: none;
            text-align: left;
            outline: none;
            font-size: 1em;
            width: 100%;
            border-radius: 5px;
            margin-bottom: 5px;
            transition: background-color 0.3s;
        }
        
        .collapsible:hover {
            background-color: #ddd;
        }
        
        .collapsible.active {
            background-color: #3498db;
            color: white;
        }
        
        .collapsible-content {
            padding: 0 15px;
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out;
            background-color: white;
            border-radius: 0 0 5px 5px;
        }
        
        .collapsible-content.active {
            max-height: 1000px;
            padding: 15px;
        }
        
        /* Charts */
        .chart-container {
            position: relative;
            height: 400px;
            margin: 20px 0;
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Footer */
        .footer {
            margin-top: 50px;
            padding: 30px;
            background-color: #2c3e50;
            color: white;
            border-radius: 10px;
            text-align: center;
        }
        
        .footer-content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .footer-section h4 {
            margin-bottom: 10px;
            color: #3498db;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .nav-list {
                flex-direction: column;
            }
            
            .nav-link {
                border-right: none;
                border-bottom: 1px solid #34495e;
            }
            
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
            
            .controls-grid {
                grid-template-columns: 1fr;
            }
            
            .ig-header {
                flex-direction: column;
                text-align: center;
                gap: 10px;
            }
            
            .findings-table {
                font-size: 0.8em;
            }
            
            .findings-table th,
            .findings-table td {
                padding: 8px;
            }
        }
        
        @media (max-width: 480px) {
            .header h1 {
                font-size: 1.5em;
            }
            
            .metric-value {
                font-size: 2em;
            }
            
            .chart-container {
                height: 300px;
                padding: 10px;
            }
        }
        
        /* Print styles */
        @media print {
            .navigation {
                display: none;
            }
            
            .container {
                box-shadow: none;
                max-width: none;
            }
            
            .collapsible-content {
                max-height: none !important;
                padding: 15px !important;
            }
            
            .chart-container {
                break-inside: avoid;
            }
        }
        """
    
    def _get_javascript_code(self, html_data: Dict[str, Any]) -> str:
        """Get JavaScript code for interactive features.
        
        Args:
            html_data: Enhanced HTML report data
            
        Returns:
            JavaScript code as string
        """
        chart_data_json = str(html_data.get("chart_data", {})).replace("'", '"')
        
        return f"""
        // Chart data
        const chartData = {chart_data_json};
        
        // Initialize charts
        function initializeCharts() {{
            if (typeof Chart === 'undefined') {{
                console.log('Chart.js not loaded, skipping chart initialization');
                return;
            }}
            
            // Implementation Groups Compliance Chart
            const igChartCtx = document.getElementById('igComplianceChart');
            if (igChartCtx) {{
                new Chart(igChartCtx, {{
                    type: 'doughnut',
                    data: chartData.igCompliance,
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                position: 'bottom'
                            }},
                            title: {{
                                display: true,
                                text: 'Implementation Groups Compliance'
                            }}
                        }}
                    }}
                }});
            }}
            
            // Overall Compliance Trend Chart
            const trendChartCtx = document.getElementById('complianceTrendChart');
            if (trendChartCtx) {{
                new Chart(trendChartCtx, {{
                    type: 'bar',
                    data: chartData.complianceTrend,
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                max: 100
                            }}
                        }},
                        plugins: {{
                            legend: {{
                                display: false
                            }},
                            title: {{
                                display: true,
                                text: 'Compliance by Implementation Group'
                            }}
                        }}
                    }}
                }});
            }}
            
            // Risk Distribution Chart
            const riskChartCtx = document.getElementById('riskDistributionChart');
            if (riskChartCtx) {{
                new Chart(riskChartCtx, {{
                    type: 'pie',
                    data: chartData.riskDistribution,
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                position: 'right'
                            }},
                            title: {{
                                display: true,
                                text: 'Risk Level Distribution'
                            }}
                        }}
                    }}
                }});
            }}
        }}
        
        // Initialize interactive features
        function initializeInteractivity() {{
            // Collapsible sections
            const collapsibles = document.querySelectorAll('.collapsible');
            collapsibles.forEach(function(collapsible) {{
                collapsible.addEventListener('click', function() {{
                    this.classList.toggle('active');
                    const content = this.nextElementSibling;
                    content.classList.toggle('active');
                }});
            }});
            
            // Navigation smooth scrolling
            const navLinks = document.querySelectorAll('.nav-link');
            navLinks.forEach(function(link) {{
                link.addEventListener('click', function(e) {{
                    e.preventDefault();
                    const targetId = this.getAttribute('href').substring(1);
                    const targetElement = document.getElementById(targetId);
                    if (targetElement) {{
                        targetElement.scrollIntoView({{
                            behavior: 'smooth',
                            block: 'start'
                        }});
                        
                        // Update active nav item
                        navLinks.forEach(nl => nl.classList.remove('active'));
                        this.classList.add('active');
                    }}
                }});
            }});
            
            // Progress bar animations
            const progressBars = document.querySelectorAll('.progress-bar');
            const observer = new IntersectionObserver(function(entries) {{
                entries.forEach(function(entry) {{
                    if (entry.isIntersecting) {{
                        const progressBar = entry.target;
                        const width = progressBar.getAttribute('data-width');
                        progressBar.style.width = width + '%';
                    }}
                }});
            }});
            
            progressBars.forEach(function(bar) {{
                observer.observe(bar);
            }});
            
            // Table sorting
            const tables = document.querySelectorAll('.findings-table');
            tables.forEach(function(table) {{
                const headers = table.querySelectorAll('th');
                headers.forEach(function(header, index) {{
                    header.style.cursor = 'pointer';
                    header.addEventListener('click', function() {{
                        sortTable(table, index);
                    }});
                }});
            }});
        }}
        
        // Table sorting function
        function sortTable(table, columnIndex) {{
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            const isNumeric = rows.every(row => {{
                const cell = row.cells[columnIndex];
                return cell && !isNaN(parseFloat(cell.textContent));
            }});
            
            rows.sort(function(a, b) {{
                const aVal = a.cells[columnIndex].textContent.trim();
                const bVal = b.cells[columnIndex].textContent.trim();
                
                if (isNumeric) {{
                    return parseFloat(aVal) - parseFloat(bVal);
                }} else {{
                    return aVal.localeCompare(bVal);
                }}
            }});
            
            rows.forEach(function(row) {{
                tbody.appendChild(row);
            }});
        }}
        
        // Search functionality
        function searchFindings(searchTerm) {{
            const tables = document.querySelectorAll('.findings-table tbody tr');
            tables.forEach(function(row) {{
                const text = row.textContent.toLowerCase();
                const matches = text.includes(searchTerm.toLowerCase());
                row.style.display = matches ? '' : 'none';
            }});
        }}
        
        // Export functionality
        function exportToCSV() {{
            const tables = document.querySelectorAll('.findings-table');
            let csvContent = '';
            
            tables.forEach(function(table) {{
                const rows = table.querySelectorAll('tr');
                rows.forEach(function(row) {{
                    const cells = row.querySelectorAll('th, td');
                    const rowData = Array.from(cells).map(cell => 
                        '"' + cell.textContent.replace(/"/g, '""') + '"'
                    ).join(',');
                    csvContent += rowData + '\\n';
                }});
                csvContent += '\\n';
            }});
            
            const blob = new Blob([csvContent], {{ type: 'text/csv' }});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'cis-compliance-findings.csv';
            a.click();
            window.URL.revokeObjectURL(url);
        }}
        
        // Resource filtering functionality
        function filterResources() {{
            const searchTerm = document.getElementById('resourceSearch').value.toLowerCase();
            const statusFilter = document.getElementById('statusFilter').value;
            const typeFilter = document.getElementById('typeFilter').value;
            const rows = document.querySelectorAll('#resourceTable tbody tr');
            
            rows.forEach(function(row) {{
                const cells = row.querySelectorAll('td');
                const resourceId = cells[0].textContent.toLowerCase();
                const resourceType = cells[1].textContent;
                const status = cells[3].textContent.includes('COMPLIANT') ? 
                    (cells[3].textContent.includes('NON_COMPLIANT') ? 'NON_COMPLIANT' : 'COMPLIANT') : 'NON_COMPLIANT';
                const evaluationReason = cells[6].textContent.toLowerCase();
                
                const matchesSearch = resourceId.includes(searchTerm) || 
                                    resourceType.toLowerCase().includes(searchTerm) ||
                                    evaluationReason.includes(searchTerm);
                const matchesStatus = !statusFilter || status === statusFilter;
                const matchesType = !typeFilter || resourceType === typeFilter;
                
                row.style.display = (matchesSearch && matchesStatus && matchesType) ? '' : 'none';
            }});
        }}
        
        // Resource table sorting
        function sortResourceTable(columnIndex) {{
            const table = document.getElementById('resourceTable');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            const isNumeric = columnIndex === 3; // Status column - sort by compliance status
            
            rows.sort(function(a, b) {{
                const aVal = a.cells[columnIndex].textContent.trim();
                const bVal = b.cells[columnIndex].textContent.trim();
                
                if (columnIndex === 3) {{ // Status column - COMPLIANT before NON_COMPLIANT
                    const aCompliant = aVal.includes('✓');
                    const bCompliant = bVal.includes('✓');
                    return bCompliant - aCompliant;
                }} else {{
                    return aVal.localeCompare(bVal);
                }}
            }});
            
            rows.forEach(function(row) {{
                tbody.appendChild(row);
            }});
        }}
        
        // Export resources to CSV
        function exportResourcesToCSV() {{
            const table = document.getElementById('resourceTable');
            const rows = table.querySelectorAll('tr');
            let csvContent = '';
            
            rows.forEach(function(row) {{
                const cells = row.querySelectorAll('th, td');
                const rowData = Array.from(cells).map(cell => 
                    '"' + cell.textContent.replace(/"/g, '""').replace(/\\s+/g, ' ').trim() + '"'
                ).join(',');
                csvContent += rowData + '\\n';
            }});
            
            const blob = new Blob([csvContent], {{ type: 'text/csv' }});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'cis-compliance-resources.csv';
            a.click();
            window.URL.revokeObjectURL(url);
        }}
        
        // Export resources to JSON
        function exportResourcesToJSON() {{
            const table = document.getElementById('resourceTable');
            const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
            const rows = Array.from(table.querySelectorAll('tbody tr'));
            
            const data = rows.map(row => {{
                const cells = Array.from(row.querySelectorAll('td'));
                const rowData = {{}};
                headers.forEach((header, index) => {{
                    rowData[header] = cells[index] ? cells[index].textContent.replace(/\\s+/g, ' ').trim() : '';
                }});
                return rowData;
            }});
            
            const jsonContent = JSON.stringify(data, null, 2);
            const blob = new Blob([jsonContent], {{ type: 'application/json' }});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'cis-compliance-resources.json';
            a.click();
            window.URL.revokeObjectURL(url);
        }}
        """
    
    def _generate_header(self, html_data: Dict[str, Any]) -> str:
        """Generate header section.
        
        Args:
            html_data: Enhanced HTML report data
            
        Returns:
            Header HTML as string
        """
        metadata = html_data["metadata"]
        exec_summary = html_data["executive_summary"]
        
        return f"""
        <header class="header">
            <h1>CIS Controls Compliance Report</h1>
            <div class="subtitle">
                AWS Account: {metadata.get('account_id', 'Unknown')} | 
                Assessment Date: {datetime.fromisoformat(metadata.get('assessment_timestamp', '')).strftime('%B %d, %Y') if metadata.get('assessment_timestamp') else 'Unknown'} |
                Overall Compliance: {exec_summary.get('overall_compliance_percentage', 0):.1f}%
            </div>
        </header>
        """
    
    def _generate_navigation(self, html_data: Dict[str, Any]) -> str:
        """Generate navigation section.
        
        Args:
            html_data: Enhanced HTML report data
            
        Returns:
            Navigation HTML as string
        """
        nav_items = html_data.get("navigation", {}).get("sections", [])
        
        nav_links = ""
        for item in nav_items:
            nav_links += f'<li class="nav-item"><a href="#{item["id"]}" class="nav-link">{item["title"]}</a></li>'
        
        return f"""
        <nav class="navigation">
            <ul class="nav-list">
                {nav_links}
            </ul>
        </nav>
        """
    
    def _generate_executive_dashboard(self, html_data: Dict[str, Any]) -> str:
        """Generate executive dashboard section.
        
        Args:
            html_data: Enhanced HTML report data
            
        Returns:
            Dashboard HTML as string
        """
        exec_summary = html_data["executive_summary"]
        metadata = html_data["metadata"]
        
        # Generate metric cards
        overall_status = self._get_status_class(exec_summary.get("overall_compliance_percentage", 0))
        
        metric_cards = f"""
        <div class="metric-card {overall_status}">
            <div class="metric-value">{exec_summary.get('overall_compliance_percentage', 0):.1f}%</div>
            <div class="metric-label">Overall Compliance</div>
            <div class="metric-trend trend-stable">Grade: {exec_summary.get('compliance_grade', 'N/A')}</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-value">{exec_summary.get('total_resources', 0):,}</div>
            <div class="metric-label">Resources Evaluated</div>
            <div class="metric-trend trend-up">Across {len(metadata.get('regions_assessed', []))} regions</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-value">{exec_summary.get('compliant_resources', 0):,}</div>
            <div class="metric-label">Compliant Resources</div>
            <div class="metric-trend trend-up">{(exec_summary.get('compliant_resources', 0) / max(exec_summary.get('total_resources', 1), 1) * 100):.1f}% of total</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-value">{exec_summary.get('non_compliant_resources', 0):,}</div>
            <div class="metric-label">Non-Compliant Resources</div>
            <div class="metric-trend trend-down">Require attention</div>
        </div>
        """
        
        # Generate IG progress bars
        ig_progress = ""
        for ig in ['ig1', 'ig2', 'ig3']:
            ig_key = f"{ig}_compliance_percentage"
            ig_value = exec_summary.get(ig_key, 0)
            ig_status = self._get_status_class(ig_value)
            ig_name = ig.upper()
            
            ig_progress += f"""
            <div class="ig-progress">
                <div class="ig-progress-header">
                    <span>{ig_name} Compliance</span>
                    <span>{ig_value:.1f}%</span>
                </div>
                <div class="progress-container">
                    <div class="progress-bar {ig_status}" data-width="{ig_value}">
                        <span class="progress-text">{ig_value:.1f}%</span>
                    </div>
                </div>
            </div>
            """
        
        # Generate charts section
        charts_section = ""
        if self.include_charts:
            charts_section = f"""
            <div class="charts-section">
                <div class="chart-container">
                    <canvas id="igComplianceChart"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="complianceTrendChart"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="riskDistributionChart"></canvas>
                </div>
            </div>
            """
        
        return f"""
        <section id="dashboard" class="dashboard">
            <h2>Executive Dashboard</h2>
            <div class="dashboard-grid">
                {metric_cards}
            </div>
            
            <div class="ig-progress-section">
                <h3>Implementation Groups Progress</h3>
                {ig_progress}
            </div>
            
            {charts_section}
        </section>
        """
    
    def _generate_implementation_groups_section(self, html_data: Dict[str, Any]) -> str:
        """Generate Implementation Groups section with unique controls per IG.
        
        Args:
            html_data: Enhanced HTML report data
            
        Returns:
            Implementation Groups HTML as string
        """
        ig_sections = ""
        
        # Define which controls are unique to each IG to avoid duplication
        unique_controls = self._get_unique_controls_per_ig(html_data["implementation_groups"])
        
        for ig_name, ig_data in html_data["implementation_groups"].items():
            controls_html = ""
            
            # Only show controls that are unique to this IG or inherited controls for context
            controls_to_show = unique_controls.get(ig_name, {})
            
            for control_id, control_data in controls_to_show.items():
                findings_count = len(control_data.get("non_compliant_findings", []))
                status_class = self._get_status_class(control_data["compliance_percentage"])
                
                # Add inheritance indicator for inherited controls
                inheritance_indicator = ""
                if ig_name != "IG1" and control_id in unique_controls.get("IG1", {}):
                    inheritance_indicator = f'<small class="inheritance-note">Inherited from IG1</small>'
                elif ig_name == "IG3" and control_id in unique_controls.get("IG2", {}):
                    inheritance_indicator = f'<small class="inheritance-note">Inherited from IG2</small>'
                
                controls_html += f"""
                <div class="control-card">
                    <div class="control-header">
                        <div class="control-id">{control_id}</div>
                        <div class="badge {control_data.get('severity_badge', 'medium')}">{findings_count} Issues</div>
                    </div>
                    <div class="control-title">{control_data.get('title', f'CIS Control {control_id}')}</div>
                    {inheritance_indicator}
                    <div class="progress-container">
                        <div class="progress-bar {status_class}" data-width="{control_data['compliance_percentage']}">
                            <span class="progress-text">{control_data['compliance_percentage']:.1f}%</span>
                        </div>
                    </div>
                    <div class="control-stats">
                        <small>{control_data['compliant_resources']}/{control_data['total_resources']} resources compliant</small>
                    </div>
                </div>
                """
            
            ig_status_class = self._get_status_class(ig_data["compliance_percentage"])
            
            # Show summary of what this IG includes
            ig_description = self._get_ig_description_with_inheritance(ig_name)
            
            ig_sections += f"""
            <div class="ig-section">
                <div class="ig-header">
                    <div class="ig-title">{ig_name} - {ig_description}</div>
                    <div class="ig-score">{ig_data['compliance_percentage']:.1f}%</div>
                </div>
                <div class="ig-content">
                    <div class="ig-summary">
                        <p><strong>{ig_data['compliant_controls']}</strong> of <strong>{ig_data['total_controls']}</strong> controls are compliant</p>
                        <p class="ig-scope">{self._get_ig_scope_description(ig_name, len(controls_to_show))}</p>
                    </div>
                    <div class="controls-grid">
                        {controls_html}
                    </div>
                </div>
            </div>
            """
        
        return f"""
        <section id="implementation-groups" class="implementation-groups">
            <h2>Implementation Groups</h2>
            <div class="ig-explanation">
                <p><strong>Note:</strong> Implementation Groups are cumulative. IG2 includes all IG1 controls plus additional ones. IG3 includes all IG1 and IG2 controls plus advanced controls.</p>
            </div>
            {ig_sections}
        </section>
        """
    
    def _generate_detailed_findings_section(self, html_data: Dict[str, Any]) -> str:
        """Generate detailed findings section.
        
        Args:
            html_data: Enhanced HTML report data
            
        Returns:
            Detailed findings HTML as string
        """
        findings_sections = ""
        
        for ig_name, ig_findings in html_data["detailed_findings"].items():
            ig_content = ""
            
            for control_id, control_findings in ig_findings.items():
                if not control_findings:
                    continue
                
                findings_rows = ""
                for finding in control_findings:
                    if finding["compliance_status"] == "NON_COMPLIANT":
                        findings_rows += f"""
                        <tr>
                            <td>{finding['resource_id']}</td>
                            <td>{finding['resource_type']}</td>
                            <td>{finding['region']}</td>
                            <td><span class="badge {finding['compliance_status'].lower()}">{finding['compliance_status']}</span></td>
                            <td>{finding['evaluation_reason']}</td>
                            <td>{finding['config_rule_name']}</td>
                        </tr>
                        """
                
                if findings_rows:
                    ig_content += f"""
                    <button class="collapsible">{control_id} - Non-Compliant Resources ({len([f for f in control_findings if f['compliance_status'] == 'NON_COMPLIANT'])} items)</button>
                    <div class="collapsible-content">
                        <table class="findings-table">
                            <thead>
                                <tr>
                                    <th>Resource ID</th>
                                    <th>Resource Type</th>
                                    <th>Region</th>
                                    <th>Compliance Status</th>
                                    <th>Reason</th>
                                    <th>Config Rule</th>
                                </tr>
                            </thead>
                            <tbody>
                                {findings_rows}
                            </tbody>
                        </table>
                    </div>
                    """
            
            if ig_content:
                findings_sections += f"""
                <div class="ig-findings">
                    <h3>{ig_name} Detailed Findings</h3>
                    {ig_content}
                </div>
                """
        
        return f"""
        <section id="detailed-findings" class="detailed-findings">
            <h2>Detailed Findings</h2>
            <div class="search-container">
                <input type="text" placeholder="Search findings..." onkeyup="searchFindings(this.value)" style="width: 100%; padding: 10px; margin-bottom: 20px; border: 1px solid #ddd; border-radius: 5px;">
            </div>
            {findings_sections}
        </section>
        """
    
    def _generate_remediation_section(self, html_data: Dict[str, Any]) -> str:
        """Generate remediation section.
        
        Args:
            html_data: Enhanced HTML report data
            
        Returns:
            Remediation HTML as string
        """
        remediation_items = ""
        
        for remediation in html_data["remediation_priorities"]:
            steps_html = ""
            for step in remediation["remediation_steps"]:
                steps_html += f"<li>{step}</li>"
            
            remediation_items += f"""
            <div class="remediation-item">
                <div class="remediation-header">
                    <h4>{remediation['control_id']} - {remediation['config_rule_name']}</h4>
                    <div class="remediation-badges">
                        <span class="badge {remediation['priority_badge']}">{remediation['priority']}</span>
                        <span class="badge {remediation['effort_badge']}">{remediation['estimated_effort']}</span>
                    </div>
                </div>
                <div class="remediation-content">
                    <h5>Remediation Steps:</h5>
                    <ol>
                        {steps_html}
                    </ol>
                    <p><strong>Documentation:</strong> <a href="{remediation['aws_documentation_link']}" target="_blank">AWS Documentation</a></p>
                </div>
            </div>
            """
        
        return f"""
        <section id="remediation" class="remediation">
            <h2>Remediation Priorities</h2>
            <div class="remediation-list">
                {remediation_items}
            </div>
            <div class="export-actions">
                <button onclick="exportToCSV()" class="export-btn">Export Findings to CSV</button>
            </div>
        </section>
        """
    
    def _generate_footer(self, html_data: Dict[str, Any]) -> str:
        """Generate footer section.
        
        Args:
            html_data: Enhanced HTML report data
            
        Returns:
            Footer HTML as string
        """
        metadata = html_data["metadata"]
        
        return f"""
        <footer class="footer">
            <div class="footer-content">
                <div class="footer-section">
                    <h4>Report Information</h4>
                    <p>Generated: {datetime.fromisoformat(metadata.get('report_generated_at', '')).strftime('%B %d, %Y at %I:%M %p') if metadata.get('report_generated_at') else 'Unknown'}</p>
                    <p>Assessment Duration: {metadata.get('assessment_duration', 'Unknown')}</p>
                    <p>Report Version: {html_data.get('report_version', '1.0')}</p>
                </div>
                <div class="footer-section">
                    <h4>Assessment Scope</h4>
                    <p>AWS Account: {metadata.get('account_id', 'Unknown')}</p>
                    <p>Regions: {', '.join(metadata.get('regions_assessed', []))}</p>
                    <p>Total Resources: {metadata.get('total_resources_evaluated', 0):,}</p>
                </div>
                <div class="footer-section">
                    <h4>About CIS Controls</h4>
                    <p>The CIS Controls are a prioritized set of cybersecurity best practices developed by the Center for Internet Security.</p>
                    <p>This report evaluates AWS configurations against CIS Controls Implementation Groups.</p>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2024 AWS CIS Assessment Tool. Generated with HTML Reporter v{html_data.get('report_version', '1.0')}</p>
            </div>
        </footer>
        """
    
    def _prepare_chart_data(self, html_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for charts.
        
        Args:
            html_data: Enhanced HTML report data
            
        Returns:
            Chart data dictionary
        """
        exec_summary = html_data["executive_summary"]
        
        # Implementation Groups compliance chart
        ig_compliance = {
            "labels": ["IG1", "IG2", "IG3"],
            "datasets": [{
                "data": [
                    exec_summary.get("ig1_compliance_percentage", 0),
                    exec_summary.get("ig2_compliance_percentage", 0),
                    exec_summary.get("ig3_compliance_percentage", 0)
                ],
                "backgroundColor": ["#3498db", "#2ecc71", "#e74c3c"],
                "borderWidth": 2,
                "borderColor": "#fff"
            }]
        }
        
        # Compliance trend chart
        compliance_trend = {
            "labels": ["IG1", "IG2", "IG3"],
            "datasets": [{
                "label": "Compliance %",
                "data": [
                    exec_summary.get("ig1_compliance_percentage", 0),
                    exec_summary.get("ig2_compliance_percentage", 0),
                    exec_summary.get("ig3_compliance_percentage", 0)
                ],
                "backgroundColor": ["#3498db", "#2ecc71", "#e74c3c"],
                "borderColor": ["#2980b9", "#27ae60", "#c0392b"],
                "borderWidth": 1
            }]
        }
        
        # Risk distribution chart
        total_resources = exec_summary.get("total_resources", 1)
        compliant = exec_summary.get("compliant_resources", 0)
        non_compliant = exec_summary.get("non_compliant_resources", 0)
        
        risk_distribution = {
            "labels": ["Compliant", "Non-Compliant"],
            "datasets": [{
                "data": [compliant, non_compliant],
                "backgroundColor": ["#27ae60", "#e74c3c"],
                "borderWidth": 2,
                "borderColor": "#fff"
            }]
        }
        
        return {
            "igCompliance": ig_compliance,
            "complianceTrend": compliance_trend,
            "riskDistribution": risk_distribution
        }
    
    def _build_navigation_structure(self, html_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build navigation structure for the report.
        
        Args:
            html_data: Enhanced HTML report data
            
        Returns:
            Navigation structure dictionary
        """
        return {
            "sections": [
                {"id": "dashboard", "title": "Dashboard"},
                {"id": "implementation-groups", "title": "Implementation Groups"},
                {"id": "detailed-findings", "title": "Detailed Findings"},
                {"id": "resource-details", "title": "Resource Details"},
                {"id": "remediation", "title": "Remediation"}
            ]
        }
    
    def _calculate_compliance_grade(self, compliance_percentage: float) -> str:
        """Calculate compliance grade based on percentage."""
        if compliance_percentage >= 95.0:
            return "A"
        elif compliance_percentage >= 85.0:
            return "B"
        elif compliance_percentage >= 75.0:
            return "C"
        elif compliance_percentage >= 60.0:
            return "D"
        else:
            return "F"
    
    def _calculate_risk_level(self, compliance_percentage: float) -> str:
        """Calculate risk level based on compliance percentage."""
        if compliance_percentage >= 90.0:
            return "LOW"
        elif compliance_percentage >= 75.0:
            return "MEDIUM"
        elif compliance_percentage >= 50.0:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _get_status_color(self, compliance_percentage: float) -> str:
        """Get status color based on compliance percentage."""
        if compliance_percentage >= 90.0:
            return "#27ae60"  # Green
        elif compliance_percentage >= 75.0:
            return "#f39c12"  # Orange
        elif compliance_percentage >= 50.0:
            return "#e67e22"  # Dark orange
        else:
            return "#e74c3c"  # Red
    
    def _get_status_class(self, compliance_percentage: float) -> str:
        """Get CSS status class based on compliance percentage."""
        if compliance_percentage >= 95.0:
            return "excellent"
        elif compliance_percentage >= 80.0:
            return "good"
        elif compliance_percentage >= 60.0:
            return "fair"
        elif compliance_percentage >= 40.0:
            return "poor"
        else:
            return "critical"
    
    def _get_severity_badge(self, control_data: Dict[str, Any]) -> str:
        """Get severity badge class for control."""
        findings_count = len(control_data.get("non_compliant_findings", []))
        if findings_count > 10:
            return "high"
        elif findings_count > 3:
            return "medium"
        else:
            return "low"
    
    def _get_priority_badge(self, priority: str) -> str:
        """Get priority badge class."""
        return priority.lower()
    
    def _get_effort_badge(self, effort: str) -> str:
        """Get effort badge class."""
        effort_lower = effort.lower()
        if "low" in effort_lower or "minimal" in effort_lower:
            return "effort-minimal"
        elif "medium" in effort_lower or "moderate" in effort_lower:
            return "effort-moderate"
        elif "high" in effort_lower or "significant" in effort_lower:
            return "effort-significant"
        else:
            return "effort-extensive"
    
    def _get_ig_description(self, ig_name: str) -> str:
        """Get Implementation Group description."""
        descriptions = {
            "IG1": "Essential Cyber Hygiene",
            "IG2": "Enhanced Security",
            "IG3": "Advanced Security"
        }
        return descriptions.get(ig_name, "Unknown Implementation Group")
    
    def _prepare_findings_for_display(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare findings for HTML display."""
        display_findings = []
        for finding in findings:
            display_finding = finding.copy()
            # Truncate long resource IDs for display
            if len(display_finding["resource_id"]) > 50:
                display_finding["resource_id_display"] = display_finding["resource_id"][:47] + "..."
            else:
                display_finding["resource_id_display"] = display_finding["resource_id"]
            display_findings.append(display_finding)
        return display_findings
    
    def set_chart_options(self, include_charts: bool = True) -> None:
        """Configure chart inclusion options.
        
        Args:
            include_charts: Whether to include interactive charts
        """
        self.include_charts = include_charts
        logger.debug(f"Updated chart options: include_charts={include_charts}")
    
    def validate_html_output(self, html_content: str) -> bool:
        """Validate that the generated HTML is well-formed.
        
        Args:
            html_content: HTML content string to validate
            
        Returns:
            True if HTML appears valid, False otherwise
        """
        # Basic HTML validation checks
        required_elements = ['<!DOCTYPE html>', '<html', '<head>', '<body>', '</html>']
        
        for element in required_elements:
            if element not in html_content:
                logger.error(f"HTML validation failed: missing {element}")
                return False
        
        # Check for balanced tags (basic check)
        open_tags = html_content.count('<div')
        close_tags = html_content.count('</div>')
        
        if abs(open_tags - close_tags) > 5:  # Allow some tolerance
            logger.warning(f"HTML validation warning: unbalanced div tags ({open_tags} open, {close_tags} close)")
        
        logger.debug("HTML validation passed")
        return True
    
    def validate_assessment_data(self, assessment_result: AssessmentResult,
                               compliance_summary: ComplianceSummary) -> bool:
        """Validate input assessment data before report generation.
        
        Args:
            assessment_result: Assessment result to validate
            compliance_summary: Compliance summary to validate
            
        Returns:
            True if data is valid, False otherwise
        """
        if not assessment_result.account_id:
            logger.error("Assessment result missing account_id")
            return False
        
        if not assessment_result.regions_assessed:
            logger.error("Assessment result missing regions_assessed")
            return False
        
        # Allow empty IG scores for HTML reporter (can handle empty data)
        # if not assessment_result.ig_scores:
        #     logger.error("Assessment result missing ig_scores")
        #     return False
        
        # Validate compliance summary
        if compliance_summary.overall_compliance_percentage < 0 or compliance_summary.overall_compliance_percentage > 100:
            logger.error(f"Invalid overall compliance percentage: {compliance_summary.overall_compliance_percentage}")
            return False
        
        logger.debug("Assessment data validation passed")
        return True
    
    def validate_assessment_data(self, assessment_result: AssessmentResult,
                               compliance_summary: ComplianceSummary) -> bool:
        """Validate input assessment data before report generation.
        
        Args:
            assessment_result: Assessment result to validate
            compliance_summary: Compliance summary to validate
            
        Returns:
            True if data is valid, False otherwise
        """
        if not assessment_result.account_id:
            logger.error("Assessment result missing account_id")
            return False
        
        if not assessment_result.regions_assessed:
            logger.error("Assessment result missing regions_assessed")
            return False
        
        # Allow empty IG scores for HTML reporter (will show empty state)
        # if not assessment_result.ig_scores:
        #     logger.error("Assessment result missing ig_scores")
        #     return False
        
        # Validate compliance summary
        if compliance_summary.overall_compliance_percentage < 0 or compliance_summary.overall_compliance_percentage > 100:
            logger.error(f"Invalid overall compliance percentage: {compliance_summary.overall_compliance_percentage}")
            return False
        
        logger.debug("Assessment data validation passed")
        return True
    
    def extract_summary_data(self, html_content: str) -> Optional[Dict[str, Any]]:
        """Extract summary data from generated HTML report.
        
        Args:
            html_content: HTML report content
            
        Returns:
            Dictionary containing summary data or None if extraction fails
        """
        try:
            # Simple extraction using string parsing
            # In a production system, would use proper HTML parsing
            
            summary_data = {}
            
            # Extract account ID
            if 'AWS Account:' in html_content:
                start = html_content.find('AWS Account:') + len('AWS Account:')
                end = html_content.find('|', start)
                if end > start:
                    summary_data['account_id'] = html_content[start:end].strip()
            
            # Extract overall compliance
            if 'Overall Compliance:' in html_content:
                start = html_content.find('Overall Compliance:') + len('Overall Compliance:')
                end = html_content.find('%', start)
                if end > start:
                    try:
                        summary_data['overall_compliance'] = float(html_content[start:end].strip())
                    except ValueError:
                        pass
            
            return summary_data if summary_data else None
            
        except Exception as e:
            logger.error(f"Failed to extract summary data from HTML: {e}")
            return None
    def _get_unique_controls_per_ig(self, implementation_groups: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Get unique controls per Implementation Group to avoid duplication.
        
        Args:
            implementation_groups: Implementation groups data
            
        Returns:
            Dictionary mapping IG names to their unique controls
        """
        unique_controls = {}
        
        # IG1 controls are always unique to IG1
        if "IG1" in implementation_groups:
            unique_controls["IG1"] = implementation_groups["IG1"]["controls"]
        
        # IG2 unique controls (excluding IG1 controls)
        if "IG2" in implementation_groups:
            ig1_control_ids = set(implementation_groups.get("IG1", {}).get("controls", {}).keys())
            ig2_unique = {}
            for control_id, control_data in implementation_groups["IG2"]["controls"].items():
                if control_id not in ig1_control_ids:
                    ig2_unique[control_id] = control_data
            unique_controls["IG2"] = ig2_unique
        
        # IG3 unique controls (excluding IG1 and IG2 controls)
        if "IG3" in implementation_groups:
            ig1_control_ids = set(implementation_groups.get("IG1", {}).get("controls", {}).keys())
            ig2_control_ids = set(implementation_groups.get("IG2", {}).get("controls", {}).keys())
            ig3_unique = {}
            for control_id, control_data in implementation_groups["IG3"]["controls"].items():
                if control_id not in ig1_control_ids and control_id not in ig2_control_ids:
                    ig3_unique[control_id] = control_data
            unique_controls["IG3"] = ig3_unique
        
        return unique_controls
    
    def _get_ig_description_with_inheritance(self, ig_name: str) -> str:
        """Get IG description with inheritance information.
        
        Args:
            ig_name: Implementation Group name
            
        Returns:
            Description string with inheritance info
        """
        descriptions = {
            "IG1": "Essential Cyber Hygiene",
            "IG2": "Enhanced Security (includes IG1)",
            "IG3": "Advanced Security (includes IG1 + IG2)"
        }
        return descriptions.get(ig_name, "Unknown Implementation Group")
    
    def _get_ig_scope_description(self, ig_name: str, unique_controls_count: int) -> str:
        """Get scope description for an Implementation Group.
        
        Args:
            ig_name: Implementation Group name
            unique_controls_count: Number of unique controls in this IG
            
        Returns:
            Scope description string
        """
        if ig_name == "IG1":
            return f"Showing {unique_controls_count} foundational controls essential for all organizations."
        elif ig_name == "IG2":
            return f"Showing {unique_controls_count} additional controls beyond IG1 for enhanced security."
        elif ig_name == "IG3":
            return f"Showing {unique_controls_count} advanced controls beyond IG1 and IG2 for comprehensive security."
        else:
            return f"Showing {unique_controls_count} controls for this implementation group."
    def _generate_resource_details_section(self, html_data: Dict[str, Any]) -> str:
        """Generate comprehensive resource details section.
        
        Args:
            html_data: Enhanced HTML report data
            
        Returns:
            Resource details HTML as string
        """
        # Collect all resources from all IGs and controls
        all_resources = []
        resource_ids_seen = set()
        
        for ig_name, ig_data in html_data["implementation_groups"].items():
            for control_id, control_data in ig_data["controls"].items():
                # Add both compliant and non-compliant findings
                for finding in control_data.get("non_compliant_findings", []):
                    resource_key = f"{finding['resource_id']}_{finding['resource_type']}_{finding['region']}"
                    if resource_key not in resource_ids_seen:
                        all_resources.append({
                            "resource_id": finding["resource_id"],
                            "resource_type": finding["resource_type"],
                            "region": finding["region"],
                            "compliance_status": finding["compliance_status"],
                            "evaluation_reason": finding["evaluation_reason"],
                            "config_rule_name": finding["config_rule_name"],
                            "control_id": control_id,
                            "implementation_group": ig_name
                        })
                        resource_ids_seen.add(resource_key)
                
                # Add compliant findings (we need to get these from the detailed findings)
                for finding in control_data.get("compliant_findings", []):
                    resource_key = f"{finding['resource_id']}_{finding['resource_type']}_{finding['region']}"
                    if resource_key not in resource_ids_seen:
                        all_resources.append({
                            "resource_id": finding["resource_id"],
                            "resource_type": finding["resource_type"],
                            "region": finding["region"],
                            "compliance_status": finding["compliance_status"],
                            "evaluation_reason": finding.get("evaluation_reason", "Resource is compliant"),
                            "config_rule_name": finding["config_rule_name"],
                            "control_id": control_id,
                            "implementation_group": ig_name
                        })
                        resource_ids_seen.add(resource_key)
        
        # Sort resources by compliance status (non-compliant first), then by resource type
        all_resources.sort(key=lambda x: (x["compliance_status"] == "COMPLIANT", x["resource_type"], x["resource_id"]))
        
        # Generate resource table rows
        resource_rows = ""
        for resource in all_resources:
            status_class = "compliant" if resource["compliance_status"] == "COMPLIANT" else "non_compliant"
            status_icon = "✓" if resource["compliance_status"] == "COMPLIANT" else "✗"
            
            resource_rows += f"""
            <tr class="resource-row {status_class}">
                <td><code>{resource['resource_id']}</code></td>
                <td>{resource['resource_type']}</td>
                <td>{resource['region']}</td>
                <td>
                    <span class="badge {status_class}">
                        {status_icon} {resource['compliance_status']}
                    </span>
                </td>
                <td>{resource['control_id']}</td>
                <td>{resource['config_rule_name']}</td>
                <td class="evaluation-reason">{resource['evaluation_reason']}</td>
            </tr>
            """
        
        # Calculate summary statistics
        total_resources = len(all_resources)
        compliant_resources = len([r for r in all_resources if r["compliance_status"] == "COMPLIANT"])
        non_compliant_resources = total_resources - compliant_resources
        compliance_percentage = (compliant_resources / total_resources * 100) if total_resources > 0 else 0
        
        # Generate resource type breakdown
        resource_type_stats = {}
        for resource in all_resources:
            resource_type = resource["resource_type"]
            if resource_type not in resource_type_stats:
                resource_type_stats[resource_type] = {"total": 0, "compliant": 0}
            resource_type_stats[resource_type]["total"] += 1
            if resource["compliance_status"] == "COMPLIANT":
                resource_type_stats[resource_type]["compliant"] += 1
        
        resource_type_breakdown = ""
        for resource_type, stats in sorted(resource_type_stats.items()):
            type_compliance = (stats["compliant"] / stats["total"] * 100) if stats["total"] > 0 else 0
            status_class = self._get_status_class(type_compliance)
            
            resource_type_breakdown += f"""
            <div class="resource-type-stat">
                <div class="resource-type-header">
                    <span class="resource-type-name">{resource_type}</span>
                    <span class="resource-type-count">{stats['compliant']}/{stats['total']}</span>
                </div>
                <div class="progress-container">
                    <div class="progress-bar {status_class}" data-width="{type_compliance}">
                        <span class="progress-text">{type_compliance:.1f}%</span>
                    </div>
                </div>
            </div>
            """
        
        return f"""
        <section id="resource-details" class="resource-details">
            <h2>Resource Details</h2>
            
            <div class="resource-summary">
                <div class="resource-stats-grid">
                    <div class="resource-stat-card">
                        <div class="stat-value">{total_resources}</div>
                        <div class="stat-label">Total Resources</div>
                    </div>
                    <div class="resource-stat-card compliant">
                        <div class="stat-value">{compliant_resources}</div>
                        <div class="stat-label">Compliant</div>
                    </div>
                    <div class="resource-stat-card non-compliant">
                        <div class="stat-value">{non_compliant_resources}</div>
                        <div class="stat-label">Non-Compliant</div>
                    </div>
                    <div class="resource-stat-card">
                        <div class="stat-value">{compliance_percentage:.1f}%</div>
                        <div class="stat-label">Compliance Rate</div>
                    </div>
                </div>
            </div>
            
            <div class="resource-type-breakdown">
                <h3>Compliance by Resource Type</h3>
                <div class="resource-type-grid">
                    {resource_type_breakdown}
                </div>
            </div>
            
            <div class="resource-table-container">
                <div class="resource-filters">
                    <input type="text" id="resourceSearch" placeholder="Search resources..." onkeyup="filterResources()" class="search-input">
                    <select id="statusFilter" onchange="filterResources()" class="filter-select">
                        <option value="">All Status</option>
                        <option value="COMPLIANT">Compliant Only</option>
                        <option value="NON_COMPLIANT">Non-Compliant Only</option>
                    </select>
                    <select id="typeFilter" onchange="filterResources()" class="filter-select">
                        <option value="">All Types</option>
                        {self._generate_resource_type_options(resource_type_stats)}
                    </select>
                </div>
                
                <table class="findings-table resource-table" id="resourceTable">
                    <thead>
                        <tr>
                            <th onclick="sortResourceTable(0)">Resource ID ↕</th>
                            <th onclick="sortResourceTable(1)">Resource Type ↕</th>
                            <th onclick="sortResourceTable(2)">Region ↕</th>
                            <th onclick="sortResourceTable(3)">Status ↕</th>
                            <th onclick="sortResourceTable(4)">Control ↕</th>
                            <th onclick="sortResourceTable(5)">Config Rule ↕</th>
                            <th>Evaluation Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        {resource_rows}
                    </tbody>
                </table>
            </div>
            
            <div class="resource-export">
                <button onclick="exportResourcesToCSV()" class="export-btn">Export to CSV</button>
                <button onclick="exportResourcesToJSON()" class="export-btn">Export to JSON</button>
            </div>
        </section>
        """
    
    def _generate_resource_type_options(self, resource_type_stats: Dict[str, Dict[str, int]]) -> str:
        """Generate option elements for resource type filter.
        
        Args:
            resource_type_stats: Resource type statistics
            
        Returns:
            HTML option elements
        """
        options = ""
        for resource_type in sorted(resource_type_stats.keys()):
            options += f'<option value="{resource_type}">{resource_type}</option>'
        return options