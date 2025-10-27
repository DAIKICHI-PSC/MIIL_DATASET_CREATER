# -*- coding: utf-8 -*-

import os #OS関連処理用モジュールの読込
import sys #システム関連処理用モジュールの読込
import time #時間関連処理用モジュールの読込
import numpy as np #行列処理用モジュールの読込
import math as mt #各種計算用モジュールの読込
import cv2 #画像処理用モジュールの読込
from PySide6 import QtCore, QtGui, QtWidgets, QtMultimedia #GUI処理ライブラリの読込。
from MIIL_DETECTION_B_GUI import Ui_MainWindow #QT Designerで作成し変換したファイルの読込
from getRectanglePos import getRectanglePos #２点の何れかが選択領域の開始点（左上）になり、終点（左下）になるか判定し、さらに終点が指定した範囲にあるかるか確認するライブラリ

from ctypes import * #C言語処理用モジュールの読込
import random #乱数処理用モジュールの読込
import re #正規表現処理用モジュールの読込

#####グローバル変数########################################
cap = 0 #キャプチャー画像取得用変数
fourcc = cv2.VideoWriter_fourcc(*'MJPG') #ビデオ保存用コーデック
aviOut = cv2.VideoWriter() #ビデオ保存用変数
capLoop = 0 #動画を表示中か判定するフラグ
camWidth = 0 #動画の横サイズ
camHeight = 0 #動画の縦サイズ
sStartFlag = 0 #領域選択開始フラグ
mX1 = 0 #マウスボタンを押した時の横方向の座標
mY1 = 0 #マウスボタンを押した時の縦方向の座標

######フレームワーク以外のグローバル変数変数########################################
label_color ={} #各ラベルのカラーコード保存用ディクショナリ
color_code = 200 #カラーコード保存用変数
label_pos = {} #各ラベルのカラーパターン保存用ディクショナリ
color_pos = 0 #カラーパターン保存用変数
trimMode = 0 #トリムモード用フラグ
tw = 0 #トリムモード用Ｗｉｄｔｈ
th = 0 #トリムモード用Ｈｅｉｇｈｔ
CapWidth = 320 #キャプチャー用Ｗｉｄｔｈ
CapHeight = 240 #キャプチャー用Ｈｅｉｇｈｔ

######QImage処理用########################################
resizeWidth = 1280 #取得画像リサイズ用横サイズ
resizeHeight = 960 #取得画像リサイズ用縦サイズ
webCam = 0 #QCamera用変数
imgCap = 0 #QCameraImageCapture用変数
camNum = 1 #接続されているカメラの番号
capProcess = 0 #キャプチャー処理中か判断するフラグ
cvPic = 0 #OpenCVで表示する画像
picReady = 0 #変換処理が終了しているか判断するフラグ

hasGPU = True
netMain = None
metaMain = None
altNames = None

def sample(probs):
    s = sum(probs)
    probs = [a/s for a in probs]
    r = random.uniform(0, 1)
    for i in range(len(probs)):
        r = r - probs[i]
        if r <= 0:
            return i
    return len(probs)-1

def c_array(ctype, values):
    arr = (ctype*len(values))()
    arr[:] = values
    return arr

class BOX(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("w", c_float),
                ("h", c_float)]

class DETECTION(Structure):
    _fields_ = [("bbox", BOX),
                ("classes", c_int),
                ("prob", POINTER(c_float)),
                ("mask", POINTER(c_float)),
                ("objectness", c_float),
                ("sort_class", c_int),
                ("uc", POINTER(c_float)),
                ("points", c_int)]

class DETNUMPAIR(Structure):
    _fields_ = [("num", c_int),
                ("dets", POINTER(DETECTION))]

class IMAGE(Structure):
    _fields_ = [("w", c_int),
                ("h", c_int),
                ("c", c_int),
                ("data", POINTER(c_float))]

class METADATA(Structure):
    _fields_ = [("classes", c_int),
                ("names", POINTER(c_char_p))]

if os.name == "nt":
    cwd = os.path.dirname(__file__)
    os.environ['PATH'] = cwd + ';' + os.environ['PATH']
    winGPUdll = os.path.join(cwd, "yolo_cpp_dll.dll")
    winNoGPUdll = os.path.join(cwd, "yolo_cpp_dll_nogpu.dll")
    envKeys = list()
    for k, v in os.environ.items():
        envKeys.append(k)
    try:
        try:
            tmp = os.environ["FORCE_CPU"].lower()
            if tmp in ["1", "true", "yes", "on"]:
                raise ValueError("ForceCPU")
            else:
                print("Flag value '"+tmp+"' not forcing CPU mode")
        except KeyError:
            if 'CUDA_VISIBLE_DEVICES' in envKeys:
                if int(os.environ['CUDA_VISIBLE_DEVICES']) < 0:
                    raise ValueError("ForceCPU")
            try:
                global DARKNET_FORCE_CPU
                if DARKNET_FORCE_CPU:
                    raise ValueError("ForceCPU")
            except NameError:
                pass
        if not os.path.exists(winGPUdll):
            raise ValueError("NoDLL")
        lib = CDLL(winGPUdll, RTLD_GLOBAL)
    except (KeyError, ValueError):
        hasGPU = False
        if os.path.exists(winNoGPUdll):
            lib = CDLL(winNoGPUdll, RTLD_GLOBAL)
            print("Notice: CPU-only mode")
        else:
            lib = CDLL(winGPUdll, RTLD_GLOBAL)
            print("Environment variables indicated a CPU run, but we didn't find `"+winNoGPUdll+"`. Trying a GPU run anyway.")
else:
    linuxGPUso = os.path.join(cwd, "darknet.so")
    lib = CDLL(linuxGPUso, RTLD_GLOBAL)

