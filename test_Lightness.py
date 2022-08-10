import cv2 as cv
import numpy as np


cap = cv.VideoCapture(0)

while True:
    #my_picture = cv.imread(r"C:\Users\ekuzh\Desktop\comp_vision\Kubik_ribik\test2.jpg")
    ret, my_picture = cap.read()
    hsv = cv.cvtColor(my_picture, cv.COLOR_BGR2HSV)
    
    ligh_channel = hsv[:,:,2]
    binary = np.zeros_like(ligh_channel)
    binary[(ligh_channel > 50)] = 255
    cv.imshow('222', binary)



    

    if cv.waitKey(1) == 27:
        break

cv.destroyAllWindows()