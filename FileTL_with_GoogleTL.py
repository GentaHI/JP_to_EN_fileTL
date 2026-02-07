import os
import re
from googletrans import Translator  # pip install googletrans==4.0.0-rc1
import unicodedata

# List of conjunctions/articles to exclude from capitalization
EXCLUDED_WORDS = ['and', 'or', 'the', 'in', 'on', 'at', 'for', 'nor', 'but', 'to', 'so', 'a', 'an', 'as']

# Allowed Translated Lists
ALLOWED_EXTS = {'.mp3', '.png', '.wav', '.psd', '.mp4', '.jpg', 'txt'}

# Normalize full-width characters
def normalize_text(text):
    return unicodedata.normalize('NFKC', text)

# Check if text contains Japanese
def contains_japanese(text):
    return re.search(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9faf]', text) is not None

# Translate Japanese to English
def translate_text(text):
    translator = Translator()
    try:
        return translator.translate(text, src='ja', dest='en').text
    except:
        return text  # fallback

def sanitize_filename(name):
    # Only remove ASCII-invalid characters, keep full-width versions (e.g., ？)
    invalid_ascii = r'[<>:"/\\|?*]'
    name = re.sub(invalid_ascii, '', name)
    # Remove control characters (invisible, non-printable)
    name = re.sub(r'[\x00-\x1f\x7f]', '', name)
    # Strip leading/trailing whitespace and dots
    return name.strip().rstrip('.')

def capitalize_filename(name):
    # Split the filename into words
    parts = re.split(r'([_\s]+)', name)
    
    result = []
    for i, word in enumerate(parts):
        if re.match(r'[_\s]+', word):  # keep delimiters like underscore or space
            result.append(word)
        else:
            # Always capitalize the first word regardless of exclusion
            if i == 0 or not result or re.match(r'[_\s]+', result[-1]):
                result.append(word.capitalize())
            elif word.lower() in EXCLUDED_WORDS:
                result.append(word.lower())
            else:
                result.append(word.capitalize())
    
    # Join back into a single string with spaces
    return ''.join(result)
   

def process_files(base_dir):
    base_dir = base_dir.replace('\\', '/')

    for root, _, files in os.walk(base_dir):
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext not in ALLOWED_EXTS:
                continue

            normalized = normalize_text(filename)
            name_without_ext = os.path.splitext(normalized)[0]

            # split by - or _
            parts = re.split(r'[-_]', name_without_ext)

            translated_parts = [
                translate_text(part) if contains_japanese(part) else part
                for part in parts
            ]

            translated_name = "_".join(
                sanitize_filename(part) for part in translated_parts
            )

            translated_name = capitalize_filename(translated_name)

            old_path = os.path.join(root, filename)
            new_filename = translated_name + ext
            new_path = os.path.join(root, new_filename)

            if old_path != new_path:
                print(f"Renaming file: {old_path} → {new_path}")
                try:
                    os.rename(old_path, new_path)
                except Exception as e:
                    print(f"Failed to rename file {old_path}: {e}")


def rename_folders(base_dir):
    base_dir = base_dir.replace('\\','/')
    for root, dirs, _ in os.walk(base_dir, topdown=False):
        for folder in dirs:
            old_path = os.path.join(root, folder)

            # normalize text folders
            normalized = normalize_text(folder)
            parts = re.split(r'[-_]', normalized)

            #start translate
            translated_parts = [translate_text(part) if contains_japanese(part) else part for part in parts]
            translated_name = "_".join(sanitize_filename(part) for part in translated_parts)
            #translated_name = capitalize_filename(translated_name)

            #translated = translate_text(normalized)
            #formatted = format_filename(translated)
            new_path = os.path.join(root, translated_name)
            if old_path != new_path:
                try:
                    os.rename(old_path, new_path)
                    print(f"Renamed folder: {old_path} → {new_path}")
                except Exception as e:
                    print(f"Failed to rename folder {old_path}: {e}")

# Run
repeat_boolean = True

while repeat_boolean == True:
    folder_path = input("Enter the directory: ").strip()
    print("Renaming files...\n")
    process_files(folder_path)
    print("Renaming folders...\n")
    rename_folders(folder_path)
    print("Rename completed...\n")
    
    check = input("\nRepeat? (input n/N to end) : ").strip()
    if check == 'n' or check == 'N' :
        repeat_boolean = False