lib.network_width.argtypes = [c_void_p]
lib.network_width.restype = c_int
lib.network_height.argtypes = [c_void_p]
lib.network_height.restype = c_int

copy_image_from_bytes = lib.copy_image_from_bytes
copy_image_from_bytes.argtypes = [IMAGE,c_char_p]

def network_width(net):
    return lib.network_width(net)

def network_height(net):
    return lib.network_height(net)

predict = lib.network_predict_ptr
predict.argtypes = [c_void_p, POINTER(c_float)]
predict.restype = POINTER(c_float)

if hasGPU:
    set_gpu = lib.cuda_set_device
    set_gpu.argtypes = [c_int]

init_cpu = lib.init_cpu

make_image = lib.make_image
make_image.argtypes = [c_int, c_int, c_int]
make_image.restype = IMAGE

get_network_boxes = lib.get_network_boxes
get_network_boxes.argtypes = [c_void_p, c_int, c_int, c_float, c_float, POINTER(c_int), c_int, POINTER(c_int), c_int]
get_network_boxes.restype = POINTER(DETECTION)

make_network_boxes = lib.make_network_boxes
make_network_boxes.argtypes = [c_void_p]
make_network_boxes.restype = POINTER(DETECTION)

free_detections = lib.free_detections
free_detections.argtypes = [POINTER(DETECTION), c_int]

free_batch_detections = lib.free_batch_detections
free_batch_detections.argtypes = [POINTER(DETNUMPAIR), c_int]

free_ptrs = lib.free_ptrs
free_ptrs.argtypes = [POINTER(c_void_p), c_int]

network_predict = lib.network_predict_ptr
network_predict.argtypes = [c_void_p, POINTER(c_float)]

reset_rnn = lib.reset_rnn
reset_rnn.argtypes = [c_void_p]

load_net = lib.load_network
load_net.argtypes = [c_char_p, c_char_p, c_int]
load_net.restype = c_void_p

load_net_custom = lib.load_network_custom
load_net_custom.argtypes = [c_char_p, c_char_p, c_int, c_int]
load_net_custom.restype = c_void_p

do_nms_obj = lib.do_nms_obj
do_nms_obj.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

do_nms_sort = lib.do_nms_sort
do_nms_sort.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

free_image = lib.free_image
free_image.argtypes = [IMAGE]

letterbox_image = lib.letterbox_image
letterbox_image.argtypes = [IMAGE, c_int, c_int]
letterbox_image.restype = IMAGE

load_meta = lib.get_metadata
lib.get_metadata.argtypes = [c_char_p]
lib.get_metadata.restype = METADATA

load_image = lib.load_image_color
load_image.argtypes = [c_char_p, c_int, c_int]
load_image.restype = IMAGE

rgbgr_image = lib.rgbgr_image
rgbgr_image.argtypes = [IMAGE]

predict_image = lib.network_predict_image
predict_image.argtypes = [c_void_p, IMAGE]
predict_image.restype = POINTER(c_float)

predict_image_letterbox = lib.network_predict_image_letterbox
predict_image_letterbox.argtypes = [c_void_p, IMAGE]
predict_image_letterbox.restype = POINTER(c_float)

network_predict_batch = lib.network_predict_batch
network_predict_batch.argtypes = [c_void_p, IMAGE, c_int, c_int, c_int,
                                   c_float, c_float, POINTER(c_int), c_int, c_int]
network_predict_batch.restype = POINTER(DETNUMPAIR)

def array_to_image(arr):
    import numpy as np
    # need to return old values to avoid python freeing memory
    arr = arr.transpose(2,0,1)
    c = arr.shape[0]
    h = arr.shape[1]
    w = arr.shape[2]
    arr = np.ascontiguousarray(arr.flat, dtype=np.float32) / 255.0
    data = arr.ctypes.data_as(POINTER(c_float))
    im = IMAGE(w,h,c,data)
    return im, arr

def classify(net, meta, im):
    out = predict_image(net, im)
    res = []
    for i in range(meta.classes):
        if altNames is None:
            nameTag = meta.names[i]
        else:
            nameTag = altNames[i]
        res.append((nameTag, out[i]))
    res = sorted(res, key=lambda x: -x[1])
    return res

def netDetect(net, meta, im, thresh=0.5, hier_thresh=0.5, nms=0.45):
    num = c_int(0)
    pnum = pointer(num)
    predict_image(net, im)
    dets = get_network_boxes(net, im.w, im.h, thresh, hier_thresh, None, 0, pnum, 0)
    num = pnum[0]
    if nms:
        do_nms_sort(dets, num, meta.classes, nms)
    res = []
    for j in range(num):
        for i in range(meta.classes):
            if dets[j].prob[i] > 0:
                b = dets[j].bbox
                if altNames is None:
                    nameTag = meta.names[i]
                else:
                    nameTag = altNames[i]
                res.append((nameTag, dets[j].prob[i], (b.x, b.y, b.w, b.h)))
    res = sorted(res, key=lambda x: -x[1])
    #free_image(im)
    free_detections(dets, num)
    return res

def netInit(configPath, weightPath, metaPath):
    global metaMain, netMain, altNames #pylint: disable=W0603
    if not os.path.exists(configPath):
        raise ValueError("Invalid config path `"+os.path.abspath(configPath)+"`")
    if not os.path.exists(weightPath):
        raise ValueError("Invalid weight path `"+os.path.abspath(weightPath)+"`")
    if not os.path.exists(metaPath):
        raise ValueError("Invalid data file path `"+os.path.abspath(metaPath)+"`")
    if netMain is None:
        netMain = load_net_custom(configPath.encode("ascii"), weightPath.encode("ascii"), 0, 1)  # batch size = 1
    if metaMain is None:
        metaMain = load_meta(metaPath.encode("ascii"))
    if altNames is None:
        try:
            with open(metaPath) as metaFH:
                metaContents = metaFH.read()
                match = re.search("names *= *(.*)$", metaContents, re.IGNORECASE | re.MULTILINE)
                if match:
                    result = match.group(1)
                else:
                    result = None
                try:
                    if os.path.exists(result):
                        with open(result) as namesFH:
                            namesList = namesFH.read().strip().split("\n")
                            altNames = [x.strip() for x in namesList]
                except TypeError:
                    pass
        except Exception:
            pass

