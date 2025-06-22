import re
import os
import sys
from urllib.parse import unquote

def extract_pdf_links(file_path):    
    # Regular expression to find PDF links in MHTML format
    pdf_pattern = re.compile(r'https?://[^\s"\'<>]+?\.pdf', re.IGNORECASE)
    
    try:
        # Try different encodings if needed
        encodings = ['utf-8', 'latin-1', 'cp1252']
        content = ''
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    content = file.read()
                break
            except UnicodeDecodeError:
                continue
        
        if not content:
            print("Error: Could not read file with any of the tried encodings.")
            return []
            
        # Find all PDF links
        pdf_links = pdf_pattern.findall(content)
        
        # Decode URL-encoded characters and clean up
        cleaned_links = []
        for link in pdf_links:
            # Remove any trailing characters that might be part of HTML attributes
            clean_link = link.split('"')[0].split('\'')[0].split(' ')[0].split('>')[0]
            # Decode URL-encoded characters
            clean_link = unquote(clean_link)
            cleaned_links.append(clean_link)
        
        # Remove duplicates while preserving order
        unique_links = []
        for link in cleaned_links:
            if link not in unique_links:
                unique_links.append(link)
        
        # Create output filename
        base_name = os.path.splitext(file_path)[0]
        output_file = f"{base_name}_pdf_links.txt"
        
        # Write links to file
        with open(output_file, 'w', encoding='utf-8') as out_file:
            for link in unique_links:
                out_file.write(link + '\n')
        
        print(f"Found {len(unique_links)} unique PDF links. Saved to: {output_file}")
        return unique_links
        
    except Exception as e:
        print(f"Error processing file: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = r"C:\Users\Home\Downloads\Data for Agent or Website\Quick Reference Guides single file.mhtml"
    
    print(f"Processing file: {file_path}")
    links = extract_pdf_links(file_path)
    
    # Print first few links as preview
    if links:
        print("\nFirst 5 links:")
        for i, link in enumerate(links[:5], 1):
            print(f"{i}. {link}")
    else:
        print("No PDF links found in the file.")
