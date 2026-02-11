import PyPDF2
import sys

# Open and read the PDF
pdf_path = "Ridge-regression-html.pdf"
with open(pdf_path, 'rb') as file:
    pdf_reader = PyPDF2.PdfReader(file)
    num_pages = len(pdf_reader.pages)
    
    print(f"Total pages: {num_pages}\n")
    print("="*80)
    
    # Extract text from all pages
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        text = page.extract_text()
        print(f"\n--- Page {page_num + 1} ---\n")
        print(text)
        print("\n" + "="*80)
