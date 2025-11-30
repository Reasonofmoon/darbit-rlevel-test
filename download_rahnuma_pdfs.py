"""
Script to download all PDF files from https://ebooks.rahnuma.org/children.html
Uses Selenium to navigate and extract PDF links, then downloads them.
"""

import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin

# Configuration
BASE_URL = "https://ebooks.rahnuma.org/children.html"
DOWNLOAD_FOLDER = r"f:\dev\darlbit-lv-test-system\rahnuma_pdfs"

# Create download folder if it doesn't exist
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def setup_driver():
    """Setup Chrome driver with options"""
    options = webdriver.ChromeOptions()
    # Uncomment the next line to run in headless mode
    # options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    
    driver = webdriver.Chrome(options=options)
    return driver

def get_pdf_html_links(driver, url):
    """Get all .pdf.html links from the children's page"""
    print(f"Navigating to {url}...")
    driver.get(url)
    time.sleep(2)  # Wait for page to load
    
    # Find all links ending with .pdf.html
    links = driver.find_elements(By.TAG_NAME, "a")
    pdf_html_links = []
    
    for link in links:
        href = link.get_attribute("href")
        if href and href.endswith(".pdf.html"):
            pdf_html_links.append(href)
    
    print(f"Found {len(pdf_html_links)} PDF pages")
    return pdf_html_links

def get_direct_pdf_link(driver, pdf_html_url):
    """Extract the direct PDF download link from a .pdf.html page"""
    print(f"  Visiting {pdf_html_url}...")
    driver.get(pdf_html_url)
    time.sleep(1)  # Wait for page to load
    
    # Find the download link (looking for links containing .pdf but not .pdf.html)
    links = driver.find_elements(By.TAG_NAME, "a")
    
    for link in links:
        href = link.get_attribute("href")
        if href and href.endswith(".pdf") and not href.endswith(".pdf.html"):
            print(f"  Found PDF link: {href}")
            return href
    
    return None

def download_pdf(url, folder):
    """Download a PDF file from the given URL"""
    try:
        # Extract filename from URL
        filename = url.split("/")[-1]
        filepath = os.path.join(folder, filename)
        
        # Check if file already exists
        if os.path.exists(filepath):
            print(f"  ✓ Already downloaded: {filename}")
            return True
        
        print(f"  Downloading: {filename}...")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Write to file
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"  ✓ Downloaded: {filename}")
        return True
    
    except Exception as e:
        print(f"  ✗ Error downloading {url}: {str(e)}")
        return False

def main():
    """Main function to orchestrate the download process"""
    driver = None
    
    try:
        # Setup driver
        driver = setup_driver()
        
        # Get all .pdf.html links from the children's page
        pdf_html_links = get_pdf_html_links(driver, BASE_URL)
        
        if not pdf_html_links:
            print("No PDF links found!")
            return
        
        # Process each .pdf.html page
        downloaded_count = 0
        failed_count = 0
        
        for i, pdf_html_link in enumerate(pdf_html_links, 1):
            print(f"\n[{i}/{len(pdf_html_links)}] Processing: {pdf_html_link}")
            
            # Get the direct PDF link
            pdf_link = get_direct_pdf_link(driver, pdf_html_link)
            
            if pdf_link:
                # Download the PDF
                if download_pdf(pdf_link, DOWNLOAD_FOLDER):
                    downloaded_count += 1
                else:
                    failed_count += 1
            else:
                print(f"  ✗ Could not find PDF link on page")
                failed_count += 1
            
            # Small delay between requests
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
    
    finally:
        if driver:
            driver.quit()
            print("\nBrowser closed.")

if __name__ == "__main__":
    main()
