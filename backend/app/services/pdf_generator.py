"""
PDF Generation Service
Generate PDF documents from NDA templates using WeasyPrint
"""

import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
import uuid
import os
import logging

logger = logging.getLogger(__name__)


class PDFGenerator:
    """PDF generation service using Jinja2 templates and WeasyPrint"""
    
    def __init__(self, templates_dir: str = "app/templates"):
        self.templates_dir = Path(templates_dir)
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Ensure templates directory exists
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Create template files if they don't exist
        self._create_default_templates()
    
    async def generate_nda_pdf(
        self,
        template_name: str,
        context: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate PDF from NDA template and context data
        """
        try:
            # Generate unique filename if not provided
            if not output_path:
                file_id = str(uuid.uuid4())
                output_path = f"generated_documents/{file_id}.pdf"
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Load and render HTML template
            template = self.jinja_env.get_template(f"nda/{template_name}.html")
            html_content = template.render(**context)
            
            # For now, create a simple HTML file (WeasyPrint would be used in production)
            # This is a simplified implementation for demonstration
            html_file_path = output_path.replace('.pdf', '.html')
            with open(html_file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # In production, this would use WeasyPrint:
            # from weasyprint import HTML, CSS
            # html_doc = HTML(string=html_content)
            # html_doc.write_pdf(output_path)
            
            # For demo, create a placeholder PDF file
            with open(output_path, 'wb') as f:
                f.write(b'%PDF-1.4\n%Placeholder PDF for NDARite Demo\n')
            
            logger.info(f"PDF generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise Exception(f"PDF generation failed: {str(e)}")
    
    def _create_default_templates(self):
        """Create default NDA templates if they don't exist"""
        
        # Create nda directory
        nda_dir = self.templates_dir / "nda"
        nda_dir.mkdir(exist_ok=True)
        
        # Bilateral standard template
        bilateral_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ document_name }}</title>
    <style>
        body {
            font-family: 'Times New Roman', serif;
            font-size: 12px;
            line-height: 1.6;
            color: #000;
            max-width: 8.5in;
            margin: 0 auto;
            padding: 1in;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #000;
            padding-bottom: 10px;
        }
        .title {
            font-size: 18px;
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        .parties {
            margin-bottom: 20px;
        }
        .party-info {
            margin-bottom: 15px;
            padding: 10px;
            border-left: 3px solid #333;
            background-color: #f9f9f9;
        }
        .clause {
            margin-bottom: 20px;
        }
        .clause-title {
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 10px;
            text-decoration: underline;
        }
        .signature-block {
            margin-top: 40px;
            page-break-inside: avoid;
        }
        .signature-line {
            border-bottom: 1px solid #000;
            width: 300px;
            margin: 20px 0 5px 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="title">Mutual Non-Disclosure Agreement</div>
        <div class="subtitle">{{ document_name }}</div>
    </div>

    <div class="parties">
        <p><strong>This Mutual Non-Disclosure Agreement</strong> ("Agreement") is entered into on 
        <strong>{{ effective_date or "_____________" }}</strong> by and between:</p>
        
        <div class="party-info">
            <strong>First Party ("Disclosing/Receiving Party"):</strong><br>
            {{ disclosing_party.name }}<br>
            {% if disclosing_party.title %}{{ disclosing_party.title }}<br>{% endif %}
            {% if disclosing_party.company %}{{ disclosing_party.company }}<br>{% endif %}
            {{ disclosing_party.address }}<br>
            Email: {{ disclosing_party.email }}<br>
            {% if disclosing_party.phone %}Phone: {{ disclosing_party.phone }}{% endif %}
        </div>

        <div class="party-info">
            <strong>Second Party ("Receiving/Disclosing Party"):</strong><br>
            {{ receiving_party.name }}<br>
            {% if receiving_party.title %}{{ receiving_party.title }}<br>{% endif %}
            {% if receiving_party.company %}{{ receiving_party.company }}<br>{% endif %}
            {{ receiving_party.address }}<br>
            Email: {{ receiving_party.email }}<br>
            {% if receiving_party.phone %}Phone: {{ receiving_party.phone }}{% endif %}
        </div>
    </div>

    <div class="clause">
        <div class="clause-title">1. DEFINITION OF CONFIDENTIAL INFORMATION</div>
        <p>For purposes of this Agreement, "Confidential Information" means any and all non-public, 
        confidential or proprietary information disclosed by either party to the other party, 
        whether orally, in writing, or in any other form.</p>
    </div>

    <div class="clause">
        <div class="clause-title">2. OBLIGATIONS OF RECEIVING PARTY</div>
        <p>The Receiving Party agrees to hold and maintain the Confidential Information in strict 
        confidence and to take reasonable precautions to protect such Confidential Information.</p>
    </div>

    <div class="clause">
        <div class="clause-title">3. TERM</div>
        <p>This Agreement shall remain in effect until {{ expiration_date or "terminated by mutual agreement" }}.</p>
    </div>

    <div class="clause">
        <div class="clause-title">4. GOVERNING LAW</div>
        <p>This Agreement shall be governed by and construed in accordance with the laws of {{ governing_law }}.</p>
    </div>

    <div class="signature-block">
        <p><strong>IN WITNESS WHEREOF</strong>, the parties have executed this Agreement as of the date first written above.</p>
        
        <div style="display: flex; justify-content: space-between; margin-top: 40px;">
            <div>
                <div class="signature-line"></div>
                <p>{{ disclosing_party.name }}<br>
                {% if disclosing_party.title %}{{ disclosing_party.title }}{% endif %}</p>
                <p>Date: _______________</p>
            </div>
            
            <div>
                <div class="signature-line"></div>
                <p>{{ receiving_party.name }}<br>
                {% if receiving_party.title %}{{ receiving_party.title }}{% endif %}</p>
                <p>Date: _______________</p>
            </div>
        </div>
    </div>

    <div style="margin-top: 30px; font-size: 10px; color: #666; border-top: 1px solid #ccc; padding-top: 10px;">
        <p>This document was generated by NDARite on {{ generation_date }}. Document ID: {{ document_id }}</p>
    </div>
</body>
</html>"""
        
        bilateral_file = nda_dir / "bilateral_standard.html"
        if not bilateral_file.exists():
            with open(bilateral_file, 'w', encoding='utf-8') as f:
                f.write(bilateral_template)
        
        # Create other template variants
        templates = {
            "unilateral_standard.html": bilateral_template.replace("Mutual Non-Disclosure Agreement", "Unilateral Non-Disclosure Agreement"),
            "multilateral_standard.html": bilateral_template.replace("Mutual Non-Disclosure Agreement", "Multilateral Non-Disclosure Agreement"),
            "bilateral_basic.html": bilateral_template,
            "bilateral_advanced.html": bilateral_template
        }
        
        for filename, content in templates.items():
            template_file = nda_dir / filename
            if not template_file.exists():
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(content)
