#Caluculate the statrting point and end point of a rectangle from 2 points
def getRectanglePos(x1, y1, x2, y2, width, height):
    #check the end point(within the picture or not)
    if x2 < 0 or x2 > width - 1 or y2 < 0 or y2 > height - 1:
        withinPixFlag = 0
    else:
        withinPixFlag = 1
    #Check which point would be the starting point(uppuer left) and the end point(bottom right)
    fsx = min(x1, x2)
    fsy = min(y1, y2)
    esx = max(x1, x2)
    esy = max(y1, y2)
    #Calculate the length of width and height from 2 points
    xL = abs(esx - fsx)
    yL = abs(esy - fsy)
    #Calculate the length of width and height from 2 points
    xL = abs(x2 - x1)
    yL = abs(y2 - y1)
    return withinPixFlag, fsx, fsy, esx, esy, xL, yL
