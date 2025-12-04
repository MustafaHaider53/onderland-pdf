import os
import fitz  # PyMuPDF
from typing import Union

from pathlib import Path

try:
    import pdfminer.high_level
except ImportError:
    pdfminer = None
try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None

def pdf_to_text(
    input_path: Union[str, Path],
    output_dir: Union[str, Path] = "output_txt",
    use_ocr: bool = True
):
    """
    Extracts text from one or many PDF files and saves them as .txt files in output_dir.
    Tries PyMuPDF, pdfminer as fallback, and OCR if enabled as last resort.

    Args:
        input_path (str|Path): Path to PDF file or directory containing PDFs.
        output_dir (str|Path): Directory to save .txt files (will be created).
        use_ocr (bool): If True, tries OCR on pages with no text.
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    if input_path.is_dir():
        pdf_files = list(input_path.glob("*.pdf"))
    elif input_path.is_file() and input_path.suffix.lower() == ".pdf":
        pdf_files = [input_path]
    else:
        raise ValueError(f"Path {input_path} is not a PDF or directory of PDFs.")

    for pdf_file in pdf_files:
        text = ""
        try:
            text = extract_with_pymupdf(pdf_file)
            if not text.strip():
                if pdfminer:
                    text = extract_with_pdfminer(pdf_file)
        except Exception as e:
            if pdfminer:
                text = extract_with_pdfminer(pdf_file)
        
        # OCR Fallback if all else fails or empty text
        if use_ocr and (not text.strip()) and pytesseract and Image:
            text = extract_with_ocr(pdf_file)
        
        # Instead of saving all text, extract card numbers only
        card_numbers = extract_card_numbers_from_text(text)
        # Ensure only unique card numbers, preserving order
        unique_card_numbers = list(dict.fromkeys(card_numbers))
        
        out_path = output_dir / (pdf_file.stem + ".txt")
        with open(out_path, "w", encoding="utf-8") as f:
            for num in unique_card_numbers:
                f.write(num + "\n")
        print(f"[OK] {pdf_file.name} -> {out_path}")

def extract_with_pymupdf(pdf_file: Path) -> str:
    doc = fitz.open(str(pdf_file))
    text = []
    for page in doc:
        text.append(page.get_text())
    return "\n".join(text)

def extract_with_pdfminer(pdf_file: Path) -> str:
    try:
        from pdfminer.high_level import extract_text
        return extract_text(str(pdf_file))
    except Exception as e:
        print(f"[WARN] PDFMiner failed: {e}")
        return ""

def extract_with_ocr(pdf_file: Path) -> str:
    from tempfile import TemporaryDirectory
    import fitz
    if not (pytesseract and Image):
        return ""
    doc = fitz.open(str(pdf_file))
    text = []
    with TemporaryDirectory() as tmpdir:
        for i, page in enumerate(doc):
            pix = page.get_pixmap()
            img_path = os.path.join(tmpdir, f"page_{i}.png")
            pix.save(img_path)
            img = Image.open(img_path)
            page_text = pytesseract.image_to_string(img, lang="eng")
            text.append(page_text)
    return "\n".join(text)

def extract_card_numbers_from_text(text: str) -> list:
    """
    Extract card numbers under the '***Card Detail(s)***' section from OCR or extracted text.
    """
    result = []
    lines = text.splitlines()
    in_card_section = False
    for i, line in enumerate(lines):
        if '***Card Detail' in line:
            in_card_section = True
            continue
        if in_card_section:
            # Look for end of section
            if line.strip() == '' or line.startswith('_') or any(w in line for w in ['Invoice', 'Thank', 'see you']):
                break
            # Look for card number format
            if any(char.isdigit() for char in line) and '-' in line:
                card = line.split()[0]
                # Remove hyphens and leading zeros, keep only the numbers
                clean_card = card.replace('-', '').lstrip('0')
                # Optionally, verify format 0000-0000-0000-0000 (check original length)
                if len(card.replace('-', '')) >= 8:  # Minimum for truncated cards
                    result.append(clean_card)
    return result

# Example usage (as importable function):
from pdf_to_text import pdf_to_text
pdf_to_text("/Users/mustafahaider/pdf_onderland/pdfs")
