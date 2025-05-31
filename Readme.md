**README.md for IMAGE2TEXT**

Extract text from images and view the results in a GUI with search functionality.

### Prerequisites
- Python 3.x
- Install: `pip install Pillow pytesseract selenium`
- Tesseract OCR (add to PATH)
- ChromeDriver (add to PATH)

### Usage
1. **Extract Text**: Run `run.py` to extract text from images into `extracted_list.csv`.
   ```
   python run.py
   ```
2. **View CSV**: Run `view.py` to view, copy, and search names.
   ```
   python view.py
   ```

### Features
- Extract text from images using Tesseract OCR.
- View CSV in a Tkinter GUI.
- Copy names to clipboard.
- Search names on Google (Wikipedia filter); browser stays open.

### Troubleshooting
- **Tesseract Path**: Add to `run.py` if needed: `pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'`
- **ChromeDriver**: Specify path in `view.py` if not in PATH: `driver = webdriver.Chrome(executable_path='path/to/chromedriver')`
- **CAPTCHA**: Use longer delays or switch to Google Custom Search API.