"""
HTML Report Generator

This module creates an HTML dashboard from drift analysis results.
"""

import os
import base64
from datetime import datetime
from typing import Dict
import pandas as pd


def generate_html_report(
    results: Dict[str, pd.DataFrame],
    save_dir: str = './reports',
    report_name: str = 'drift_report.html',
    title: str = 'Drift Analysis Report',
    ai_advice: str = None
) -> str:
    """
    Creates an HTML dashboard containing all charts.
    
    Parameters:
    -----------
    results : Dict[str, pd.DataFrame]
        Output of DriftAnalyzer.full_analysis()
    save_dir : str
        Directory to save charts and HTML
    report_name : str
        HTML file name
    title : str
        Report title
    
    Returns:
    --------
    str: Path to the created HTML file
    """
    os.makedirs(save_dir, exist_ok=True)
    
    # Statistical test descriptions
    test_descriptions = {
        'Kolmogorov-Smirnov': {
            'short': 'Tests if two distributions are the same',
            'long': '''The Kolmogorov-Smirnov (KS) test is a non-parametric test that checks if 
            two samples come from the same distribution. It measures the maximum distance 
            between the cumulative distribution functions (CDF).
            If p < α, the two distributions are statistically different and drift is detected.'''
        },
        'Mann-Whitney U': {
            'short': 'Compares medians of two groups',
            'long': '''The Mann-Whitney U test (Wilcoxon rank-sum test) tests if the medians of 
            two independent samples are equal. It does not require a normal distribution assumption.
            If p < α, the central tendencies of the two groups are different (location shift).'''
        },
        'Levene (Variance)': {
            'short': 'Tests for homogeneity of variances',
            'long': '''Levene's test checks if the variances of two or more groups are equal. 
            It is robust against departures from normality.
            If p < α, the variances of the groups are different (variance shift).'''
        },
        'Chi-Square': {
            'short': 'Compares distributions of categorical variables',
            'long': '''The Chi-Square test checks if the observed frequencies differ significantly 
            from the expected frequencies. Used for categorical variables.
            If p < α, the category distributions are different.'''
        },
        'Fisher Z-Test (Correlation)': {
            'short': 'Compares two correlation coefficients',
            'long': '''Tests if two Pearson correlation coefficients are statistically different 
            using Fisher Z-transformation. Measures the change in feature-target relationship.
            If p < α, the correlations are significantly different (concept drift).'''
        },
        "Cramer's V": {
            'short': 'Measures relationship strength for categorical variables',
            'long': '''Cramer's V measures the strength of association between two categorical 
            variables between 0 and 1. Derived from the chi-square statistic. 
            If the difference in V between Train and Score > 0.1, concept drift is accepted.'''
        }
    }
    
    # Convert image files to base64
    def img_to_base64(img_path):
        if os.path.exists(img_path):
            with open(img_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        return None
    
    # Create summary table
    summary_rows = []
    if 'data_drift' in results:
        df = results['data_drift']
        drift_count = df['Drift Detected'].sum()
        total_tests = len(df)
        summary_rows.append({
            'Analysis': 'Data Drift',
            'Total Tests': total_tests,
            'Drift Detected': drift_count,
            'Drift Rate': f"{drift_count/total_tests*100:.1f}%"
        })
    
    if 'temporal_drift' in results:
        df = results['temporal_drift']
        drift_count = df['Drift_Detected'].sum()
        total_tests = len(df)
        summary_rows.append({
            'Analysis': 'Temporal Drift',
            'Total Tests': total_tests,
            'Drift Detected': drift_count,
            'Drift Rate': f"{drift_count/total_tests*100:.1f}%"
        })
    
    if 'concept_drift' in results:
        df = results['concept_drift']
        drift_count = df['Drift_Detected'].sum()
        total_tests = len(df)
        summary_rows.append({
            'Analysis': 'Concept Drift',
            'Total Tests': total_tests,
            'Drift Detected': drift_count,
            'Drift Rate': f"{drift_count/total_tests*100:.1f}%"
        })
    
    summary_df = pd.DataFrame(summary_rows)
    summary_html = summary_df.to_html(index=False, classes='summary-table') if len(summary_rows) > 0 else ""
    
    # 🚨 Alarm Summary (Variable-based)
    alarm_counts = {}
    if 'data_drift' in results:
        df = results['data_drift']
        drifted = df[df['Drift Detected'] == True]
        for col in drifted['Column'].unique():
            count = drifted[drifted['Column'] == col].shape[0]
            alarm_counts[col] = alarm_counts.get(col, 0) + count
    if 'temporal_drift' in results:
        df = results['temporal_drift']
        drifted = df[df['Drift_Detected'] == True]
        for col in drifted['Column'].unique():
            count = drifted[drifted['Column'] == col].shape[0]
            alarm_counts[col] = alarm_counts.get(col, 0) + count
    if 'concept_drift' in results:
        df = results['concept_drift']
        drifted = df[df['Drift_Detected'] == True]
        for feat in drifted['Feature'].unique():
            count = drifted[drifted['Feature'] == feat].shape[0]
            alarm_counts[feat] = alarm_counts.get(feat, 0) + count

    alarm_html = ""
    if alarm_counts:
        alarm_df = pd.DataFrame([{'Variable': k, 'Total Alarms': v} for k, v in alarm_counts.items()])
        alarm_df = alarm_df.sort_values('Total Alarms', ascending=False)
        alarm_html = f'''
        <div class="alarm-summary">
            <h3>🚨 Variable Alarm Summary</h3>
            {alarm_df.to_html(index=False, classes='detail-table alarm-table')}
        </div>'''

    # Tooltip helper function
    def add_tooltip(test_name):
        if test_name in test_descriptions:
            desc = test_descriptions[test_name]
            return f'''<span class="tooltip-wrapper">
                {test_name} 
                <span class="info-icon">ℹ️</span>
                <span class="tooltip-text">{desc['short']}</span>
            </span>'''
        return test_name
    
    # P-value format function
    def format_pvalue(pval, threshold=0.05):
        if pd.isna(pval):
            return '<span class="pval">N/A</span>'
        
        # If drift exists (p < threshold) -> Red
        if pval < threshold:
            if pval < 0.001:
                return f'<span class="pval pval-drift">{pval:.2e}</span>'
            else:
                return f'<span class="pval pval-drift">{pval:.4f}</span>'
        # If no drift (p >= threshold) -> Green
        else:
            return f'<span class="pval pval-pass">{pval:.4f}</span>'
    
    # Data drift details - build table with tooltips
    data_drift_html = ""
    if 'data_drift' in results:
        drifted = results['data_drift'][results['data_drift']['Drift Detected'] == True]
        if len(drifted) > 0:
            # Build HTML table manually (for tooltips)
            data_drift_html = '''<table class="detail-table">
                <thead><tr><th>Column</th><th>Test</th><th>P-Value</th></tr></thead>
                <tbody>'''
            for _, row in drifted.iterrows():
                test_with_tooltip = add_tooltip(row['Test'])
                pval_formatted = format_pvalue(row['P-Value'])
                data_drift_html += f'''<tr>
                    <td>{row['Column']}</td>
                    <td>{test_with_tooltip}</td>
                    <td>{pval_formatted}</td>
                </tr>'''
            data_drift_html += '</tbody></table>'
        else:
            data_drift_html = "<p class='success'>✅ No data drift detected!</p>"
    
    # Concept drift details - table with tooltips
    concept_drift_html = ""
    if 'concept_drift' in results:
        drifted = results['concept_drift'][results['concept_drift']['Drift_Detected'] == True]
        if len(drifted) > 0:
            has_score = 'Score_Metric' in drifted.columns
            score_header = '<th>Score_Metric</th>' if has_score else ''
            concept_drift_html = f'''<table class="detail-table">
                <thead><tr><th>Feature</th><th>Method</th><th>Train_Metric</th>{score_header}<th>P_Value</th></tr></thead>
                <tbody>'''
            for _, row in drifted.iterrows():
                method_with_tooltip = add_tooltip(row['Method'])
                score_val = f"<td>{row['Score_Metric']:.4f}</td>" if has_score else ''
                pval_formatted = format_pvalue(row.get('P_Value'))
                concept_drift_html += f'''<tr>
                    <td>{row['Feature']}</td>
                    <td>{method_with_tooltip}</td>
                    <td>{row['Train_Metric']:.4f}</td>
                    {score_val}
                    <td>{pval_formatted}</td>
                </tr>'''
            concept_drift_html += '</tbody></table>'
        else:
            concept_drift_html = "<p class='success'>✅ No concept drift detected!</p>"
    
    # First drift points - table with tooltips
    first_drift_html = ""
    if 'first_drift_points' in results:
        df = results['first_drift_points']
        first_drift_html = '''<table class="detail-table">
            <thead><tr><th>Column</th><th>Window_Start</th><th>Test</th><th>Statistic</th><th>P-Value</th></tr></thead>
            <tbody>'''
        for _, row in df.iterrows():
            test_with_tooltip = add_tooltip(row['Test'])
            pval_formatted = format_pvalue(row['P-Value'])
            first_drift_html += f'''<tr>
                <td>{row['Column']}</td>
                <td>{row['Window_Start']}</td>
                <td>{test_with_tooltip}</td>
                <td>{row['Statistic']:.4f}</td>
                <td>{pval_formatted}</td>
            </tr>'''
        first_drift_html += '</tbody></table>'
    
    # Methodology section HTML
    methodology_html = '''
    <div class="methodology-cards">
    '''
    for test_name, desc in test_descriptions.items():
        methodology_html += f'''
        <div class="method-card">
            <h4>{test_name}</h4>
            <p>{desc['long']}</p>
        </div>
        '''
    methodology_html += '</div>'
    
    # Chart list
    charts = {
        'Performance Impact Analysis': 'performance_impact.png',
        'Data Drift Dashboard': 'dashboard_data_drift.png',
        'Concept Drift Dashboard': 'dashboard_concept_drift.png',
        'Data Drift Heatmap': 'data_drift_heatmap.png',
        'P-Value Distribution': 'data_drift_pvalues.png',
        'Temporal Drift (Line)': 'temporal_drift_line.png',
        'Temporal Drift (Heatmap)': 'temporal_drift_heatmap.png',
        'Correlation Comparison': 'concept_correlation_comparison.png',
        'Relationship Change': 'concept_relationship_change.png',
        'Concept P-Value': 'concept_pvalue.png'
    }
    
    # Add charts to HTML
    charts_html = ""
    modals_html = ""  # Collecting modals separately (Z-index/Stacking context issue)
    
    chart_id = 0
    for chart_title, filename in charts.items():
        img_path = os.path.join(save_dir, filename)
        if os.path.exists(img_path):
            img_base64 = img_to_base64(img_path)
            
            # Chart Card
            charts_html += f'''
            <div class="chart-container" draggable="true" onclick="openModal('modal-{chart_id}')">
                <h3>{chart_title}</h3>
                <img src="data:image/png;base64,{img_base64}" alt="{chart_title}">
                <p class="click-hint">🔍 Click to enlarge | ✥ Drag to reorder</p>
            </div>
            '''
            
            # Modal (Body'nin sonuna eklenecek)
            modals_html += f'''
            <div id="modal-{chart_id}" class="modal" onclick="closeModal('modal-{chart_id}')">
                <span class="modal-close">&times;</span>
                <div class="modal-content">
                    <h3>{chart_title}</h3>
                    <img src="data:image/png;base64,{img_base64}" alt="{chart_title}">
                </div>
            </div>
            '''
            chart_id += 1
    
    # HTML template
    html_template = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            padding: 30px;
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }}
        
        h1 {{
            font-size: 2.5rem;
            background: linear-gradient(90deg, #00d4ff, #7b2cbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        
        .timestamp {{
            color: #888;
            font-size: 0.9rem;
        }}
        
        .section {{
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            backdrop-filter: blur(10px);
        }}
        
        h2 {{
            color: #00d4ff;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(0,212,255,0.3);
        }}
        
        h3 {{
            color: #fff;
            margin-bottom: 15px;
            font-size: 1.1rem;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        
        th {{
            background: rgba(0,212,255,0.2);
            color: #00d4ff;
            font-weight: 600;
        }}
        
        tr:hover {{
            background: rgba(255,255,255,0.05);
        }}
        
        .success {{
            color: #2ecc71;
            padding: 15px;
            background: rgba(46,204,113,0.1);
            border-radius: 8px;
        }}
        
        .alarm-summary {{
            margin-top: 30px;
            padding: 20px;
            background: rgba(231, 76, 60, 0.1);
            border-radius: 12px;
            border: 1px solid rgba(231, 76, 60, 0.3);
        }}
        
        .alarm-table th {{
            background: rgba(231, 76, 60, 0.2);
            color: #e74c3c;
        }}
        
        .alarm-table td:last-child {{
            font-weight: bold;
            color: #e74c3c;
            text-align: center;
        }}
        
        /* P-Value Styles */
        .pval {{
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9rem;
            padding: 4px 8px;
            border-radius: 4px;
            background: rgba(255,255,255,0.05);
        }}
        
        .pval-drift {{
            background: rgba(231, 76, 60, 0.2);
            color: #e74c3c;
            font-weight: 600;
        }}
        
        .pval-pass {{
            background: rgba(46, 204, 113, 0.2);
            color: #2ecc71;
            font-weight: 600;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 25px;
        }}
        
        .chart-container {{
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            padding: 20px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: grab;
            user-select: none;
        }}
        
        .chart-container:active {{
            cursor: grabbing;
        }}
        
        .chart-container.dragging {{
            opacity: 0.5;
            transform: scale(1.02);
        }}
        
        .chart-container.drag-over {{
            border: 2px dashed #00d4ff;
            background: rgba(0,212,255,0.1);
        }}
        
        .chart-container:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        
        .chart-container img {{
            width: 100%;
            height: auto;
            border-radius: 8px;
        }}
        
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }}
        
        .card {{
            background: linear-gradient(135deg, rgba(0,212,255,0.1), rgba(123,44,191,0.1));
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }}
        
        .card-value {{
            font-size: 2rem;
            font-weight: bold;
            color: #00d4ff;
        }}
        
        .card-label {{
            color: #888;
            margin-top: 5px;
        }}
        
        footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.85rem;
        }}
        
        /* Navigation */
        .nav {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0,0,0,0.5);
            padding: 15px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            z-index: 999;
        }}
        
        .nav a {{
            display: block;
            color: #00d4ff;
            text-decoration: none;
            padding: 8px 0;
            font-size: 0.9rem;
        }}
        
        .nav a:hover {{
            color: #fff;
        }}
        
        /* Tooltip Styles */
        .tooltip-wrapper {{
            position: relative;
            display: inline-block;
        }}
        
        .info-icon {{
            cursor: help;
            font-size: 0.9em;
            opacity: 0.7;
            transition: opacity 0.2s;
        }}
        
        .info-icon:hover {{
            opacity: 1;
        }}
        
        .tooltip-text {{
            visibility: hidden;
            width: 280px;
            background: linear-gradient(135deg, #2d3436, #1e272e);
            color: #fff;
            text-align: left;
            padding: 12px 15px;
            border-radius: 8px;
            position: absolute;
            z-index: 100;
            bottom: 125%;
            left: 50%;
            margin-left: -140px;
            opacity: 0;
            transition: opacity 0.3s, visibility 0.3s;
            font-size: 0.85rem;
            line-height: 1.4;
            box-shadow: 0 5px 20px rgba(0,0,0,0.4);
            border: 1px solid rgba(0,212,255,0.3);
        }}
        
        .tooltip-text::after {{
            content: "";
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -8px;
            border-width: 8px;
            border-style: solid;
            border-color: #2d3436 transparent transparent transparent;
        }}
        
        .tooltip-wrapper:hover .tooltip-text {{
            visibility: visible;
            opacity: 1;
        }}
        
        /* Methodology Cards */
        .methodology-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }}
        
        .method-card {{
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            padding: 20px;
            border-left: 4px solid #00d4ff;
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        .method-card:hover {{
            transform: translateX(5px);
            box-shadow: 0 5px 20px rgba(0,212,255,0.2);
        }}
        
        .method-card h4 {{
            color: #00d4ff;
            margin-bottom: 10px;
            font-size: 1.1rem;
        }}
        
        .method-card p {{
            color: #bbb;
            font-size: 0.9rem;
            line-height: 1.6;
        }}
        
        /* Modal Styles */
        .modal {{
            display: none;
            position: fixed;
            z-index: 10000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.95);
            /* Centering Setup */
            align-items: center;
            justify-content: center;
            animation: fadeIn 0.3s ease;
            backdrop-filter: none; /* Prevent stacking issues */
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        .modal-content {{
            /* Removed margin: 2% auto */
            padding: 20px;
            max-width: 95%;
            max-height: 95vh;
            text-align: center;
            position: relative;
        }}
        
        .modal-content img {{
            max-width: 100%;
            max-height: 90vh; /* Increased from 85vh */
            border-radius: 10px;
            box-shadow: 0 5px 30px rgba(0,212,255,0.3);
        }}
        
        .modal-content h3 {{
            color: #00d4ff;
            margin-bottom: 20px;
            font-size: 1.5rem;
        }}
        
        .modal-close {{
            position: fixed;
            top: 20px;
            right: 35px;
            color: #fff;
            font-size: 50px;
            font-weight: bold;
            cursor: pointer;
            z-index: 10001;
            transition: color 0.3s;
        }}
        
        .modal-close:hover {{
            color: #e74c3c;
        }}
        
        .chart-container {{
            cursor: pointer;
        }}
        
        .click-hint {{
            color: #888;
            font-size: 0.8rem;
            margin-top: 10px;
            text-align: center;
            opacity: 0.7;
        }}
        
        .chart-container:hover .click-hint {{
            opacity: 1;
            color: #00d4ff;
        }}

        /* AI Advisor Section */
        .ai-advice-content {{
            background: rgba(123, 44, 191, 0.05);
            border-left: 4px solid #7b2cbf;
            padding: 20px;
            border-radius: 0 12px 12px 0;
            white-space: pre-wrap;
            line-height: 1.6;
            font-size: 0.95rem;
            color: #ddd;
        }}

        .ai-badge {{
            display: inline-block;
            background: linear-gradient(90deg, #7b2cbf, #00d4ff);
            color: white;
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 0.7rem;
            font-weight: bold;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
    </style>
    <script>
        function openModal(modalId) {{
            // Use flex to display and center
            document.getElementById(modalId).style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }}
        
        function closeModal(modalId) {{
            document.getElementById(modalId).style.display = 'none';
            document.body.style.overflow = 'auto';
        }}
        
        // Closing with ESC key
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                var modals = document.querySelectorAll('.modal');
                modals.forEach(function(modal) {{
                    modal.style.display = 'none';
                }});
                document.body.style.overflow = 'auto';
            }}
        }});

        // Drag and Drop Logic
        document.addEventListener('DOMContentLoaded', () => {{
            const grid = document.querySelector('.charts-grid');
            let dragSrcEl = null;

            function handleDragStart(e) {{
                this.classList.add('dragging');
                dragSrcEl = this;
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/html', this.innerHTML);
            }}

            function handleDragOver(e) {{
                if (e.preventDefault) {{
                    e.preventDefault();
                }}
                e.dataTransfer.dropEffect = 'move';
                return false;
            }}

            function handleDragEnter(e) {{
                this.classList.add('drag-over');
            }}

            function handleDragLeave(e) {{
                this.classList.remove('drag-over');
            }}

            function handleDrop(e) {{
                if (e.stopPropagation) {{
                    e.stopPropagation();
                }}

                if (dragSrcEl !== this) {{
                    // Swap content
                    // Note: Since we moved modals outside, we only swap the visible content
                    // and the onclick attribute which refers to the modal ID.
                    
                    const targetHTML = this.innerHTML;
                    const targetOnClick = this.getAttribute('onclick');
                    
                    this.innerHTML = dragSrcEl.innerHTML;
                    this.setAttribute('onclick', dragSrcEl.getAttribute('onclick'));
                    
                    dragSrcEl.innerHTML = targetHTML;
                    dragSrcEl.setAttribute('onclick', targetOnClick);
                }}

                return false;
            }}

            function handleDragEnd(e) {{
                this.classList.remove('dragging');
                items.forEach(function (item) {{
                    item.classList.remove('drag-over');
                }});
            }}

            let items = document.querySelectorAll('.charts-grid .chart-container');
            items.forEach(function(item) {{
                item.addEventListener('dragstart', handleDragStart, false);
                item.addEventListener('dragenter', handleDragEnter, false);
                item.addEventListener('dragover', handleDragOver, false);
                item.addEventListener('dragleave', handleDragLeave, false);
                item.addEventListener('drop', handleDrop, false);
                item.addEventListener('dragend', handleDragEnd, false);
            }});
        }});
    </script>
</head>
<body>
    <nav class="nav">
        <a href="#summary">📋 Summary</a>
        <a href="#data-drift">🔍 Data Drift</a>
        <a href="#temporal">⏰ Temporal</a>
        <a href="#concept-drift">🎯 Concept Drift</a>
        {f'<a href="#ai-advisor">🧠 AI Advisor</a>' if ai_advice else ''}
        <a href="#charts">📈 Charts</a>
        <a href="#methodology">📚 Methodology</a>
    </nav>

    <div class="container">
        <header>
            <h1>📊 {title}</h1>
            <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </header>
        
        <section class="section" id="summary">
            <h2>📋 Summary</h2>
            {summary_html}
            {alarm_html}
        </section>
        
        <section class="section" id="data-drift">
            <h2>🔍 Data Drift Details</h2>
            {data_drift_html if data_drift_html else "<p>No data drift analysis performed.</p>"}
        </section>
        
        <section class="section" id="temporal">
            <h2>⏰ First Drift Points</h2>
            {first_drift_html if first_drift_html else "<p>No temporal analysis performed.</p>"}
        </section>
        
        <section class="section" id="concept-drift">
            <h2>🎯 Concept Drift Details</h2>
            {concept_drift_html if concept_drift_html else "<p>No concept drift analysis performed.</p>"}
        </section>

        {f'''
        <section class="section" id="ai-advisor">
            <h2>🧠 AI Recommendations</h2>
            <div class="ai-badge">AI Generated Insight</div>
            <div class="ai-advice-content">{ai_advice}</div>
        </section>
        ''' if ai_advice else ''}
        
        <section class="section" id="charts">
            <h2>📈 Charts</h2>
            <div class="charts-grid">
                {charts_html}
            </div>
        </section>
        
        <section class="section" id="methodology">
            <h3>📚 Methodology & Explanations</h3>
            <p style="color: #888; margin-bottom: 20px;">Explanations of the statistical tests used in this report:</p>
            {methodology_html}
        </div>

        <footer>
            <div class="card-label">Generated with <b>DriftImpact</b> • {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        </footer>
    </div>
    
    <!-- Modals are placed here to avoid stacking context issues -->
    {modals_html}
</body>
</html>
    '''
    
    # Save HTML file
    html_path = os.path.join(save_dir, report_name)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"🌐 HTML Dashboard created: {html_path}")
    return html_path
