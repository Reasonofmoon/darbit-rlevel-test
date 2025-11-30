"""
Simple script to download all PDF files from https://ebooks.rahnuma.org/children.html
Uses requests and BeautifulSoup instead of Selenium for better compatibility.
"""

import os
import time
import requests
from bs4 import BeautifulSoup

# Configuration
BASE_URL = "https://ebooks.rahnuma.org/children.html"
DOWNLOAD_FOLDER = r"f:\dev\darlbit-lv-test-system\rahnuma_pdfs"

# Create download folder if it doesn't exist
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def get_pdf_html_links(url):
    """Get all .pdf.html links from the children's page"""
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
        print(f"Error fetching main page: {str(e)}")
        return []

def get_direct_pdf_link(pdf_html_url):
    """Extract the direct PDF download link from a .pdf.html page"""
    print(f"  Visiting {pdf_html_url}...")
    try:
        response = requests.get(pdf_html_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the download link (looking for links containing .pdf but not .pdf.html)
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.endswith('.pdf') and not href.endswith('.pdf.html'):
                print(f"  Found PDF link: {href}")
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
        
        # Get file size if available
        total_size = int(response.headers.get('content-length', 0))
        
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

def main():
    """Main function to orchestrate the download process"""
    try:
        # Get all .pdf.html links from the children's page
        pdf_html_links = get_pdf_html_links(BASE_URL)
        
        if not pdf_html_links:
            print("No PDF links found!")
            return
        
        # Process each .pdf.html page
        downloaded_count = 0
        failed_count = 0
        
        for i, pdf_html_link in enumerate(pdf_html_links, 1):
            print(f"\n[{i}/{len(pdf_html_links)}] Processing: {pdf_html_link}")
            
            # Get the direct PDF link
            pdf_link = get_direct_pdf_link(pdf_html_link)
            
            if pdf_link:
                # Download the PDF
                if download_pdf(pdf_link, DOWNLOAD_FOLDER):
                    downloaded_count += 1
                else:
                    failed_count += 1
            else:
                print(f"  ✗ Could not find PDF link on page")
                failed_count += 1
            
            # Small delay between requests to be polite
            time.sleep(1)
        
        # Summary
        print("\n" + "="*60)
        print("DOWNLOAD SUMMARY")
        print("="*60)
        print(f"Total PDF pages found: {len(pdf_html_links)}")
        print(f"Successfully downloaded: {downloaded_count}")
        print(f"Failed: {failed_count}")
        print(f"Download folder: {DOWNLOAD_FOLDER}")
        print("="*60)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
