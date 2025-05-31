import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageEnhance
import pytesseract
import csv
import os

class TextExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Text to CSV Extractor")
        self.root.geometry("400x300")

        # GUI Elements
        self.label = tk.Label(root, text="Select one or more images to extract text and save as CSV")
        self.label.pack(pady=10)

        self.select_btn = tk.Button(root, text="Select Images", command=self.select_images)
        self.select_btn.pack(pady=5)

        self.extract_btn = tk.Button(root, text="Extract and Save CSV", command=self.extract_and_save, state=tk.DISABLED)
        self.extract_btn.pack(pady=5)

        self.status_label = tk.Label(root, text="")
        self.status_label.pack(pady=10)

        self.debug_label = tk.Label(root, text="Raw OCR Output:")
        self.debug_label.pack()

        self.debug_text = tk.Text(root, height=6, width=40)
        self.debug_text.pack(pady=5)

        self.image_paths = []

    def select_images(self):
        self.image_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff")])
        if self.image_paths:
            self.status_label.config(text=f"Selected {len(self.image_paths)} image(s)")
            self.extract_btn.config(state=tk.NORMAL)
        else:
            self.status_label.config(text="No images selected")
            self.extract_btn.config(state=tk.DISABLED)

    def extract_and_save(self):
        if not self.image_paths:
            messagebox.showerror("Error", "Please select at least one image!")
            return

        try:
            all_extracted_names = []
            total_images = len(self.image_paths)

            for idx, image_path in enumerate(self.image_paths, 1):
                self.status_label.config(text=f"Extracting text from image {idx}/{total_images}...")
                self.root.update()

                # Preprocess image
                image = Image.open(image_path).convert('L')  # Convert to grayscale
                image = image.resize((int(image.width * 2), int(image.height * 2)), Image.Resampling.LANCZOS)  # Increase resolution
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(2)  # Increase contrast

                # Extract text with Tesseract, using PSM 6 (single block of text)
                text = pytesseract.image_to_string(image, config='--psm 6')

                # Display raw extracted text for debugging
                self.debug_text.delete(1.0, tk.END)
                self.debug_text.insert(tk.END, text)

                # Process the text into a list
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    # Look for lines that start with a number followed by a dot
                    if line and line.split('.')[0].replace(',', '').isdigit():
                        parts = line.split('.', 1)
                        if len(parts) > 1:
                            name = parts[1].strip()
                            # Remove any trailing numbers or page numbers (e.g., "1")
                            name = name.split(' ')[0:-1] if name.endswith((' 1', ' 2', ' 3')) else name
                            name = name.strip()
                            if name and name not in all_extracted_names and "UNCLASSIFIED" not in name:
                                all_extracted_names.append(name)

            # Save to CSV
            output_csv = "extracted_list.csv"
            with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Name"])  # Header
                for name in all_extracted_names:
                    writer.writerow([name])

            self.status_label.config(text=f"Success! Saved as {output_csv}")
            messagebox.showinfo("Success", f"Text extracted from {total_images} image(s) and saved to {output_csv}")

        except Exception as e:
            self.status_label.config(text="Error occurred")
            messagebox.showerror("Error", f"Failed to extract text: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TextExtractorApp(root)
    root.mainloop()