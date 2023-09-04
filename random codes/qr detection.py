import cv2
import numpy as np

# Load image, grayscale, Otsu's threshold
image = cv2.imread(r"C:\Users\Windows 10 Pro\Desktop\Codes\Donny\C13A6514.JPG")
scale = 0.2
width = int(image.shape[1] * scale)
height = int(image.shape[0] * scale)
image = cv2.resize(image, (width, height))

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = 255 - gray
thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

# Compute rotated bounding box
coords = np.column_stack(np.where(thresh > 0))
angle = cv2.minAreaRect(coords)[-1]

if angle < -45:
    angle = -(90 + angle)
else:
    angle = -angle
print("Skew angle: ", angle)

# Rotate image to deskew
(h, w) = image.shape[:2]
center = (w // 2, h // 2)
M = cv2.getRotationMatrix2D(center, angle, 1.0)
rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

detector = cv2.QRCodeDetector()
data, points, straight_qrcode = detector.detectAndDecode(rotated)
print("QR data:", data)

cv2.imshow('rotated', rotated)
cv2.waitKey(0)


# image = cv2.imread(r"C:\Users\Windows 10 Pro\Downloads\Donny\qr.JPG")
# scale = 0.3
# width = int(image.shape[1] * scale)
# height = int(image.shape[0] * scale)
# image = cv2.resize(image, (width, height))
# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
# # The bigger the kernel, the more the white region increases.
# # If the resizing step was ignored, then the kernel will have to be bigger
# # than the one given here.
# kernel = np.ones((3, 3), np.uint8)
# thresh = cv2.dilate(thresh, kernel, iterations=1)

# contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
# bboxes = []
# for cnt in contours:
#     area = cv2.contourArea(cnt)
#     xmin, ymin, width, height = cv2.boundingRect(cnt)
#     extent = area / (width * height)

#     # filter non-rectangular objects and small objects
#     if (extent > np.pi / 4) and (area > 100):
#         bboxes.append((xmin, ymin, xmin + width, ymin + height))

# # for xmin, ymin, xmax, ymax in bboxes:
# #     roi = image[ymin:ymax, xmin:xmax]
# detector = cv2.QRCodeDetector()
# data, points, straight_qrcode = detector.detectAndDecode(gray)
# print("QR data:", data)
# print("\nPoints:", points)
# print("\nSTR:", straight_qrcode)
# cv2.imshow("", thresh)
# # add wait key. window waits until user presses a key
# cv2.waitKey(0)
# # and finally destroy/close all open windows
# cv2.destroyAllWindows()
