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

def getRotatedRectanglePos(deg, cx, cy, fx, fy, ex, ey, width, height): #Degree, CenterX, CenterY, LeftUpperX, LeftUpperY, RightLowerX, LeftLowerY, Width, Height
    deg = deg * -1
    x1, y1 = calcPos(deg, cx, cy, fx, fy)
    x2, y2 = calcPos(deg, cx, cy, ex, fy)
    x3, y3 = calcPos(deg, cx, cy, ex, ey)
    x4, y4 = calcPos(deg, cx, cy, fx, ey)
    fsx = min(x1, x2, x3, x4)
    fsy = min(y1, y2, y3, y4)
    esx = max(x1, x2, x3, x4)
    esy = max(y1, y2, y3, y4)
    if fsx < 0:
        fsx = 0
    if fsy < 0:
        fsy = 0
    if esx > width:
        esx = width -1
    if esy > height:
        esy = height - 1
    #Calculate the length of width and height from 2 points
    xL = abs(esx - fsx)
    yL = abs(esy - fsy)
    return fsx, fsy, esx, esy, xL, yL #LeftUpperX, LeftUpperY, RightLowerX, LeftLowerY, Width, Height
