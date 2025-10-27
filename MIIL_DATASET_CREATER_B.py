# -*- coding: utf-8 -*-

import os #OS関連処理用モジュールの読込
import sys #システム関連処理用モジュールの読込
import time #時間関連処理用モジュールの読込
import numpy as np #行列処理用モジュールの読込
import math as mt #各種計算用モジュールの読込
import cv2 #画像処理用モジュールの読込
import glob #ファイルパス一括取得用モジュールの読込
from PySide6 import QtCore, QtGui, QtWidgets, QtMultimedia #GUI処理ライブラリの読込。
from MIIL_DATASET_CREATER_B_GUI import Ui_MainWindow #QT Designerで作成し変換したファイルの読込
from getRectanglePos import getRectanglePos #２点の何れかが選択領域の開始点（左上）になり、終点（左下）になるか判定し、さらに終点が指定した範囲にあるかるか確認するライブラリ
from getRotatedRectanglePos import getRotatedRectanglePos #座標回転後の四角内包座取得用モジュールの読込
from getRotatedPos import getRotatedPos #回転座標取得用モジュールの読込
import shutil #ドライブ操作用モジュールの読込
import random

#####グローバル変数########################################
cap = 0
#cap = cv2.VideoCapture(0) #キャプチャーオブジェクトを作成
#cap.set(3, 320) #3 = CV_CAP_PROP_FRAME_WIDTH
#cap.set(4, 240) #4 = CV_CAP_PROP_FRAME_HEIGHT
capLoop = 0 #動画を表示中か判定するフラグ
#camWidth = 320 #動画の横サイズ
#camHeight = 240 #動画の縦サイズ
sStartFlag = 0 #領域選択開始フラグ
sFlag = 0 #領域選択成功フラグ
mX1 = 0 #マウスボタンを押した時の横方向の座標
mY1 = 0 #マウスボタンを押した時の縦方向の座標
mX2 = 0 #マウスボタンを離した時の横方向の座標
mY2 = 0 #マウスボタンを離した時の縦方向の座標
ssX = 0 #選択領域開始点（左上）の横方向座標
ssY = 0 #選択領域開始点（左上）の縦方向座標
seX = 0 #選択領域終点（右下）の横方向座標（デフォルトではフレームワークで未使用）
seY = 0 #選択領域終点（右下）の縦方向座標（デフォルトではフレームワークで未使用）
sXL = 0 #選択領域の横方向座標の長さ（開始点＋長さで終点を求める場合は１を引く）
sYL = 0 #選択領域の縦方向座標の長さ（開始点＋長さで終点を求める場合は１を引く）

######フレームワーク以外のグローバル変数変数########################################
FileNum = 0 #読込んだファイル数を記憶
DirPath = "" #写真が保存してあるフォルダパスを記憶
SettingDataDir = "" #領域生データ保存用フォルダ
AnnotationDir = "" #アノテーションデータ保存用フォルダ
#DarknetAnnotationDir = "" #Darknetアノテーションデータ保存用フォルダ
SettingList = [] #設定データ保存用リスト
CurPic = "" #読込んだ画像データ
CurPicWidth = 0
CurPicHeight = 0
CapWidth = 320 #キャプチャー用Ｗｉｄｔｈ
CapHeight = 240 #キャプチャー用Ｈｅｉｇｈｔ
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
aviOut = cv2.VideoWriter()
cFlag = 0 #１フレーム読込み用
rnFlag = 0 #1を設定した場合、listWidget2のイベント発生時に処理をしないようにする。
trimMode = 0 #トリムモード用フラグ
tw = 0 #トリムモード用Ｗｉｄｔｈ
th = 0 #トリムモード用Ｈｅｉｇｈｔ
label_color ={} #各ラベルのカラーコード保存用ディクショナリ
color_code = 255 #カラーコード保存用変数
label_pos = {} #各ラベルのカラーパターン保存用ディクショナリ
color_pos = 0 #カラーパターン保存用変数
curLabel = 0 #現在のラベル番号

######QImage処理用########################################
resizeWidth = 1280 #取得画像リサイズ用横サイズ
resizeHeight = 960 #取得画像リサイズ用縦サイズ
webCam = 0 #QCamera用変数
imgCap = 0 #QCameraImageCapture用変数
camNum = 1 #接続されているカメラの番号
capProcess = 0 #キャプチャー処理中か判断するフラグ
cvPic = 0 #OpenCVで表示する画像
picReady = 0 #変換処理が終了しているか判断するフラグ

#####各種処理用関数########################################
#=====メインループ処理========================================
#スタートボタンで開始
def mainLoop():
    global capLoop
    global sStartFlag
    global sFlag
    global ssX
    global ssY
    global sXL
    global sYL
    global FileNum
    global DirPath
    global cFlag
    global aviOut
    global CurPic
    global CurPicWidth
    global CurPicHeight
    global capProcess
    global picReady
    global label_color
    global label_pos
    global color_pos
    global color_code
    global curLabel
    curLabelColor1 = 2550 #現在のラベル表示色
    curLabelColor2 = 1550 #現在のラベル表示色
    while(True):
        if capLoop == 1:
            ##########
            #カメラから写真を取得するモード
            ##########
            if win.ui.radioButton1.isChecked() == True: ##########CAMERA INPUT MODE##########
                if imgCap.isReadyForCapture() == True and capProcess == 0 and picReady == 0: #キャプチャー可能状態かつキャプチャープロセス中でない場合
                    webCam.searchAndLock() #カメラの動作を一時停止
                    capProcess = 1 #キャプチャープロセス中とする
                    imgCap.capture() #画像をカメラからキャプチャー
                if picReady == 1:
                    #frame = gray(frame)
                    ########## frameB = frameとした場合、frameBに対する処理がframeに反映されてしまう
                    ########## frameと同じサイズの空画像frameBを作成し、そこにframeコピーする事で上記の問題は改善出来る
                    frameB = np.copy(cvPic) #画像を画像にコピー
                    ##########
                    ##########
                    #!!!!!!!!!!openCVの処理は此処で行う!!!!!!!!!!
                    if trimMode == 1: #トリムモードで領域が選択されている場合
                        trimY = int((CapHeight - int(th)) / 2)
                        trimX = int((CapWidth - int(tw)) / 2)
                        frameB = frameB[trimY:trimY + int(th), trimX:trimX + int(tw)] #指定したサイズに画像をトリム
                    cv2.imshow("MIIL MDC CAMERA MODE",frameB)
                    cvKey = cv2.waitKey(1)
                    if cvKey == 32: ##########SPACE KEY##########
                        cv2.imwrite(DirPath + '/' + str(FileNum) + '.jpg', frameB)
                        time.sleep(0.5)
                        f = open(DirPath + '/' + str(FileNum) + '.txt', "w")
                        f.write('')
                        f.close()
                        win.ui.listWidget2.addItem(str(FileNum))
                        Lpos = win.ui.listWidget2.count() - 1
                        win.ui.listWidget2.setCurrentRow(Lpos)
                        app.processEvents() #ボタン処理のタイミング確認用
                        if capLoop == 1:
                            font_size = 2
                            font = cv2.FONT_HERSHEY_PLAIN
                            cv2.putText(frameB, str(FileNum) + '.jpg SAVED.' , (5, 25), font, font_size,(0, 0, 255), 1)
                            cv2.imshow("MIIL MDC CAMERA MODE",frameB)
                            app.processEvents()
                            time.sleep(1)
                        app.processEvents() #ボタン処理のタイミング確認用
                        if capLoop == 1:
                            cv2.imshow("MIIL MDC CAMERA MODE",frameB)
                        FileNum += 1
                    picReady = 0 #キャプチャープロセス中としない
                    webCam.unlock() #カメラの動作を再開
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            ##########
            #認識領域描画モード
            ##########
            elif win.ui.radioButton2.isChecked() == True: ##########LABEL DRAWING ON PICTURE MODE##########
                frame = np.copy(CurPic)
                if capLoop == 1:
                    #frame = gray(frame)
                    ########## frameB = frameとした場合、frameBに対する処理がframeに反映されてしまう
                    ########## frameと同じサイズの空画像frameBを作成し、そこにframeコピーする事で上記の問題は改善出来る
                    frameB = np.copy(frame) #画像を画像にコピー
                    ##########
                    ##########
                    #!!!!!!!!!!openCVの処理は此処で行う!!!!!!!!!!
                    if len(SettingList) > 0:
                        curLabelProcess = 0
                        for x in SettingList:
                            ROW, LABEL,TX, TY, BX, BY = x.split(',')
                            if(LABEL in label_color) == False: #ラベル名がラベル色保存用ディクショナリにないか確認
                                label_color[LABEL] = color_code #ラベルに対する色を保存
                                label_pos[LABEL] = color_pos #ラベルに対するカラーパターンを保存
                                color_pos += 1
                                if color_pos == 6: #6パターン毎に色の明度を下げる
                                    color_pos = 0
                                    color_code -= 10
                            TX = int(TX)
                            TY = int(TY)
                            BX = int(BX)
                            BY = int(BY)
                            font_size = 1 #フォントサイズを指定
                            #pix_size = 10
                            font = cv2.FONT_HERSHEY_PLAIN #フォントを指定
                            if curLabelProcess == curLabel:
                                curCol1 = int(curLabelColor1 / 10)
                                curCol2 = int(curLabelColor2 / 10)
                                cv2.putText(frameB, LABEL,(TX - 6, TY - 1), font, font_size, (curCol2, curCol2, curCol2), 1) #ラベル名の影を描画
                                cv2.putText(frameB, LABEL,(TX - 7, TY - 2), font, font_size, (curCol1, curCol1, curCol1), 1) #ラベル名を描画
                                cv2.rectangle(frameB, (TX + 1, TY + 1), (BX, BY), (curCol2, curCol2, curCol2), 1) #検出領域に枠の影を描画
                                cv2.rectangle(frameB, (TX, TY), (BX - 1, BY - 1), (curCol1, curCol1, curCol1), 1) #検出領域に枠を描画
                            else:
                                if label_pos[LABEL] == 0: #パターン０の色設定
                                    cv2.putText(frameB, LABEL,(TX - 6, TY - 1), font, font_size, (0, 0, 0), 1) #ラベル名の影を描画
                                    cv2.putText(frameB, LABEL,(TX - 7, TY - 2), font, font_size, (label_color[LABEL], 0, 0), 1) #ラベル名を描画
                                    cv2.rectangle(frameB, (TX + 1, TY + 1), (BX, BY), (0, 0, 0), 1) #検出領域に枠の影を描画
                                    cv2.rectangle(frameB, (TX, TY), (BX - 1, BY - 1), (label_color[LABEL], 0, 0), 1) #検出領域に枠を描画
                                elif label_pos[LABEL] == 1: #パターン１の色設定
                                    cv2.putText(frameB, LABEL,(TX - 6, TY - 1), font, font_size, (0, 0, 0), 1) #ラベル名の影を描画
                                    cv2.putText(frameB, LABEL,(TX - 7, TY - 2), font, font_size, (0, label_color[LABEL], 0), 1) #ラベル名を描画
                                    cv2.rectangle(frameB, (TX + 1, TY + 1), (BX, BY), (0, 0, 0), 1) #検出領域に枠の影を描画
                                    cv2.rectangle(frameB, (TX, TY), (BX - 1, BY - 1), (0, label_color[LABEL], 0), 1) #検出領域に枠を描画
                                elif label_pos[LABEL] == 2: #パターン２の色設定
                                    cv2.putText(frameB, LABEL,(TX - 6, TY - 1), font, font_size, (0, 0, 0), 1) #ラベル名の影を描画
                                    cv2.putText(frameB, LABEL,(TX - 7, TY - 2), font, font_size, (0, 0, label_color[LABEL]), 1) #ラベル名を描画
                                    cv2.rectangle(frameB, (TX + 1, TY + 1), (BX, BY), (0, 0, 0), 1) #検出領域に枠の影を描画
                                    cv2.rectangle(frameB, (TX, TY), (BX - 1, BY - 1), (0, 0, label_color[LABEL]), 1) #検出領域に枠を描画
                                elif label_pos[LABEL] == 3: #パターン３の色設定
                                    cv2.putText(frameB, LABEL,(TX - 6, TY - 1), font, font_size, (0, 0, 0), 1) #ラベル名の影を描画
                                    cv2.putText(frameB, LABEL,(TX - 7, TY - 2), font, font_size, (label_color[LABEL], label_color[LABEL], 0), 1) #ラベル名を描画
                                    cv2.rectangle(frameB, (TX + 1, TY + 1), (BX, BY), (0, 0, 0), 1) #検出領域に枠の影を描画
                                    cv2.rectangle(frameB, (TX, TY), (BX - 1, BY - 1), (label_color[LABEL], label_color[LABEL], 0), 1) #検出領域に枠を描画
                                elif label_pos[LABEL] == 4: #パターン４の色設定
                                    cv2.putText(frameB, LABEL,(TX - 6, TY - 1), font, font_size, (0, 0, 0), 1) #ラベル名の影を描画
                                    cv2.putText(frameB, LABEL,(TX - 7, TY - 2), font, font_size, (label_color[LABEL], 0, label_color[LABEL]), 1) #ラベル名を描画
                                    cv2.rectangle(frameB, (TX + 1, TY + 1), (BX, BY), (0, 0, 0), 1) #検出領域に枠の影を描画
                                    cv2.rectangle(frameB, (TX, TY), (BX - 1, BY - 1), (label_color[LABEL], 0, label_color[LABEL]), 1) #検出領域に枠を描画
                                elif label_pos[LABEL] == 5: #パターン５の色設定
                                    cv2.putText(frameB, LABEL,(TX - 6, TY - 1), font, font_size, (0, 0, 0), 1) #ラベル名の影を描画
                                    cv2.putText(frameB, LABEL,(TX - 7, TY - 2), font, font_size, (0, label_color[LABEL], label_color[LABEL]), 1) #ラベル名を描画
                                    cv2.rectangle(frameB, (TX + 1, TY + 1), (BX, BY), (0, 0, 0), 1) #検出領域に枠の影を描画
                                    cv2.rectangle(frameB, (TX, TY), (BX - 1, BY - 1), (0, label_color[LABEL], label_color[LABEL]), 1) #検出領域に枠を描画
                            curLabelProcess += 1
                        curLabelColor1 -= 5
                        curLabelColor2 -= 5
                        if curLabelColor1 < 1550:
                            curLabelColor1 = 2550
                        if curLabelColor2 < 550:
                            curLabelColor2 = 1550
                    else:
                        cv2.rectangle(frameB, (0, 0), (CurPicWidth - 1, CurPicHeight - 1), (0, 0, 255), 1)
                        font_size = 1
                        font = cv2.FONT_HERSHEY_PLAIN
                        cv2.putText(frameB, 'EXCLUDE', (10, 20),font, font_size,(0,0,255),1)
                    if sStartFlag == 1: #領域選択開始後の処理
                        frameB = cv2.rectangle(frameB, (ssX, ssY), (sXL, sYL), (0, 0, 255), 1)
                    if trimMode == 1:
                        cv2.rectangle(frameB, (mX1, mY1), (mX1 + int(tw) - 1, mY1 + int(th) - 1), (255, 0, 0), 1)
                    cvKey = cv2.waitKey(1)
                    Lcnt1 = win.ui.listWidget1.count()
                    cur1 = win.ui.listWidget1.currentRow()
                    Lcnt2 = win.ui.listWidget2.count()
                    cur2 = win.ui.listWidget2.currentRow()
                    if cvKey == 113 and Lcnt1 > 0: ##########KEY Q##########
                        if cur1 - 1 >= 0:
                            cur1 = cur1 - 1
                            win.ui.listWidget1.setCurrentRow(cur1)
                    elif cvKey == 97 and Lcnt1 > 0: ##########KEY A##########
                        if cur1 + 1 <= Lcnt1 - 1:
                            cur1 = cur1 + 1
                            win.ui.listWidget1.setCurrentRow(cur1)
                    elif cvKey == 119 and Lcnt2 > 0: ##########KEY W##########
                        if cur2 - 1 >= 0:
                            cur2 = cur2 - 1
                            win.ui.listWidget2.setCurrentRow(cur2)
                    elif cvKey == 115 and Lcnt2 > 0: ##########KEY S##########
                        if cur2 + 1 <= Lcnt2 - 1:
                            cur2 = cur2 + 1
                            win.ui.listWidget2.setCurrentRow(cur2)
                    elif cvKey == 101 and Lcnt2 > 0: ##########KEY E##########
                        if curLabel - 1 >= 0:
                            curLabel = curLabel - 1
                    elif cvKey == 100 and Lcnt2 > 0: ##########KEY D##########
                        if curLabel + 1 <= len(SettingList) - 1:
                            curLabel = curLabel + 1
                    elif cvKey == 98 and Lcnt2 > 0 and len(SettingList) > 0: ##########KEY B##########
                        del SettingList[curLabel]
                        filepath = SettingDataDir + '/' + win.ui.listWidget2.currentItem().text() + '.set'
                        filepath2 = AnnotationDir + '/' + win.ui.listWidget2.currentItem().text() + '.xml'
                        filepath3 = DirPath + '/' + win.ui.listWidget2.currentItem().text() + '.txt'
                        if len(SettingList) > 0:
                            text = ""
                            for x in SettingList:
                                text = text + x + "\n"
                            f = open(filepath, "w")
                            f.writelines(text)
                            f.close()
                            fY = CurPic.shape[0]
                            fX = CurPic.shape[1]
                            text2 = '<annotation>' + '\n<filename>' + win.ui.listWidget2.currentItem().text() + '.jpg</filename>\n<size>\n<width>' + str(fX) + '</width>' + '\n' + '<height>' + str(fY) + '</height>\n</size>\n'
                            for x in SettingList:
                                ROW, LABEL,TX, TY, BX, BY = x.split(',')
                                text2 = text2 + '<object>\n<name>' + LABEL + '</name>\n<bndbox>' + '\n' + '<xmin>' + str(int(TX)) + '</xmin>' + '\n' + '<ymin>' + str(int(TY)) + '</ymin>' + '\n' + '<xmax>' + str(int(BX)) + '</xmax>' + '\n' + '<ymax>' + str(int(BY)) + '</ymax>\n</bndbox>\n</object>\n'
                            text2 = text2 + '</annotation>\n'
                            f = open(filepath2, "w")
                            f.writelines(text2)
                            f.close()
                            text3 = ""
                            for x in SettingList:
                                ROW, LABEL,TX, TY, BX, BY = x.split(',')
                                cw = 1 / CurPicWidth
                                ch = 1 / CurPicHeight
                                cnx = (int(TX) + int(BX)) / 2
                                cny = (int(TY) + int(BY)) / 2
                                cnw = int(BX) - int(TX)
                                cnh = int(BY) - int(TY)
                                cnx = cnx * cw
                                cny = cny * ch
                                cnw = cnw * cw
                                cnh = cnh * ch
                                text3 = text3 + ROW + ' ' + str(cnx) + ' ' + str(cny) + ' ' + str(cnw) + ' ' + str(cnh) + '\n'
                            f = open(filepath3, "w")
                            f.writelines(text3)
                            f.close()
                        else:
                            if os.path.isfile(filepath):
                                os.remove(filepath)
                            if os.path.isfile(filepath2):
                                os.remove(filepath2)
                            if os.path.isfile(filepath3) == False:
                                f = open(filepath3, "w")
                                f.write('')
                                f.close()
                        curLabel = 0
                    elif cvKey == 116 and Lcnt2 > 0 and trimMode == 1: ##########KEY T##########
                        if mX1 > 0 and mY1 and mX1 + int(tw) - 1 <= CurPicWidth and mY1 + int(th) - 1 <= CurPicHeight:
                            frameB = frame[mY1:mY1 + int(th), mX1:mX1 + int(tw)]
                            cv2.imwrite(DirPath + '/' + win.ui.listWidget2.currentItem().text() +'.jpg', frameB)
                            CurPic = frameB
                            CurPicHeight = CurPic.shape[0]
                            CurPicWidth = CurPic.shape[1]
                            sFile = SettingDataDir + '/' + win.ui.listWidget2.currentItem().text() +'.set'
                            aFile = AnnotationDir + '/' + win.ui.listWidget2.currentItem().text() +'.xml'
                            dFile = DirPath + '/' + win.ui.listWidget2.currentItem().text() +'.txt'
                            if os.path.isfile(sFile):
                                os.remove(sFile)
                                SettingList.clear()
                            if os.path.isfile(aFile):
                                os.remove(aFile)
                            if os.path.isfile(dFile):
                                os.remove(dFile)
                            if os.path.isfile(dFile) == False:
                                f = open(dFile, "w")
                                f.write('')
                                f.close()
                    elif cvKey == 27 and Lcnt2 > 0: ##########KEY ESC##########
                        sFile = SettingDataDir + '/' + win.ui.listWidget2.currentItem().text() +'.set'
                        aFile = AnnotationDir + '/' + win.ui.listWidget2.currentItem().text() +'.xml'
                        dFile = DirPath + '/' + win.ui.listWidget2.currentItem().text() +'.txt'
                        if os.path.isfile(sFile):
                            os.remove(sFile)
                            SettingList.clear()
                        if os.path.isfile(aFile):
                            os.remove(aFile)
                        if os.path.isfile(dFile):
                            os.remove(dFile)
                        if os.path.isfile(dFile) == False:
                            f = open(dFile, "w")
                            f.write('')
                            f.close()
                    app.processEvents() #ボタン処理のタイミング確認用
                    if capLoop == 1:
                        currentListIndex = win.ui.listWidget2.currentRow()
                        if currentListIndex != -1:
                            cv2.imshow("MIIL MDC DRAW MODE",frameB)
                            cv2.setMouseCallback("MIIL MDC DRAW MODE", onInput)
                else:
                    break
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            ##########
            #ビデオ録画モード
            ##########
            elif win.ui.radioButton3.isChecked() == True: ##########VIDEO RECORDING MODE##########
                if imgCap.isReadyForCapture() == True and capProcess == 0 and picReady == 0: #キャプチャー可能状態かつキャプチャープロセス中でない場合
                    webCam.searchAndLock() #カメラの動作を一時停止
                    capProcess = 1 #キャプチャープロセス中とする
                    imgCap.capture() #画像をカメラからキャプチャー
                if picReady == 1:
                    frameB = np.copy(cvPic) #画像を画像にコピー  
                    if capLoop == 1:
                        cv2.imshow("MIIL MDC VIDEO MODE",frameB)
                        aviOut.write(frameB)
                        app.processEvents() #ボタン処理のタイミング確認用
                    picReady = 0 #キャプチャープロセス中としない
                    webCam.unlock() #カメラの動作を再開
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            ##########
            #ビデオファイルから写真を取得するモード
            ##########
            elif win.ui.radioButton4.isChecked() == True: ##########GET PICTRE FROM VIDEO FILE##########
                if cFlag == 1:
                    ret, frame = cap.read()
                    cFlag = 0
                if ret == True:
                    frameB = np.copy(cvPic) #画像を画像にコピー                      
                else:
                    msgbox = QtWidgets.QMessageBox()
                    msgbox.setWindowTitle("MDC")
                    msgbox.setText("Failed to process video.\nIf reading from the video is not done, please change camera ID or camera resolution to capture.") #メッセージボックスのテキストを設定
                    ret = msgbox.exec() #メッセージボックスを表示
                    break
                cvKey = cv2.waitKey(1)
                if cvKey == 32: ##########KEY SPACE##########
                    cv2.imwrite(DirPath + '/' + str(FileNum) + '.jpg', frame)
                    f = open(DirPath + '/' + str(FileNum) + '.txt', "w")
                    f.write('')
                    f.close()
                    win.ui.listWidget2.addItem(str(FileNum))
                    Lpos = win.ui.listWidget2.count() -1
                    win.ui.listWidget2.setCurrentRow(Lpos)
                    app.processEvents() #ボタン処理のタイミング確認用
                    if capLoop == 1:
                        font_size = 2
                        font = cv2.FONT_HERSHEY_PLAIN
                        cv2.putText(frameB, str(FileNum) + '.jpg SAVED.' , (5, 25), font, font_size,(0, 0, 255), 1)
                        cv2.imshow("MIIL MDC FILE MODE",frameB)
                        app.processEvents()
                    frameB = np.copy(cvPic) #画像を画像にコピー
                    app.processEvents() #ボタン処理のタイミング確認用
                    if capLoop == 1:
                        cv2.imshow("MIIL MDC FILE MODE",frameB)
                    FileNum += 1
                elif cvKey == 116 and trimMode == 1: ##########KEY T##########
                    fY = frame.shape[0]
                    fX = frame.shape[1]
                    if mX1 > 0 and mY1 and mX1 + int(tw) - 1 <= fX and mY1 + int(th) - 1 <= fY:
                        frameB = frame[mY1:mY1 + int(th), mX1:mX1 + int(tw)]
                        cv2.imwrite(DirPath + '/' + str(FileNum) +'.jpg', frameB)
                        f = open(DirPath + '/' + str(FileNum) + '.txt', "w")
                        f.write('')
                        f.close()
                        app.processEvents()
                        if capLoop == 1:
                            cv2.imshow("MIIL MDC FILE MODE",frameB)
                            app.processEvents()
                            time.sleep(1)
                        win.ui.listWidget2.addItem(str(FileNum))
                        Lpos = win.ui.listWidget2.count() -1
                        win.ui.listWidget2.setCurrentRow(Lpos)
                        FileNum += 1
                        frameB = np.copy(cvPic) #画像を画像にコピー
                elif cvKey == 122: ##########KEY Z##########
                    cFlag = 1
                app.processEvents() #ボタン処理のタイミング確認用
                if capLoop == 1:
                    if trimMode == 1:
                        cv2.rectangle(frameB, (mX1, mY1), (mX1 + int(tw) - 1, mY1 + int(th) - 1), (255, 0, 0), 1)
                    cv2.imshow("MIIL MDC FILE MODE", frameB)
                    cv2.setMouseCallback("MIIL MDC FILE MODE", onInput)
        else:
            break
        app.processEvents()

