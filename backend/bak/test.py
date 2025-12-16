from utils.pdf_converter import convert_pptx_to_pdf
from pathlib import Path

# Convert one file
pdf_path = convert_pptx_to_pdf(
    Path("ticket.pptx"),
    Path("output/pdfs")
)