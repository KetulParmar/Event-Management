from io import BytesIO
from django.template.loader import render_to_string
from xhtml2pdf import pisa


def generate_invoice_pdf(context):
    template_path = 'invoice_template.html'
    html = render_to_string(template_path, context)

    result = BytesIO()
    pdf_status = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf_status.err:
        return result
    else:
        return None
