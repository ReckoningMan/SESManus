import os
import re
from bs4 import BeautifulSoup
from urllib.parse import unquote

def extract_pdf_links(file_path):
    try:
        # Read the file with appropriate encoding
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
        
        # Create BeautifulSoup object
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find all elements that might contain PDF links
        elements = soup.find_all(['a', 'link', 'script', 'div'], string=re.compile(r'\.pdf', re.I))
        
        # Extract all text content and find PDF links using regex
        all_text = str(soup)
        pdf_links = re.findall(r'https?://[^\s"\'<>]+?\.pdf', all_text, re.IGNORECASE)
        
        # Clean and decode the links
        clean_links = []
        for link in pdf_links:
            # Remove any trailing characters that might be part of HTML attributes
            clean_link = re.sub(r'[\s\'"<>].*$', '', link)
            # Decode URL-encoded characters
            clean_link = unquote(clean_link)
            if clean_link not in clean_links:
                clean_links.append(clean_link)
        
        return clean_links
        
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    file_path = r"C:\Users\Home\Downloads\Data for Agent or Website\Quick Reference Guides single file.mhtml"
    output_file = r"C:\Users\Home\Downloads\Data for Agent or Website\extracted_pdf_links.txt"
    
    print(f"Extracting PDF links from: {file_path}")
    pdf_links = extract_pdf_links(file_path)
    
    # Write links to file
    with open(output_file, 'w', encoding='utf-8') as f:
        for link in pdf_links:
            f.write(f"{link}\n")
    
    # Print results
    print(f"\nFound {len(pdf_links)} unique PDF links.")
    print(f"Links saved to: {output_file}")
    
    if pdf_links:
        print("\nFirst 5 links:")
        for i, link in enumerate(pdf_links[:5], 1):
            print(f"{i}. {link}")