#####Pysideのウィンドウ処理クラス########################################
class MainWindow1(QtWidgets.QMainWindow): #QtWidgets.QMainWindowを継承
#=====GUI用クラス継承の定型文========================================
    def __init__(self, parent = None): #クラス初期化時にのみ実行される関数（コンストラクタと呼ばれる）
        super(MainWindow1, self).__init__(parent) #親クラスのコンストラクタを呼び出す（親クラスのコンストラクタを再利用したい場合）　指定する引数は、親クラスのコンストラクタの引数からselfを除いた引数
        self.ui = Ui_MainWindow() #uiクラスの作成。Ui_MainWindowのMainWindowは、QT DesignerのobjectNameで設定した名前
        self.ui.setupUi(self) #uiクラスの設定
        self.ui.comboBox1.addItems(["320x240", "640x480", "800x600", "1024x768", "1280x960", "1400x1050", "2592x1944", "320x180", "640x360", "1280x720", "1600x900", "1920x1080"]) #####コンボボックスにアイテムを追加
        self.ui.comboBox1.setCurrentIndex(0) #####コンボボックスのアイテムを選択
        self.ui.comboBox2.addItems(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]) #コンボボックスにアイテムを追加
        self.ui.comboBox2.setCurrentIndex(0) #コンボボックスのアイテムを選択
        self.ui.comboBox3.addItems(["320x240", "640x480", "800x600", "1024x768", "1280x960", "1400x1050", "2592x1944", "320x180", "640x360", "1280x720", "1600x900", "1920x1080"]) #####コンボボックスにアイテムを追加
        self.ui.comboBox3.setCurrentIndex(0) #####コンボボックスのアイテムを選択
        #self.ui.comboBox2.addItems(["0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1.0"]) #####コンボボックスにアイテムを追加
        #self.ui.comboBox2.setCurrentIndex(6) #####コンボボックスのアイテムを選択
        #-----シグナルにメッソドを関連付け----------------------------------------
        self.ui.listWidget2.currentRowChanged.connect(self.listWidget2_changed) #listWidget2_changedは任意（新方式）
        self.ui.comboBox1.currentIndexChanged.connect(self.comboBox1_changed) #comboBox1_changedは任意
        self.ui.checkBox1.clicked.connect(self.checkBox1_clicked) #checkBox1_clickedは任意
        self.ui.pushButton1.clicked.connect(self.pushButton1_clicked) #pushButton1_clickedは任意
        self.ui.pushButton2.clicked.connect(self.pushButton2_clicked) #pushButton2_clickedは任意
        self.ui.pushButton3.clicked.connect(self.pushButton3_clicked) #pushButton1_clickedは任意
        self.ui.pushButton4.clicked.connect(self.pushButton4_clicked) #pushButton2_clickedは任意
        self.ui.pushButton5.clicked.connect(self.pushButton5_clicked) #pushButton1_clickedは任意
        self.ui.pushButton6.clicked.connect(self.pushButton6_clicked) #pushButton2_clickedは任意
        self.ui.pushButton7.clicked.connect(self.pushButton7_clicked) #pushButton7_clickedは任意
        self.ui.pushButton8.clicked.connect(self.pushButton8_clicked) #pushButton8_clickedは任意
        self.ui.pushButton9.clicked.connect(self.pushButton9_clicked) #pushButton9_clickedは任意
        self.ui.pushButton10.clicked.connect(self.pushButton10_clicked) #pushButton10_clickedは任意
        self.ui.pushButton11.clicked.connect(self.pushButton11_clicked) #pushButton11_clickedは任意
        self.ui.pushButton12.clicked.connect(self.pushButton12_clicked) #pushButton12_clickedは任意
        self.ui.pushButton13.clicked.connect(self.pushButton13_clicked) #pushButton13_clickedは任意
        self.ui.pushButton14.clicked.connect(self.pushButton14_clicked) #pushButton14_clickedは任意
        self.ui.pushButton15.clicked.connect(self.pushButton15_clicked) #pushButton15_clickedは任意
        self.ui.pushButton16.clicked.connect(self.pushButton16_clicked) #pushButton16_clickedは任意
        self.ui.pushButton17.clicked.connect(self.pushButton17_clicked) #pushButton17_clickedは任意
        self.ui.pushButton18.clicked.connect(self.pushButton18_clicked) #pushButton18_clickedは任意
        self.ui.pushButton19.clicked.connect(self.pushButton19_clicked) #pushButton19_clickedは任意
        self.ui.pushButton20.clicked.connect(self.pushButton20_clicked) #pushButton20_clickedは任意
        self.ui.pushButton21.clicked.connect(self.pushButton21_clicked) #pushButton21_clickedは任意
        self.ui.pushButton22.clicked.connect(self.pushButton22_clicked) #pushButton22_clickedは任意
        self.ui.pushButton23.clicked.connect(self.pushButton23_clicked) #pushButton23_clickedは任意
        self.ui.pushButton24.clicked.connect(self.pushButton24_clicked) #pushButton24_clickedは任意
        self.ui.pushButton25.clicked.connect(self.pushButton25_clicked) #pushButton25_clickedは任意
        self.ui.pushButton26.clicked.connect(self.pushButton26_clicked) #pushButton26_clickedは任意
        self.ui.pushButton27.clicked.connect(self.pushButton27_clicked) #pushButton27_clickedは任意
        self.ui.pushButton28.clicked.connect(self.pushButton28_clicked) #pushButton28_clickedは任意
        self.ui.pushButton29.clicked.connect(self.pushButton29_clicked) #pushButton29_clickedは任意
        self.ui.pushButton30.clicked.connect(self.pushButton30_clicked) #pushButton30_clickedは任意
        self.ui.pushButton31.clicked.connect(self.pushButton31_clicked) #pushButton31_clickedは任意
        self.ui.pushButton32.clicked.connect(self.pushButton32_clicked) #pushButton32_clickedは任意
        self.ui.pushButton33.clicked.connect(self.pushButton33_clicked) #pushButton33_clickedは任意
        self.ui.pushButton34.clicked.connect(self.pushButton34_clicked) #pushButton34_clickedは任意
        self.ui.pushButton35.clicked.connect(self.pushButton35_clicked) #pushButton35_clickedは任意
        self.ui.pushButton36.clicked.connect(self.pushButton36_clicked) #pushButton36_clickedは任意
        self.ui.pushButton37.clicked.connect(self.pushButton37_clicked) #pushButton37_clickedは任意

