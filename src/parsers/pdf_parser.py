import pypdf

def extract_text_from_pdf(file_path: str) -> str:
    text_content = []
    with open(file_path, 'rb') as pdf_file:
        reader = pypdf.PdfReader(pdf_file)
        for page in reader.pages:
            text_content.append(page.extract_text() or "")
    return "\n".join(text_content)
