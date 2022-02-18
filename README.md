# MIIL_DATASET_CREATER
Annotation tool espetially for Yolo2 Yolo3 Yolo4


Annotation tool for YoLo.
You will need the following:
Python 3.7.1 and above
PySide2
numpy
cv2
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
#Four#
If you want to crop the image to the specified size, check TRIM and specify the width and height.
#Five#
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



YoLo用のアノテーションツールです。
以下が必要となります。
Python 3.7.1以上
PySide2
numpy
cv2
他に必要なライブラリがあれば、インストールして下さい。


以下がアノテーションを作成する流れとなります。
# 1 #
学習に必要な写真を格納したフォルダを準備。
ファイル名は連番である必要があります。
連番でない場合は、RENUMBER FILES IN A FOLDERボタンを押し、写真の入ったフォルダを指定して下さい。
#2#
PICTURE FOLDERを指定します。
ラベルを作成、又は読み込みます。
# 3 #
カメラIDを指定します。
通常は0で大丈夫だと思います。
# 4 #
画像を指定したサイズで切り出したい場合は、TRIMにチェックを入れ、幅と高さを指定します。
# 5 #
DRAWを選択し、STARTボタンを押します。
# 6 #
トリムする場合は、トリムする領域を赤枠に収め、Tキーを押します。
写真上で右クリックしながら領域を決め、ボタンを離すとアノテーションが作成されます。
ESCキーを押すと、すべてのアノテーションが削除されます。
EキーとDキーでアノテーションを選び、Bキーを押すと、選んだアノテーションのみ削除されます。
QキーとWキーでラベルが切り換えられ、AキーとSキーで写真が切り換えられます。



CAMERAを選択して、STARTボタンを押すと、USBカメラから写真が取得出来ます。
スペースキーを押して、写真を取得して下さい。



RECORDを選択して、STARTボタンを押すと、単純に動画を保存します。
事前にVIDEO FILE、幅と高さを選択して下さい。
対応していないサイズでは、保存に失敗します。



FILEを選択して、STARTボタンを押すと、動画から写真を取得出来ます。
事前にVIDEO FILEを選択して下さい。
トリムも可能です。
スペースキーを押して、写真を取得して下さい。
Zキーで動画を進めます。



RIGIONにあるボタンで、写真の回転等が可能です。
AUTOのついたボタンは、Start PosisionとEnd Position間の写真を全て処理します。
写真の最終番号がEnd Positionでない場合があるので、注意して下さい。
実際にリストボックスの最後の写真をクリックして、番号をCurrent Positionで確認する必要があります。



MIIL_DATASET_CREATER_A.pyでカメラが使えない場合は、MIIL_DATASET_CREATER_B.pyを試して下さい。
