import numpy as np
import cv2

def obstacle_risk(frame_bgr):
    # Very simple placeholder: treat dark/contrasty regions as obstacles.
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blur, 60, 120)
    h, w = edges.shape
    thirds = w // 3
    left = np.mean(edges[:, :thirds]) / 255.0
    center = np.mean(edges[:, thirds:2*thirds]) / 255.0
    right = np.mean(edges[:, 2*thirds:]) / 255.0
    return float(left), float(center), float(right)