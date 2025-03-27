from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import requests
import urllib.parse
import re

# Create a directory to save images if it doesn't exist
download_dir = os.path.join(os.getcwd(), 'bike')
os.makedirs(download_dir, exist_ok=True)
print(f"Images will be saved to: {download_dir}")

# Properly initialize the WebDriver with options to avoid detection
options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--start-maximized')
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)


def clean_filename(filename):
    # Remove invalid characters for filenames
    return re.sub(r'[\\/*?:"<>|]', "", filename)

# Function to download image - simplified to just download without validation
def download_image(img_url, img_alt, index):
    try:
        # Create a filename from the alt text or use the index if alt is empty
        if img_alt and len(img_alt.strip()) > 0:
            filename = clean_filename(img_alt)[:50]  # Limit filename length
        else:
            filename = f"image_{index}"
        
        # Get file extension from URL or default to jpg
        if '.' in img_url.split('/')[-1]:
            try:
                ext = img_url.split('/')[-1].split('.')[-1].lower()
                # Only use valid image extensions
                if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']:
                    pass
                else:
                    ext = 'jpg'  # Default to jpg for unknown extensions
            except:
                ext = 'jpg'
        else:
            ext = 'jpg'
            
        # Add extension
        filename = f"{filename}.{ext}"
        filepath = os.path.join(download_dir, filename)
        
        # Check if file already exists, add number if it does
        counter = 1
        original_filename = filename
        while os.path.exists(filepath):
            filename = f"{original_filename.split('.')[0]}_{counter}.{ext}"
            filepath = os.path.join(download_dir, filename)
            counter += 1
        
        # Download the image
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8'
        }
        response = requests.get(img_url, stream=True, timeout=15, headers=headers)
        
        if response.status_code == 200:
            # Save the image without validation
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(8192):
                    f.write(chunk)
            print(f"Downloaded: {filename}")
            return True
        else:
            print(f"Failed to download image: {response.status_code}")
    except Exception as e:
        print(f"Error downloading image: {e}")
    return False

# List of search URLs to process
search_urls = [
    # "https://www.google.com/search?q=honda+bike+india&tbm=isch",
    # "https://www.google.com/search?q=tvs+bike+models&tbm=isch",
    # "https://www.google.com/search?q=suzuki+bike+india&tbm=isch",
    # "https://www.google.com/search?q=yamaha+bike+india&tbm=isch",
    "https://www.google.com/search?q=bajaj+bike+india&tbm=isch",
    "https://www.google.com/search?q=ktm+bike+india&tbm=isch",
    "https://www.google.com/search?q=kawasaki+bike+india&tbm=isch",
    "https://www.google.com/search?q=aprilia+bike+india&tbm=isch",


]

# Function to process a single search URL - simplified to just download images without checking dimensions
def process_search_url(url, max_images=100):
    print(f"\n{'='*50}")
    print(f"Processing search URL: {url}")
    print(f"{'='*50}\n")
    
    # Open Google Images search
    driver.get(url)
    
    # Wait for the page to load
    time.sleep(3)
    print("Page title:", driver.title)
    
    # Find all thumbnail images
    thumbnails = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".H8Rx8c"))
    )
    
    print(f"Found {len(thumbnails)} image thumbnails")
    
    # Track successful downloads for this URL
    successful_downloads = 0
    
    # Process each thumbnail
    for index, thumbnail in enumerate(thumbnails):
        # Stop if we've reached the maximum number of images
        if successful_downloads >= max_images:
            print(f"Reached maximum of {max_images} successful downloads for this URL")
            break
            
        try:
            print(f"\nProcessing image {index+1}")
            
            # Scroll to the thumbnail
            driver.execute_script("arguments[0].scrollIntoView();", thumbnail)
            time.sleep(1)
            
            # Click on the thumbnail to open the larger image preview
            thumbnail.click()
            time.sleep(2)
            
            # Try to find the high-resolution image in the right panel
            try:
                # First try to find the specific high-res image with iPVvYb class (displayed image)
                try:
                    high_res_img = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".sFlh5c.FyHeAf.iPVvYb"))
                    )
                except:
                    # Fallback: try to find any high-res image
                    high_res_img = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".sFlh5c.FyHeAf"))
                    )
                
                # Get the high-resolution image URL and alt text
                img_url = high_res_img.get_attribute("src")
                img_alt = high_res_img.get_attribute("alt")
                
                # If we have a valid image URL, download it
                if img_url and not img_url.startswith("data:") and not img_url.startswith("https://encrypted-tbn0"):
                    print(f"Downloading image: {img_url[:50]}...")
                    download_success = download_image(img_url, img_alt, index)
                    if download_success:
                        successful_downloads += 1
                # Try to get the source URL if available
                else:
                    try:
                        source_link = driver.find_element(By.CSS_SELECTOR, "a.YsLeY")
                        original_source_url = source_link.get_attribute("href")
                        
                        # Open the source page in a new tab
                        driver.execute_script("window.open(arguments[0]);", original_source_url)
                        
                        # Switch to the new tab
                        driver.switch_to.window(driver.window_handles[-1])
                        
                        # Wait for the page to load
                        time.sleep(3)
                        
                        # Try to find images on the page
                        images = driver.find_elements(By.TAG_NAME, "img")
                        
                        if images:
                            # Just get the first image with a valid src
                            for img in images:
                                src = img.get_attribute("src")
                                if src and not src.startswith("data:") and len(src) > 10:
                                    print(f"Downloading image from source page: {src[:50]}...")
                                    download_success = download_image(src, img_alt or "source_image", index)
                                    if download_success:
                                        successful_downloads += 1
                                    break
                        
                        # Close the tab and switch back to the main window
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    except Exception as e:
                        print(f"Error with source page: {e}")
                    
            except Exception as e:
                print(f"Error finding image: {e}")
                
        except Exception as e:
            print(f"Error processing thumbnail {index+1}: {e}")
        
        # Small delay before next image
        time.sleep(1)
    
    return successful_downloads

# Process each search URL
total_downloads = 0
for url in search_urls:
    downloads = process_search_url(url, max_images=100)
    total_downloads += downloads
    print(f"Downloaded {downloads} images from {url}")

print(f"\nTotal images downloaded: {total_downloads}")

# Close the browser
driver.quit()
