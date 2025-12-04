# PDF Card Number Extractor

This tool automatically extracts card numbers from PDF files and saves them as clean numeric strings.

## Features

- Extracts card numbers from PDF files using multiple extraction methods (PyMuPDF, PDFMiner, OCR)
- Automatically cleans card numbers (removes hyphens and leading zeros)
- Supports both manual processing and automatic file watching

## Installation

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Manual Processing

Process all PDFs in a directory:
```bash
python pdf_to_text.py
```

Process a specific PDF file:
```bash
python pdf_to_text.py path/to/file.pdf
```

Process PDFs in a specific directory:
```bash
python pdf_to_text.py path/to/pdf/directory
```

### Automatic File Watching

Start watching a directory for new PDF files:
```bash
python pdf_to_text.py --watch
```

Watch a specific directory:
```bash
python pdf_to_text.py --watch path/to/watch/directory
```

The program will automatically process any new PDF files added to the watched directory and extract card numbers to the output directory.

### Options

- `-o, --output OUTPUT`: Specify output directory (default: output_txt)
- `-w, --watch`: Enable automatic file watching mode
- `-h, --help`: Show help message

## Output

Card numbers are extracted and saved as clean numeric strings (without hyphens or leading zeros) in text files in the output directory.
