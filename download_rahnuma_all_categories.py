"""
Script to download all PDF files from multiple Rahnuma ebook categories
Downloads from Computer and Literature categories
"""

import os
import sys
import time
import requests
from bs4 import BeautifulSoup

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# Configuration
CATEGORIES = {
    'computer': 'https://ebooks.rahnuma.org/computer.html',
    'literature': 'https://ebooks.rahnuma.org/literature.html',
}

BASE_DOWNLOAD_FOLDER = r"f:\dev\darlbit-lv-test-system\rahnuma_pdfs"

def get_pdf_html_links(url):
    """Get all .pdf.html links from a category page"""
    print(f"Fetching {url}...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all links ending with .pdf.html
        pdf_html_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.endswith('.pdf.html'):
                # Make absolute URL if needed
                if not href.startswith('http'):
                    href = f"https://ebooks.rahnuma.org/{href}"
                pdf_html_links.append(href)
        
        print(f"Found {len(pdf_html_links)} PDF pages")
        return pdf_html_links
    
    except Exception as e:
        print(f"Error fetching category page: {str(e)}")
        return []

def get_direct_pdf_link(pdf_html_url):
    """Extract the direct PDF download link from a .pdf.html page"""
    try:
        response = requests.get(pdf_html_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the download link (looking for links containing .pdf but not .pdf.html)
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.endswith('.pdf') and not href.endswith('.pdf.html'):
                return href
        
        return None
    
    except Exception as e:
        print(f"  Error fetching PDF page: {str(e)}")
        return None

def download_pdf(url, folder):
    """Download a PDF file from the given URL"""
    try:
        # Extract filename from URL
        filename = url.split("/")[-1]
        # Decode URL-encoded characters
        from urllib.parse import unquote
        filename = unquote(filename)
        
        filepath = os.path.join(folder, filename)
        
        # Check if file already exists
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            if file_size > 0:
                print(f"  ✓ Already downloaded: {filename} ({file_size:,} bytes)")
                return True
        
        print(f"  Downloading: {filename}...")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Write to file
        downloaded_size = 0
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded_size += len(chunk)
        
        print(f"  ✓ Downloaded: {filename} ({downloaded_size:,} bytes)")
        return True
    
    except Exception as e:
        print(f"  ✗ Error downloading {url}: {str(e)}")
        return False

def download_category(category_name, category_url):
    """Download all PDFs from a specific category"""
    print("\n" + "="*70)
    print(f"PROCESSING CATEGORY: {category_name.upper()}")
    print("="*70)
    
    # Create category-specific folder
    category_folder = os.path.join(BASE_DOWNLOAD_FOLDER, category_name)
    os.makedirs(category_folder, exist_ok=True)
    
    # Get all .pdf.html links from the category page
    pdf_html_links = get_pdf_html_links(category_url)
    
    if not pdf_html_links:
        print(f"No PDF links found in {category_name} category!")
        return 0, 0
    
    # Process each .pdf.html page
    downloaded_count = 0
    failed_count = 0
    
    for i, pdf_html_link in enumerate(pdf_html_links, 1):
        print(f"\n[{i}/{len(pdf_html_links)}] Processing: {pdf_html_link}")
        
        # Get the direct PDF link
        pdf_link = get_direct_pdf_link(pdf_html_link)
        
        if pdf_link:
            # Download the PDF
            if download_pdf(pdf_link, category_folder):
                downloaded_count += 1
            else:
                failed_count += 1
        else:
            print(f"  ✗ Could not find PDF link on page")
            failed_count += 1
        
        # Small delay between requests to be polite
        time.sleep(1)
    
    return downloaded_count, failed_count

def main():
    """Main function to orchestrate the download process"""
    print("="*70)
    print("RAHNUMA EBOOKS DOWNLOADER - MULTIPLE CATEGORIES")
    print("="*70)
    print(f"Base download folder: {BASE_DOWNLOAD_FOLDER}")
    print(f"Categories to download: {', '.join(CATEGORIES.keys())}")
    print("="*70)
    
    total_downloaded = 0
    total_failed = 0
    
    try:
        for category_name, category_url in CATEGORIES.items():
            downloaded, failed = download_category(category_name, category_url)
            total_downloaded += downloaded
            total_failed += failed
        
        # Final Summary
        print("\n" + "="*70)
        print("FINAL SUMMARY - ALL CATEGORIES")
        print("="*70)
        print(f"Total categories processed: {len(CATEGORIES)}")
        print(f"Total PDFs downloaded: {total_downloaded}")
        print(f"Total failed: {total_failed}")
        print(f"Download folder: {BASE_DOWNLOAD_FOLDER}")
        print("="*70)
        
        # Show folder structure
        print("\nFolder structure:")
        for category_name in CATEGORIES.keys():
            category_folder = os.path.join(BASE_DOWNLOAD_FOLDER, category_name)
            if os.path.exists(category_folder):
                file_count = len([f for f in os.listdir(category_folder) if f.endswith('.pdf')])
                print(f"  {category_folder}: {file_count} PDFs")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
