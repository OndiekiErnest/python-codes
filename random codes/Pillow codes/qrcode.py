from cv2 import (imread, QRCodeDetector, resize,
                 cvtColor, COLOR_BGR2GRAY, getRotationMatrix2D,
                 THRESH_OTSU, THRESH_BINARY, warpAffine, threshold,
                 minAreaRect, INTER_CUBIC, BORDER_REPLICATE,
                 )
import numpy as np
from pyzbar.pyzbar import decode, ZBarSymbol


def readQR_CV(filename, scale=0.2) -> str:
    """ function to read the QR code in an image """
    try:
        # load the image
        image = imread(filename)
        # new dims scaled
        width = int(image.shape[1] * scale)
        height = int(image.shape[0] * scale)
        # resize to smaller scale for faster qr detection
        image = resize(image, (width, height))
        # convert to gray
        gray = cvtColor(image, COLOR_BGR2GRAY)
        gray = 255 - gray
        thresh = threshold(gray, 0, 255, THRESH_BINARY + THRESH_OTSU)[1]

        # compute rotated bounding box
        coords = np.column_stack(np.where(thresh > 0))
        angle = minAreaRect(coords)[-1]

        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # deskew image
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        # matrix
        M = getRotationMatrix2D(center, angle, 1.0)
        rotated = warpAffine(image, M, (w, h), flags=INTER_CUBIC, borderMode=BORDER_REPLICATE)
        # initialize the QR code detector
        detector = QRCodeDetector()
        # try to find a QR code in the image
        data, points, binary_qrcode = detector.detectAndDecode(rotated)
        # if it didn't find anything, return false
        if points is None or binary_qrcode is None:
            return ""
        # otherwise return true
        else:
            return data
    # if an exception was thrown, return false
    except Exception as e:
        return str(e)


def readQR_ZB(filename):
    """ """
    image = imread(filename)
    gray_img = cvtColor(image, 0)
    codes = decode(gray_img, symbols=[ZBarSymbol.QRCODE])

    for obj in codes:

        code_data = obj.data.decode("utf-8")
        code_type = obj.type

        yield (code_data, code_type)

    yield (None, None)

# import cv2
# import numpy as np
# from pyzbar.pyzbar import decode


# def decoder(image):
#     gray_img = cv2.cvtColor(image, 0)
#     barcode = decode(gray_img)

#     for obj in barcode:
#         points = obj.polygon
#         (x, y, w, h) = obj.rect
#         pts = np.array(points, np.int32)
#         pts = pts.reshape((-1, 1, 2))
#         cv2.polylines(image, [pts], True, (0, 255, 0), 3)

#         barcodeData = obj.data.decode("utf-8")
#         barcodeType = obj.type
#         cv2.putText(frame, barcodeType, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

#         return barcodeData, barcodeType
#     return None, None


# cap = cv2.VideoCapture(0)
# while 1:
#     ret, frame = cap.read()
#     data, codetype = decoder(frame)
#     cv2.imshow('Image', frame)
#     code = cv2.waitKey(10)
#     if code == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()
# print(data, codetype)

if __name__ == '__main__':
    # d = readQR_CV(filename)
    # print(d)
    for data, codetype in readQR_ZB(filename):
        if data and codetype:
            print("Data:\n", data, "\n")
            print("Code type:\n", codetype)
