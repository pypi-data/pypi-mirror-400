"""
PDF Export and Citation Generation

Generates publication-ready PDF reports and citation text for papers.
"""

from datetime import datetime
from typing import Optional, Dict, Any
import io
from pathlib import Path

def generate_citation(format: str = "apa") -> str:
    """
    Generate citation text for NeuroOps.
    
    Args:
        format: Citation format ('apa', 'bibtex', 'plain')
        
    Returns:
        Citation string
    """
    year = datetime.now().year
    version = "0.3.0"
    
    if format == "apa":
        return (
            f"Moscheni, A. ({year}). NeuroOps: A visual diff tool for neuroscience "
            f"data quality control (Version {version}) [Computer software]. "
            f"https://github.com/arthurmoscheni/NeuroGit"
        )
    
    elif format == "bibtex":
        return f"""@software{{moscheni{year}neuroops,
  author = {{Moscheni, Arthur}},
  title = {{NeuroOps: A Visual Diff Tool for Neuroscience Data Quality Control}},
  year = {{{year}}},
  version = {{{version}}},
  url = {{https://github.com/arthurmoscheni/NeuroGit}}
}}"""
    
    elif format == "plain":
        return f"NeuroOps v{version} (Moscheni, {year})"
    
    else:
        raise ValueError(f"Unknown citation format: {format}")

def generate_methods_section(
    data_type: str,
    preprocessing_steps: Optional[list] = None,
    custom_text: Optional[str] = None
) -> str:
    """
    Generate methods section text for papers.
    
    Args:
        data_type: 'EEG' or 'MRI'
        preprocessing_steps: List of preprocessing steps applied
        custom_text: Optional custom text to append
        
    Returns:
        Methods section paragraph
    """
    year = datetime.now().year
    
    base_text = (
        f"Data quality was assessed using NeuroOps v0.3.0 (Moscheni, {year}), "
        f"an open-source visual diff tool for neuroscience data. "
    )
    
    if data_type == "EEG":
        base_text += (
            "Raw and preprocessed EEG signals were compared in both time and "
            "frequency domains to verify artifact removal while preserving "
            "neural activity. "
        )
    elif data_type == "MRI":
        base_text += (
            "Raw and preprocessed MRI volumes were compared slice-by-slice "
            "to verify preprocessing steps (e.g., skull stripping, smoothing) "
            "without introducing artifacts. "
        )
    
    if preprocessing_steps:
        steps_text = ", ".join(preprocessing_steps)
        base_text += f"Preprocessing steps included: {steps_text}. "
    
    base_text += (
        "Visual inspection of the difference maps confirmed that preprocessing "
        "removed artifacts without distorting the underlying signal."
    )
    
    if custom_text:
        base_text += f" {custom_text}"
    
    return base_text

def export_to_pdf(
    figure,
    output_path: str,
    title: str,
    metadata: Dict[str, Any],
    notes: Optional[str] = None
) -> str:
    """
    Export current view to PDF report.
    
    Args:
        figure: Matplotlib figure object
        output_path: Path to save PDF
        title: Report title
        metadata: Dictionary with file info, parameters, etc.
        notes: Optional notes/findings
        
    Returns:
        Path to saved PDF
    """
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.units import inch
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
        from reportlab.lib import colors
    except ImportError:
        raise ImportError(
            "reportlab is required for PDF export. "
            "Install with: pip install reportlab"
        )
    
    # Create PDF
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Container for PDF elements
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Metadata section
    story.append(Paragraph("Report Metadata", styles['Heading2']))
    
    metadata_data = [
        ['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        ['Tool', 'NeuroOps v0.3.0'],
    ]
    
    for key, value in metadata.items():
        if isinstance(value, (str, int, float)):
            metadata_data.append([str(key).replace('_', ' ').title(), str(value)])
    
    metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    story.append(metadata_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Visualization
    story.append(Paragraph("Quality Control Visualization", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
    # Save matplotlib figure to buffer
    img_buffer = io.BytesIO()
    figure.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    
    # Add image to PDF
    img = Image(img_buffer, width=6.5*inch, height=4*inch)
    story.append(img)
    story.append(Spacer(1, 0.3*inch))
    
    # Notes section
    if notes:
        story.append(Paragraph("Findings & Notes", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        notes_para = Paragraph(notes.replace('\n', '<br/>'), styles['BodyText'])
        story.append(notes_para)
        story.append(Spacer(1, 0.2*inch))
    
    # Citation
    story.append(Paragraph("Citation", styles['Heading2']))
    citation_text = generate_citation('apa')
    story.append(Paragraph(citation_text, styles['BodyText']))
    
    # Build PDF
    doc.build(story)
    
    return output_path

def export_to_html(
    figure,
    output_path: str,
    title: str,
    metadata: Dict[str, Any],
    notes: Optional[str] = None,
    interactive: bool = False
) -> str:
    """
    Export to standalone HTML report (alternative to PDF).
    
    Args:
        figure: Matplotlib or Plotly figure
        output_path: Path to save HTML
        title: Report title
        metadata: Dictionary with file info
        notes: Optional notes
        interactive: If True, embed interactive Plotly chart
        
    Returns:
        Path to saved HTML
    """
    import base64
    
    # Convert figure to base64
    if hasattr(figure, 'to_html'):
        # Plotly figure
        plot_html = figure.to_html(include_plotlyjs='cdn', full_html=False)
    else:
        # Matplotlib figure
        img_buffer = io.BytesIO()
        figure.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.read()).decode()
        plot_html = f'<img src="data:image/png;base64,{img_base64}" style="max-width: 100%;">'
    
    # Build HTML
    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1000px;
            margin: 40px auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        .metadata {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .metadata-item {{
            margin: 5px 0;
        }}
        .metadata-key {{
            font-weight: bold;
            display: inline-block;
            width: 150px;
        }}
        .notes {{
            background: #fff9e6;
            border-left: 4px solid #f39c12;
            padding: 15px;
            margin: 20px 0;
        }}
        .citation {{
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 15px;
            margin: 20px 0;
            font-style: italic;
        }}
        @media print {{
            body {{ background: white; }}
            .container {{ box-shadow: none; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        
        <h2>Report Metadata</h2>
        <div class="metadata">
            <div class="metadata-item">
                <span class="metadata-key">Generated:</span>
                {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
            <div class="metadata-item">
                <span class="metadata-key">Tool:</span>
                NeuroOps v0.3.0
            </div>
"""
    
    for key, value in metadata.items():
        if isinstance(value, (str, int, float)):
            html_template += f"""
            <div class="metadata-item">
                <span class="metadata-key">{str(key).replace('_', ' ').title()}:</span>
                {value}
            </div>
"""
    
    html_template += """
        </div>
        
        <h2>Quality Control Visualization</h2>
"""
    
    html_template += plot_html
    
    if notes:
        html_template += f"""
        <h2>Findings & Notes</h2>
        <div class="notes">
            {notes.replace(chr(10), '<br>')}
        </div>
"""
    
    citation = generate_citation('apa')
    html_template += f"""
        <h2>Citation</h2>
        <div class="citation">
            {citation}
        </div>
    </div>
</body>
</html>
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    return output_path
