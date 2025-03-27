import cv2
import numpy as np
import os
import random
from PIL import Image, ImageEnhance
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

input_folder = "/home/san/Desktop/selenium/downloaded_images"
output_folder = "scooter"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def augment_image(img_path, output_folder, index):
    try:
        img = Image.open(img_path)
        
        # Convert to RGB mode to ensure compatibility with JPEG format
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Rotation
        angles = [-30, -15, 15, 30]
        for angle in angles:
            img_rotated = img.rotate(angle)
            img_rotated.save(f"{output_folder}/rotated_{index}_{angle}.jpg")

        # Contrast
        contrast = ImageEnhance.Contrast(img)
        img_contrast = contrast.enhance(1.5)  # Increase contrast
        img_contrast.save(f"{output_folder}/contrast_{index}.jpg")

        # Brightness
        bright = ImageEnhance.Brightness(img)
        img_bright = bright.enhance(1.2)  # Slightly increase brightness
        img_bright.save(f"{output_folder}/bright_{index}.jpg")

        # Flipping
        img_flip = img.transpose(Image.FLIP_LEFT_RIGHT)
        img_flip.save(f"{output_folder}/flip_{index}.jpg")

        # Adding Noise
        img_np = np.array(img)
        noise = np.random.randint(0, 50, img_np.shape, dtype='uint8')
        img_noisy = cv2.add(img_np, noise)
        cv2.imwrite(f"{output_folder}/noise_{index}.jpg", img_noisy)
        
        logging.info(f"Successfully processed image: {img_path}")
        return True
    except Exception as e:
        logging.error(f"Error processing image {img_path}: {str(e)}")
        return False

# Process all images
success_count = 0
error_count = 0
for idx, img_name in enumerate(os.listdir(input_folder)):
    img_path = os.path.join(input_folder, img_name)
    try:
        if os.path.isfile(img_path):
            if augment_image(img_path, output_folder, idx):
                success_count += 1
            else:
                error_count += 1
    except Exception as e:
        logging.error(f"Error with file {img_path}: {str(e)}")
        error_count += 1

logging.info(f"Processing complete. Successfully processed {success_count} images. Failed to process {error_count} images.")
