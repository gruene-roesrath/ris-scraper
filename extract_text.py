# This script extracts full text (as far as possible)
# from PDF documents

import subprocess
import sys
import os
import shlex


pdftotext_path = '/usr/local/bin/pdftotext'
ocrmypdf_path = '/usr/local/bin/ocrmypdf'

source_path = './documents'

fulltext_path = './fulltext'


def extract_text(path):
    """
    Extracts text from a PDF document
    """
    cmd = pdftotext_path + " -nopgbrk -enc UTF-8 '%s' -" % path
    return subprocess.check_output(cmd, encoding='UTF-8', shell=True)

def create_ocr_variant(path):
    """
    Creates an OCRed variant of the input PDF
    """
    basepath, filename = os.path.split(path)
    ocr_path = os.path.join(basepath, "ocr")
    output_file_path = os.path.join(ocr_path, filename)
    os.makedirs(ocr_path, exist_ok=True)

    cmd = ocrmypdf_path + " --rotate-pages -l deu '%s' '%s'" % (path, output_file_path)
    output = subprocess.check_output(cmd, encoding='UTF-8', shell=True)
    return output_file_path

def main():
    for root, _, files in os.walk(source_path, topdown=True):
        for filename in files:
            document_id = os.path.basename(root)

            # skip if thisdir is not a numeric name
            try:
                int(document_id)
            except ValueError:
                continue

            # skip non-PDF documents
            if not filename.lower().endswith(".pdf"):
                continue

            pdf_path = os.path.join(root, filename)
            output_dir = os.path.join(fulltext_path, document_id)
            output_file = os.path.join(output_dir, filename + ".txt")

            # check of fulltext exists and is newer than original
            if os.path.exists(output_file):
                if os.path.getmtime(output_file) > os.path.getmtime(pdf_path):
                    # Skipping because already done
                    continue

            print("Extracting text from %s" % pdf_path)
            try:
                result = extract_text(pdf_path)
            except subprocess.CalledProcessError as e:
                print("ERROR: %s" % e)
            except UnicodeDecodeError as e:
                print("ERROR: Problem with character set. Skipping. Originial error:\n%s" % e)
                continue

            ocr_variant_path = None
            if result == "":
                print("ERROR: Could not extract any text. Creating an OCRed variant.")

                try:
                    ocr_variant_path = create_ocr_variant(pdf_path)
                except Exception as e:
                    print("ERROR: %s" % e)
                    continue

                try:
                    result = extract_text(ocr_variant_path)
                except subprocess.CalledProcessError as e:
                    print("ERROR: %s" % e)
                    continue

            os.makedirs(output_dir, exist_ok=True)
            with open(output_file, "w") as textfile:
                textfile.write(result)

if __name__ == '__main__':
    main()