#####各種処理用関数########################################
#=====メインループ処理========================================
##########
#カメラから画像を取得し物体を認識
##########
#スタートボタンで開始
def mainLoop():

    global capLoop
    global camHeight
    global sStartFlag
    global label_color
    global label_pos
    global color_pos
    global color_code
    global capProcess
    global picReady

    while(True):
        #!!!!!!!!!!openCVの処理は此処で行う!!!!!!!!!!
        if capLoop == 1: #ループモードの場合
            #print(imgCap.isReadyForCapture())
            #"Failed to configure preview format"のエラーが発生したら、カメラの番号と解像度それぞれを確認する。
            if imgCap.isReadyForCapture() == True and capProcess == 0 and picReady == 0: #キャプチャー可能状態かつキャプチャープロセス中でない場合
                webCam.searchAndLock() #カメラの動作を一時停止
                capProcess = 1 #キャプチャープロセス中とする
                imgCap.capture() #画像をカメラからキャプチャー
            if picReady == 1:
                #frame = gray(frame)
                ########## frameB = frameとした場合、frameBに対する処理がframeに反映されてしまう
                ########## frameと同じサイズの空画像frameBを作成し、そこにframeコピーする事で上記の問題は改善出来る
                frameB = np.copy(cvPic)
                
                #kernel = np.ones((3,3),np.uint8)
                #frameB = cv2.morphologyEx(frameB, cv2.MORPH_OPEN, kernel)

                #frameB = cv2.fastNlMeansDenoisingColored(frameB,None,10,10,7,21)

                if win.ui.lineEdit6.text() != '' and win.ui.lineEdit7.text() != '' and trimMode == 1: #トリムモードで領域が選択されている場合
                    frameB = frameB[int(win.ui.lineEdit7.text()):int(win.ui.lineEdit7.text()) + int(th), int(win.ui.lineEdit6.text()):int(win.ui.lineEdit6.text()) + int(tw)] #指定したサイズに画像をトリム
                    #frameB = cv2.fastNlMeansDenoisingColored(frameB,None,10,10,7,21)
                custom_image = cv2.cvtColor(frameB, cv2.COLOR_BGR2RGB) #画像をBGR形式からRGB形式に変換
                im, arr = array_to_image(custom_image) #配列から画像へ変換
                detections = netDetect(netMain, metaMain, im, float(win.ui.comboBox1.currentText())) #物体検出
                imcaption = []
                for detection in detections: #検出リスト配列から各検出を取得
                    LABEL = detection[0] #ラベル名を取得
                    if(LABEL in label_color) == False: #ラベル名がラベル色保存用ディクショナリにないか確認
                        label_color[LABEL] = color_code #ラベルに対する色を保存
                        label_pos[LABEL] = color_pos #ラベルに対するカラーパターンを保存
                        color_pos += 1
                        if color_pos == 6: #6パターン毎に色の明度を下げる
                            color_pos = 0
                            color_code -= 10
                    CONFIDENCE = detection[1] #検出物の信頼度を格納
                    pstring = LABEL+": "+str(np.rint(100 * CONFIDENCE))+"%" #ラベルと信頼度を文字列として格納
                    imcaption.append(pstring) #文字列として格納したラベルと信頼度をリスト配列に格納
                    print(pstring) #ラベルと信頼度をコンソールに表示
                    bounds = detection[2] #領域の横幅と縦幅を取得
                    xEntent = int(bounds[2]) #領域の長さ（横方向）
                    yExtent = int(bounds[3]) #領域の長さ（縦方向）
                    xCoord = int(bounds[0] - bounds[2]/2) #領域左上の横方向座標を計算
                    yCoord = int(bounds[1] - bounds[3]/2) #領域左上の縦方向座標を計算
                    TX = xCoord #領域左上の横方向座標を格納
                    TY = yCoord #領域左上の縦方向座標を格納
                    BX = xCoord + xEntent #領域右下の横方向座標を格納
                    BY = yCoord + yExtent #領域右下の縦方向座標を格納
                    cv2.rectangle(frameB, (TX + 1, TY + 1), (BX, BY), (0, 0, 0), 1) #検出領域に枠の影を描画
                    cv2.rectangle(frameB, (TX, TY), (BX - 1, BY - 1), (256, 256, 256), 1) #検出領域に枠を描画
                    font_size = 1 #フォントサイズを指定
                    #pix_size = 10
                    font = cv2.FONT_HERSHEY_PLAIN #フォントを指定
                    if label_pos[LABEL] == 0: #パターン０の色設定
                        cv2.rectangle(frameB, (TX, TY - 20), (TX + 100, TY - 1), (label_color[LABEL], 0, 0), -1) #ラベル名描画領域を塗りつぶし
                    elif label_pos[LABEL] == 1: #パターン１の色設定
                        cv2.rectangle(frameB, (TX, TY - 20), (TX + 100, TY - 1), (0, label_color[LABEL], 0), -1) #ラベル名描画領域を塗りつぶし
                    elif label_pos[LABEL] == 2: #パターン２の色設定
                        cv2.rectangle(frameB, (TX, TY - 20), (TX + 100, TY - 1), (0, 0, label_color[LABEL]), -1) #ラベル名描画領域を塗りつぶし
                    elif label_pos[LABEL] == 3: #パターン３の色設定
                        cv2.rectangle(frameB, (TX, TY - 20), (TX + 100, TY - 1), (label_color[LABEL], label_color[LABEL], 0), -1) #ラベル名描画領域を塗りつぶし
                    elif label_pos[LABEL] == 4: #パターン４の色設定
                        cv2.rectangle(frameB, (TX, TY - 20), (TX + 100, TY - 1), (label_color[LABEL], 0, label_color[LABEL]), -1) #ラベル名描画領域を塗りつぶし
                    elif label_pos[LABEL] == 5: #パターン５の色設定
                        cv2.rectangle(frameB, (TX, TY - 20), (TX + 100, TY - 1), (0, label_color[LABEL], label_color[LABEL]), -1) #ラベル名描画領域を塗りつぶし
                    cv2.rectangle(frameB, (TX + 1, TY - 20), (TX + 100, TY - 1), (0, 0, 0), 1) #ラベル名描画領域に枠の影を描画
                    cv2.rectangle(frameB, (TX, TY - 21), (TX + 100, TY - 1), (256, 256, 256), 1) #ラベル名描画領域に枠を描画
                    cv2.putText(frameB, LABEL,(TX + 3, TY - 6), font, font_size, (0, 0, 0), 1) #ラベル名の影を描画
                    cv2.putText(frameB, LABEL,(TX + 2, TY - 7), font, font_size, (256, 256, 256), 1) #ラベル名を描画
                if trimMode == 1 and sStartFlag == 1: #トリムモードが有効で領域選択中の処理
                    frameB = cv2.rectangle(frameB, (mX1, mY1), (mX1 + int(tw), mY1 + int(th)), (0, 0, 255), 1) #選択領域に枠を描画
                cv2.imshow("MIIL DETECTION",frameB) #画像を表示
                cv2.setMouseCallback("MIIL DETECTION",onMouse) #画像に対するマウス入力を取得
                if win.ui.checkBox2.isChecked() == True: #画像保存モードの場合
                    try:
                        aviOut.write(frameB) #動画保存を試みる
                    except Exception:
                        print('FAIL TO SAVE THE MOVIE. TRY OTHER RESOLUTION.') #エラーが発生した場合の処理
                picReady = 0 #キャプチャープロセス中としない
                webCam.unlock() #カメラの動作を再開
        else:
            break

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        app.processEvents() #ループ中に他のイベントを実行



