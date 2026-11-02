"""Convert DOCX report to PDF using Microsoft Word COM and inspect resulting pagination."""

import sys
from pathlib import Path
import win32com.client
import pymupdf

docx_path = Path("Online_Course_Completion_Prediction_Project_Report.docx").resolve()
pdf_path = Path("Online_Course_Completion_Prediction_Project_Report.pdf").resolve()

print(f"Converting '{docx_path.name}' to '{pdf_path.name}' via Microsoft Word COM...")

word = win32com.client.Dispatch("Word.Application")
word.Visible = False
word.DisplayAlerts = False

try:
    doc = word.Documents.Open(str(docx_path))
    # Update all fields in document (pagination, cross-references)
    try:
        doc.Fields.Update()
    except Exception as e:
        print("Note: Fields update skipped or completed:", e)
        
    doc.SaveAs(str(pdf_path), FileFormat=17) # 17 = wdFormatPDF
    page_count = doc.ComputeStatistics(2) # 2 = wdStatisticPages
    print(f"Microsoft Word computed page count: {page_count} pages")
    doc.Close(False)
finally:
    word.Quit()

print("Conversion complete. Inspecting with PyMuPDF...")
pdf = pymupdf.open(str(pdf_path))
actual_pdf_pages = len(pdf)
print(f"Actual PDF total page count: {actual_pdf_pages} pages")

for i in range(min(5, actual_pdf_pages)):
    page = pdf[i]
    print(f"  Page {i+1}: size={page.rect.width}x{page.rect.height}, text_length={len(page.get_text())}")

print(f"  ... Last Page {actual_pdf_pages}: text_length={len(pdf[-1].get_text())}")
pdf.close()

if actual_pdf_pages >= 20:
    print(f"SUCCESS: The report satisfies the requirement of MORE THAN 20 PAGES (Actual: {actual_pdf_pages} pages)!")
else:
    print(f"WARNING: The report has {actual_pdf_pages} pages, which is below the 20-page threshold.")
