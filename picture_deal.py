#-*- encoding:utf-8 -*-
import cv2
import os
import numpy as np
import datetime

class Matcher:
    def __init__(self, workingDir):
        self.workingDir = workingDir
        self.originalDir = os.path.join(workingDir, "original")
        self.compareDir = os.path.join(workingDir, "compared")
        self.resultDir = os.path.join(workingDir, "result")

    @staticmethod
    def mkdir(dir_name):
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)
        return dir_name

    def __getMarkableFileName(self, originalName):
        '''
        return [final file name]
        '''
        srcName= originalName.split(os.sep)[-1]
        return str(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')) + "-" + srcName

    def getOriginalSavePath(self, fileName):
        return os.path.join(Matcher.mkdir(self.originalDir), self.__getMarkableFileName(fileName))

    def getComparedSavePath(self, fileName):
        return os.path.join(Matcher.mkdir(self.compareDir), self.__getMarkableFileName(fileName))

    def getResultSavePath(self, fileName):
        return os.path.join(Matcher.mkdir(self.resultDir), self.__getMarkableFileName(fileName))

    def compareAndSave(self, before, after, result):
        '''
            compare two file and save to result file path
            return: different rectangle coordinate
        '''
        f1 = np.array(cv2.imread(before))
        f2 = np.array(cv2.imread(after))
        frame = f2.copy()

        if f1.shape != f2.shape:
            raise Exception("Original shape is not equal to Compared's! Original : %s, Compared: %s" % (str(f1.shape), str(f2.shape)))

        gray1 = cv2.cvtColor(f1, cv2.COLOR_BGR2GRAY)  # 灰度化
        gray1 = cv2.GaussianBlur(gray1, (3,3), 0)
        gray2 = cv2.cvtColor(f2, cv2.COLOR_BGR2GRAY)  # 灰度化
        gray2 = cv2.GaussianBlur(gray2, (3,3), 0)
        frameDelta = cv2.absdiff(gray1, gray2)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]#二值化
        bin = cv2.dilate(thresh, None, iterations = 3)#图像膨胀
        
        # 判断opencv的版本是 2 还是 3
        major = cv2.__version__.split('.')[0]
        if int(major) == 3:
            _, contours, hierarchy = cv2.findContours(bin.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        else:
            contours, hierarchy = cv2.findContours(bin.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        rectangles = []
        if (len(contours) > 0):
            for index, c in enumerate(contours):
                x, y, w, h = cv2.boundingRect(c)
                rectangles.append({'x': x, 'y': y, 'w': w, 'h': h})
                frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        
        try:
            print(result)
            cv2.imwrite(result, frame)
        except IOError:
            raise Exception("Failed to save compared result file to '%s'" % (result))
        
        return rectangles
