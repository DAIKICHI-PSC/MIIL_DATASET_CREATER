# MIIL_DATASET_CREATER
Annotation tool espetially for Yolo2 Yolo3 Yolo4


Annotation tool for YoLo.

You will need the following:

Python 3.7.1 and above

PySide2

numpy

opencv-python

If you have any other required libraries, please install them.



The following is the flow of creating annotations.
# 1 #
Prepare a folder that stores the photos you need for learning.
The file names must be serial numbers.
If it is not a serial number, press the RENUMBER FILES IN A FOLDER button and specify the folder containing the photos.
# 2 #
Specify PICTURE FOLDER.
Create or load a label.
# 3 #
Specify the camera ID.
Normally, 0 is fine.
# 4 #
If you want to crop the image to the specified size, check TRIM and specify the width and height.
# 5 #
Select DRAW and press the START button.
# 6 #
To trim, place the area to be trimmed in the red frame and press the T key.
Right-click on the photo to determine the area and release the button to create the annotation.
Press the ESC key to remove all annotations.
Select an annotation with the E and D keys and press the B key to delete only the selected annotation.
You can switch labels with the Q and W keys, and switch photos with the A and S keys.



Select CAMERA and press the START button to get photos from your USB camera.
Press the spacebar to get the photo.



Select RECORD and press the START button to simply save the video.
Please select VIDEO FILE, width and height in advance.
If the size is not supported, the save will fail.



Select FILE and press the START button to get photos from the video.
Please select VIDEO FILE in advance.
Trim is also possible.
Press the spacebar to get the photo.
Press the Z key to advance the video.



You can rotate the photo with the button on RIGION.
Buttons with AUTO process all photos between Start Posision and End Position.
Please note that the final number of the photo may not be the End Position.
You actually need to click on the last photo in the listbox to see the number in Current Position.



If you can't use your camera with MIIL_DATASET_CREATER_A.py, try MIIL_DATASET_CREATER_B.py



YoLo?????????????????????????????????????????????

?????????????????????????????????

Python 3.7.1??????

PySide2

numpy

cv2

?????????????????????????????????????????????????????????????????????????????????



?????????????????????????????????????????????????????????????????????
# 1 #
???????????????????????????????????????????????????????????????
?????????????????????????????????????????????????????????
???????????????????????????RENUMBER FILES IN A FOLDER??????????????????????????????????????????????????????????????????????????????
# 2 #
PICTURE FOLDER?????????????????????
????????????????????????????????????????????????
# 3 #
?????????ID?????????????????????
?????????0?????????????????????????????????
# 4 #
???????????????????????????????????????????????????????????????TRIM????????????????????????????????????????????????????????????
# 5 #
DRAW???????????????START???????????????????????????
# 6 #
?????????????????????????????????????????????????????????????????????T????????????????????????
???????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
ESC??????????????????????????????????????????????????????????????????????????????
E?????????D??????????????????????????????????????????B??????????????????????????????????????????????????????????????????????????????
Q?????????W??????????????????????????????????????????A?????????S?????????????????????????????????????????????



CAMERA??????????????????START????????????????????????USB?????????????????????????????????????????????
??????????????????????????????????????????????????????????????????



RECORD??????????????????START????????????????????????????????????????????????????????????
?????????VIDEO FILE??????????????????????????????????????????
??????????????????????????????????????????????????????????????????



FILE??????????????????START??????????????????????????????????????????????????????????????????
?????????VIDEO FILE???????????????????????????
???????????????????????????
??????????????????????????????????????????????????????????????????
Z?????????????????????????????????



RIGION????????????????????????????????????????????????????????????
AUTO???????????????????????????Start Posision???End Position???????????????????????????????????????
????????????????????????End Position?????????????????????????????????????????????????????????
?????????????????????????????????????????????????????????????????????????????????Current Position???????????????????????????????????????



MIIL_DATASET_CREATER_A.py???????????????????????????????????????MIIL_DATASET_CREATER_B.py????????????????????????