#####Pysideのウィンドウ処理クラス########################################
class MainWindow1(QtWidgets.QMainWindow, Ui_MainWindow): #QtWidgets.QMainWindowを継承
#=====GUI用クラス継承の定型文========================================
    def __init__(self, parent = None): #クラス初期化時にのみ実行される関数（コンストラクタと呼ばれる）
        super(MainWindow1, self).__init__(parent) #親クラスのコンストラクタを呼び出す（親クラスのコンストラクタを再利用したい場合）　指定する引数は、親クラスのコンストラクタの引数からselfを除いた引数
        self.ui = Ui_MainWindow() #uiクラスの作成。Ui_MainWindowのMainWindowは、QT DesignerのobjectNameで設定した名前
        self.ui.setupUi(self) #uiクラスの設定
        self.ui.comboBox1.addItems(["0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1.0"]) #コンボボックスにアイテムを追加
        self.ui.comboBox1.setCurrentIndex(4) #コンボボックスのアイテムを選択
        self.ui.comboBox2.addItems(["320x240", "640x480", "800x600", "1024x768", "1280x960", "1400x1050", "2448x2048", "2592x1944", "320x180", "640x360", "1280x720", "1600x900", "1920x1080"]) #コンボボックスにアイテムを追加
        self.ui.comboBox2.setCurrentIndex(0) #コンボボックスのアイテムを選択
        self.ui.comboBox3.addItems(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]) #コンボボックスにアイテムを追加
        self.ui.comboBox3.setCurrentIndex(0) #コンボボックスのアイテムを選択
        self.ui.comboBox4.addItems(["320x240", "640x480", "800x600", "1024x768", "1280x960", "1400x1050", "2448x2048", "2592x1944", "320x180", "640x360", "1280x720", "1600x900", "1920x1080"]) #コンボボックスにアイテムを追加
        self.ui.comboBox4.setCurrentIndex(0) #コンボボックスのアイテムを選択
        #-----シグナルにメッソドを関連付け----------------------------------------
        self.ui.checkBox1.clicked.connect(self.checkBox1_clicked) #checkBox1_clickedは任意
        self.ui.checkBox2.clicked.connect(self.checkBox2_clicked) #checkBox2_clickedは任意
        #self.ui.checkBox3.clicked.connect(self.checkBox3_clicked) #checkBox3_clickedは任意
        self.ui.comboBox2.currentIndexChanged.connect(self.comboBox2_changed) #comboBox2_changedは任意
        self.ui.comboBox4.currentIndexChanged.connect(self.comboBox4_changed) #comboBox4_changedは任意
        self.ui.pushButton1.clicked.connect(self.pushButton1_clicked) #pushButton1_clickedは任意
        self.ui.pushButton2.clicked.connect(self.pushButton2_clicked) #pushButton2_clickedは任意
        self.ui.pushButton3.clicked.connect(self.pushButton3_clicked) #pushButton3_clickedは任意
        self.ui.pushButton4.clicked.connect(self.pushButton4_clicked) #pushButton4_clickedは任意
        self.ui.pushButton5.clicked.connect(self.pushButton5_clicked) #pushButton5_clickedは任意
        self.ui.pushButton6.clicked.connect(self.pushButton6_clicked) #pushButton6_clickedは任意
        self.ui.pushButton7.clicked.connect(self.pushButton7_clicked) #pushButton7_clickedは任意
        self.ui.pushButton8.clicked.connect(self.pushButton8_clicked) #pushButton8_clickedは任意
        self.ui.pushButton9.clicked.connect(self.pushButton9_clicked) #pushButton9_clickedは任意

