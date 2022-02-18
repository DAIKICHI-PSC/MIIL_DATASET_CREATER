#Caluculate the statrting point and end point of a rotated rectangle from 2 points and degree.
import numpy as np

def calcPos(deg, cx, cy, x, y):
    point = np.array([x - cx, y - cy]) 
    #deg = deg * 30
    rad = deg * np.pi / 180
    rMat = np.array([[np.cos(rad), -np.sin(rad)],[np.sin(rad), np.cos(rad)]])
    spin = np.dot(rMat, point)
    rx = spin[0]
    ry = spin[1]
    return int(rx) + cx, int(ry) + cy

def getRotatedPos(deg, cx, cy, fx, fy, ex, ey): #Degree, CenterX, CenterY, LeftUpperX, LeftUpperY, RightLowerX, LeftLowerY, Width, Height
    deg = deg * -1
    x1, y1 = calcPos(deg, cx, cy, fx, fy)
    x2, y2 = calcPos(deg, cx, cy, ex, fy)
    x3, y3 = calcPos(deg, cx, cy, ex, ey)
    x4, y4 = calcPos(deg, cx, cy, fx, ey)
    return x1, y1, x2, y2, x3, y3, x4, y4
