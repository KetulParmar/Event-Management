from io import BytesIO
from django.template.loader import render_to_string
from xhtml2pdf import pisa


def generate_invoice_pdf(context):
    print("🔧 Starting PDF generation...")
    template_path = 'invoice_template.html'
    html = render_to_string(template_path, context)

    result = BytesIO()
    pdf_status = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf_status.err:
        print("✅ PDF generated successfully.")
        return result  # ✅ return BytesIO object here
    else:
        print("❌ PDF generation failed.")
        return None