#=====ウィジットのシグナル処理用メッソド========================================
    #-----checkBox1用イベント処理----------------------------------------
    ##########
    #トリムモードが変更された際の処理
    ##########
    def checkBox1_clicked(self):
        global tw
        global th
        global trimMode
        if self.ui.checkBox2.isChecked() == False: #録画モードではない場合
            if self.ui.checkBox1.isChecked() == True: #トリムモードの場合
                tw = self.ui.lineEdit1.text() #トリムする横幅を取得
                th = self.ui.lineEdit2.text() #トリムする縦幅を取得
                if tw.isdigit() == False or th.isdigit() == False: #トリムサイズが数字か確認
                    msgbox = QtWidgets.QMessageBox(self)
                    msgbox.setText("Need digits.") #メッセージボックスのテキストを設定
                    ret = msgbox.exec() #メッセージボックスを表示
                    self.ui.checkBox1.setChecked(False) #チェックを外す
                elif int(tw) < 100 or int(th) < 100: #トリムの最小サイズ以上か確認
                    msgbox = QtWidgets.QMessageBox(self)
                    msgbox.setText("Value should be more than 100.") #メッセージボックスのテキストを設定
                    ret = msgbox.exec() #メッセージボックスを表示
                    self.ui.checkBox1.setChecked(False) #チェックを外す
                elif self.ui.checkBox3.isChecked() == False and (int(tw) > CapWidth or int(th) > CapHeight): #トリムサイズがキャプチャーサイズ以下か確認
                    msgbox = QtWidgets.QMessageBox(self)
                    msgbox.setText("value of VIDEO SIZE should be less than the source size.") #メッセージボックスのテキストを設定
                    ret = msgbox.exec() #メッセージボックスを表示
                    self.ui.checkBox1.setChecked(False) #チェックを外す
                elif self.ui.checkBox3.isChecked() == True and (int(tw) > resizeWidth or int(th) > resizeHeight): #トリムサイズがキャプチャーサイズ以下か確認
                    msgbox = QtWidgets.QMessageBox(self)
                    msgbox.setText("value of RESIZE should be less than the source size.") #メッセージボックスのテキストを設定
                    ret = msgbox.exec() #メッセージボックスを表示
                    self.ui.checkBox1.setChecked(False) #チェックを外す
                else: #トリムモードにする
                    self.ui.pushButton8.setEnabled(False)
                    self.ui.lineEdit1.setEnabled(False)
                    self.ui.lineEdit2.setEnabled(False)
                    self.ui.comboBox2.setEnabled(False)
                    self.ui.comboBox4.setEnabled(False)
                    self.ui.checkBox3.setEnabled(False)
                    trimMode = 1
            else: #トリムモードでない場合
                self.ui.lineEdit6.setText("")
                self.ui.lineEdit7.setText("")
                self.ui.pushButton8.setEnabled(True)
                self.ui.lineEdit1.setEnabled(True)
                self.ui.lineEdit2.setEnabled(True)
                self.ui.comboBox2.setEnabled(True)
                self.ui.comboBox4.setEnabled(True)
                self.ui.checkBox3.setEnabled(True)
                trimMode = 0
        else: #録画モードの場合
            self.ui.checkBox1.setChecked(False)
            self.ui.pushButton8.setEnabled(True)
            self.ui.lineEdit1.setEnabled(True)
            self.ui.lineEdit2.setEnabled(True)
            self.ui.comboBox2.setEnabled(True)
            self.ui.comboBox4.setEnabled(True)
            self.ui.checkBox3.setEnabled(True)
            trimMode = 0
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setText("YOU CAN NOT USE TRIM MODE WHEN REC MODE IS ON.")
            ret = msgbox.exec()

    #-----checkBox2用イベント処理----------------------------------------
    ##########
    #録画モードが変更された場合の処理
    ##########
    def checkBox2_clicked(self):
        if self.ui.checkBox1.isChecked() == True:
            self.ui.checkBox2.setChecked(False)
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setText("YOU CAN NOT USE REC MODE WHEN TRIM MODE IS ON.")
            ret = msgbox.exec()

    #-----checkBox3用イベント処理----------------------------------------
    ##########
    #画像サイズ変更モードが変更された場合の処理
    ##########
    #def checkBox3_clicked(self):
        #global trimMode
        #self.ui.lineEdit6.setText('')
        #self.ui.lineEdit7.setText('')
        #self.ui.checkBox1.setChecked(False)
        #self.ui.comboBox2.setEnabled(True)
        #self.ui.comboBox4.setEnabled(True)
        #trimMode = 0

    #-----comboBox2用イベント処理----------------------------------------
    ##########
    #画像サイズが変更された際の処理
    ##########
    def comboBox2_changed(self):
        global CapWidth
        global CapHeight
        global trimMode
        res = self.ui.comboBox2.currentText() #キャプチャーサイズを取得
        rx, ry = res.split('x') #キャプチャーサイズを代入
        CapWidth = int(rx) #キャプチャー幅を記憶
        CapHeight = int(ry) #キャプチャー高さを記憶
        #self.ui.lineEdit6.setText('')
        #self.ui.lineEdit7.setText('')
        #self.ui.checkBox1.setChecked(False)
        #self.ui.comboBox2.setEnabled(True)
        #self.ui.comboBox4.setEnabled(True)
        #trimMode = 0

    #-----comboBox4用イベント処理----------------------------------------
    ##########
    #画像サイズ変更モードが変更された際の処理
    ##########
    def comboBox4_changed(self):
        global resizeWidth
        global resizeHeight
        global trimMode
        res = self.ui.comboBox4.currentText() #キャプチャーサイズを取得
        rx, ry = res.split('x') #キャプチャーサイズを代入
        resizeWidth = int(rx) #キャプチャー幅を記憶
        resizeHeight = int(ry) #キャプチャー高さを記憶
        #self.ui.lineEdit6.setText('')
        #self.ui.lineEdit7.setText('')
        #self.ui.checkBox1.setChecked(False)
        #self.ui.comboBox2.setEnabled(True)
        #self.ui.comboBox4.setEnabled(True)
        #trimMode = 0

    #-----pushButton1用イベント処理----------------------------------------
    ##########
    #検出を開始
    ##########
    def pushButton1_clicked(self):
        global capLoop
        global cap
        global aviOut
        global CapWidth
        global CapHeight
        global camNum
        global webCam
        global imgCap
        global resizeWidth
        global resizeHeight

        if self.ui.lineEdit3.text() == '':
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setText("PLEASE SET PARAMETER FILE.")
            ret = msgbox.exec()
        elif self.ui.lineEdit4.text() == '':
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setText("PLEASE SET MODEL FILE.")
            ret = msgbox.exec()
        elif self.ui.lineEdit5.text() == '':
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setText("PLEASE SET WEIGHT FILE.")
            ret = msgbox.exec()
        elif self.ui.checkBox2.isChecked() == True and self.ui.lineEdit8.text() == '':
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setText("PLEASE SET VIDEO FILE.")
            ret = msgbox.exec()
        else:
            camNum =int(self.ui.comboBox3.currentText())
            res = self.ui.comboBox2.currentText()
            cx, cy = res.split('x')
            CapWidth = int(cx)
            CapHeight = int(cy)
            res = self.ui.comboBox4.currentText()
            cx, cy = res.split('x')
            resizeWidth = int(cx)
            resizeHeight = int(cy)
            online_webcams = QtMultimedia.QCameraInfo.availableCameras() #カメラが使用可能か確認
            if not online_webcams:
                msgbox = QtWidgets.QMessageBox()
                msgbox.setWindowTitle("ERROR")
                msgbox.setText("NO CAMERA FOUND.") #メッセージボックスのテキストを設定
                pass #quit
            webCam = QtMultimedia.QCamera(online_webcams[camNum]) #カメラオブジェクトを作成
            webCam.setCaptureMode(QtMultimedia.QCamera.CaptureStillImage) #画像取得モードをイメージにする
            webCam.error.connect(lambda: self.warn(webCam.errorString())) #エラー処理
            settings = QtMultimedia.QCameraViewfinderSettings() #カメラ設定用オブジェクトを作成
            settings.setResolution(QtCore.QSize(CapWidth,CapHeight)) #解像度を設定
            webCam.setViewfinderSettings(settings) #設定を適用
            webCam.start() #カメラの動作を開始
            imgCap = QtMultimedia.QCameraImageCapture(webCam) #キャプチャー用オブジェクトを作成
            imgCap.setCaptureDestination(QtMultimedia.QCameraImageCapture.CaptureToBuffer) #画像の保存先をバッファーに設定
            imgCap.imageCaptured.connect(lambda PID, QP:self.getPic(PID, QP)) #キャプチャーイベント発生時にgetPic関数を呼び出す

            netInit(self.ui.lineEdit4.text(), self.ui.lineEdit5.text(), self.ui.lineEdit3.text()) #設定を初期化
            if self.ui.checkBox2.isChecked() == True:
                if self.ui.checkBox3.isChecked() == False:
                    aviOut = cv2.VideoWriter(self.ui.lineEdit8.text(),fourcc, 20.0, (CapWidth, CapHeight)) #録画用に設定
                else:
                    aviOut = cv2.VideoWriter(self.ui.lineEdit8.text(),fourcc, 20.0, (resizeWidth, resizeHeight)) #録画用に設定
            self.ui.pushButton1.setEnabled(False)
            self.ui.pushButton2.setEnabled(True)
            self.ui.pushButton3.setEnabled(False)
            self.ui.pushButton4.setEnabled(False)
            self.ui.pushButton5.setEnabled(False)
            self.ui.pushButton6.setEnabled(False)
            self.ui.pushButton7.setEnabled(False)
            self.ui.pushButton8.setEnabled(False)
            self.ui.pushButton9.setEnabled(False)
            self.ui.lineEdit1.setEnabled(False)
            self.ui.lineEdit2.setEnabled(False)
            self.ui.comboBox1.setEnabled(False)
            self.ui.comboBox2.setEnabled(False)
            self.ui.comboBox3.setEnabled(False)
            self.ui.comboBox4.setEnabled(False)
            self.ui.checkBox1.setEnabled(False)
            self.ui.checkBox2.setEnabled(False)
            self.ui.checkBox3.setEnabled(False)
            if capLoop == 0:
                capLoop = 1 #ループ中とする
                mainLoop() #メインループ用関数を実行

    #-----pushButton2用イベント処理----------------------------------------
    ##########
    #検出を終了
    ##########
    def pushButton2_clicked(self):
        global cap
        global capLoop
        global metaMain
        global netMain
        global altNames
        global capProcess
        global picReady
        if capLoop == 1:
            capLoop = 0 #ループ中ではないとする
            time.sleep(0.2)
        self.ui.pushButton1.setEnabled(True)
        self.ui.pushButton2.setEnabled(False)
        self.ui.pushButton3.setEnabled(True)
        self.ui.pushButton4.setEnabled(True)
        self.ui.pushButton5.setEnabled(True)
        self.ui.pushButton6.setEnabled(True)
        self.ui.pushButton7.setEnabled(True)
        self.ui.pushButton9.setEnabled(True)
        if trimMode == 0:
            self.ui.comboBox2.setEnabled(True)
            self.ui.comboBox4.setEnabled(True)
            self.ui.pushButton8.setEnabled(True)
            self.ui.lineEdit1.setEnabled(True)
            self.ui.lineEdit2.setEnabled(True)
        self.ui.comboBox1.setEnabled(True)
        self.ui.comboBox3.setEnabled(True)
        self.ui.checkBox1.setEnabled(True)
        self.ui.checkBox2.setEnabled(True)
        self.ui.checkBox3.setEnabled(True)
        netMain = None
        metaMain = None
        altNames = None
        webCam.stop()
        aviOut.release() #録画用オブジェクトを廃棄
        cv2.destroyAllWindows() #画像表示用のウィンドウを全て閉じる
        capProcess = 0
        picReady = 0

    #-----pushButton3用イベント処理----------------------------------------
    ##########
    #設定読込み処理
    ##########
    def pushButton3_clicked(self):
    #####ファイル読込
        global cap
        global CapWidth
        global CapHeight
        global trimMode
        global tw
        global th
        global resizeWidth
        global resizeHeight
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "",'mdy File (*.mdy)') #設定ファイルを選択
        if filepath: #ファイルが存在するか確認
            #####ファイル名のみの取得
            filename1 = filepath.rsplit(".", 1) #ファイルパスの文字列右側から指定文字列で分割
            filename2 = filename1[0].rsplit("/", 1) #ファイルパスの文字列右側から指定文字列で分割
            f = open(filepath, "r") #ファイルの読み込み開始
            text = f.readlines() #テキストを一行ずつ配列として読込む（行の終わりの改行コードも含めて読込む）
            f.close() #ファイルの読み込み終了
            self.ui.comboBox1.setCurrentIndex(int(text[0].replace("\n", ""))) #改行コードを削除してデータを読込む
            self.ui.comboBox2.setCurrentIndex(int(text[1].replace("\n", ""))) #改行コードを削除してデータを読込む
            res = self.ui.comboBox2.currentText() #キャプチャーサイズを取得
            rx, ry = res.split('x') #キャプチャーサイズを代入
            CapWidth = int(rx) #キャプチャー幅を記憶
            CapHeight = int(ry) #キャプチャー高さを記憶
            self.ui.comboBox3.setCurrentIndex(int(text[2].replace("\n", ""))) #改行コードを削除してデータを読込む
            self.ui.lineEdit1.setText(text[3].replace("\n", "")) #改行コードを削除してデータを読込む
            self.ui.lineEdit2.setText(text[4].replace("\n", "")) #改行コードを削除してデータを読込む
            self.ui.lineEdit3.setText(text[5].replace("\n", "")) #改行コードを削除してデータを読込む
            self.ui.lineEdit4.setText(text[6].replace("\n", "")) #改行コードを削除してデータを読込む
            self.ui.lineEdit5.setText(text[7].replace("\n", "")) #改行コードを削除してデータを読込む
            self.ui.lineEdit6.setText(text[8].replace("\n", "")) #改行コードを削除してデータを読込む
            self.ui.lineEdit7.setText(text[9].replace("\n", "")) #改行コードを削除してデータを読込む
            self.ui.lineEdit8.setText(text[10].replace("\n", "")) #改行コードを削除してデータを読込む
            tw = self.ui.lineEdit1.text()
            th = self.ui.lineEdit2.text()
            cFlag = int(text[11])
            if cFlag == 1:
                self.ui.checkBox1.setChecked(True)
                self.ui.checkBox3.setEnabled(False)
                self.ui.comboBox2.setEnabled(False)
                self.ui.comboBox4.setEnabled(False)
                self.ui.pushButton8.setEnabled(False)
                self.ui.lineEdit1.setEnabled(False)
                self.ui.lineEdit2.setEnabled(False)
                trimMode = 1
            else:
                self.ui.checkBox1.setChecked(False)
                self.ui.checkBox3.setEnabled(True)
                self.ui.pushButton8.setEnabled(True)
                self.ui.lineEdit1.setEnabled(True)
                self.ui.lineEdit2.setEnabled(True)
                self.ui.comboBox2.setEnabled(True)
                self.ui.comboBox4.setEnabled(True)
                trimMode = 0
            if int(text[12]) == 0:
                self.ui.checkBox2.setChecked(False)
            else:
                self.ui.checkBox2.setChecked(True)
            self.ui.comboBox4.setCurrentIndex(int(text[13].replace("\n", ""))) #改行コードを削除してデータを読込む
            res = self.ui.comboBox4.currentText() #キャプチャーサイズを取得
            rx, ry = res.split('x') #キャプチャーサイズを代入
            resizeWidth = int(rx) #キャプチャー幅を記憶
            resizeHeight = int(ry) #キャプチャー高さを記憶
            if int(text[14]) == 0:
                self.ui.checkBox3.setChecked(False)
            else:
                self.ui.checkBox3.setChecked(True)
            #####
    #####

    #-----pushButton4用イベント処理----------------------------------------
    ##########
    #設定書込み処理
    ##########
    def pushButton4_clicked(self):
    #####ファイル書込み
        filepath, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", "",'mdy File (*.mdy)')
        if filepath: #ファイルが存在するか確認
            #####ファイル名のみの取得
            filename1 = filepath.rsplit(".", 1) #ファイルパスの文字列右側から指定文字列で分割
            filename2 = filename1[0].rsplit("/", 1) #ファイルパスの文字列右側から指定文字列で分割
            #os.chdir(filename2[0] + "/") #カレントディレクトリをファイルパスへ変更
            f = open(filepath, "w") #ファイルの書き込み開始
            if self.ui.checkBox1.isChecked() == True:
                cFlag = 1
            else:
                cFlag = 0
            text = str(self.ui.comboBox1.currentIndex()) + "\n" + \
            str(self.ui.comboBox2.currentIndex()) + "\n" + \
            str(self.ui.comboBox3.currentIndex()) + "\n" + \
            self.ui.lineEdit1.text() + "\n" + \
            self.ui.lineEdit2.text() + "\n" + \
            self.ui.lineEdit3.text() + "\n" + \
            self.ui.lineEdit4.text() + "\n" + \
            self.ui.lineEdit5.text() + "\n" + \
            self.ui.lineEdit6.text() + "\n" + \
            self.ui.lineEdit7.text() + "\n" + \
            self.ui.lineEdit8.text() + "\n" + \
            str(cFlag) + "\n"
            if self.ui.checkBox2.isChecked() == True:
                text = text + "1\n"
            else:
                text = text + "0\n"
            text = text + str(self.ui.comboBox4.currentIndex()) + "\n"
            if self.ui.checkBox3.isChecked() == True:
                text = text + "1\n"
            else:
                text = text + "0\n"
            f.writelines(text) #空ファイルとして書込み
            f.close() #ファイルの書き込み終了
            msgbox = QtWidgets.QMessageBox(self)
            msgbox = QtWidgets.QMessageBox(self) #####メッセージボックスを準備
            msgbox.setText("FILE : Saved.") #####メッセージボックスのテキストを設定
            ret = msgbox.exec() #####メッセージボックスを表示
            #####
    #####

    #-----pushButton5用イベント処理----------------------------------------
    def pushButton5_clicked(self):
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "",'prm File (*.prm)')
        if filepath: #ファイルが存在するか確認
            self.ui.lineEdit3.setText(filepath)

    #-----pushButton6用イベント処理----------------------------------------
    def pushButton6_clicked(self):
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "",'cfg File (*.cfg)')
        if filepath: #ファイルが存在するか確認
            self.ui.lineEdit4.setText(filepath)

    #-----pushButton7用イベント処理----------------------------------------
    def pushButton7_clicked(self):
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "",'weights File (*.weights)')
        if filepath: #ファイルが存在するか確認
            self.ui.lineEdit5.setText(filepath)

    #-----pushButton8用イベント処理----------------------------------------
    def pushButton8_clicked(self):
        win.ui.lineEdit6.setText('')
        win.ui.lineEdit7.setText('')

    #-----pushButton9用イベント処理----------------------------------------
    def pushButton9_clicked(self):
        filepath, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", "",'avi File (*.avi)')
        if filepath: #ファイルが存在するか確認
            self.ui.lineEdit8.setText(filepath)

    #-----画像取得イベント処理----------------------------------------
    def getPic(self, picID, pic):
        global capProcess
        global cvPic
        global picReady
        #print(picID)
        cvPic = self.QImageToCvMat(pic) #QImageをOpenCVで表示可能なフォーマットに変換
        if self.ui.checkBox3.isChecked() == True:
            cvPic = cv2.resize(cvPic, (resizeWidth, resizeHeight)) #画像サイズ変更
        capProcess = 0
        picReady = 1

    #-----QImageからOpenCVのフォーマットへ変換する関数----------------------------------------
    def QImageToCvMat(self,img):
        img = img.convertToFormat(QtGui.QImage.Format.Format_RGB32)
        width = img.width()
        height = img.height()
        bit = img.constBits()
        CvMat = np.array(bit).reshape(height, width, 4) #  Copies the data
        return CvMat

    #-----エラー処理用関数----------------------------------------
    def warn(self, stat):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setWindowTitle("WARNNING")
        msgbox.setText(stat) #メッセージボックスのテキストを設定

