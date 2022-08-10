import cv2 as cv

cap = cv.VideoCapture(0)

def nothing(x):
    pass

cv.namedWindow('result')

cv.createTrackbar('minH', 'result', 0, 255, nothing)
cv.createTrackbar('minS', 'result', 0, 255, nothing)
cv.createTrackbar('minV', 'result', 0, 255, nothing)

cv.createTrackbar('maxH', 'result', 0, 255, nothing)
cv.createTrackbar('maxS', 'result', 0, 255, nothing)
cv.createTrackbar('maxV', 'result', 0, 255, nothing)

while True:
    #my_picture = cv.imread(r"C:\Users\ekuzh\Desktop\comp_vision\Kubik_ribik\test2.jpg")
    ret, my_picture = cap.read()
    hsv = cv.cvtColor(my_picture, cv.COLOR_BGR2HSV)
    blur = cv.blur(hsv, (5,5))


    minb = cv.getTrackbarPos('minH', 'result')
    ming = cv.getTrackbarPos('minS', 'result')
    minr = cv.getTrackbarPos('minV', 'result')

    maxb = cv.getTrackbarPos('maxH', 'result')
    maxg = cv.getTrackbarPos('maxS', 'result')
    maxr = cv.getTrackbarPos('maxV', 'result')

    mask = cv.inRange(blur, (minb, ming, minr), (maxb, maxg, maxr))
    cv.imshow('mask', mask)


    result = cv.bitwise_and(my_picture, my_picture, mask = mask)
    cv.imshow('result', result)

    if cv.waitKey(1) == 27:
        break

cv.destroyAllWindows()
