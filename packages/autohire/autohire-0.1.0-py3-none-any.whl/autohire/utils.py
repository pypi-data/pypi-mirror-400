import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from fpdf import FPDF
import docx
import os

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text()
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text
    except Exception as e:
        return f"Error reading URL: {str(e)}"

def extract_text_from_docx(docx_path):
    try:
        doc = docx.Document(docx_path)
        text = []
        for para in doc.paragraphs:
            text.append(para.text)
        return '\n'.join(text)
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

def extract_text_from_txt(txt_path):
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        try:
            with open(txt_path, 'r', encoding='latin-1') as f:
                 return f.read()
        except Exception as e:
            return f"Error reading TXT: {str(e)}"

def extract_text(ident):
    if ident.startswith("http"):
        return extract_text_from_url(ident)
    
    ext = os.path.splitext(ident)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(ident)
    elif ext == '.docx':
        return extract_text_from_docx(ident)
    elif ext == '.txt':
        return extract_text_from_txt(ident)
    else:
        return extract_text_from_txt(ident) # fallback

def create_pdf_from_text(text, output_path):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        # Handle unicode characters roughly by replacing or using a unicode font
        # For MVP, we'll stick to latin-1 safe text or handle errors
        safe_text = text.encode('latin-1', 'replace').decode('latin-1')
        
        pdf.multi_cell(0, 10, safe_text)
        pdf.output(output_path)
        return True
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return False
