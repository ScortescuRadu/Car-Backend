import cv2
import numpy as np
from PIL import Image
import pytesseract
from io import BytesIO
import pytesseract

def process_image_and_extract_license_plate(image_file):
    # Convert the image to a format suitable for OpenCV
    image = Image.open(image_file)
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Preprocess the image for better OCR results
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(gray, 30, 200)

    # Find contours and extract the license plate region
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    screenCnt = None

    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * peri, True)
        if len(approx) == 4:
            screenCnt = approx
            break

    if screenCnt is None:
        return None

    mask = np.zeros(gray.shape, np.uint8)
    cv2.drawContours(mask, [screenCnt], 0, 255, -1)
    new_image = cv2.bitwise_and(image, image, mask=mask)

    # OCR to extract the license plate
    config = '-l eng --oem 1 --psm 8'
    text = pytesseract.image_to_string(new_image, config=config)
    return text.strip()