#=====ウィジットのシグナル処理用メッソド========================================
    #-----checkBox1用イベント処理----------------------------------------
    def checkBox1_clicked(self):
        global tw
        global th
        global trimMode
        if self.ui.checkBox1.isChecked() == True:
            tw = self.ui.lineEdit4.text()
            th = self.ui.lineEdit5.text()
            if tw.isdigit() == False or th.isdigit() == False:
                msgbox = QtWidgets.QMessageBox(self)
                msgbox.setWindowTitle("MDC")
                msgbox.setText("Need digits.") #メッセージボックスのテキストを設定
                ret = msgbox.exec() #メッセージボックスを表示
                self.ui.checkBox1.setChecked(False) #チェックを外す
            elif int(tw) < 100 or int(th) < 100:
                msgbox = QtWidgets.QMessageBox(self)
                msgbox.setWindowTitle("MDC")
                msgbox.setText("Value should be more than 100.") #メッセージボックスのテキストを設定
                ret = msgbox.exec() #メッセージボックスを表示
                self.ui.checkBox1.setChecked(False) #チェックを外す
            #elif int(tw) > CapWidth or int(th) > CapHeight:
                #msgbox = QtWidgets.QMessageBox(self)
                #msgbox.setWindowTitle("MDC")
                #msgbox.setText("value should be less than the source size.") #メッセージボックスのテキストを設定
                #ret = msgbox.exec() #メッセージボックスを表示
                #self.ui.checkBox1.setChecked(False) #チェックを外す
            else:
                self.ui.lineEdit4.setEnabled(False)
                self.ui.lineEdit5.setEnabled(False)
                #self.ui.comboBox1.setEnabled(False)
                trimMode = 1
        else:
            self.ui.lineEdit4.setEnabled(True)
            self.ui.lineEdit5.setEnabled(True)
            #self.ui.comboBox1.setEnabled(True)
            trimMode = 0

    #-----listWidget2用イベント処理----------------------------------------
    def listWidget2_changed(self):
        global SettingDataDir #領域生データ保存用フォルダ
        global SettingList #設定データ保存用リスト
        global CurPic
        global CurPicWidth
        global CurPicHeight
        global sStartFlag
        global sFlag
        global curLabel
        curLabel = 0
        currentListIndex = self.ui.listWidget2.currentRow()
        self.ui.lineEdit6.setText(str(currentListIndex))
        if rnFlag == 0 and currentListIndex != -1: #listWidget2のイベント処理が可能な場合。
            sStartFlag = 0
            sFlag = 0
            SettingList.clear()
            picpath = DirPath + '/' + self.ui.listWidget2.currentItem().text() + '.jpg'
            if os.path.isfile(picpath):
                CurPic = cv2.imread(picpath)
                CurPicHeight = CurPic.shape[0]
                CurPicWidth = CurPic.shape[1]
                filepath = SettingDataDir + '/' + self.ui.listWidget2.currentItem().text() + '.set'
                if os.path.isfile(filepath):
                    #####ファイル名のみの取得
                    f = open(filepath, "r")
                    text = f.readlines() #改行コードも含む
                    f.close()
                    if len(text) > 0:
                        for setting in text:
                            SettingList.append(setting.replace("\n", ""))
                    else:
                        msgbox = QtWidgets.QMessageBox(self)
                        msgbox.setWindowTitle("MDC")
                        msgbox.setText("Something is wrong with setting data.") #メッセージボックスのテキストを設定
                        ret = msgbox.exec() #メッセージボックスを表示
                    #####
            else:
                msgbox = QtWidgets.QMessageBox(self)
                msgbox.setWindowTitle("MDC")
                msgbox.setText("Something is wrong with picture data.") #メッセージボックスのテキストを設定
                ret = msgbox.exec() #メッセージボックスを表示

    #-----comboBox1用イベント処理----------------------------------------
    def comboBox1_changed(self):
        #global cap
        global CapWidth
        global CapHeight
        res = self.ui.comboBox1.currentText()
        rx, ry = res.split('x')
        #cap.set(3, int(rx)) #3 = CV_CAP_PROP_FRAME_WIDTH
        #cap.set(4, int(ry)) #4 = CV_CAP_PROP_FRAME_HEIGHT
        CapWidth = int(rx)
        CapHeight = int(ry)

    #-----pushButton1用イベント処理----------------------------------------
    def pushButton1_clicked(self):
        global capLoop
        global aviOut
        global cap
        global CapWidth
        global CapHeight
        global cFlag
        global camNum
        global webCam
        global imgCap
        global resizeWidth
        global resizeHeight
        global curLabel
        curLabel = 0
        currentListIndex = self.ui.listWidget1.currentRow()
        currentListIndex2 = self.ui.listWidget2.currentRow()
        if self.ui.lineEdit1.text() == "" and self.ui.radioButton3.isChecked() != True:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText("Please set a picture folder path.") #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif self.ui.radioButton2.isChecked() == True and currentListIndex2 == -1: #FileNum == 0:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText("No file in the directory.") #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif self.ui.radioButton2.isChecked() == True and currentListIndex == -1:
            msgbox = QtWidgets.QMessageBox() #####メッセージボックスを準備
            msgbox.setWindowTitle("MDC")
            msgbox.setText("No label selected.") #####メッセージボックスのテキストを設定
            ret = msgbox.exec() #####メッセージボックスを表示
        elif self.ui.radioButton3.isChecked() == True and self.ui.lineEdit3.text() == "":
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText("Please set a video file name to save.") #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif self.ui.radioButton4.isChecked() == True and self.ui.lineEdit3.text() == "":
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText("Please open a movie file.") #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif self.ui.radioButton1.isChecked() == True and self.ui.checkBox1.isChecked() == True:
            if int(tw) > CapWidth or int(th) > CapHeight:
                msgbox = QtWidgets.QMessageBox(self)
                msgbox.setWindowTitle("MDC")
                msgbox.setText("Triming size should be less than the source size.") #メッセージボックスのテキストを設定
                ret = msgbox.exec() #メッセージボックスを表示
        elif self.ui.radioButton4.isChecked() == True and self.ui.checkBox1.isChecked() == True:
            if int(tw) > CapWidth or int(th) > CapHeight:
                msgbox = QtWidgets.QMessageBox(self)
                msgbox.setWindowTitle("MDC")
                msgbox.setText("Triming size should be less than the source size.") #メッセージボックスのテキストを設定
                ret = msgbox.exec() #メッセージボックスを表示
        else:
            self.ui.pushButton1.setEnabled(False)
            self.ui.pushButton2.setEnabled(True)
            self.ui.pushButton3.setEnabled(False)
            self.ui.pushButton4.setEnabled(False)
            self.ui.pushButton5.setEnabled(False)
            self.ui.pushButton6.setEnabled(False)
            self.ui.pushButton7.setEnabled(False)
            self.ui.pushButton8.setEnabled(False)
            self.ui.pushButton9.setEnabled(False)
            self.ui.pushButton11.setEnabled(False)
            self.ui.pushButton12.setEnabled(False)
            self.ui.pushButton17.setEnabled(False)
            self.ui.pushButton20.setEnabled(False)
            self.ui.pushButton31.setEnabled(False)
            if win.ui.radioButton2.isChecked() == True:
                self.ui.pushButton10.setEnabled(True)
                self.ui.pushButton13.setEnabled(True)
                self.ui.pushButton14.setEnabled(True)
                self.ui.pushButton15.setEnabled(True)
                self.ui.pushButton16.setEnabled(True)
                self.ui.pushButton18.setEnabled(True)
                self.ui.pushButton19.setEnabled(True)
                self.ui.pushButton21.setEnabled(True)
                self.ui.pushButton22.setEnabled(True)
                self.ui.pushButton23.setEnabled(True)
                self.ui.pushButton24.setEnabled(True)
                self.ui.pushButton25.setEnabled(True)
                self.ui.pushButton26.setEnabled(True)
                self.ui.pushButton27.setEnabled(True)
                self.ui.pushButton28.setEnabled(True)
                self.ui.pushButton29.setEnabled(True)
                self.ui.pushButton30.setEnabled(True)
                self.ui.pushButton32.setEnabled(True)
                self.ui.pushButton33.setEnabled(True)
                self.ui.pushButton34.setEnabled(True)
                self.ui.pushButton35.setEnabled(True)
                self.ui.pushButton36.setEnabled(True)
                self.ui.pushButton37.setEnabled(True)
            self.ui.radioButton1.setEnabled(False)
            self.ui.radioButton2.setEnabled(False)
            self.ui.radioButton3.setEnabled(False)
            self.ui.radioButton4.setEnabled(False)
            self.ui.lineEdit2.setEnabled(False)
            self.ui.lineEdit4.setEnabled(False)
            self.ui.lineEdit5.setEnabled(False)
            self.ui.checkBox1.setEnabled(False)
            self.ui.comboBox1.setEnabled(False)
            self.ui.comboBox2.setEnabled(False)
            self.ui.comboBox3.setEnabled(False)
            if self.ui.radioButton1.isChecked() == True:
                camNum =int(self.ui.comboBox2.currentText())
                res = self.ui.comboBox1.currentText()
                cx, cy = res.split('x')
                CapWidth = int(cx)
                CapHeight = int(cy)
                res = self.ui.comboBox3.currentText()
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
            elif self.ui.radioButton3.isChecked() == True:
                camNum =int(self.ui.comboBox2.currentText())
                res = self.ui.comboBox1.currentText()
                cx, cy = res.split('x')
                CapWidth = int(cx)
                CapHeight = int(cy)
                res = self.ui.comboBox3.currentText()
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
                rate, buttonState = QtWidgets.QInputDialog.getItem(self, "MDC", "Please choose frame rate.", ["1", "2", "3", "4", "5", "10", "20", "30", "60", "120", "144", "240"], 4, False)
                if buttonState:
                    aviOut = cv2.VideoWriter(self.ui.lineEdit3.text(), fourcc, int(rate), (resizeWidth, resizeHeight))
                else:
                    msgbox = QtWidgets.QMessageBox(self) #####メッセージボックスを準備
                    msgbox.setWindowTitle("MDC")
                    msgbox.setText("Set frame rate to 20.") #####メッセージボックスのテキストを設定
                    ret = msgbox.exec() #####メッセージボックスを表示
                    aviOut = cv2.VideoWriter(self.ui.lineEdit3.text(), fourcc, 20, (resizeWidth, resizeHeight))
            elif self.ui.radioButton4.isChecked() == True:
                #cap = cv2.VideoCapture(0)
                cap = cv2.VideoCapture(self.ui.lineEdit3.text())
                cFlag = 1
            if capLoop == 0:
                capLoop = 1
                mainLoop()

    #-----pushButton2用イベント処理----------------------------------------
    def pushButton2_clicked(self):
        global capLoop
        global sStartFlag
        global sFlag
        global capProcess
        global picReady
        if capLoop == 1:
            capLoop = 0
            time.sleep(0.2)
        sStartFlag = 0
        sFlag = 0
        self.ui.pushButton1.setEnabled(True)
        self.ui.pushButton2.setEnabled(False)
        self.ui.pushButton3.setEnabled(True)
        self.ui.pushButton4.setEnabled(True)
        self.ui.pushButton5.setEnabled(True)
        self.ui.pushButton6.setEnabled(True)
        self.ui.pushButton7.setEnabled(True)
        self.ui.pushButton8.setEnabled(True)
        self.ui.pushButton9.setEnabled(True)
        self.ui.pushButton10.setEnabled(False)
        self.ui.pushButton11.setEnabled(True)
        self.ui.pushButton12.setEnabled(True)
        self.ui.pushButton13.setEnabled(False)
        self.ui.pushButton14.setEnabled(False)
        self.ui.pushButton15.setEnabled(False)
        self.ui.pushButton16.setEnabled(False)
        self.ui.pushButton17.setEnabled(True)
        self.ui.pushButton18.setEnabled(False)
        self.ui.pushButton19.setEnabled(False)
        self.ui.pushButton20.setEnabled(True)
        self.ui.pushButton21.setEnabled(False)
        self.ui.pushButton22.setEnabled(False)
        self.ui.pushButton23.setEnabled(False)
        self.ui.pushButton24.setEnabled(False)
        self.ui.pushButton25.setEnabled(False)
        self.ui.pushButton26.setEnabled(False)
        self.ui.pushButton27.setEnabled(False)
        self.ui.pushButton28.setEnabled(False)
        self.ui.pushButton29.setEnabled(False)
        self.ui.pushButton30.setEnabled(False)
        self.ui.pushButton32.setEnabled(False)
        self.ui.pushButton33.setEnabled(False)
        self.ui.pushButton34.setEnabled(False)
        self.ui.pushButton35.setEnabled(False)
        self.ui.pushButton36.setEnabled(False)
        self.ui.pushButton37.setEnabled(False)
        self.ui.pushButton31.setEnabled(True)
        self.ui.radioButton1.setEnabled(True)
        self.ui.radioButton2.setEnabled(True)
        self.ui.radioButton3.setEnabled(True)
        self.ui.radioButton4.setEnabled(True)
        self.ui.lineEdit2.setEnabled(True)
        self.ui.lineEdit4.setEnabled(True)
        self.ui.lineEdit5.setEnabled(True)
        self.ui.checkBox1.setEnabled(True)
        #if trimMode == 0:
        self.ui.comboBox1.setEnabled(True)
        self.ui.comboBox2.setEnabled(True)
        self.ui.comboBox3.setEnabled(True)
        if self.ui.radioButton1.isChecked() == True:
            webCam.stop()
        elif self.ui.radioButton3.isChecked() == True:
            webCam.stop()
            aviOut.release() #録画用オブジェクトを廃棄
        elif self.ui.radioButton4.isChecked() == True:
            cap.release() #キャプチャー用オブジェクトを廃棄
        cv2.destroyAllWindows()
        capProcess = 0
        picReady = 0

    #-----処理開始----------------------------------------
    def process_start(self):
        self.ui.pushButton2.setEnabled(False)
        self.ui.pushButton10.setEnabled(False)
        self.ui.pushButton13.setEnabled(False)
        self.ui.pushButton14.setEnabled(False)
        self.ui.pushButton15.setEnabled(False)
        self.ui.pushButton16.setEnabled(False)
        self.ui.pushButton18.setEnabled(False)
        self.ui.pushButton19.setEnabled(False)
        self.ui.pushButton21.setEnabled(False)
        self.ui.pushButton22.setEnabled(False)
        self.ui.pushButton23.setEnabled(False)
        self.ui.pushButton24.setEnabled(False)
        self.ui.pushButton25.setEnabled(False)
        self.ui.pushButton26.setEnabled(False)
        self.ui.pushButton27.setEnabled(False)
        self.ui.pushButton28.setEnabled(False)
        self.ui.pushButton29.setEnabled(False)
        self.ui.pushButton30.setEnabled(False)
        self.ui.pushButton32.setEnabled(False)
        self.ui.pushButton33.setEnabled(False)
        self.ui.pushButton34.setEnabled(False)
        self.ui.pushButton35.setEnabled(False)
        self.ui.pushButton36.setEnabled(False)
        self.ui.pushButton37.setEnabled(False)
        self.ui.listWidget1.setEnabled(False)
        self.ui.listWidget2.setEnabled(False)
        self.ui.lineEdit7.setEnabled(False)
        self.ui.lineEdit8.setEnabled(False)

    #-----処理開始----------------------------------------
    def process_end(self):
        self.ui.pushButton2.setEnabled(True)
        self.ui.pushButton10.setEnabled(True)
        self.ui.pushButton13.setEnabled(True)
        self.ui.pushButton14.setEnabled(True)
        self.ui.pushButton15.setEnabled(True)
        self.ui.pushButton16.setEnabled(True)
        self.ui.pushButton18.setEnabled(True)
        self.ui.pushButton19.setEnabled(True)
        self.ui.pushButton21.setEnabled(True)
        self.ui.pushButton22.setEnabled(True)
        self.ui.pushButton23.setEnabled(True)
        self.ui.pushButton24.setEnabled(True)
        self.ui.pushButton25.setEnabled(True)
        self.ui.pushButton26.setEnabled(True)
        self.ui.pushButton27.setEnabled(True)
        self.ui.pushButton28.setEnabled(True)
        self.ui.pushButton29.setEnabled(True)
        self.ui.pushButton30.setEnabled(True)
        self.ui.pushButton32.setEnabled(True)
        self.ui.pushButton33.setEnabled(True)
        self.ui.pushButton34.setEnabled(True)
        self.ui.pushButton35.setEnabled(True)
        self.ui.pushButton36.setEnabled(True)
        self.ui.pushButton37.setEnabled(True)
        self.ui.listWidget1.setEnabled(True)
        self.ui.listWidget2.setEnabled(True)
        self.ui.lineEdit7.setEnabled(True)
        self.ui.lineEdit8.setEnabled(True)

    #-----pushButton3用イベント処理----------------------------------------
    def pushButton3_clicked(self):
        global FileNum #読込んだファイル数を記憶
        global DirPath #写真が保存してあるフォルダパスを記憶
        global SettingDataDir #領域生データ保存用フォルダ
        global AnnotationDir #アノテーションデータ保存用フォルダ
        global rnFlag
        #####ディレクトリ選択
        DirPath = QtWidgets.QFileDialog.getExistingDirectory(self) #写真が保存してあるフォルダを選択
        if DirPath: #フォルダが選択された場合
            rnFlag = 1 #listWidget2のイベント発生時に処理をしないようにする。
            self.ui.listWidget2.clear()
            self.ui.lineEdit1.setText(DirPath) #フォルダパスを表示
            DN = DirPath.rsplit('/', 1) #フォルダパスの文字列右側から指定文字列で分割
            SettingDataDir = DN[0] + '/' + DN[1] + '_setting'
            AnnotationDir = DN[0] + '/' + DN[1] + '_annotation'
            if os.path.isdir(SettingDataDir) == False:
                os.mkdir(SettingDataDir)
                msgbox = QtWidgets.QMessageBox(self)
                msgbox.setText(DN[1] + '_setting directory created.') #メッセージボックスのテキストを設定
                ret = msgbox.exec() #メッセージボックスを表示
            if os.path.isdir(AnnotationDir) == False:
                os.mkdir(AnnotationDir)
                msgbox = QtWidgets.QMessageBox(self)
                msgbox.setText(DN[1] + '_annotation directory created.') #メッセージボックスのテキストを設定
                ret = msgbox.exec() #メッセージボックスを表示
            NumList = [] #ファイルの連番名記憶用リスト
            FileList = glob.glob(DirPath + '/*.jpg') #フォルダ内の各ファイルパスをリスト形式で取得
            for FN in FileList: 
                FN1 = FN.rsplit(".", 1) #ファイルパスの文字列右側から指定文字列で分割
                FN1[0] = FN1[0].replace('\\', '/') #globのバグを修正
                FN2 = FN1[0].rsplit('/', 1) #ファイルパスの文字列右側から指定文字列で分割
                if FN2[1].isdigit() == True: #ファイル名が数字か確認
                    if os.path.isfile(FN1[0] + '.txt') == False: #画像と同名のテキストファイルがあるか確認
                        f = open(FN1[0] + '.txt', "w")
                        f.write('')
                        f.close()
                    NumList.append(int(FN2[1])) #ファイルの連番名を取得
                    NumList.sort()
                else:
                    print("\nNOTICE : A file whose name is not digit was found while reading jpg files.")
                    print("NOTICE : Please check " + FN2[1] + ".jpg\n")
            if len(NumList) > 0:
                FileNum = max(NumList) + 1#ファイルの連番名の最大値を取得
                self.ui.listWidget2.clear()
                for x in NumList:
                    self.ui.listWidget2.addItem(str(x))
                rnFlag = 0
                self.ui.listWidget2.setCurrentRow(0)
            else:
                rnFlag = 0
                FileNum = 0

    #-----pushButton4用イベント処理----------------------------------------
    def pushButton4_clicked(self):
    #####ファイル読込
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "",'lab File (*.lab)')
        if filepath:
            #####ファイル名のみの取得
            filename1 = filepath.rsplit(".", 1) #ファイルパスの文字列右側から指定文字列で分割
            filename2 = filename1[0].rsplit("/", 1) #ファイルパスの文字列右側から指定文字列で分割
            #os.chdir(filename2[0] + "/") #カレントディレクトリをファイルパスへ変更
            f = open(filepath, "r")
            text = f.readlines() #改行コードも含む
            f.close()
            self.ui.listWidget1.clear()
            if len(text) > 0:
                for Label in text:
                    self.ui.listWidget1.addItem(Label.replace("\n", ""))
                self.ui.listWidget1.setCurrentRow(0)
            #####
    #####

    #-----pushButton5用イベント処理----------------------------------------
    def pushButton5_clicked(self):
    #####ファイル書込み
        Lcount = self.ui.listWidget1.count()
        if Lcount == 0:
            msgbox = QtWidgets.QMessageBox(self) #####メッセージボックスを準備
            msgbox.setWindowTitle("MDC")
            msgbox.setText("No item in the list.") #####メッセージボックスのテキストを設定
            ret = msgbox.exec() #####メッセージボックスを表示
            return
        filepath, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", "",'lab File (*.lab)')
        if filepath:
            #####ファイル名のみの取得
            filename1 = filepath.rsplit(".", 1) #ファイルパスの文字列右側から指定文字列で分割
            filename2 = filename1[0].rsplit("/", 1) #ファイルパスの文字列右側から指定文字列で分割
            #os.chdir(filename2[0] + "/") #カレントディレクトリをファイルパスへ変更
            f = open(filepath, "w")
            CurRow = 0
            text = ""
            for CurRow in range(Lcount):
                text = text + self.ui.listWidget1.item(CurRow).text() + "\n"
                CurRow += 1
            f.writelines(text)
            f.close()
            msgbox = QtWidgets.QMessageBox(self) #####メッセージボックスを準備
            msgbox.setWindowTitle("MDC")
            msgbox.setText("FILE : Saved.") #####メッセージボックスのテキストを設定
            ret = msgbox.exec() #####メッセージボックスを表示
            #####
    #####

    #-----pushButton6用イベント処理----------------------------------------
    def pushButton6_clicked(self):
    #####リストウィジットにアイテムを追加
        if self.ui.lineEdit2.text() == "":
            msgbox = QtWidgets.QMessageBox(self) #####メッセージボックスを準備
            msgbox.setWindowTitle("MDC")
            msgbox.setText("No text to add.") #####メッセージボックスのテキストを設定
            ret = msgbox.exec() #####メッセージボックスを表示
        else:
            self.ui.listWidget1.addItem(self.ui.lineEdit2.text())
            self.ui.listWidget1.setCurrentRow(0)
    #####

    #-----pushButton7用イベント処理----------------------------------------
    def pushButton7_clicked(self):
    #####リストウィジットにアイテムを追加
        currentListIndex = self.ui.listWidget1.currentRow()
        if currentListIndex == -1:
            msgbox = QtWidgets.QMessageBox(self) #####メッセージボックスを準備
            msgbox.setWindowTitle("MDC")
            msgbox.setText("No item selected.") #####メッセージボックスのテキストを設定
            ret = msgbox.exec() #####メッセージボックスを表示
        else:
            self.ui.listWidget1.takeItem(currentListIndex)
    #####

    #-----pushButton8用イベント処理----------------------------------------
    def pushButton8_clicked(self):
    #####ファイル読込
        filepath, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Open File", "",'avi File (*.avi)')
        if filepath:
            self.ui.lineEdit3.setText(filepath)

    #-----pushButton9用イベント処理----------------------------------------
    def pushButton9_clicked(self):
    #####ファイル読込
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "",'avi File (*.avi)')
        if filepath:
            self.ui.lineEdit3.setText(filepath)

    #-----pushButton10用イベント処理----------------------------------------
    def pushButton10_clicked(self):
    #####リストウィジットにアイテムを追加
        currentListIndex = self.ui.listWidget2.currentRow()
        if currentListIndex == -1:
            msgbox = QtWidgets.QMessageBox(self) #####メッセージボックスを準備
            msgbox.setWindowTitle("MDC")
            msgbox.setText("No item selected.") #####メッセージボックスのテキストを設定
            ret = msgbox.exec() #####メッセージボックスを表示
        else:
            fName = self.ui.listWidget2.currentItem().text()
            self.ui.listWidget2.takeItem(currentListIndex)
            pFile = DirPath + '/' + fName +'.jpg'
            sFile = SettingDataDir + '/' + fName +'.set'
            aFile = AnnotationDir + '/' + fName +'.xml'
            dFile = DirPath + '/' + fName +'.txt'
            if os.path.isfile(pFile):
                os.remove(pFile)
            if os.path.isfile(sFile):
                os.remove(sFile)
            if os.path.isfile(aFile):
                os.remove(aFile)
            if os.path.isfile(dFile):
                os.remove(dFile)
            cv2.destroyAllWindows()
    #####

    #-----pushButton11用イベント処理----------------------------------------
    def pushButton11_clicked(self):
        msgbox = QtWidgets.QMessageBox(self)
        ret = msgbox.question(None, "MDC", "Renumber file names.", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) #選択用メッセージボックスを表示
        if ret == QtWidgets.QMessageBox.Yes: #メッセージボックスでYESが選択された場合
            cn, buttonState = QtWidgets.QInputDialog.getInt(self, "MDC", "Please input starting number.", 0, 0, 9999999, 1)
            if buttonState:
                global DirPath #写真が保存してあるフォルダパスを記憶
                global SettingDataDir #領域生データ保存用フォルダ
                global AnnotationDir #アノテーションデータ保存用フォルダ
                #global DarknetAnnotationDir #アノテーションデータ保存用フォルダ
                global rnFlag
                global FileNum
                lCount = self.ui.listWidget2.count()
                if lCount == 0:
                    msgbox = QtWidgets.QMessageBox(self)
                    msgbox.setWindowTitle("MDC")
                    msgbox.setText('No item in the list.') #メッセージボックスのテキストを設定
                    ret = msgbox.exec() #メッセージボックスを表示
                #elif cn.isdigit() == False:
                    #msgbox = QtWidgets.QMessageBox(self)
                    #msgbox.setWindowTitle("MDC")
                    #msgbox.setText('Please input digits.') #メッセージボックスのテキストを設定
                    #ret = msgbox.exec() #メッセージボックスを表示         
                else:
                    rnFlag = 1
                    iNum = int(cn)
                    cNum = 0
                    LWitems = []
                    progC = 0
                    progP = 0
                    prog = QtWidgets.QProgressDialog('Renaming files.', None, 0, 100, None, QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.CustomizeWindowHint)
                    prog.setWindowTitle("MDC")
                    prog.setFixedSize(prog.sizeHint())
                    prog.setValue(progP)
                    prog.show()
                    while(True):
                        self.ui.listWidget2.setCurrentRow(cNum)
                        LWitems.append(iNum)
                        pFile = DirPath + '/' + win.ui.listWidget2.currentItem().text() +'.jpg'
                        npFile = DirPath + '/a' + str(iNum) +'.jpg'
                        sFile = SettingDataDir + '/' + win.ui.listWidget2.currentItem().text() +'.set'
                        nsFile = SettingDataDir + '/a' + str(iNum) +'.set'
                        aFile = AnnotationDir + '/' + win.ui.listWidget2.currentItem().text() +'.xml'
                        naFile = AnnotationDir + '/a' + str(iNum) +'.xml'
                        daFile = DirPath + '/' + win.ui.listWidget2.currentItem().text() +'.txt'
                        dnaFile = DirPath + '/a' + str(iNum) +'.txt'
                        if os.path.isfile(pFile):
                            os.rename(pFile, npFile)
                        if os.path.isfile(sFile):
                            os.rename(sFile, nsFile)
                        if os.path.isfile(aFile):
                            os.rename(aFile, naFile)
                        if os.path.isfile(daFile):
                            os.rename(daFile, dnaFile)
                        iNum += 1
                        cNum += 1
                        progC += 1
                        progP = int(100 * progC / (lCount * 2))
                        prog.setValue(progP)
                        app.processEvents()
                        if cNum > lCount - 1:
                            break
                    iNum = int(cn)
                    cNum = 0
                    while(True):
                        pFile = DirPath + '/a' + str(iNum) +'.jpg'
                        npFile = DirPath + '/' + str(iNum) +'.jpg'
                        sFile = SettingDataDir + '/a' + str(iNum) +'.set'
                        nsFile = SettingDataDir + '/' + str(iNum) +'.set'
                        aFile = AnnotationDir + '/a' + str(iNum) +'.xml'
                        naFile = AnnotationDir + '/' + str(iNum) +'.xml'
                        daFile = DirPath + '/a' + str(iNum) +'.txt'
                        dnaFile = DirPath + '/' + str(iNum) +'.txt'
                        if os.path.isfile(pFile):
                            os.rename(pFile, npFile)
                        if os.path.isfile(sFile):
                            os.rename(sFile, nsFile)
                        if os.path.isfile(aFile):
                            os.rename(aFile, naFile)
                            f = open(naFile, "r")
                            text = f.readlines() #改行コードも含む
                            f.close()
                            text2 = ""
                            if len(text) > 0:
                                for line in text:
                                    if(("<filename>" in line) == True):
                                        line = '<filename>' + str(iNum) +'.jpg' + '</filename>\n'
                                    text2 = text2 + line
                                f = open(naFile, "w")
                                f.write(text2)
                                f.close()
                        if os.path.isfile(daFile):
                            os.rename(daFile, dnaFile)
                        iNum += 1
                        cNum += 1
                        progC += 1
                        progP = int(100 * progC / (lCount * 2))
                        prog.setValue(progP)
                        app.processEvents()
                        if cNum > lCount - 1:
                            break
                    self.ui.listWidget2.clear()
                    LWitems.sort()
                    for x in LWitems:
                        self.ui.listWidget2.addItem(str(x))
                    FileNum = iNum
                    rnFlag = 0
                    self.ui.listWidget2.setCurrentRow(0)
                    msgbox = QtWidgets.QMessageBox(self)
                    msgbox.setWindowTitle("MDC")
                    msgbox.setText('Reumbering done.') #メッセージボックスのテキストを設定
                    ret = msgbox.exec() #メッセージボックスを表示

    #-----pushButton12用イベント処理----------------------------------------
    def pushButton12_clicked(self):
        ##########
        #指定したディレクトリのファイル名を連番にする
        ##########
        msgbox = QtWidgets.QMessageBox(self)
        ret = msgbox.question(None, "MDC", "If you would like to renumber file names to serial number, press yes.\nDo not renumber the files in the folder you are currently editing or the folder you have edited.\nOtherwise the data is going to be corrupted!!!\n\nThis function renumbers any files in the folder.\nPlease only place files you want to renumber in the folder.", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) #選択用メッセージボックスを表示
        if ret == QtWidgets.QMessageBox.Yes: #メッセージボックスでYESが選択された場合
            #####ディレクトリ選択
            tmpPath = QtWidgets.QFileDialog.getExistingDirectory(self) #写真が保存してあるフォルダを選択
            if tmpPath: #フォルダが選択された場合
                cn, buttonState = QtWidgets.QInputDialog.getInt(self, "MDC", "Please input starting number.", 0, 0, 9999999, 1)
                if buttonState:
                    FileList = glob.glob(tmpPath + '/*.jpg') #フォルダ内の各ファイルパスをリスト形式で取得
                    FileList2 = []
                    lCount = len(FileList)
                    progC = 0
                    progP = 0
                    prog = QtWidgets.QProgressDialog('Renaming files.', None, 0, 100, None, QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.CustomizeWindowHint)
                    prog.setWindowTitle("MDC")
                    prog.setFixedSize(prog.sizeHint())
                    prog.setValue(progP)
                    prog.show()
                    for FN in FileList:
                        FileList2.append(FN.replace('\\', '/')) #globのバグを修正
                        print(str(len(FileList)))
                    iNum = cn
                    rF = []
                    for FN in FileList2:
                        npFile = tmpPath + '/abcdefghijklmnopqrstuvqxyz' + str(iNum) +'.jpg'
                        os.rename(FN, npFile)
                        iNum += 1
                        progC += 1
                        progP = int(100 * progC / (lCount * 2))
                        prog.setValue(progP)
                        app.processEvents()
                        rF.append(npFile)
                    iNum = cn
                    for FN in rF:
                        npFile = tmpPath + '/' + str(iNum) +'.jpg'
                        os.rename(FN, npFile)
                        iNum += 1
                        progC += 1
                        progP = int(100 * progC / (lCount * 2))
                        prog.setValue(progP)
                        app.processEvents()
                    msgbox = QtWidgets.QMessageBox(self)
                    msgbox.setWindowTitle("MDC")
                    msgbox.setText('Reumbering done.') #メッセージボックスのテキストを設定
                    ret = msgbox.exec() #メッセージボックスを表示
                #####

    #-----pushButton13用イベント処理----------------------------------------
    def pushButton13_clicked(self):
        ##########
        #現在の画像を回転させ保存する
        ##########
        degree, buttonState = QtWidgets.QInputDialog.getItem(self, "MDC", "Please choose dgrees to rotate the pictures.", ["1", "2", "3", "4", "5", "8", "10", "15", "30", "60", "90", "120", "180"], 2, False)
        if buttonState:
            self.process_start()
            if self.ui.listWidget2.count() != -1:
                self.rotatePic(int(degree))
            self.process_end()

    #-----pushButton14用イベント処理----------------------------------------
    def pushButton14_clicked(self):
        ##########
        #現在の画像の輝度と色合いを変えて保存する
        ##########
        text, buttonState = QtWidgets.QInputDialog.getItem(self, "MDC", "Please choose what to change and add to the list.", ["GAMMA", "COLOR", "GAMMA AND COLOR"], 0, False)
        if buttonState:
            if text == "GAMMA":
                flag = 0
            elif text == "COLOR":
                flag = 1
            else:
                flag = 2
            self.process_start()
            if self.ui.listWidget2.count() != -1:
                self.cngGamma(flag)
            self.process_end()

    #-----pushButton15用イベント処理----------------------------------------
    def pushButton15_clicked(self):
        ##########
        #リストウィジット内全ての画像ファイルを回転させ保存する
        ##########
        SP = self.ui.lineEdit7.text()
        EP = self.ui.lineEdit8.text()
        if self.ui.listWidget2.count() == -1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('No file in the directory.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif SP.isdigit() == False:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Please input digit for start position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif EP.isdigit() == False:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Please input digit for end position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(SP) > int(EP):
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Start position should be equal or smaller than end position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(SP) > self.ui.listWidget2.count() - 1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Start position should be equal or smaller than max picture position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(EP) > self.ui.listWidget2.count() - 1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('End position should be equal or smaller than max picture position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        else:
            SP = int(SP)
            EP = int(EP) + 1

            msgbox = QtWidgets.QMessageBox(self)
            ret = msgbox.question(None, "MDC", "Create rotated files from pictures in the list?", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) #選択用メッセージボックスを表示
            if ret == QtWidgets.QMessageBox.Yes: #メッセージボックスでYESが選択された場合
                degree, buttonState = QtWidgets.QInputDialog.getItem(self, "MDC", "Please choose dgrees to rotate the pictures.", ["1", "2", "3", "4", "5", "8", "10", "15", "30", "60", "90", "120", "180"], 2, False)
                if buttonState:
                    step, buttonState = QtWidgets.QInputDialog.getInt(self, "MDC", "Please choose steps.", 1, 0, 100, 1)
                    if buttonState:
                        self.process_start()
                        #listItemCount = self.ui.listWidget2.count()
                        #if self.ui.listWidget2.count() != -1:
                        count = 0
                        for x in range(SP, EP):
                            self.ui.listWidget2.setCurrentRow(x)
                            count += 1
                            if count == step:
                                self.rotatePic(int(degree))
                                app.processEvents()
                                count = 0
                        self.process_end()

    #-----pushButton16用イベント処理----------------------------------------
    def pushButton16_clicked(self):
        ##########
        #リストウィジット内全ての画像ファイルを輝度と色合いを変えて保存する
        ##########
        SP = self.ui.lineEdit7.text()
        EP = self.ui.lineEdit8.text()
        if self.ui.listWidget2.count() == -1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('No file in the directory.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif SP.isdigit() == False:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Please input digit for start position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif EP.isdigit() == False:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Please input digit for end position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(SP) > int(EP):
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Start position should be equal or smaller than end position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(SP) > self.ui.listWidget2.count() - 1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Start position should be equal or smaller than max picture position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(EP) > self.ui.listWidget2.count() - 1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('End position should be equal or smaller than max picture position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        else:
            SP = int(SP)
            EP = int(EP) + 1

            msgbox = QtWidgets.QMessageBox(self)
            ret = msgbox.question(None, "MDC", "Create colored files from pictures in the list?", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) #選択用メッセージボックスを表示
            if ret == QtWidgets.QMessageBox.Yes: #メッセージボックスでYESが選択された場合
                text, buttonState = QtWidgets.QInputDialog.getItem(self, "MDC", "Please choose what to change and add to the list.", ["GAMMA", "COLOR", "GAMMA AND COLOR"], 0, False)
                if buttonState:
                    if text == "GAMMA":
                        flag = 0
                    elif text == "COLOR":
                        flag = 1
                    else:
                        flag = 2
                    step, buttonState = QtWidgets.QInputDialog.getInt(self, "MDC", "Please choose steps.", 1, 0, 100, 1)
                    if buttonState:
                        self.process_start()
                        count = 0
                        for x in range(SP, EP):
                            self.ui.listWidget2.setCurrentRow(x)
                            count += 1
                            if count == step:
                                self.cngGamma(flag)
                                app.processEvents()
                                count = 0
                        self.process_end()

    #-----pushButton17用イベント処理----------------------------------------
    def pushButton17_clicked(self):
        ##########
        #ビデオから画像ファイルを自動保存
        ##########
        msgbox = QtWidgets.QMessageBox(self)
        ret = msgbox.question(None, "MDC", "Get pictures from a video file automaticaly?\nPlease do not choose the foulder you are currently editing.", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) #選択用メッセージボックスを表示
        if ret == QtWidgets.QMessageBox.Yes: #メッセージボックスでYESが選択された場合
            filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Load File", "",'avi File (*.avi)')
            if filepath: #ファイルパスが選択されているか確認
                DirPath = QtWidgets.QFileDialog.getExistingDirectory(self) #フォルダの選択
                if DirPath: #フォルダが選択された場合
                    intVal, buttonState = QtWidgets.QInputDialog.getInt(self, "MDC", "Please set first file number.", 0, 0, 1000000, 1)
                    if buttonState:
                        step, buttonState = QtWidgets.QInputDialog.getInt(self, "MDC", "Please choose steps.", 1, 0, 100, 1)
                        if buttonState:
                            cap = cv2.VideoCapture(filepath)
                            capNum = intVal
                            count = 0
                            while(True):
                                ret, frame = cap.read()
                                if ret == True:
                                    count += 1
                                    if count == step:
                                        if trimMode == 1: #トリムモードで領域が選択されている場合
                                            vidHeight, vidWidth = frame.shape[:2]
                                            trimH = int((vidHeight - int(th)) / 2)
                                            trimW = int((vidWidth - int(tw)) / 2)
                                            frame = frame[trimH:trimH + int(th), trimW:trimW + int(tw)] #指定したサイズに画像をトリム
                                        cv2.imshow("CAPTURE",frame)
                                        cv2.imwrite(DirPath + '/' + str(capNum) + '.jpg', frame)
                                        capNum += 1
                                        count = 0
                                        app.processEvents() #ボタン処理のタイミング確認用
                                else:
                                    cap.release() #キャプチャー用オブジェクトを廃棄
                                    cv2.destroyAllWindows()
                                    msgbox = QtWidgets.QMessageBox()
                                    msgbox.setWindowTitle("MDC")
                                    msgbox.setText("Done.") #メッセージボックスのテキストを設定
                                    ret = msgbox.exec() #メッセージボックスを表示
                                    break

    #-----pushButton18用イベント処理----------------------------------------
    def pushButton18_clicked(self):
        ##########
        #現在の画像を射影変換し保存する
        ##########
        self.process_start()
        if self.ui.listWidget2.count() != -1:
            self.persPic()
        self.process_end()

    #-----pushButton19用イベント処理----------------------------------------
    def pushButton19_clicked(self):
        ##########
        #リストウィジット内の全ての画像を射影変換し保存する
        ##########
        SP = self.ui.lineEdit7.text()
        EP = self.ui.lineEdit8.text()
        if self.ui.listWidget2.count() == -1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('No file in the directory.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif SP.isdigit() == False:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Please input digit for start position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif EP.isdigit() == False:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Please input digit for end position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(SP) > int(EP):
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Start position should be equal or smaller than end position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(SP) > self.ui.listWidget2.count() - 1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Start position should be equal or smaller than max picture position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(EP) > self.ui.listWidget2.count() - 1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('End position should be equal or smaller than max picture position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        else:
            SP = int(SP)
            EP = int(EP) + 1

            step, buttonState = QtWidgets.QInputDialog.getInt(self, "MDC", "Please choose steps.", 1, 0, 100, 1)
            if buttonState:
                self.process_start()
                count = 0
                for x in range(SP, EP):
                    self.ui.listWidget2.setCurrentRow(x)
                    count += 1
                    if count == step:
                        self.persPic()
                        app.processEvents()
                        count = 0
                self.process_end()

    #-----pushButton20用イベント処理----------------------------------------
    def pushButton20_clicked(self):
        ##########
        #指定したディレクトリの画像サイズを全て変更する
        ##########
        msgbox = QtWidgets.QMessageBox(self)
        ret = msgbox.question(None, "MDC", "If you would like to resize pictures, press yes.\nDo not resise the files in the folder you are currently editing or the folder you have edited.\nOtherwise the data is going to be corrupted!!!\n\nThis function resize any pictures in the folder.\nPlease only place files you want to resize in the folder.", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) #選択用メッセージボックスを表示
        if ret == QtWidgets.QMessageBox.Yes: #メッセージボックスでYESが選択された場合
            #####ディレクトリ選択
            tmpPath = QtWidgets.QFileDialog.getExistingDirectory(self) #写真が保存してあるフォルダを選択
            if tmpPath: #フォルダが選択された場合
                text, buttonState = QtWidgets.QInputDialog.getItem(self, "MDC", "Choose a way to resize pictures", ["CHOOSE PERCENTAGE", "INPUT PERCENTAGE", "INPUT SIZE"], 0, False)
                if buttonState:
                    if text == "CHOOSE PERCENTAGE":
                        percentage, buttonState = QtWidgets.QInputDialog.getItem(self, "MDC", "Please choose percentage to resize the pictures.", ["10", "20", "30", "40", "50", "60", "70", "80", "90", "110", "120", "130", "140", "150", "160", "170", "180", "190", "200"], 4, False)
                        if buttonState:
                            percentage = int(percentage) * 0.01
                            FileList = glob.glob(tmpPath + '/*.jpg') #フォルダ内の各ファイルパスをリスト形式で取得
                            FileList2 = []
                            lCount = len(FileList)
                            progC = 0
                            progP = 0
                            prog = QtWidgets.QProgressDialog('Resize files.', None, 0, 100, None, QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.CustomizeWindowHint)
                            prog.setWindowTitle("MDC")
                            prog.setFixedSize(prog.sizeHint())
                            prog.setValue(progP)
                            prog.show()
                            for FN in FileList:
                                FileList2.append(FN.replace('\\', '/')) #globのバグを修正
                            for FN in FileList2:
                                img = cv2.imread(FN)
                                height = img.shape[0]
                                width = img.shape[1]
                                img2 = cv2.resize(img , (int(width * percentage), int(height * percentage)))
                                cv2.imwrite(FN, img2)
                                progC += 1
                                progP = int(100 * progC / (lCount))
                                prog.setValue(progP)
                                app.processEvents()
                            msgbox = QtWidgets.QMessageBox(self)
                            msgbox.setWindowTitle("MDC")
                            msgbox.setText('Resizing done.') #メッセージボックスのテキストを設定
                            ret = msgbox.exec() #メッセージボックスを表示
                    if text == "INPUT PERCENTAGE":
                        percentage, buttonState = QtWidgets.QInputDialog.getInt(self, "MDC", "Please input percentage to resize the pictures.", 50, 10, 200, 10)
                        if buttonState:
                            percentage = int(percentage) * 0.01
                            FileList = glob.glob(tmpPath + '/*.jpg') #フォルダ内の各ファイルパスをリスト形式で取得
                            FileList2 = []
                            lCount = len(FileList)
                            progC = 0
                            progP = 0
                            prog = QtWidgets.QProgressDialog('Resize files.', None, 0, 100, None, QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.CustomizeWindowHint)
                            prog.setWindowTitle("MDC")
                            prog.setFixedSize(prog.sizeHint())
                            prog.setValue(progP)
                            prog.show()
                            for FN in FileList:
                                FileList2.append(FN.replace('\\', '/')) #globのバグを修正
                            for FN in FileList2:
                                img = cv2.imread(FN)
                                height = img.shape[0]
                                width = img.shape[1]
                                img2 = cv2.resize(img , (int(width * percentage), int(height * percentage)))
                                cv2.imwrite(FN, img2)
                                progC += 1
                                progP = int(100 * progC / (lCount))
                                prog.setValue(progP)
                                app.processEvents()
                            msgbox = QtWidgets.QMessageBox(self)
                            msgbox.setWindowTitle("MDC")
                            msgbox.setText('Resizing done.') #メッセージボックスのテキストを設定
                            ret = msgbox.exec() #メッセージボックスを表示
                    if text == "INPUT SIZE":
                        width, buttonState = QtWidgets.QInputDialog.getInt(self, "MDC", "Please input width to resize the pictures.", 608, 1, 99999, 1)
                        if buttonState:
                            height, buttonState = QtWidgets.QInputDialog.getInt(self, "MDC", "Please input height to resize the pictures.", 608, 1, 99999, 1)
                            if buttonState:
                                FileList = glob.glob(tmpPath + '/*.jpg') #フォルダ内の各ファイルパスをリスト形式で取得
                                FileList2 = []
                                lCount = len(FileList)
                                progC = 0
                                progP = 0
                                prog = QtWidgets.QProgressDialog('Resize files.', None, 0, 100, None, QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.CustomizeWindowHint)
                                prog.setWindowTitle("MDC")
                                prog.setFixedSize(prog.sizeHint())
                                prog.setValue(progP)
                                prog.show()
                                for FN in FileList:
                                    FileList2.append(FN.replace('\\', '/')) #globのバグを修正
                                for FN in FileList2:
                                    img = cv2.imread(FN)
                                    #height = img.shape[0]
                                    #width = img.shape[1]
                                    img2 = cv2.resize(img , (width, height))
                                    cv2.imwrite(FN, img2)
                                    progC += 1
                                    progP = int(100 * progC / (lCount))
                                    prog.setValue(progP)
                                    app.processEvents()
                                msgbox = QtWidgets.QMessageBox(self)
                                msgbox.setWindowTitle("MDC")
                                msgbox.setText('Resizing done.') #メッセージボックスのテキストを設定
                                ret = msgbox.exec() #メッセージボックスを表示
            #####

    #-----pushButton21用イベント処理----------------------------------------
    def pushButton21_clicked(self):
        ##########
        #画像サイズを変更する
        ##########
        if self.ui.listWidget2.count() != -1:
            self.process_start()
            msgbox = QtWidgets.QMessageBox(self)
            ret = msgbox.question(None, "MDC", "Resize the picture currently selected?", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) #選択用メッセージボックスを表示
            if ret == QtWidgets.QMessageBox.Yes: #メッセージボックスでYESが選択された場合
                text, buttonState = QtWidgets.QInputDialog.getItem(self, "MDC", "Choose a way to resize pictures", ["CHOOSE PERCENTAGE", "INPUT PERCENTAGE", "INPUT SIZE"], 0, False)
                if buttonState:
                    if text == "CHOOSE PERCENTAGE":
                        percentage, buttonState = QtWidgets.QInputDialog.getItem(self, "MDC", "Please choose percentage to resize the pictures.", ["10", "20", "30", "40", "50", "60", "70", "80", "90", "110", "120", "130", "140", "150", "160", "170", "180", "190", "200"], 4, False)
                        if buttonState:
                            self.resizePic(percentage, 0, 0, mode = 0)
                    if text == "INPUT PERCENTAGE":
                        percentage, buttonState = QtWidgets.QInputDialog.getInt(self, "MDC", "Please input percentage to resize the pictures.", 50, 10, 200, 10)
                        if buttonState:
                            self.resizePic(percentage, 0, 0, mode = 0)
                    if text == "INPUT SIZE":
                        width, buttonState = QtWidgets.QInputDialog.getInt(self, "MDC", "Please input width to resize the pictures.", 608, 1, 99999, 1)
                        if buttonState:
                            height, buttonState = QtWidgets.QInputDialog.getInt(self, "MDC", "Please input height to resize the pictures.", 608, 1, 99999, 1)
                            if buttonState:
                                self.resizePic(0, width, height, mode = 1)
            self.process_end()
        #####

    #-----pushButton22用イベント処理----------------------------------------
    def pushButton22_clicked(self):
        ##########
        #画像サイズを全て変更する
        ##########
        SP = self.ui.lineEdit7.text()
        EP = self.ui.lineEdit8.text()
        if self.ui.listWidget2.count() == -1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('No file in the directory.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif SP.isdigit() == False:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Please input digit for start position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif EP.isdigit() == False:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Please input digit for end position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(SP) > int(EP):
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Start position should be equal or smaller than end position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(SP) > self.ui.listWidget2.count() - 1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Start position should be equal or smaller than max picture position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(EP) > self.ui.listWidget2.count() - 1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('End position should be equal or smaller than max picture position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        else:
            SP = int(SP)
            EP = int(EP) + 1

        #if self.ui.listWidget2.count() != -1:
            self.process_start()
            msgbox = QtWidgets.QMessageBox(self)
            ret = msgbox.question(None, "MDC", "Resize all pictures in the folder?", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) #選択用メッセージボックスを表示
            if ret == QtWidgets.QMessageBox.Yes: #メッセージボックスでYESが選択された場合
                text, buttonState = QtWidgets.QInputDialog.getItem(self, "MDC", "Choose a way to resize pictures", ["CHOOSE PERCENTAGE", "INPUT PERCENTAGE", "INPUT SIZE"], 0, False)
                if buttonState:
                    if text == "CHOOSE PERCENTAGE":
                        percentage, buttonState = QtWidgets.QInputDialog.getItem(self, "MDC", "Please choose percentage to resize the pictures.", ["10", "20", "30", "40", "50", "60", "70", "80", "90", "110", "120", "130", "140", "150", "160", "170", "180", "190", "200"], 4, False)
                        if buttonState:
                            for x in range(SP, EP):
                                self.ui.listWidget2.setCurrentRow(x)
                                self.resizePic(percentage, 0, 0, mode = 0)
                                app.processEvents()
                    if text == "INPUT PERCENTAGE":
                        percentage, buttonState = QtWidgets.QInputDialog.getInt(self, "MDC", "Please input percentage to resize the pictures.", 50, 10, 200, 10)
                        if buttonState:
                            for x in range(SP, EP):
                                self.ui.listWidget2.setCurrentRow(x)
                                self.resizePic(percentage, 0, 0, mode = 0)
                                app.processEvents()
                    if text == "INPUT SIZE":
                        width, buttonState = QtWidgets.QInputDialog.getInt(self, "MDC", "Please input width to resize the pictures.", 608, 1, 99999, 1)
                        if buttonState:
                            height, buttonState = QtWidgets.QInputDialog.getInt(self, "MDC", "Please input height to resize the pictures.", 608, 1, 99999, 1)
                            if buttonState:
                                for x in range(SP, EP):
                                    self.ui.listWidget2.setCurrentRow(x)
                                    self.resizePic(0, width, height, mode = 1)
                                    app.processEvents()
            self.process_end()
        #####

    #-----pushButton23用イベント処理----------------------------------------
    def pushButton23_clicked(self):
        ##########
        #領域を切り抜き回転させ背景ににコピー後保存する
        ##########
        #####ディレクトリ選択
        msgbox = QtWidgets.QMessageBox(self)
        ret = msgbox.question(None, "MDC", "Create rotated files from a picture in the list with different background?\nPlease choose a folder contains background pictures.", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) #選択用メッセージボックスを表示
        if ret == QtWidgets.QMessageBox.Yes: #メッセージボックスでYESが選択された場合
            tmpPath = QtWidgets.QFileDialog.getExistingDirectory(self) #写真が保存してあるフォルダを選択
            if tmpPath: #フォルダが選択された場合
                FileList = glob.glob(tmpPath + '/*.jpg') #フォルダ内の各ファイルパスをリスト形式で取得
                if len(FileList) == 0:
                    msgbox = QtWidgets.QMessageBox(self)
                    msgbox.setWindowTitle("MDC")
                    msgbox.setText('JPEG file not found in the folder.') #メッセージボックスのテキストを設定
                    ret = msgbox.exec() #メッセージボックスを表示
                else:
                    degree, buttonState = QtWidgets.QInputDialog.getItem(self, "MDC", "Please choose dgrees to rotate the pictures.", ["1", "2", "3", "4", "5", "8", "10", "15", "30", "60", "90", "120", "180"], 2, False)
                    if buttonState:
                        FileList2 = []
                        for FN in FileList:
                            FileList2.append(FN.replace('\\', '/')) #globのバグを修正
                        self.pasteRotatePic(int(degree), FileList2)

    #-----pushButton24用イベント処理----------------------------------------
    def pushButton24_clicked(self):
        ##########
        #フォルダ内全ての写真に対して、領域を切り抜き回転させ背景にコピー後保存する
        ##########
        SP = self.ui.lineEdit7.text()
        EP = self.ui.lineEdit8.text()
        if self.ui.listWidget2.count() == -1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('No file in the directory.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif SP.isdigit() == False:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Please input digit for start position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif EP.isdigit() == False:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Please input digit for end position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(SP) > int(EP):
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Start position should be equal or smaller than end position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(SP) > self.ui.listWidget2.count() - 1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Start position should be equal or smaller than max picture position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(EP) > self.ui.listWidget2.count() - 1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('End position should be equal or smaller than max picture position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        else:
            SP = int(SP)
            EP = int(EP) + 1

            msgbox = QtWidgets.QMessageBox(self)
            ret = msgbox.question(None, "MDC", "Create rotated files from pictures in the list with different background?\nPlease choose a folder contains background pictures.", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) #選択用メッセージボックスを表示
            if ret == QtWidgets.QMessageBox.Yes: #メッセージボックスでYESが選択された場合
                tmpPath = QtWidgets.QFileDialog.getExistingDirectory(self) #写真が保存してあるフォルダを選択
                if tmpPath: #フォルダが選択された場合
                    FileList = glob.glob(tmpPath + '/*.jpg') #フォルダ内の各ファイルパスをリスト形式で取得
                    if len(FileList) == 0:
                        msgbox = QtWidgets.QMessageBox(self)
                        msgbox.setWindowTitle("MDC")
                        msgbox.setText('JPEG file not found in the folder.') #メッセージボックスのテキストを設定
                        ret = msgbox.exec() #メッセージボックスを表示
                    else:
                        degree, buttonState = QtWidgets.QInputDialog.getItem(self, "MDC", "Please choose dgrees to rotate the pictures.", ["1", "2", "3", "4", "5", "8", "10", "15", "30", "60", "90", "120", "180"], 2, False)
                        if buttonState:
                            step, buttonState = QtWidgets.QInputDialog.getInt(self, "MDC", "Please choose steps.", 1, 0, 100, 1)
                            if buttonState:
                                self.process_start()
                                FileList2 = []
                                for FN in FileList:
                                    FileList2.append(FN.replace('\\', '/')) #globのバグを修正
                                count = 0
                                for x in range(SP, EP):
                                    self.ui.listWidget2.setCurrentRow(x)
                                    count += 1
                                    if count == step:
                                        self.pasteRotatePic(int(degree), FileList2)
                                        app.processEvents()
                                        count = 0
                                self.process_end()

    #-----pushButton25用イベント処理----------------------------------------
    def pushButton25_clicked(self):
        ##########
        #領域を切り抜き回転保存する
        ##########
        #####ディレクトリ選択
        degree, buttonState = QtWidgets.QInputDialog.getItem(self, "MDC", "Please choose dgrees to rotate the pictures.", ["1", "2", "3", "4", "5", "8", "10", "15", "30", "60", "90", "120", "180"], 2, False)
        if buttonState:
            self.cutRotatePic(int(degree))

    #-----pushButton26用イベント処理----------------------------------------
    def pushButton26_clicked(self):
        ##########
        #フォルダ内全ての写真に対して、領域を切り抜き回転させ保存する
        ##########
        SP = self.ui.lineEdit7.text()
        EP = self.ui.lineEdit8.text()
        if self.ui.listWidget2.count() == -1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('No file in the directory.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif SP.isdigit() == False:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Please input digit for start position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif EP.isdigit() == False:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Please input digit for end position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(SP) > int(EP):
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Start position should be equal or smaller than end position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(SP) > self.ui.listWidget2.count() - 1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Start position should be equal or smaller than max picture position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(EP) > self.ui.listWidget2.count() - 1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('End position should be equal or smaller than max picture position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        else:
            SP = int(SP)
            EP = int(EP) + 1

            msgbox = QtWidgets.QMessageBox(self)
            ret = msgbox.question(None, "MDC", "Create rotated files from pictures in the list with black background?", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) #選択用メッセージボックスを表示
            if ret == QtWidgets.QMessageBox.Yes: #メッセージボックスでYESが選択された場合
                degree, buttonState = QtWidgets.QInputDialog.getItem(self, "MDC", "Please choose dgrees to rotate the pictures.", ["1", "2", "3", "4", "5", "8", "10", "15", "30", "60", "90", "120", "180"], 2, False)
                if buttonState:
                    step, buttonState = QtWidgets.QInputDialog.getInt(self, "MDC", "Please choose steps.", 1, 0, 100, 1)
                    if buttonState:
                        self.process_start()
                        count = 0
                        for x in range(SP, EP):
                            self.ui.listWidget2.setCurrentRow(x)
                            count += 1
                            if count == step:
                                self.cutBRotatePic(int(degree))
                                app.processEvents()
                                count = 0
                        self.process_end()

    #-----pushButton25用イベント処理----------------------------------------
    def pushButton27_clicked(self):
        ##########
        #領域を切り抜き回転保存する
        ##########
        #####ディレクトリ選択
        degree, buttonState = QtWidgets.QInputDialog.getItem(self, "MDC", "Please choose dgrees to rotate the pictures.", ["1", "2", "3", "4", "5", "8", "10", "15", "30", "60", "90", "120", "180"], 2, False)
        if buttonState:
            self.cutBRotatePic(int(degree))

    #-----pushButton26用イベント処理----------------------------------------
    def pushButton28_clicked(self):
        ##########
        #フォルダ内全ての写真に対して、領域を切り抜き回転させ保存する
        ##########
        SP = self.ui.lineEdit7.text()
        EP = self.ui.lineEdit8.text()
        if self.ui.listWidget2.count() == -1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('No file in the directory.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif SP.isdigit() == False:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Please input digit for start position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif EP.isdigit() == False:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Please input digit for end position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(SP) > int(EP):
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Start position should be equal or smaller than end position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(SP) > self.ui.listWidget2.count() - 1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Start position should be equal or smaller than max picture position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(EP) > self.ui.listWidget2.count() - 1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('End position should be equal or smaller than max picture position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        else:
            SP = int(SP)
            EP = int(EP) + 1

            msgbox = QtWidgets.QMessageBox(self)
            ret = msgbox.question(None, "MDC", "Create rotated files from pictures in the list with black background?", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) #選択用メッセージボックスを表示
            if ret == QtWidgets.QMessageBox.Yes: #メッセージボックスでYESが選択された場合
                degree, buttonState = QtWidgets.QInputDialog.getItem(self, "MDC", "Please choose dgrees to rotate the pictures.", ["1", "2", "3", "4", "5", "8", "10", "15", "30", "60", "90", "120", "180"], 2, False)
                if buttonState:
                    step, buttonState = QtWidgets.QInputDialog.getInt(self, "MDC", "Please choose steps.", 1, 0, 100, 1)
                    if buttonState:
                        self.process_start()
                        count = 0
                        for x in range(SP, EP):
                            self.ui.listWidget2.setCurrentRow(x)
                            count += 1
                            if count == step:
                                self.cutBRotatePic(int(degree))
                                app.processEvents()
                                count = 0
                        self.process_end()

    #-----pushButton29用イベント処理----------------------------------------
    def pushButton29_clicked(self):
        ##########
        #領域を切り抜き回転させ背景ににコピー後保存する
        ##########
        #####ディレクトリ選択
        msgbox = QtWidgets.QMessageBox(self)
        ret = msgbox.question(None, "MDC", "Create rotated files from a picture in the list with different background?\nPlease choose a folder contains background pictures.", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) #選択用メッセージボックスを表示
        if ret == QtWidgets.QMessageBox.Yes: #メッセージボックスでYESが選択された場合
            tmpPath = QtWidgets.QFileDialog.getExistingDirectory(self) #写真が保存してあるフォルダを選択
            if tmpPath: #フォルダが選択された場合
                FileList = glob.glob(tmpPath + '/*.jpg') #フォルダ内の各ファイルパスをリスト形式で取得
                if len(FileList) == 0:
                    msgbox = QtWidgets.QMessageBox(self)
                    msgbox.setWindowTitle("MDC")
                    msgbox.setText('JPEG file not found in the folder.') #メッセージボックスのテキストを設定
                    ret = msgbox.exec() #メッセージボックスを表示
                else:
                    degree, buttonState = QtWidgets.QInputDialog.getItem(self, "MDC", "Please choose dgrees to rotate the pictures.", ["1", "2", "3", "4", "5", "8", "10", "15", "30", "60", "90", "120", "180"], 2, False)
                    if buttonState:
                        FileList2 = []
                        for FN in FileList:
                            FileList2.append(FN.replace('\\', '/')) #globのバグを修正
                        self.pasteBRotatePic(int(degree), FileList2)

    #-----pushButton30用イベント処理----------------------------------------
    def pushButton30_clicked(self):
        ##########
        #フォルダ内全ての写真に対して、領域を切り抜き回転させ背景にコピー後保存する
        ##########
        SP = self.ui.lineEdit7.text()
        EP = self.ui.lineEdit8.text()
        if self.ui.listWidget2.count() == -1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('No file in the directory.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif SP.isdigit() == False:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Please input digit for start position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif EP.isdigit() == False:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Please input digit for end position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(SP) > int(EP):
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Start position should be equal or smaller than end position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(SP) > self.ui.listWidget2.count() - 1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Start position should be equal or smaller than max picture position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(EP) > self.ui.listWidget2.count() - 1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('End position should be equal or smaller than max picture position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        else:
            SP = int(SP)
            EP = int(EP) + 1

            msgbox = QtWidgets.QMessageBox(self)
            ret = msgbox.question(None, "MDC", "Create rotated files from pictures in the list with different background?\nPlease choose a folder contains background pictures.", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) #選択用メッセージボックスを表示
            if ret == QtWidgets.QMessageBox.Yes: #メッセージボックスでYESが選択された場合
                tmpPath = QtWidgets.QFileDialog.getExistingDirectory(self) #写真が保存してあるフォルダを選択
                if tmpPath: #フォルダが選択された場合
                    FileList = glob.glob(tmpPath + '/*.jpg') #フォルダ内の各ファイルパスをリスト形式で取得
                    if len(FileList) == 0:
                        msgbox = QtWidgets.QMessageBox(self)
                        msgbox.setWindowTitle("MDC")
                        msgbox.setText('JPEG file not found in the folder.') #メッセージボックスのテキストを設定
                        ret = msgbox.exec() #メッセージボックスを表示
                    else:
                        degree, buttonState = QtWidgets.QInputDialog.getItem(self, "MDC", "Please choose dgrees to rotate the pictures.", ["1", "2", "3", "4", "5", "8", "10", "15", "30", "60", "90", "120", "180"], 2, False)
                        if buttonState:
                            step, buttonState = QtWidgets.QInputDialog.getInt(self, "MDC", "Please choose steps.", 1, 0, 100, 1)
                            if buttonState:
                                self.process_start()
                                FileList2 = []
                                for FN in FileList:
                                    FileList2.append(FN.replace('\\', '/')) #globのバグを修正
                                count = 0
                                for x in range(SP, EP):
                                    self.ui.listWidget2.setCurrentRow(x)
                                    count += 1
                                    if count == step:
                                        self.pasteBRotatePic(int(degree), FileList2)
                                        app.processEvents()
                                        count = 0
                                self.process_end()

    #-----pushButton31用イベント処理----------------------------------------
    def pushButton31_clicked(self):
    #####写真からビデオを作成
        filepath, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Open File", "",'avi File (*.avi)')
        if filepath:
            dirPath = QtWidgets.QFileDialog.getExistingDirectory(self) #写真が保存してあるフォルダを選択
            if dirPath: #フォルダが選択された場合
                FileList = glob.glob(dirPath + '/*.jpg') #フォルダ内の各ファイルパスをリスト形式で取得
                if len(FileList) == 0:
                    msgbox = QtWidgets.QMessageBox(self)
                    msgbox.setWindowTitle("MDC")
                    msgbox.setText('JPEG file not found in the folder.') #メッセージボックスのテキストを設定
                    ret = msgbox.exec() #メッセージボックスを表示
                else:
                    rate, buttonState = QtWidgets.QInputDialog.getItem(self, "MDC", "Please choose frame rate.", ["1", "2", "3", "4", "5", "10", "20", "30", "60", "120", "144", "240"], 4, False)
                    if buttonState:
                        msgbox = QtWidgets.QMessageBox(self)
                        ans = msgbox.question(None, "MDC", "Put file names on pictures.", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) #選択用メッセージボックスを表示
                        tmp = FileList[0]
                        tmp = tmp.replace('\\', '/') #globのバグを修正
                        tmpImg = cv2.imread(tmp)
                        imgHeight = tmpImg.shape[0]
                        imgWidth = tmpImg.shape[1]
                        aviOut = cv2.VideoWriter(filepath, fourcc, int(rate), (imgWidth, imgHeight))
                        for FN in FileList:
                            fPath = FN.replace('\\', '/') #globのバグを修正
                            img = cv2.imread(fPath)
                            if ans == QtWidgets.QMessageBox.Yes: #メッセージボックスでYESが選択された場合
                                fPath1 = fPath.rsplit(".", 1) #ファイルパスの文字列右側から指定文字列で分割
                                fPath2 = fPath1[0].rsplit("/", 1) #ファイルパスの文字列右側から指定文字列で分割
                                font_size = 1
                                font = cv2.FONT_HERSHEY_PLAIN
                                cv2.putText(img, fPath2[1], (5, 25), font, font_size, (255, 255, 255), 1)
                            cv2.imshow("MIIL MDC", img)
                            app.processEvents() #ボタン処理のタイミング確認用
                            aviOut.write(img)
                        cv2.destroyAllWindows()
                        msgbox = QtWidgets.QMessageBox(self)
                        msgbox.setWindowTitle("MDC")
                        msgbox.setText('Video file created.') #メッセージボックスのテキストを設定
                        ret = msgbox.exec() #メッセージボックスを表示

    #-----pushButton32用イベント処理----------------------------------------
    def pushButton32_clicked(self):
        ##########
        #現在の画像を回転させ保存する
        ##########
        degree, buttonState = QtWidgets.QInputDialog.getItem(self, "MDC", "Please choose dgrees to rotate the pictures.", ["1", "2", "3", "4", "5", "8", "10", "15", "30", "60", "90", "120", "180"], 2, False)
        if buttonState:
            self.process_start()
            if self.ui.listWidget2.count() != -1:
                self.rotatePicPC(int(degree))
            self.process_end()

    #-----pushButton33用イベント処理----------------------------------------
    def pushButton33_clicked(self):
        ##########
        #リストウィジット内全ての画像ファイルを回転させ保存する
        ##########
        SP = self.ui.lineEdit7.text()
        EP = self.ui.lineEdit8.text()
        if self.ui.listWidget2.count() == -1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('No file in the directory.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif SP.isdigit() == False:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Please input digit for start position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif EP.isdigit() == False:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Please input digit for end position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(SP) > int(EP):
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Start position should be equal or smaller than end position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(SP) > self.ui.listWidget2.count() - 1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Start position should be equal or smaller than max picture position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(EP) > self.ui.listWidget2.count() - 1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('End position should be equal or smaller than max picture position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        else:
            SP = int(SP)
            EP = int(EP) + 1

            msgbox = QtWidgets.QMessageBox(self)
            ret = msgbox.question(None, "MDC", "Create rotated files from pictures in the list?", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) #選択用メッセージボックスを表示
            if ret == QtWidgets.QMessageBox.Yes: #メッセージボックスでYESが選択された場合
                degree, buttonState = QtWidgets.QInputDialog.getItem(self, "MDC", "Please choose dgrees to rotate the pictures.", ["1", "2", "3", "4", "5", "8", "10", "15", "30", "60", "90", "120", "180"], 2, False)
                if buttonState:
                    step, buttonState = QtWidgets.QInputDialog.getInt(self, "MDC", "Please choose steps.", 1, 0, 100, 1)
                    if buttonState:
                        self.process_start()
                        #listItemCount = self.ui.listWidget2.count()
                        #if self.ui.listWidget2.count() != -1:
                        count = 0
                        for x in range(SP, EP):
                            self.ui.listWidget2.setCurrentRow(x)
                            count += 1
                            if count == step:
                                self.rotatePicPC(int(degree))
                                app.processEvents()
                                count = 0
                        self.process_end()

    #-----pushButton34用イベント処理----------------------------------------
    def pushButton34_clicked(self):
        ##########
        #現在の画像を反転させて保存する
        ##########
        self.process_start()
        if self.ui.listWidget2.count() != -1:
            self.reversePic()
        self.process_end()

    #-----pushButton35用イベント処理----------------------------------------
    def pushButton35_clicked(self):
        ##########
        #現在の画像を反転させて保存する
        ##########
        SP = self.ui.lineEdit7.text()
        EP = self.ui.lineEdit8.text()
        if self.ui.listWidget2.count() == -1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('No file in the directory.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif SP.isdigit() == False:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Please input digit for start position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif EP.isdigit() == False:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Please input digit for end position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(SP) > int(EP):
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Start position should be equal or smaller than end position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(SP) > self.ui.listWidget2.count() - 1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Start position should be equal or smaller than max picture position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(EP) > self.ui.listWidget2.count() - 1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('End position should be equal or smaller than max picture position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        else:
            SP = int(SP)
            EP = int(EP) + 1

            msgbox = QtWidgets.QMessageBox(self)
            ret = msgbox.question(None, "MDC", "Flip the picture?", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) #選択用メッセージボックスを表示
            if ret == QtWidgets.QMessageBox.Yes: #メッセージボックスでYESが選択された場合
                step, buttonState = QtWidgets.QInputDialog.getInt(self, "MDC", "Please choose steps.", 1, 0, 100, 1)
                if buttonState:
                    self.process_start()
                    #listItemCount = self.ui.listWidget2.count()
                    #if self.ui.listWidget2.count() != -1:
                    count = 0
                    for x in range(SP, EP):
                        self.ui.listWidget2.setCurrentRow(x)
                        count += 1
                        if count == step:
                            self.reversePic()
                            app.processEvents()
                            count = 0
                    self.process_end()

    #-----pushButton36用イベント処理----------------------------------------
    def pushButton36_clicked(self):
        ##########
        #現在の画像を移動させて保存する
        ##########
        self.process_start()
        if self.ui.listWidget2.count() != -1:
            self.movePic()
        self.process_end()

    #-----pushButton37用イベント処理----------------------------------------
    def pushButton37_clicked(self):
        ##########
        #現在の画像を移動させて保存する
        ##########
        SP = self.ui.lineEdit7.text()
        EP = self.ui.lineEdit8.text()
        if self.ui.listWidget2.count() == -1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('No file in the directory.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif SP.isdigit() == False:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Please input digit for start position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif EP.isdigit() == False:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Please input digit for end position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(SP) > int(EP):
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Start position should be equal or smaller than end position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(SP) > self.ui.listWidget2.count() - 1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('Start position should be equal or smaller than max picture position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        elif int(EP) > self.ui.listWidget2.count() - 1:
            msgbox = QtWidgets.QMessageBox(self)
            msgbox.setWindowTitle("MDC")
            msgbox.setText('End position should be equal or smaller than max picture position.') #メッセージボックスのテキストを設定
            ret = msgbox.exec() #メッセージボックスを表示
        else:
            SP = int(SP)
            EP = int(EP) + 1

            msgbox = QtWidgets.QMessageBox(self)
            ret = msgbox.question(None, "MDC", "Shift the picture?", QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) #選択用メッセージボックスを表示
            if ret == QtWidgets.QMessageBox.Yes: #メッセージボックスでYESが選択された場合
                step, buttonState = QtWidgets.QInputDialog.getInt(self, "MDC", "Please choose steps.", 1, 0, 100, 1)
                if buttonState:
                    self.process_start()
                    #listItemCount = self.ui.listWidget2.count()
                    #if self.ui.listWidget2.count() != -1:
                    count = 0
                    for x in range(SP, EP):
                        self.ui.listWidget2.setCurrentRow(x)
                        count += 1
                        if count == step:
                            self.movePic()
                            app.processEvents()
                            count = 0
                    self.process_end()

    #-----画像反転保存用関数----------------------------------------
    def reversePic(self):
        ##########
        #現在の画像を反転させ保存する
        ##########
        global FileNum
        items = []
        cIndex = self.ui.listWidget2.currentRow()

        frameR = np.copy(CurPic)
        fPic = cv2.flip(frameR, 1)
        cv2.imwrite(DirPath + '/' + str(FileNum) + '.jpg', fPic)
        text1 = ""
        text2 = ""
        text3 = ""
        fY = CurPic.shape[0]
        fX = CurPic.shape[1]
        xmlHeader = '<annotation>' + '\n<filename>' + str(FileNum) + '.jpg</filename>\n<size>\n<width>' + str(fX) + '</width>' + '\n' + '<height>' + str(fY) + '</height>\n</size>\n'
        xmlfooter = '</annotation>\n'
        for x in SettingList:
            ROW, LABEL,TX, TY, BX, BY = x.split(',')
            ROW = ROW.replace(" ", "")
            LABEL = LABEL.replace(" ", "")
            fsx = abs(int(TX) - (CurPicWidth -1))
            fsy = int(TY)
            esx = abs(int(BX) - (CurPicWidth -1))
            esy = int(BY)
            _ , fsx, fsy, esx, esy, _ , _ = getRectanglePos(fsx, fsy, esx, esy, CurPicWidth, CurPicHeight)
            filepath = SettingDataDir + '/' + str(FileNum) + '.set'
            filepath2 = AnnotationDir + '/' + str(FileNum) + '.xml'
            filepath3 = DirPath + '/' + str(FileNum) + '.txt'
            text1 = text1 + ROW + ', ' + LABEL + ', ' + str(fsx) + ', ' + str(fsy) + ', ' + str(esx) + ', ' + str(esy) + '\n'
            text2 = text2 + '<object>\n<name>' + LABEL + '</name>\n<bndbox>' + '\n' + '<xmin>' + str(fsx) + '</xmin>' + '\n' + '<ymin>' + str(fsy) + '</ymin>' + '\n' + '<xmax>' + str(esx) + '</xmax>' + '\n' + '<ymax>' + str(esy) + '</ymax>\n</bndbox>\n</object>\n'
            cw = 1 / CurPicWidth
            ch = 1 / CurPicHeight
            cnx = (fsx + esx) / 2
            cny = (fsy + esy) / 2
            cnw = esx - fsx
            cnh = esy - fsy
            cnx = cnx * cw
            cny = cny * ch
            cnw = cnw * cw
            cnh = cnh * ch
            text3 = text3 + ROW + ' ' + str(cnx) + ' ' + str(cny) + ' ' + str(cnw) + ' ' + str(cnh) + '\n'
            cv2.rectangle(fPic, (fsx, fsy), (esx, esy), (0, 255, 0), 1)
            font_size = 1
            font = cv2.FONT_HERSHEY_PLAIN
            cv2.putText(fPic, LABEL, (fsx + 2, fsy - 2), font, font_size,(0,255,0),1)
        f = open(filepath, "w")
        f.writelines(text1)
        f.close()
        text2 = xmlHeader + text2 + xmlfooter
        f = open(filepath2, "w")
        f.writelines(text2)
        f.close()
        f = open(filepath3, "w")
        f.writelines(text3)
        f.close()
        cv2.imshow("MIIL MDC DRAW MODE", fPic)
        items.append(str(FileNum))
        FileNum += 1
        #Lpos = win.ui.listWidget2.count() - 1
        #self.ui.listWidget2.setCurrentRow(Lpos)
        app.processEvents() #ボタン処理のタイミング確認用

        self.ui.listWidget2.addItems(items)
        self.ui.listWidget2.setCurrentRow(cIndex)

    #-----画像回転保存用関数----------------------------------------
    def pasteBRotatePic(self, degree, BackgroundList):
        ##########
        #領域を切り抜き回転させ背景がにコピー後保存する
        ##########
        global FileNum
        items = []
        rTimes = int(360 / degree)
        cIndex = self.ui.listWidget2.currentRow()
        for x in SettingList:
            ROW, LABEL,TX, TY, BX, BY = x.split(',')
            ROW = ROW.replace(" ", "")
            LABEL = LABEL.replace(" ", "")
        if len(SettingList) == 1:
            fy = CurPic.shape[0]
            fx = CurPic.shape[1]

            copyPic = np.copy(CurPic)
            imageArray = np.zeros((fy, fx, 3), np.uint8)
            cutPic = copyPic[int(TY):int(BY), int(TX):int(BX)]
            imageArray[int(TY):int(BY), int(TX):int(BX)] = cutPic
            
            for i in range(1, rTimes):
                deg = i * degree
                cx = int(TX) + int((int(BX) - int(TX)) / 2)
                cy = int(TY) + int((int(BY) - int(TY)) / 2)
                fsx, fsy, esx, esy, _ , _ = getRotatedRectanglePos(deg, cx, cy, int(TX), int(TY), int(BX), int(BY), CurPicWidth, CurPicHeight)
                frameR = np.copy(imageArray)
                M = cv2.getRotationMatrix2D((cx, cy), deg, 1)
                fPic = cv2.warpAffine(frameR,M,(CurPicWidth, CurPicHeight), borderValue=(255, 255, 255))

                bgPic = cv2.imread(random.choice(BackgroundList))
                cutPicB = fPic[fsy:esy, fsx:esx]
                bgPic[fsy:esy, fsx:esx] = cutPicB
                cv2.imwrite(DirPath + '/' + str(FileNum) + '.jpg', bgPic)

                filepath = SettingDataDir + '/' + str(FileNum) + '.set'
                filepath2 = AnnotationDir + '/' + str(FileNum) + '.xml'
                filepath3 = DirPath + '/' + str(FileNum) + '.txt'
                text = ROW + ', ' + LABEL + ', ' + str(fsx) + ', ' + str(fsy) + ', ' + str(esx) + ', ' + str(esy) + '\n'
                f = open(filepath, "w")
                f.writelines(text)
                f.close()

                text = '<annotation>' + '\n<filename>' + str(FileNum) + '.jpg</filename>\n<size>\n<width>' + str(fx) + '</width>' + '\n' + '<height>' + str(fy) + '</height>\n</size>\n'
                text = text + '<object>\n<name>' + LABEL + '</name>\n<bndbox>' + '\n' + '<xmin>' + str(fsx) + '</xmin>' + '\n' + '<ymin>' + str(fsy) + '</ymin>' + '\n' + '<xmax>' + str(esx) + '</xmax>' + '\n' + '<ymax>' + str(esy) + '</ymax>\n</bndbox>\n</object>\n'
                text = text + '</annotation>\n'
                f = open(filepath2, "w")
                f.writelines(text)
                f.close()

                cw = 1 / CurPicWidth
                ch = 1 / CurPicHeight
                cnx = (fsx + esx) / 2
                cny = (fsy + esy) / 2
                cnw = esx - fsx
                cnh = esy - fsy
                cnx = cnx * cw
                cny = cny * ch
                cnw = cnw * cw
                cnh = cnh * ch
                text = ROW + ' ' + str(cnx) + ' ' + str(cny) + ' ' + str(cnw) + ' ' + str(cnh) + '\n'
                f = open(filepath3, "w")
                f.writelines(text)
                f.close()

                cv2.rectangle(bgPic, (fsx, fsy), (esx, esy), (0, 255, 0), 1)
                font_size = 1
                font = cv2.FONT_HERSHEY_PLAIN
                cv2.putText(bgPic, LABEL,(fsx + 2, fsy - 2),font, font_size,(0,255,0),1)
                cv2.imshow("MIIL MDC DRAW MODE", bgPic)

                items.append(str(FileNum))
                FileNum += 1
                #Lpos = win.ui.listWidget2.count() - 1
                #self.ui.listWidget2.setCurrentRow(Lpos)
                app.processEvents() #ボタン処理のタイミング確認用

            self.ui.listWidget2.addItems(items)
            self.ui.listWidget2.setCurrentRow(cIndex)

    #-----画像回転保存用関数----------------------------------------
    def cutBRotatePic(self, degree):
        ##########
        #領域を切り抜き回転させ背景がにコピー後保存する
        ##########
        global FileNum
        items = []
        rTimes = int(360 / degree)
        cIndex = self.ui.listWidget2.currentRow()
        for x in SettingList:
            ROW, LABEL,TX, TY, BX, BY = x.split(',')
            ROW = ROW.replace(" ", "")
            LABEL = LABEL.replace(" ", "")
        if len(SettingList) == 1:
            fy = CurPic.shape[0]
            fx = CurPic.shape[1]

            copyPic = np.copy(CurPic)
            imageArray = np.zeros((fy, fx, 3), np.uint8)
            cutPic = copyPic[int(TY):int(BY), int(TX):int(BX)]
            imageArray[int(TY):int(BY), int(TX):int(BX)] = cutPic
            
            for i in range(1, rTimes):
                deg = i * degree
                cx = int(TX) + int((int(BX) - int(TX)) / 2)
                cy = int(TY) + int((int(BY) - int(TY)) / 2)
                fsx, fsy, esx, esy, _ , _ = getRotatedRectanglePos(deg, cx, cy, int(TX), int(TY), int(BX), int(BY), CurPicWidth, CurPicHeight)
                frameR = np.copy(CurPic)
                frameRB = np.copy(imageArray)
                M = cv2.getRotationMatrix2D((cx, cy), deg, 1)
                fPic = cv2.warpAffine(frameR,M,(CurPicWidth, CurPicHeight), borderValue=(255, 255, 255))
                fPicB = cv2.warpAffine(frameRB,M,(CurPicWidth, CurPicHeight), borderValue=(255, 255, 255))
                cutPicB = fPicB[fsy:esy, fsx:esx]
                fPic[fsy:esy, fsx:esx] = cutPicB
                cv2.imwrite(DirPath + '/' + str(FileNum) + '.jpg', fPic)

                filepath = SettingDataDir + '/' + str(FileNum) + '.set'
                filepath2 = AnnotationDir + '/' + str(FileNum) + '.xml'
                filepath3 = DirPath + '/' + str(FileNum) + '.txt'
                text = ROW + ', ' + LABEL + ', ' + str(fsx) + ', ' + str(fsy) + ', ' + str(esx) + ', ' + str(esy) + '\n'
                f = open(filepath, "w")
                f.writelines(text)
                f.close()

                text = '<annotation>' + '\n<filename>' + str(FileNum) + '.jpg</filename>\n<size>\n<width>' + str(fx) + '</width>' + '\n' + '<height>' + str(fy) + '</height>\n</size>\n'
                text = text + '<object>\n<name>' + LABEL + '</name>\n<bndbox>' + '\n' + '<xmin>' + str(fsx) + '</xmin>' + '\n' + '<ymin>' + str(fsy) + '</ymin>' + '\n' + '<xmax>' + str(esx) + '</xmax>' + '\n' + '<ymax>' + str(esy) + '</ymax>\n</bndbox>\n</object>\n'
                text = text + '</annotation>\n'
                f = open(filepath2, "w")
                f.writelines(text)
                f.close()

                cw = 1 / CurPicWidth
                ch = 1 / CurPicHeight
                cnx = (fsx + esx) / 2
                cny = (fsy + esy) / 2
                cnw = esx - fsx
                cnh = esy - fsy
                cnx = cnx * cw
                cny = cny * ch
                cnw = cnw * cw
                cnh = cnh * ch
                text = ROW + ' ' + str(cnx) + ' ' + str(cny) + ' ' + str(cnw) + ' ' + str(cnh) + '\n'
                f = open(filepath3, "w")
                f.writelines(text)
                f.close()

                cv2.rectangle(fPic, (fsx, fsy), (esx, esy), (0, 255, 0), 1)
                font_size = 1
                font = cv2.FONT_HERSHEY_PLAIN
                cv2.putText(fPic, LABEL,(fsx + 2, fsy - 2),font, font_size,(0,255,0),1)
                cv2.imshow("MIIL MDC DRAW MODE", fPic)

                items.append(str(FileNum))
                FileNum += 1
                #Lpos = win.ui.listWidget2.count() - 1
                #self.ui.listWidget2.setCurrentRow(Lpos)
                app.processEvents() #ボタン処理のタイミング確認用

            self.ui.listWidget2.addItems(items)
            self.ui.listWidget2.setCurrentRow(cIndex)


    #-----画像回転保存用関数----------------------------------------
    def cutRotatePic(self, degree):
        ##########
        #領域を切り抜き回転させ背景がにコピー後保存する
        ##########
        global FileNum
        items = []
        rTimes = int(360 / degree)
        cIndex = self.ui.listWidget2.currentRow()
        for x in SettingList:
            ROW, LABEL,TX, TY, BX, BY = x.split(',')
            ROW = ROW.replace(" ", "")
            LABEL = LABEL.replace(" ", "")
        if len(SettingList) == 1:
            fy = CurPic.shape[0]
            fx = CurPic.shape[1]

            copyPic = np.copy(CurPic)
            imageArray = np.zeros((fy, fx, 3), np.uint8)
            cutPic = copyPic[int(TY):int(BY), int(TX):int(BX)]
            imageArray[int(TY):int(BY), int(TX):int(BX)] = cutPic
            
            for i in range(1, rTimes):
                deg = i * degree
                cx = int(TX) + int((int(BX) - int(TX)) / 2)
                cy = int(TY) + int((int(BY) - int(TY)) / 2)
                fsx, fsy, esx, esy, _ , _ = getRotatedRectanglePos(deg, cx, cy, int(TX), int(TY), int(BX), int(BY), CurPicWidth, CurPicHeight)
                frameR = np.copy(imageArray)
                M = cv2.getRotationMatrix2D((cx, cy), deg, 1)
                fPic = cv2.warpAffine(frameR,M,(CurPicWidth, CurPicHeight), borderValue=(255, 255, 255))
                cv2.imwrite(DirPath + '/' + str(FileNum) + '.jpg', fPic)

                filepath = SettingDataDir + '/' + str(FileNum) + '.set'
                filepath2 = AnnotationDir + '/' + str(FileNum) + '.xml'
                filepath3 = DirPath + '/' + str(FileNum) + '.txt'
                text = ROW + ', ' + LABEL + ', ' + str(fsx) + ', ' + str(fsy) + ', ' + str(esx) + ', ' + str(esy) + '\n'
                f = open(filepath, "w")
                f.writelines(text)
                f.close()

                text = '<annotation>' + '\n<filename>' + str(FileNum) + '.jpg</filename>\n<size>\n<width>' + str(fx) + '</width>' + '\n' + '<height>' + str(fy) + '</height>\n</size>\n'
                text = text + '<object>\n<name>' + LABEL + '</name>\n<bndbox>' + '\n' + '<xmin>' + str(fsx) + '</xmin>' + '\n' + '<ymin>' + str(fsy) + '</ymin>' + '\n' + '<xmax>' + str(esx) + '</xmax>' + '\n' + '<ymax>' + str(esy) + '</ymax>\n</bndbox>\n</object>\n'
                text = text + '</annotation>\n'
                f = open(filepath2, "w")
                f.writelines(text)
                f.close()

                cw = 1 / CurPicWidth
                ch = 1 / CurPicHeight
                cnx = (fsx + esx) / 2
                cny = (fsy + esy) / 2
                cnw = esx - fsx
                cnh = esy - fsy
                cnx = cnx * cw
                cny = cny * ch
                cnw = cnw * cw
                cnh = cnh * ch
                text = ROW + ' ' + str(cnx) + ' ' + str(cny) + ' ' + str(cnw) + ' ' + str(cnh) + '\n'
                f = open(filepath3, "w")
                f.writelines(text)
                f.close()

                cv2.rectangle(fPic, (fsx, fsy), (esx, esy), (0, 255, 0), 1)
                font_size = 1
                font = cv2.FONT_HERSHEY_PLAIN
                cv2.putText(fPic, LABEL,(fsx + 2, fsy - 2),font, font_size,(0,255,0),1)
                cv2.imshow("MIIL MDC DRAW MODE", fPic)

                items.append(str(FileNum))
                FileNum += 1
                #Lpos = win.ui.listWidget2.count() - 1
                #self.ui.listWidget2.setCurrentRow(Lpos)
                app.processEvents() #ボタン処理のタイミング確認用

            self.ui.listWidget2.addItems(items)
            self.ui.listWidget2.setCurrentRow(cIndex)

    #-----画像回転保存用関数----------------------------------------
    def pasteRotatePic(self, degree, BackgroundList):
        ##########
        #領域を切り抜き回転させ背景がにコピー後保存する
        ##########
        global FileNum
        items = []
        rTimes = int(360 / degree)
        cIndex = self.ui.listWidget2.currentRow()
        for x in SettingList:
            ROW, LABEL,TX, TY, BX, BY = x.split(',')
            ROW = ROW.replace(" ", "")
            LABEL = LABEL.replace(" ", "")
        if len(SettingList) == 1:
            fy = CurPic.shape[0]
            fx = CurPic.shape[1]

            #copyPic = np.copy(CurPic)
            #imageArray = np.zeros((fy, fx, 3), np.uint8)
            #cutPic = copyPic[int(TY):int(BY), int(TX):int(BX)]
            #imageArray[int(TY):int(BY), int(TX):int(BX)] = cutPic
            
            for i in range(1, rTimes):
                deg = i * degree
                cx = int(TX) + int((int(BX) - int(TX)) / 2)
                cy = int(TY) + int((int(BY) - int(TY)) / 2)
                fsx, fsy, esx, esy, _ , _ = getRotatedRectanglePos(deg, cx, cy, int(TX), int(TY), int(BX), int(BY), CurPicWidth, CurPicHeight)
                frameR = np.copy(CurPic)
                M = cv2.getRotationMatrix2D((cx, cy), deg, 1)
                fPic = cv2.warpAffine(frameR,M,(CurPicWidth, CurPicHeight), borderValue=(255, 255, 255))

                x1, y1, x2, y2, x3 , y3, x4, y4 = getRotatedPos(deg, cx, cy, int(TX), int(TY), int(BX), int(BY))
                maskPic = np.zeros((fy, fx, 3), np.uint8)
                # 任意の描画したいポリゴンの頂点を与える
                contours = np.array(
                    [
                        [x1, y1],
                        [x2, y2],
                        [x3, y3],
                        [x4, y4],
                    ]
                )
                cv2.fillConvexPoly(maskPic, points = contours, color=(255, 255, 255))
                bgPic = cv2.imread(random.choice(BackgroundList))
                roi = bgPic[0:fy, 0:fx, :]
                rPic = np.where(maskPic==255, fPic, roi)
                cv2.imwrite(DirPath + '/' + str(FileNum) + '.jpg', rPic)

                filepath = SettingDataDir + '/' + str(FileNum) + '.set'
                filepath2 = AnnotationDir + '/' + str(FileNum) + '.xml'
                filepath3 = DirPath + '/' + str(FileNum) + '.txt'
                text = ROW + ', ' + LABEL + ', ' + str(fsx) + ', ' + str(fsy) + ', ' + str(esx) + ', ' + str(esy) + '\n'
                f = open(filepath, "w")
                f.writelines(text)
                f.close()

                text = '<annotation>' + '\n<filename>' + str(FileNum) + '.jpg</filename>\n<size>\n<width>' + str(fx) + '</width>' + '\n' + '<height>' + str(fy) + '</height>\n</size>\n'
                text = text + '<object>\n<name>' + LABEL + '</name>\n<bndbox>' + '\n' + '<xmin>' + str(fsx) + '</xmin>' + '\n' + '<ymin>' + str(fsy) + '</ymin>' + '\n' + '<xmax>' + str(esx) + '</xmax>' + '\n' + '<ymax>' + str(esy) + '</ymax>\n</bndbox>\n</object>\n'
                text = text + '</annotation>\n'
                f = open(filepath2, "w")
                f.writelines(text)
                f.close()

                cw = 1 / CurPicWidth
                ch = 1 / CurPicHeight
                cnx = (fsx + esx) / 2
                cny = (fsy + esy) / 2
                cnw = esx - fsx
                cnh = esy - fsy
                cnx = cnx * cw
                cny = cny * ch
                cnw = cnw * cw
                cnh = cnh * ch
                text = ROW + ' ' + str(cnx) + ' ' + str(cny) + ' ' + str(cnw) + ' ' + str(cnh) + '\n'
                f = open(filepath3, "w")
                f.writelines(text)
                f.close()

                cv2.rectangle(rPic, (fsx, fsy), (esx, esy), (0, 255, 0), 1)
                font_size = 1
                font = cv2.FONT_HERSHEY_PLAIN
                cv2.putText(rPic, LABEL,(fsx + 2, fsy - 2),font, font_size,(0,255,0),1)
                cv2.imshow("MIIL MDC DRAW MODE", rPic)

                items.append(str(FileNum))
                FileNum += 1
                #Lpos = win.ui.listWidget2.count() - 1
                #self.ui.listWidget2.setCurrentRow(Lpos)
                app.processEvents() #ボタン処理のタイミング確認用

            self.ui.listWidget2.addItems(items)
            self.ui.listWidget2.setCurrentRow(cIndex)

    #-----画像回転保存用関数（リージョン中心）----------------------------------------
    def rotatePic(self, degree):
        ##########
        #現在の画像を回転させ保存する
        ##########
        global FileNum
        items = []
        rTimes = int(360 / degree)
        cIndex = self.ui.listWidget2.currentRow()
        for x in SettingList:
            ROW, LABEL,TX, TY, BX, BY = x.split(',')
            ROW = ROW.replace(" ", "")
            LABEL = LABEL.replace(" ", "")

        if len(SettingList) == 1:
            for i in range(1, rTimes):
                deg = i * degree
                cx = int(TX) + int((int(BX) - int(TX)) / 2)
                cy = int(TY) + int((int(BY) - int(TY)) / 2)
                fsx, fsy, esx, esy, _ , _ = getRotatedRectanglePos(deg, cx, cy, int(TX), int(TY), int(BX), int(BY), CurPicWidth, CurPicHeight)
                frameR = np.copy(CurPic)
                M = cv2.getRotationMatrix2D((cx, cy), deg, 1)
                print(M)
                fPic = cv2.warpAffine(frameR,M,(CurPicWidth, CurPicHeight), borderValue=(255, 255, 255))
                cv2.imwrite(DirPath + '/' + str(FileNum) + '.jpg', fPic)

                filepath = SettingDataDir + '/' + str(FileNum) + '.set'
                filepath2 = AnnotationDir + '/' + str(FileNum) + '.xml'
                filepath3 = DirPath + '/' + str(FileNum) + '.txt'
                text = ROW + ', ' + LABEL + ', ' + str(fsx) + ', ' + str(fsy) + ', ' + str(esx) + ', ' + str(esy) + '\n'
                f = open(filepath, "w")
                f.writelines(text)
                f.close()

                fY = CurPic.shape[0]
                fX = CurPic.shape[1]
                text = '<annotation>' + '\n<filename>' + str(FileNum) + '.jpg</filename>\n<size>\n<width>' + str(fX) + '</width>' + '\n' + '<height>' + str(fY) + '</height>\n</size>\n'
                text = text + '<object>\n<name>' + LABEL + '</name>\n<bndbox>' + '\n' + '<xmin>' + str(fsx) + '</xmin>' + '\n' + '<ymin>' + str(fsy) + '</ymin>' + '\n' + '<xmax>' + str(esx) + '</xmax>' + '\n' + '<ymax>' + str(esy) + '</ymax>\n</bndbox>\n</object>\n'
                text = text + '</annotation>\n'
                f = open(filepath2, "w")
                f.writelines(text)
                f.close()

                cw = 1 / CurPicWidth
                ch = 1 / CurPicHeight
                cnx = (fsx + esx) / 2
                cny = (fsy + esy) / 2
                cnw = esx - fsx
                cnh = esy - fsy
                cnx = cnx * cw
                cny = cny * ch
                cnw = cnw * cw
                cnh = cnh * ch
                text = ROW + ' ' + str(cnx) + ' ' + str(cny) + ' ' + str(cnw) + ' ' + str(cnh) + '\n'
                f = open(filepath3, "w")
                f.writelines(text)
                f.close()

                cv2.rectangle(fPic, (fsx, fsy), (esx, esy), (0, 255, 0), 1)
                font_size = 1
                font = cv2.FONT_HERSHEY_PLAIN
                cv2.putText(fPic, LABEL,(fsx + 2, fsy - 2),font, font_size,(0,255,0),1)
                cv2.imshow("MIIL MDC DRAW MODE", fPic)

                items.append(str(FileNum))
                FileNum += 1
                #Lpos = win.ui.listWidget2.count() - 1
                #self.ui.listWidget2.setCurrentRow(Lpos)
                app.processEvents() #ボタン処理のタイミング確認用

            self.ui.listWidget2.addItems(items)
            self.ui.listWidget2.setCurrentRow(cIndex)

    #-----画像回転保存用関数（画像中心）----------------------------------------
    def rotatePicPC(self, degree):
        ##########
        #現在の画像を回転させ保存する
        ##########
        global FileNum
        items = []
        rTimes = int(360 / degree)
        cIndex = self.ui.listWidget2.currentRow()

        for i in range(1, rTimes):
            deg = i * degree
            cx = int((CurPicWidth -1) / 2)
            cy = int((CurPicHeight -1) / 2)
            frameR = np.copy(CurPic)
            M = cv2.getRotationMatrix2D((cx, cy), deg, 1)
            fPic = cv2.warpAffine(frameR,M,(CurPicWidth, CurPicHeight), borderValue=(255, 255, 255))
            cv2.imwrite(DirPath + '/' + str(FileNum) + '.jpg', fPic)
            text1 = ""
            text2 = ""
            text3 = ""
            fY = CurPic.shape[0]
            fX = CurPic.shape[1]
            xmlHeader = '<annotation>' + '\n<filename>' + str(FileNum) + '.jpg</filename>\n<size>\n<width>' + str(fX) + '</width>' + '\n' + '<height>' + str(fY) + '</height>\n</size>\n'
            xmlfooter = '</annotation>\n'
            if len(SettingList) > 0:
                for x in SettingList:
                    ROW, LABEL,TX, TY, BX, BY = x.split(',')
                    ROW = ROW.replace(" ", "")
                    LABEL = LABEL.replace(" ", "")
                    fsx, fsy, esx, esy, _ , _ = getRotatedRectanglePos(deg, cx, cy, int(TX), int(TY), int(BX), int(BY), CurPicWidth, CurPicHeight)

                    filepath = SettingDataDir + '/' + str(FileNum) + '.set'
                    filepath2 = AnnotationDir + '/' + str(FileNum) + '.xml'
                    filepath3 = DirPath + '/' + str(FileNum) + '.txt'
                    text1 = text1 + ROW + ', ' + LABEL + ', ' + str(fsx) + ', ' + str(fsy) + ', ' + str(esx) + ', ' + str(esy) + '\n'

                    text2 = text2 + '<object>\n<name>' + LABEL + '</name>\n<bndbox>' + '\n' + '<xmin>' + str(fsx) + '</xmin>' + '\n' + '<ymin>' + str(fsy) + '</ymin>' + '\n' + '<xmax>' + str(esx) + '</xmax>' + '\n' + '<ymax>' + str(esy) + '</ymax>\n</bndbox>\n</object>\n'

                    cw = 1 / CurPicWidth
                    ch = 1 / CurPicHeight
                    cnx = (fsx + esx) / 2
                    cny = (fsy + esy) / 2
                    cnw = esx - fsx
                    cnh = esy - fsy
                    cnx = cnx * cw
                    cny = cny * ch
                    cnw = cnw * cw
                    cnh = cnh * ch
                    text3 = text3 + ROW + ' ' + str(cnx) + ' ' + str(cny) + ' ' + str(cnw) + ' ' + str(cnh) + '\n'

                    cv2.rectangle(fPic, (fsx, fsy), (esx, esy), (0, 255, 0), 1)
                    font_size = 1
                    font = cv2.FONT_HERSHEY_PLAIN
                    cv2.putText(fPic, LABEL, (fsx + 2, fsy - 2), font, font_size,(0,255,0),1)

                f = open(filepath, "w")
                f.writelines(text1)
                f.close()

                text2 = xmlHeader + text2 + xmlfooter
                f = open(filepath2, "w")
                f.writelines(text2)
                f.close()

                f = open(filepath3, "w")
                f.writelines(text3)
                f.close()
            else:
                filepath3 = DirPath + '/' + str(FileNum) + '.txt'
                f = open(filepath3, "w")
                f.writelines("")
                f.close()

            cv2.imshow("MIIL MDC DRAW MODE", fPic)
            items.append(str(FileNum))
            FileNum += 1
            #Lpos = win.ui.listWidget2.count() - 1
            #self.ui.listWidget2.setCurrentRow(Lpos)
            app.processEvents() #ボタン処理のタイミング確認用

        self.ui.listWidget2.addItems(items)
        self.ui.listWidget2.setCurrentRow(cIndex)

    #-----輝度・色合い変更保存用関数１----------------------------------------
    def cngGamma(self, flag):
        ##########
        #現在の画像の輝度と色合いを変えて保存する
        ##########
        lookUpTable = np.empty((1,256), np.uint8) #ガンマ値を使ってLook up tableを作成
        currentListIndex = self.ui.listWidget2.currentRow()
        if currentListIndex != -1: #listWidget2のアイテムが選択されている場合。

            currentListText = self.ui.listWidget2.currentItem().text()
            sFile = SettingDataDir + '/' + currentListText +'.set'
            xFile = AnnotationDir + '/' + currentListText +'.xml'
            tFile = DirPath + '/' + currentListText +'.txt'
            CurPicB = np.copy(CurPic) #画像を画像にコピー

            if flag == 0 or flag == 2:
                CurPicC = np.copy(CurPicB) #画像を画像にコピー
                self.saveFile(CurPicC, sFile, xFile, tFile, 1.4)
                #CurPicC = np.copy(CurPicB) #画像を画像にコピー
                #self.saveFile(CurPicC, sFile, xFile, tFile, 1.2)
                #CurPicC = np.copy(CurPicB) #画像を画像にコピー
                #self.saveFile(CurPicC, sFile, xFile, tFile, 0.8)
                CurPicC = np.copy(CurPicB) #画像を画像にコピー
                self.saveFile(CurPicC, sFile, xFile, tFile, 0.6)

            if flag == 1 or flag == 2:
                b,g,r = cv2.split(CurPicB) #色要素を分割
                gamma = 0.8 #ガンマ値を決める
                for i in range(256):
                    lookUpTable[0,i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
                bL = cv2.LUT(b, lookUpTable) #Look up tableを使って画像の輝度値を変更
                gamma = 1.2 #ガンマ値を決める
                for i in range(256):
                    lookUpTable[0,i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
                bH = cv2.LUT(b, lookUpTable) #Look up tableを使って画像の輝度値を変更
                gamma = 0.8 #ガンマ値を決める
                for i in range(256):
                    lookUpTable[0,i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
                gL = cv2.LUT(g, lookUpTable) #Look up tableを使って画像の輝度値を変更
                gamma = 1.2 #ガンマ値を決める
                for i in range(256):
                    lookUpTable[0,i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
                gH = cv2.LUT(g, lookUpTable) #Look up tableを使って画像の輝度値を変更
                #ガンマ値を決める
                gamma = 0.8 #ガンマ値を決める
                for i in range(256):
                    lookUpTable[0,i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
                rL = cv2.LUT(r, lookUpTable) #Look up tableを使って画像の輝度値を変更
                gamma = 1.2 #ガンマ値を決める
                for i in range(256):
                    lookUpTable[0,i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
                rH = cv2.LUT(r, lookUpTable) #Look up tableを使って画像の輝度値を変更
                CurPicC = cv2.merge((bL, gL, r)) #色要素を結合
                self.saveFile(CurPicC, sFile, xFile, tFile, 0)
                CurPicC = cv2.merge((bL, gL, rH)) #色要素を結合
                self.saveFile(CurPicC, sFile, xFile, tFile, 0)
                CurPicC = cv2.merge((bL, g, rL)) #色要素を結合
                self.saveFile(CurPicC, sFile, xFile, tFile, 0)
                CurPicC = cv2.merge((bL ,g, r)) #色要素を結合
                self.saveFile(CurPicC, sFile, xFile, tFile, 0)
                CurPicC = cv2.merge((bL, g, rH)) #色要素を結合
                self.saveFile(CurPicC, sFile, xFile, tFile, 0)
                CurPicC = cv2.merge((bL, gH, rL)) #色要素を結合
                self.saveFile(CurPicC, sFile, xFile, tFile, 0)
                CurPicC = cv2.merge((bL, gH, r)) #色要素を結合
                self.saveFile(CurPicC, sFile, xFile, tFile, 0)
                CurPicC = cv2.merge((bL, gH, rH)) #色要素を結合
                self.saveFile(CurPicC, sFile, xFile, tFile, 0)
                CurPicC = cv2.merge((b, gL, rL)) #色要素を結合
                self.saveFile(CurPicC, sFile, xFile, tFile, 0)
                CurPicC = cv2.merge((b, gL, r)) #色要素を結合
                self.saveFile(CurPicC, sFile, xFile, tFile, 0)
                CurPicC = cv2.merge((b, gL, rH)) #色要素を結合
                self.saveFile(CurPicC, sFile, xFile, tFile, 0)
                CurPicC = cv2.merge((b, g, rL)) #色要素を結合
                self.saveFile(CurPicC, sFile, xFile, tFile, 0)
                CurPicC = cv2.merge((b, g, rH)) #色要素を結合
                self.saveFile(CurPicC, sFile, xFile, tFile, 0)
                CurPicC = cv2.merge((b, gH, rL)) #色要素を結合
                self.saveFile(CurPicC, sFile, xFile, tFile, 0)
                CurPicC = cv2.merge((b, gH, r)) #色要素を結合
                self.saveFile(CurPicC, sFile, xFile, tFile, 0)
                CurPicC = cv2.merge((b, gH, rH)) #色要素を結合
                self.saveFile(CurPicC, sFile, xFile, tFile, 0)
                CurPicC = cv2.merge((bH, gL, rL)) #色要素を結合
                self.saveFile(CurPicC, sFile, xFile, tFile, 0)
                CurPicC = cv2.merge((bH, gL, r)) #色要素を結合
                self.saveFile(CurPicC, sFile, xFile, tFile, 0)
                CurPicC = cv2.merge((bH, gL, rH)) #色要素を結合
                self.saveFile(CurPicC, sFile, xFile, tFile, 0)
                CurPicC = cv2.merge((bH, g, rL)) #色要素を結合
                self.saveFile(CurPicC, sFile, xFile, tFile, 0)
                CurPicC = cv2.merge((bH, g, r)) #色要素を結合
                self.saveFile(CurPicC, sFile, xFile, tFile, 0)
                CurPicC = cv2.merge((bH, g, rH)) #色要素を結合
                self.saveFile(CurPicC, sFile, xFile, tFile, 0)
                CurPicC = cv2.merge((bH, gH, rL)) #色要素を結合
                self.saveFile(CurPicC, sFile, xFile, tFile, 0)
                CurPicC = cv2.merge((bH, gH, r)) #色要素を結合
                self.saveFile(CurPicC, sFile, xFile, tFile, 0)
            self.ui.listWidget2.setCurrentRow(currentListIndex)

    #-----輝度・色合い変更保存用関数２----------------------------------------
    def saveFile(self, CurPicC, sFile, xFile, tFile, gamma):
        global FileNum
        if gamma > 0:
            lookUpTable = np.empty((1,256), np.uint8) #ガンマ値を使ってLook up tableを作成
            for i in range(256):
                lookUpTable[0,i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
            CurPicC = cv2.LUT(CurPicC, lookUpTable) #Look up tableを使って画像の輝度値を変更
        cv2.imwrite(DirPath + '/' + str(FileNum) + '.jpg', CurPicC)
        if os.path.isfile(sFile):
            shutil.copyfile(sFile, SettingDataDir + '/' + str(FileNum) +'.set')
        if os.path.isfile(xFile):
            shutil.copyfile(xFile, AnnotationDir + '/' + str(FileNum) +'.xml')
        if os.path.isfile(tFile):
            shutil.copyfile(tFile, DirPath + '/' + str(FileNum) +'.txt')
        self.ui.listWidget2.addItem(str(FileNum))
        self.ui.listWidget2.setCurrentRow(self.ui.listWidget2.count() - 1)
        FileNum += 1
        fs = np.copy(CurPicC)
        if len(SettingList) > 0:
            for x in SettingList:
                ROW, LABEL, TX, TY, BX, BY = x.split(',')
                cv2.rectangle(fs, (int(TX), int(TY)), (int(BX), int(BY)), (0, 255, 0), 1)
                font_size = 1
                font = cv2.FONT_HERSHEY_PLAIN
                cv2.putText(fs, LABEL,(int(TX) + 2, int(TY) - 2),font, font_size,(0,255,0),1)
                cv2.imshow("MIIL MDC DRAW MODE",fs)
        app.processEvents()

    #-----射影変換保存用関数----------------------------------------
    def persPic(self):
        ##########
        #現在の画像を射影変換し保存する
        ##########
        global FileNum
        items = []
        cIndex = self.ui.listWidget2.currentRow()
        if len(SettingList) == 1:
            for x in SettingList:
                img = np.copy(CurPic)
                ROW, LABEL, TX, TY, BX, BY = x.split(',')
                TX = int(TX)
                TY = int(TY)
                BX = int(BX)
                BY = int(BY)
                DX = int((BX - TX) * 0.07)
                DY = int((BY - TY) * 0.07)

                cornersOrg = np.float32([[TX, TY], [BX, TY], [BX, BY], [TX, BY]])
                cornersPer = np.float32([[TX + DX, TY + DY], [BX - DX, TY + DY], [BX, BY], [TX, BY]])
                pt=cv2.getPerspectiveTransform(cornersOrg, cornersPer)
                imgB = cv2.warpPerspective(img,pt,(CurPicWidth, CurPicHeight))
                cv2.imwrite(DirPath + '/' + str(FileNum) + '.jpg', imgB)
                filepath = SettingDataDir + '/' + str(FileNum) + '.set'
                filepath2 = AnnotationDir + '/' + str(FileNum) + '.xml'
                filepath3 = DirPath + '/' + str(FileNum) + '.txt'
                text = ROW + ', ' + LABEL + ', ' + str(TX) + ', ' + str(TY + DY) + ', ' + str(BX) + ', ' + str(BY) + '\n'
                f = open(filepath, "w")
                f.writelines(text)
                f.close()
                fY = CurPic.shape[0]
                fX = CurPic.shape[1]
                text = '<annotation>' + '\n<filename>' + str(FileNum) + '.jpg</filename>\n<size>\n<width>' + str(fX) + '</width>' + '\n' + '<height>' + str(fY) + '</height>\n</size>\n'
                text = text + '<object>\n<name>' + LABEL + '</name>\n<bndbox>' + '\n' + '<xmin>' + str(TX) + '</xmin>' + '\n' + '<ymin>' + str(TY + DY) + '</ymin>' + '\n' + '<xmax>' + str(BX) + '</xmax>' + '\n' + '<ymax>' + str(BY) + '</ymax>\n</bndbox>\n</object>\n'
                text = text + '</annotation>\n'
                f = open(filepath2, "w")
                f.writelines(text)
                f.close()
                cw = 1 / CurPicWidth
                ch = 1 / CurPicHeight
                cnx = (TX + BX) / 2
                cny = (TY + BY + DY) / 2
                cnw = BX - TX
                cnh = BY - TY - DY
                cnx = cnx * cw
                cny = cny * ch
                cnw = cnw * cw
                cnh = cnh * ch
                text = ROW + ' ' + str(cnx) + ' ' + str(cny) + ' ' + str(cnw) + ' ' + str(cnh) + '\n'
                f = open(filepath3, "w")
                f.writelines(text)
                f.close()
                items.append(str(FileNum))
                FileNum += 1
                cv2.rectangle(imgB, (TX, TY +DY), (BX, BY), (0, 255, 0), 1)
                font_size = 1
                font = cv2.FONT_HERSHEY_PLAIN
                cv2.putText(imgB, LABEL,(TX + 2, (TY + DY) - 2),font, font_size,(0,255,0),1)
                cv2.imshow("MIIL MDC DRAW MODE", imgB)
                app.processEvents() #ボタン処理のタイミング確認用

                cornersOrg = np.float32([[TX, TY], [BX, TY], [BX, BY], [TX, BY]])
                cornersPer = np.float32([[TX, TY], [BX - DX, TY + DY], [BX -DX, BY -DY], [TX, BY]])
                pt=cv2.getPerspectiveTransform(cornersOrg, cornersPer)
                imgB = cv2.warpPerspective(img,pt,(CurPicWidth, CurPicHeight))
                cv2.imwrite(DirPath + '/' + str(FileNum) + '.jpg', imgB)
                filepath = SettingDataDir + '/' + str(FileNum) + '.set'
                filepath2 = AnnotationDir + '/' + str(FileNum) + '.xml'
                filepath3 = DirPath + '/' + str(FileNum) + '.txt'
                text = ROW + ', ' + LABEL + ', ' + str(TX) + ', ' + str(TY) + ', ' + str(BX - DX) + ', ' + str(BY) + '\n'
                f = open(filepath, "w")
                f.writelines(text)
                f.close()
                fY = CurPic.shape[0]
                fX = CurPic.shape[1]
                text = '<annotation>' + '\n<filename>' + str(FileNum) + '.jpg</filename>\n<size>\n<width>' + str(fX) + '</width>' + '\n' + '<height>' + str(fY) + '</height>\n</size>\n'
                text = text + '<object>\n<name>' + LABEL + '</name>\n<bndbox>' + '\n' + '<xmin>' + str(TX) + '</xmin>' + '\n' + '<ymin>' + str(TY) + '</ymin>' + '\n' + '<xmax>' + str(BX -DX) + '</xmax>' + '\n' + '<ymax>' + str(BY) + '</ymax>\n</bndbox>\n</object>\n'
                text = text + '</annotation>\n'
                f = open(filepath2, "w")
                f.writelines(text)
                f.close()
                cw = 1 / CurPicWidth
                ch = 1 / CurPicHeight
                cnx = (TX + BX - DX) / 2
                cny = (TY + BY) / 2
                cnw = BX - TX - DX
                cnh = BY - TY
                cnx = cnx * cw
                cny = cny * ch
                cnw = cnw * cw
                cnh = cnh * ch
                text = ROW + ' ' + str(cnx) + ' ' + str(cny) + ' ' + str(cnw) + ' ' + str(cnh) + '\n'
                f = open(filepath3, "w")
                f.writelines(text)
                f.close()
                items.append(str(FileNum))
                FileNum += 1
                cv2.rectangle(imgB, (TX, TY), (BX - DX, BY), (0, 255, 0), 1)
                font_size = 1
                font = cv2.FONT_HERSHEY_PLAIN
                cv2.putText(imgB, LABEL,(TX + 2, TY - 2),font, font_size,(0,255,0),1)
                cv2.imshow("MIIL MDC DRAW MODE", imgB)
                app.processEvents() #ボタン処理のタイミング確認用

                cornersOrg = np.float32([[TX, TY], [BX, TY], [BX, BY], [TX, BY]])
                cornersPer = np.float32([[TX, TY], [BX, TY], [BX -DX, BY -DY], [TX + DX, BY - DY]])
                pt=cv2.getPerspectiveTransform(cornersOrg, cornersPer)
                imgB = cv2.warpPerspective(img,pt,(CurPicWidth, CurPicHeight))
                cv2.imwrite(DirPath + '/' + str(FileNum) + '.jpg', imgB)
                filepath = SettingDataDir + '/' + str(FileNum) + '.set'
                filepath2 = AnnotationDir + '/' + str(FileNum) + '.xml'
                filepath3 = DirPath + '/' + str(FileNum) + '.txt'
                text = ROW + ', ' + LABEL + ', ' + str(TX) + ', ' + str(TY) + ', ' + str(BX) + ', ' + str(BY - DY) + '\n'
                f = open(filepath, "w")
                f.writelines(text)
                f.close()
                fY = CurPic.shape[0]
                fX = CurPic.shape[1]
                text = '<annotation>' + '\n<filename>' + str(FileNum) + '.jpg</filename>\n<size>\n<width>' + str(fX) + '</width>' + '\n' + '<height>' + str(fY) + '</height>\n</size>\n'
                text = text + '<object>\n<name>' + LABEL + '</name>\n<bndbox>' + '\n' + '<xmin>' + str(TX) + '</xmin>' + '\n' + '<ymin>' + str(TY) + '</ymin>' + '\n' + '<xmax>' + str(BX) + '</xmax>' + '\n' + '<ymax>' + str(BY - DY) + '</ymax>\n</bndbox>\n</object>\n'
                text = text + '</annotation>\n'
                f = open(filepath2, "w")
                f.writelines(text)
                f.close()
                cw = 1 / CurPicWidth
                ch = 1 / CurPicHeight
                cnx = (TX + BX) / 2
                cny = (TY + BY - DY) / 2
                cnw = BX - TX
                cnh = BY - TY - DY
                cnx = cnx * cw
                cny = cny * ch
                cnw = cnw * cw
                cnh = cnh * ch
                text = ROW + ' ' + str(cnx) + ' ' + str(cny) + ' ' + str(cnw) + ' ' + str(cnh) + '\n'
                f = open(filepath3, "w")
                f.writelines(text)
                f.close()
                items.append(str(FileNum))
                FileNum += 1
                cv2.rectangle(imgB, (TX, TY), (BX, BY - DY), (0, 255, 0), 1)
                font_size = 1
                font = cv2.FONT_HERSHEY_PLAIN
                cv2.putText(imgB, LABEL,(TX + 2, TY - 2),font, font_size,(0,255,0),1)
                cv2.imshow("MIIL MDC DRAW MODE", imgB)
                app.processEvents() #ボタン処理のタイミング確認用

                cornersOrg = np.float32([[TX, TY], [BX, TY], [BX, BY], [TX, BY]])
                cornersPer = np.float32([[TX + DX, TY + DY], [BX, TY], [BX, BY], [TX + DX, BY - DY]])
                pt=cv2.getPerspectiveTransform(cornersOrg, cornersPer)
                imgB = cv2.warpPerspective(img,pt,(CurPicWidth, CurPicHeight))
                cv2.imwrite(DirPath + '/' + str(FileNum) + '.jpg', imgB)
                filepath = SettingDataDir + '/' + str(FileNum) + '.set'
                filepath2 = AnnotationDir + '/' + str(FileNum) + '.xml'
                filepath3 = DirPath + '/' + str(FileNum) + '.txt'
                text = ROW + ', ' + LABEL + ', ' + str(TX + DX) + ', ' + str(TY) + ', ' + str(BX) + ', ' + str(BY) + '\n'
                f = open(filepath, "w")
                f.writelines(text)
                f.close()
                fY = CurPic.shape[0]
                fX = CurPic.shape[1]
                text = '<annotation>' + '\n<filename>' + str(FileNum) + '.jpg</filename>\n<size>\n<width>' + str(fX) + '</width>' + '\n' + '<height>' + str(fY) + '</height>\n</size>\n'
                text = text + '<object>\n<name>' + LABEL + '</name>\n<bndbox>' + '\n' + '<xmin>' + str(TX + DX) + '</xmin>' + '\n' + '<ymin>' + str(TY) + '</ymin>' + '\n' + '<xmax>' + str(BX) + '</xmax>' + '\n' + '<ymax>' + str(BY) + '</ymax>\n</bndbox>\n</object>\n'
                text = text + '</annotation>\n'
                f = open(filepath2, "w")
                f.writelines(text)
                f.close()
                cw = 1 / CurPicWidth
                ch = 1 / CurPicHeight
                cnx = (TX + BX + DX) / 2
                cny = (TY + BY) / 2
                cnw = BX - TX - DX
                cnh = BY - TY
                cnx = cnx * cw
                cny = cny * ch
                cnw = cnw * cw
                cnh = cnh * ch
                text = ROW + ' ' + str(cnx) + ' ' + str(cny) + ' ' + str(cnw) + ' ' + str(cnh) + '\n'
                f = open(filepath3, "w")
                f.writelines(text)
                f.close()
                items.append(str(FileNum))
                FileNum += 1
                cv2.rectangle(imgB, (TX + DX, TY), (BX, BY), (0, 255, 0), 1)
                font_size = 1
                font = cv2.FONT_HERSHEY_PLAIN
                cv2.putText(imgB, LABEL,(TX + 2 + DX, TY - 2),font, font_size,(0,255,0),1)
                cv2.imshow("MIIL MDC DRAW MODE", imgB)
                app.processEvents() #ボタン処理のタイミング確認用

                #DX = DX * 2
                #DY = DY * 2
                cornersOrg = np.float32([[TX, TY], [BX, TY], [BX, BY], [TX, BY]])
                cornersPer = np.float32([[TX + DX, TY + DY], [BX- DX, TY + DY], [BX - DX, BY - DY], [TX + DX, BY - DY]])
                pt=cv2.getPerspectiveTransform(cornersOrg, cornersPer)
                imgB = cv2.warpPerspective(img,pt,(CurPicWidth, CurPicHeight))
                cv2.imwrite(DirPath + '/' + str(FileNum) + '.jpg', imgB)
                filepath = SettingDataDir + '/' + str(FileNum) + '.set'
                filepath2 = AnnotationDir + '/' + str(FileNum) + '.xml'
                filepath3 = DirPath + '/' + str(FileNum) + '.txt'
                text = ROW + ', ' + LABEL + ', ' + str(TX + DX) + ', ' + str(TY + DY) + ', ' + str(BX - DX) + ', ' + str(BY - DY) + '\n'
                f = open(filepath, "w")
                f.writelines(text)
                f.close()
                fY = CurPic.shape[0]
                fX = CurPic.shape[1]
                text = '<annotation>' + '\n<filename>' + str(FileNum) + '.jpg</filename>\n<size>\n<width>' + str(fX) + '</width>' + '\n' + '<height>' + str(fY) + '</height>\n</size>\n'
                text = text + '<object>\n<name>' + LABEL + '</name>\n<bndbox>' + '\n' + '<xmin>' + str(TX + DX) + '</xmin>' + '\n' + '<ymin>' + str(TY + DY) + '</ymin>' + '\n' + '<xmax>' + str(BX - DX) + '</xmax>' + '\n' + '<ymax>' + str(BY - DY) + '</ymax>\n</bndbox>\n</object>\n'
                text = text + '</annotation>\n'
                f = open(filepath2, "w")
                f.writelines(text)
                f.close()
                cw = 1 / CurPicWidth
                ch = 1 / CurPicHeight
                cnx = (TX + BX) / 2
                cny = (TY + BY) / 2
                cnw = BX - TX - DX * 2
                cnh = BY - TY - DY * 2
                cnx = cnx * cw
                cny = cny * ch
                cnw = cnw * cw
                cnh = cnh * ch
                text = ROW + ' ' + str(cnx) + ' ' + str(cny) + ' ' + str(cnw) + ' ' + str(cnh) + '\n'
                f = open(filepath3, "w")
                f.writelines(text)
                f.close()
                items.append(str(FileNum))
                FileNum += 1
                cv2.rectangle(imgB, (TX + DX, TY + DY), (BX - DX, BY - DY), (0, 255, 0), 1)
                font_size = 1
                font = cv2.FONT_HERSHEY_PLAIN
                cv2.putText(imgB, LABEL,(TX + 2 + DX, TY + DY - 2),font, font_size,(0,255,0),1)
                cv2.imshow("MIIL MDC DRAW MODE", imgB)
                app.processEvents() #ボタン処理のタイミング確認用

            self.ui.listWidget2.addItems(items)
            self.ui.listWidget2.setCurrentRow(cIndex)

    #-----画像リサイズ保存用関数----------------------------------------
    def resizePic(self, percentage = "50", rwidth =608, rheight = 608, mode = 0):
        ##########
        #現在の画像をリサイズし保存する
        ##########
        cIndex = self.ui.listWidget2.currentItem().text()

        filepath = SettingDataDir + '/' + str(cIndex) + '.set'
        filepath2 = AnnotationDir + '/' + str(cIndex) + '.xml'
        filepath3 = DirPath + '/' + str(cIndex) + '.txt'

        fPath = DirPath + '/' + str(cIndex) + '.jpg'
        img = cv2.imread(fPath)
        cv2.imshow("MIIL MDC DRAW MODE", img)
        height = img.shape[0]
        width = img.shape[1]
        if mode == 0:
            percentage = int(percentage) * 0.01
            img2 = cv2.resize(img , (int(width * percentage), int(height * percentage)))
        else:
            img2 = cv2.resize(img , (rwidth, rheight))
        cv2.imwrite(fPath, img2)
        fy = img2.shape[0]
        fx = img2.shape[1]

        text1 = ""
        text2 = ""
        text3 = ""
        for x in SettingList:
            ROW, LABEL,TX, TY, BX, BY = x.split(',')
            ROW = ROW.replace(" ", "")
            LABEL = LABEL.replace(" ", "")
            if mode == 0:
                fsx = int(int(TX) * percentage)
                fsy = int(int(TY) * percentage)
                esx = int(int(BX) * percentage)
                esy = int(int(BY) * percentage)
            else:
                exy = CurPic.shape[0]
                exx = CurPic.shape[1]
                fsx = int(rwidth * int(TX) / exx)
                fsy = int(rheight * int(TY) / exy)
                esx = int(rwidth * int(BX) / exx)
                esy = int(rheight * int(BY) / exy)

            text1 = text1 + ROW + ', ' + LABEL + ', ' + str(fsx) + ', ' + str(fsy) + ', ' + str(esx) + ', ' + str(esy) + '\n'
            text2 = text2 + '<object>\n<name>' + LABEL + '</name>\n<bndbox>' + '\n' + '<xmin>' + str(fsx) + '</xmin>' + '\n' + '<ymin>' + str(fsy) + '</ymin>' + '\n' + '<xmax>' + str(esx) + '</xmax>' + '\n' + '<ymax>' + str(esy) + '</ymax>\n</bndbox>\n</object>\n'
            cw = 1 / fx
            ch = 1 / fy
            cnx = (fsx + esx) / 2
            cny = (fsy + esy) / 2
            cnw = esx - fsx
            cnh = esy - fsy
            cnx = cnx * cw
            cny = cny * ch
            cnw = cnw * cw
            cnh = cnh * ch
            text3 = text3 + ROW + ' ' + str(cnx) + ' ' + str(cny) + ' ' + str(cnw) + ' ' + str(cnh) + '\n'

        if len(SettingList) > 0:
            f = open(filepath, "w")
            f.writelines(text1)
            f.close()

            text2 = '<annotation>' + '\n<filename>' + str(cIndex) + '.jpg</filename>\n<size>\n<width>' + str(fx) + '</width>' + '\n' + '<height>' + str(fy) + '</height>\n</size>\n' + text2 + '</annotation>\n'
            f = open(filepath2, "w")
            f.writelines(text2)
            f.close()

            f = open(filepath3, "w")
            f.writelines(text3)
            f.close()

            cv2.rectangle(img2, (fsx, fsy), (esx, esy), (0, 255, 0), 1)
            font_size = 1
            font = cv2.FONT_HERSHEY_PLAIN
            cv2.putText(img2, LABEL,(fsx + 2, fsy - 2),font, font_size,(0,255,0),1)

        cv2.imshow("MIIL MDC DRAW MODE", img2)
        app.processEvents() #ボタン処理のタイミング確認用
        self.listWidget2_changed()

    #-----画像移動----------------------------------------
    def movePic(self):
        ##########
        #現在の画像を移動させ保存する
        ##########
        global FileNum
        items = []
        cIndex = self.ui.listWidget2.currentRow()
        frameR = np.copy(CurPic)

        if len(SettingList) > 0:

            TX_A = []
            TY_A = []
            BX_A = []
            BY_A = []
            for x in SettingList:
                ROW, LABEL,TX, TY, BX, BY = x.split(',')
                TX_A.append(int(TX))
                TY_A.append(int(TY))
                BX_A.append(int(BX))
                BY_A.append(int(BY))
            TX_MIN = min(TX_A)
            TY_MIN = min(TY_A)
            BX_MAX = (CurPicWidth -1) - max(BX_A)
            BY_MAX = (CurPicHeight -1) - max(BY_A)

            mx= TX_MIN*-1
            my= TY_MIN*-1
            M = np.float32([[1,0,mx],[0,1,my]])
            fPic = cv2.warpAffine(frameR,M,(CurPicWidth, CurPicHeight), borderValue=(255, 255, 255))
            cv2.imwrite(DirPath + '/' + str(FileNum) + '.jpg', fPic)
            text1 = ""
            text2 = ""
            text3 = ""
            fY = CurPic.shape[0]
            fX = CurPic.shape[1]
            xmlHeader = '<annotation>' + '\n<filename>' + str(FileNum) + '.jpg</filename>\n<size>\n<width>' + str(fX) + '</width>' + '\n' + '<height>' + str(fY) + '</height>\n</size>\n'
            xmlfooter = '</annotation>\n'
            for x in SettingList:
                ROW, LABEL,TX, TY, BX, BY = x.split(',')
                ROW = ROW.replace(" ", "")
                LABEL = LABEL.replace(" ", "")
                fsx = int(TX) + mx
                fsy = int(TY) + my
                esx = int(BX) + mx
                esy = int(BY) + my
                filepath = SettingDataDir + '/' + str(FileNum) + '.set'
                filepath2 = AnnotationDir + '/' + str(FileNum) + '.xml'
                filepath3 = DirPath + '/' + str(FileNum) + '.txt'
                text1 = text1 + ROW + ', ' + LABEL + ', ' + str(fsx) + ', ' + str(fsy) + ', ' + str(esx) + ', ' + str(esy) + '\n'
                text2 = text2 + '<object>\n<name>' + LABEL + '</name>\n<bndbox>' + '\n' + '<xmin>' + str(fsx) + '</xmin>' + '\n' + '<ymin>' + str(fsy) + '</ymin>' + '\n' + '<xmax>' + str(esx) + '</xmax>' + '\n' + '<ymax>' + str(esy) + '</ymax>\n</bndbox>\n</object>\n'
                cw = 1 / CurPicWidth
                ch = 1 / CurPicHeight
                cnx = (fsx + esx) / 2
                cny = (fsy + esy) / 2
                cnw = esx - fsx
                cnh = esy - fsy
                cnx = cnx * cw
                cny = cny * ch
                cnw = cnw * cw
                cnh = cnh * ch
                text3 = text3 + ROW + ' ' + str(cnx) + ' ' + str(cny) + ' ' + str(cnw) + ' ' + str(cnh) + '\n'
                cv2.rectangle(fPic, (fsx, fsy), (esx, esy), (0, 255, 0), 1)
                font_size = 1
                font = cv2.FONT_HERSHEY_PLAIN
                cv2.putText(fPic, LABEL, (fsx + 2, fsy - 2), font, font_size,(0,255,0),1)
            f = open(filepath, "w")
            f.writelines(text1)
            f.close()
            text2 = xmlHeader + text2 + xmlfooter
            f = open(filepath2, "w")
            f.writelines(text2)
            f.close()
            f = open(filepath3, "w")
            f.writelines(text3)
            f.close()
            cv2.imshow("MIIL MDC DRAW MODE", fPic)
            items.append(str(FileNum))
            FileNum += 1
            #Lpos = win.ui.listWidget2.count() - 1
            #self.ui.listWidget2.setCurrentRow(Lpos)
            app.processEvents() #ボタン処理のタイミング確認用
            self.ui.listWidget2.addItems(items)
            self.ui.listWidget2.setCurrentRow(cIndex)

            mx= BX_MAX
            my= TY_MIN*-1
            M = np.float32([[1,0,mx],[0,1,my]])
            fPic = cv2.warpAffine(frameR,M,(CurPicWidth, CurPicHeight), borderValue=(255, 255, 255))
            cv2.imwrite(DirPath + '/' + str(FileNum) + '.jpg', fPic)
            text1 = ""
            text2 = ""
            text3 = ""
            fY = CurPic.shape[0]
            fX = CurPic.shape[1]
            xmlHeader = '<annotation>' + '\n<filename>' + str(FileNum) + '.jpg</filename>\n<size>\n<width>' + str(fX) + '</width>' + '\n' + '<height>' + str(fY) + '</height>\n</size>\n'
            xmlfooter = '</annotation>\n'
            for x in SettingList:
                ROW, LABEL,TX, TY, BX, BY = x.split(',')
                ROW = ROW.replace(" ", "")
                LABEL = LABEL.replace(" ", "")
                fsx = int(TX) + mx
                fsy = int(TY) + my
                esx = int(BX) + mx
                esy = int(BY) + my
                filepath = SettingDataDir + '/' + str(FileNum) + '.set'
                filepath2 = AnnotationDir + '/' + str(FileNum) + '.xml'
                filepath3 = DirPath + '/' + str(FileNum) + '.txt'
                text1 = text1 + ROW + ', ' + LABEL + ', ' + str(fsx) + ', ' + str(fsy) + ', ' + str(esx) + ', ' + str(esy) + '\n'
                text2 = text2 + '<object>\n<name>' + LABEL + '</name>\n<bndbox>' + '\n' + '<xmin>' + str(fsx) + '</xmin>' + '\n' + '<ymin>' + str(fsy) + '</ymin>' + '\n' + '<xmax>' + str(esx) + '</xmax>' + '\n' + '<ymax>' + str(esy) + '</ymax>\n</bndbox>\n</object>\n'
                cw = 1 / CurPicWidth
                ch = 1 / CurPicHeight
                cnx = (fsx + esx) / 2
                cny = (fsy + esy) / 2
                cnw = esx - fsx
                cnh = esy - fsy
                cnx = cnx * cw
                cny = cny * ch
                cnw = cnw * cw
                cnh = cnh * ch
                text3 = text3 + ROW + ' ' + str(cnx) + ' ' + str(cny) + ' ' + str(cnw) + ' ' + str(cnh) + '\n'
                cv2.rectangle(fPic, (fsx, fsy), (esx, esy), (0, 255, 0), 1)
                font_size = 1
                font = cv2.FONT_HERSHEY_PLAIN
                cv2.putText(fPic, LABEL, (fsx + 2, fsy - 2), font, font_size,(0,255,0),1)
            f = open(filepath, "w")
            f.writelines(text1)
            f.close()
            text2 = xmlHeader + text2 + xmlfooter
            f = open(filepath2, "w")
            f.writelines(text2)
            f.close()
            f = open(filepath3, "w")
            f.writelines(text3)
            f.close()
            cv2.imshow("MIIL MDC DRAW MODE", fPic)
            items.append(str(FileNum))
            FileNum += 1
            #Lpos = win.ui.listWidget2.count() - 1
            #self.ui.listWidget2.setCurrentRow(Lpos)
            app.processEvents() #ボタン処理のタイミング確認用
            self.ui.listWidget2.addItems(items)
            self.ui.listWidget2.setCurrentRow(cIndex)

            mx= BX_MAX
            my= BY_MAX
            M = np.float32([[1,0,mx],[0,1,my]])
            fPic = cv2.warpAffine(frameR,M,(CurPicWidth, CurPicHeight), borderValue=(255, 255, 255))
            cv2.imwrite(DirPath + '/' + str(FileNum) + '.jpg', fPic)
            text1 = ""
            text2 = ""
            text3 = ""
            fY = CurPic.shape[0]
            fX = CurPic.shape[1]
            xmlHeader = '<annotation>' + '\n<filename>' + str(FileNum) + '.jpg</filename>\n<size>\n<width>' + str(fX) + '</width>' + '\n' + '<height>' + str(fY) + '</height>\n</size>\n'
            xmlfooter = '</annotation>\n'
            for x in SettingList:
                ROW, LABEL,TX, TY, BX, BY = x.split(',')
                ROW = ROW.replace(" ", "")
                LABEL = LABEL.replace(" ", "")
                fsx = int(TX) + mx
                fsy = int(TY) + my
                esx = int(BX) + mx
                esy = int(BY) + my
                filepath = SettingDataDir + '/' + str(FileNum) + '.set'
                filepath2 = AnnotationDir + '/' + str(FileNum) + '.xml'
                filepath3 = DirPath + '/' + str(FileNum) + '.txt'
                text1 = text1 + ROW + ', ' + LABEL + ', ' + str(fsx) + ', ' + str(fsy) + ', ' + str(esx) + ', ' + str(esy) + '\n'
                text2 = text2 + '<object>\n<name>' + LABEL + '</name>\n<bndbox>' + '\n' + '<xmin>' + str(fsx) + '</xmin>' + '\n' + '<ymin>' + str(fsy) + '</ymin>' + '\n' + '<xmax>' + str(esx) + '</xmax>' + '\n' + '<ymax>' + str(esy) + '</ymax>\n</bndbox>\n</object>\n'
                cw = 1 / CurPicWidth
                ch = 1 / CurPicHeight
                cnx = (fsx + esx) / 2
                cny = (fsy + esy) / 2
                cnw = esx - fsx
                cnh = esy - fsy
                cnx = cnx * cw
                cny = cny * ch
                cnw = cnw * cw
                cnh = cnh * ch
                text3 = text3 + ROW + ' ' + str(cnx) + ' ' + str(cny) + ' ' + str(cnw) + ' ' + str(cnh) + '\n'
                cv2.rectangle(fPic, (fsx, fsy), (esx, esy), (0, 255, 0), 1)
                font_size = 1
                font = cv2.FONT_HERSHEY_PLAIN
                cv2.putText(fPic, LABEL, (fsx + 2, fsy - 2), font, font_size,(0,255,0),1)
            f = open(filepath, "w")
            f.writelines(text1)
            f.close()
            text2 = xmlHeader + text2 + xmlfooter
            f = open(filepath2, "w")
            f.writelines(text2)
            f.close()
            f = open(filepath3, "w")
            f.writelines(text3)
            f.close()
            cv2.imshow("MIIL MDC DRAW MODE", fPic)
            items.append(str(FileNum))
            FileNum += 1
            #Lpos = win.ui.listWidget2.count() - 1
            #self.ui.listWidget2.setCurrentRow(Lpos)
            app.processEvents() #ボタン処理のタイミング確認用
            self.ui.listWidget2.addItems(items)
            self.ui.listWidget2.setCurrentRow(cIndex)

            mx= TX_MIN*-1
            my= BY_MAX
            M = np.float32([[1,0,mx],[0,1,my]])
            fPic = cv2.warpAffine(frameR,M,(CurPicWidth, CurPicHeight), borderValue=(255, 255, 255))
            cv2.imwrite(DirPath + '/' + str(FileNum) + '.jpg', fPic)
            text1 = ""
            text2 = ""
            text3 = ""
            fY = CurPic.shape[0]
            fX = CurPic.shape[1]
            xmlHeader = '<annotation>' + '\n<filename>' + str(FileNum) + '.jpg</filename>\n<size>\n<width>' + str(fX) + '</width>' + '\n' + '<height>' + str(fY) + '</height>\n</size>\n'
            xmlfooter = '</annotation>\n'
            for x in SettingList:
                ROW, LABEL,TX, TY, BX, BY = x.split(',')
                ROW = ROW.replace(" ", "")
                LABEL = LABEL.replace(" ", "")
                fsx = int(TX) + mx
                fsy = int(TY) + my
                esx = int(BX) + mx
                esy = int(BY) + my
                filepath = SettingDataDir + '/' + str(FileNum) + '.set'
                filepath2 = AnnotationDir + '/' + str(FileNum) + '.xml'
                filepath3 = DirPath + '/' + str(FileNum) + '.txt'
                text1 = text1 + ROW + ', ' + LABEL + ', ' + str(fsx) + ', ' + str(fsy) + ', ' + str(esx) + ', ' + str(esy) + '\n'
                text2 = text2 + '<object>\n<name>' + LABEL + '</name>\n<bndbox>' + '\n' + '<xmin>' + str(fsx) + '</xmin>' + '\n' + '<ymin>' + str(fsy) + '</ymin>' + '\n' + '<xmax>' + str(esx) + '</xmax>' + '\n' + '<ymax>' + str(esy) + '</ymax>\n</bndbox>\n</object>\n'
                cw = 1 / CurPicWidth
                ch = 1 / CurPicHeight
                cnx = (fsx + esx) / 2
                cny = (fsy + esy) / 2
                cnw = esx - fsx
                cnh = esy - fsy
                cnx = cnx * cw
                cny = cny * ch
                cnw = cnw * cw
                cnh = cnh * ch
                text3 = text3 + ROW + ' ' + str(cnx) + ' ' + str(cny) + ' ' + str(cnw) + ' ' + str(cnh) + '\n'
                cv2.rectangle(fPic, (fsx, fsy), (esx, esy), (0, 255, 0), 1)
                font_size = 1
                font = cv2.FONT_HERSHEY_PLAIN
                cv2.putText(fPic, LABEL, (fsx + 2, fsy - 2), font, font_size,(0,255,0),1)
            f = open(filepath, "w")
            f.writelines(text1)
            f.close()
            text2 = xmlHeader + text2 + xmlfooter
            f = open(filepath2, "w")
            f.writelines(text2)
            f.close()
            f = open(filepath3, "w")
            f.writelines(text3)
            f.close()
            cv2.imshow("MIIL MDC DRAW MODE", fPic)
            items.append(str(FileNum))
            FileNum += 1
            #Lpos = win.ui.listWidget2.count() - 1
            #self.ui.listWidget2.setCurrentRow(Lpos)
            app.processEvents() #ボタン処理のタイミング確認用
            self.ui.listWidget2.addItems(items)
            self.ui.listWidget2.setCurrentRow(cIndex)

    #-----画像取得イベント処理----------------------------------------
    def getPic(self, picID, pic):
        global capProcess
        global cvPic
        global picReady
        
        #print(picID)
        cvPic = self.QImageToCvMat(pic) #QImageをOpenCVで表示可能なフォーマットに変換
        cvPic = cv2.resize(cvPic , (resizeWidth, resizeHeight)) #画像サイズ変更
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
def onInput(event, x, y, flags, param):  
        global capLoop
        #global camWidth
        #global camHeight
        global sStartFlag
        global sFlag
        global mX1
        global mY1
        global mX2
        global mY2
        global ssX
        global ssY
        global sXL
        global sYL
        #マウスが移動た時の処理
        #マウスボタンがクリックされた時の処理
        if event == cv2.EVENT_LBUTTONDOWN and win.ui.radioButton2.isChecked() == True:
            if sStartFlag == 0 and capLoop == 1:
                sFlag = 0
                sStartFlag = 1
                #マウス位置の取得
                mX1 = x
                mY1 = y
                mX2 = x
                mY2 = y
                ret, ssX, ssY, sXL, sYL, _ , _ = getRectanglePos(mX1, mY1, mX2, mY2, CurPicWidth, CurPicHeight)
        #マウスボタンがリリースされた時の処理
        elif event == cv2.EVENT_LBUTTONUP and win.ui.radioButton2.isChecked() == True:
            if sStartFlag == 1:
                sStartFlag = 0
                #マウス位置の取得
                mX2 = x
                mY2 = y
                ret, ssX, ssY, sXL, sYL, W , H = getRectanglePos(mX1, mY1, mX2, mY2, CurPicWidth, CurPicHeight)
                if W > 10 and H > 10 and ret == 1:
                    sFlag = 1
                    filepath = SettingDataDir + '/' + win.ui.listWidget2.currentItem().text() + '.set'
                    filepath2 = AnnotationDir + '/' + win.ui.listWidget2.currentItem().text() + '.xml'
                    filepath3 = DirPath + '/' + win.ui.listWidget2.currentItem().text() + '.txt'
                    text = str(win.ui.listWidget1.currentRow()) + ', ' + win.ui.listWidget1.currentItem().text() + ', ' + str(ssX) + ', ' + str(ssY) + ', ' + str(sXL) + ', ' + str(sYL)
                    SettingList.append(text)
                    text2 = ""
                    for x in SettingList:
                        text2 = text2 + x + "\n"
                    f = open(filepath, "w")
                    f.writelines(text2)
                    f.close()
                    fY = CurPic.shape[0]
                    fX = CurPic.shape[1]
                    text3 = '<annotation>' + '\n<filename>' + win.ui.listWidget2.currentItem().text() + '.jpg</filename>\n<size>\n<width>' + str(fX) + '</width>' + '\n' + '<height>' + str(fY) + '</height>\n</size>\n'
                    for x in SettingList:
                        ROW, LABEL,TX, TY, BX, BY = x.split(',')
                        text3 = text3 + '<object>\n<name>' + LABEL + '</name>\n<bndbox>' + '\n' + '<xmin>' + str(int(TX)) + '</xmin>' + '\n' + '<ymin>' + str(int(TY)) + '</ymin>' + '\n' + '<xmax>' + str(int(BX)) + '</xmax>' + '\n' + '<ymax>' + str(int(BY)) + '</ymax>\n</bndbox>\n</object>\n'
                    text3 = text3 + '</annotation>\n'
                    f = open(filepath2, "w")
                    f.writelines(text3)
                    f.close()
                    text4 = ""
                    for x in SettingList:
                        ROW, LABEL,TX, TY, BX, BY = x.split(',')
                        cw = 1 / CurPicWidth
                        ch = 1 / CurPicHeight
                        cnx = (int(TX) + int(BX)) / 2
                        cny = (int(TY) + int(BY)) / 2
                        cnw = int(BX) - int(TX)
                        cnh = int(BY) - int(TY)
                        cnx = cnx * cw
                        cny = cny * ch
                        cnw = cnw * cw
                        cnh = cnh * ch
                        text4 = text4 + ROW + ' ' + str(cnx) + ' ' + str(cny) + ' ' + str(cnw) + ' ' + str(cnh) + '\n'
                    f = open(filepath3, "w")
                    f.writelines(text4)
                    f.close()
                else:
                    msgbox = QtWidgets.QMessageBox() #####メッセージボックスを準備
                    msgbox.setWindowTitle("MDC")
                    msgbox.setText("The region width and height must be greater than 10 pixel.") #####メッセージボックスのテキストを設定
                    ret = msgbox.exec() #####メッセージボックスを表示
        #マウスボタンが移動した時の処理
        elif event == cv2.EVENT_MOUSEMOVE:
            if sStartFlag == 1:
                #マウス位置の取得
                mX2 = x
                mY2 = y
                ret, ssX, ssY, sXL, sYL, _ , _ = getRectanglePos(mX1, mY1, mX2, mY2, CurPicWidth, CurPicHeight)
            else:
                mX1 = x
                mY1 = y

#####メイン処理（グローバル）########################################
#=====メイン処理定型文========================================
if __name__ == '__main__': #C言語のmain()に相当。このファイルが実行された場合、以下の行が実行される（モジュールとして読込まれた場合は、実行されない）
    app = QtWidgets.QApplication(sys.argv) #アプリケーションオブジェクト作成（sys.argvはコマンドライン引数のリスト）
    win = MainWindow1() #MainWindow1クラスのインスタンスを作成
    win.show() #ウィンドウを表示　win.showFullScreen()やwin.showEvent()を指定する事でウィンドウの状態を変える事が出来る
    sys.exit(app.exec()) #引数が関数の場合は、関数が終了するまで待ち、その関数の返値を上位プロセスに返す
