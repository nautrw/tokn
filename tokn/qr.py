import os
import cv2
import pathlib
import zxingcpp


def read_qr_code(filename: str):
    img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    qr_results = zxingcpp.read_barcodes(img)

    if len(qr_results) != 1:
        raise ValueError("no qr code found or more than one")

    return qr_results[0].text
