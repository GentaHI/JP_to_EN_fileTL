import os
import re
from googletrans import Translator  # pip install googletrans==4.0.0-rc1
import unicodedata

# List of conjunctions/articles to exclude from capitalization
EXCLUDED_WORDS = ['and', 'or', 'the', 'in', 'on', 'at', 'for', 'nor', 'but', 'to', 'so', 'a', 'an', 'as']

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
   
# Main processing
def process_files(directory):
    directory = directory.replace('\\','/')
    for filename in os.listdir(directory):
        if filename.endswith("mp3") or filename.endswith("png") or filename.endswith("wav") or filename.endswith("jpg"):
            if filename.endswith("mp3"):
                file_extension = ".mp3"
            elif filename.endswith("png"):
                file_extension = ".png"
            elif filename.endswith("wav"):
                file_extension = ".wav"
            elif filename.endswith("jpg"):
                file_extension = ".jpg"
            normalized = normalize_text(filename)
            name_without_ext = os.path.splitext(normalized)[0]

            # Extract Japanese parts using regex
            parts = re.split(r'[-_]', name_without_ext)
            translated_parts = [translate_text(part) if contains_japanese(part) else part for part in parts]
            translated_name = "_".join(sanitize_filename(part) for part in translated_parts)
            translated_name = capitalize_filename(translated_name)
            
            old_path = os.path.join(directory, filename)
            new_filename = translated_name + file_extension
            new_path = os.path.join(directory, new_filename)

            print(f"Renaming: {filename} -> {new_filename}")
            os.rename(old_path, new_path)

# Run
repeat_boolean = True

while repeat_boolean == True:
    folder_path = input("Enter the directory: ").strip()
    process_files(folder_path)

    check = input("Repeat? (input n/N to end) : ").strip()
    if check == 'n' or check == 'N' :
        repeat_boolean = False