#=====メインウィンドウのイベント処理========================================
    #-----ウィンドウ終了イベントのフック----------------------------------------
    def closeEvent(self, event): #event.accept() event.ignore()で処理を選択可能
        global capLoop
        if capLoop == 1: #ループ実行中の場合
            event.ignore() #メインウィンドウの終了イベントをキャンセル
        else: #ループが実行中でない場合
            event.accept() #メインウィンドウの終了イベントを実行

#=====メインウィンドウで取得したウィジットのイベント処理========================================
def onMouse(event, x, y, flags, param):  
    global capLoop
    global camWidth
    global camHeight
    global sStartFlag
    global mX1
    global mY1
    #マウスボタンがクリックされた時の処理
    if event == cv2.EVENT_LBUTTONDOWN and trimMode == 1 and win.ui.lineEdit6.text() == '':
        #マウス位置の取得
        mX1 = x
        mY1 = y
        sStartFlag = 1
    #マウスボタンがリリースされた時の処理
    elif event == cv2.EVENT_LBUTTONUP and trimMode == 1 and win.ui.lineEdit6.text() == '':
        if sStartFlag == 1:
            sStartFlag = 0
            if mX1 > 0 and mY1 >0 and mX1 + int(tw) <= CapWidth and mY1 + int(th) <= CapHeight:
                win.ui.lineEdit6.setText(str(mX1))
                win.ui.lineEdit7.setText(str(mY1))
    #マウスボタンが移動した時の処理
    elif event == cv2.EVENT_MOUSEMOVE and trimMode == 1 and win.ui.lineEdit6.text() == '':
        #マウス位置の取得
        mX1 = x
        mY1 = y

#####メイン処理（グローバル）########################################
#=====メイン処理定型文========================================
if __name__ == '__main__': #C言語のmain()に相当。このファイルが実行された場合、以下の行が実行される（モジュールとして読込まれた場合は、実行されない）
    app = QtWidgets.QApplication(sys.argv) #アプリケーションオブジェクト作成（sys.argvはコマンドライン引数のリスト）
    win = MainWindow1() #MainWindow1クラスのインスタンスを作成
    win.show() #ウィンドウを表示　win.showFullScreen()やwin.showEvent()を指定する事でウィンドウの状態を変える事が出来る
    sys.exit(app.exec()) #引数が関数の場合は、関数が終了するまで待ち、その関数の返値を上位プロセスに返す
