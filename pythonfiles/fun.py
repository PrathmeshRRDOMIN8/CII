import uvicorn
from fastapi import FastAPI, File, UploadFile,Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import cv2 
import sys
import shutil
import base64
from asyncore import read
import pytesseract
import numpy as np
import imutils
app=FastAPI()

origins=["http://localhost:3000",
"localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
widthImg = 500
heightImg = 120


def preProcessing(img):
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (1, 1), 1)
    imgCanny = cv2.Canny(imgBlur, 200, 200)
    kernel = np.ones((1, 1))
    imgDial = cv2.dilate(imgCanny, kernel, iterations=1)
    imgThres = cv2.erode(imgDial, kernel, iterations=1)
    return imgThres

def getContours(img):
    biggest = np.array([])
    imgContour = img.copy()
    maxArea = 0
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 5000:
            # cv2.drawContours(imgContour, cnt, -1, (255, 0, 0), 3)
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            if area > maxArea and len(approx) == 4:
                biggest = approx
                maxArea = area
    cv2.drawContours(imgContour, biggest, -1, (255, 0, 0), 20)
    return biggest

def reorder(myPoints):
    myPoints = myPoints.reshape((4, 2))
    myPointsNew = np.zeros((4, 1, 2), np.int32)
    add = myPoints.sum(1)
    # print("add", add)
    myPointsNew[0] = myPoints[np.argmin(add)]
    myPointsNew[3] = myPoints[np.argmax(add)]
    diff = np.diff(myPoints, axis=1)
    myPointsNew[1] = myPoints[np.argmin(diff)]
    myPointsNew[2] = myPoints[np.argmax(diff)]
    # print("NewPoints",myPointsNew)
    return myPointsNew

def getWarp(img, biggest):
    biggest = reorder(biggest)
    pts1 = np.float32(biggest)
    pts2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    imgOutput = cv2.warpPerspective(img, matrix, (widthImg, heightImg))

    #imgCropped = imgOutput[20:imgOutput.shape[0] - 20, 20:imgOutput.shape[1] - 20]
    imgCropped = imgOutput[0:imgOutput.shape[0], 0:imgOutput.shape[1]]
    imgCropped = cv2.resize(imgCropped, (widthImg, heightImg))

    return imgCropped

 




@app.post("/img")
def NumberPlateImage(file:UploadFile):
    # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
    with open(f"{file.filename}","wb") as buf:
        shutil.copyfileobj(file.file,buf)
    
    img = cv2.imread(os.path.join(os.getcwd(),file.filename))
    temp=img

    cascade = cv2.CascadeClassifier(r'Files/haarcascade_russian_plate_number.xml')

    states = { "AN": "Andaman and Nicobar", "AP": "Andhra Pradesh", "AR": "AR",
    "CH": "Chandigarh" , "DN": "Dadra and Nagar Haveli", "DD": "Daman & Diu",
    "HR": "Haryana", "HP":"Himachal Pradesh", "JK" : " Jammu and Kashmir",
    "MP": "Madhya Pradesh", "MN": "Manipur", "PY": "Pondicherry", "PN": "Punjab", "RJ": "Rajasthan",
    "SK":"Sikkim", "WB": "West Bengal", "CG": "Chhattisgarh", "TS": "Telangana"}

    # img = cv2.imread(r"Files/num_plate.jpg")
    img = img.astype('uint8')

   

    plate = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    plate_orig = plate.copy()
    nplate = cascade.detectMultiScale(plate, 1.1,4)

    if len(nplate) != 0:

        for (x,y,w,h) in nplate:
            a,b = (int(0.02*img.shape[0]), int(0.01*img.shape[1]))
            #a,b = 0,0
            plate = img[y+a:y+h-a, x+b:x+w-b, :]



    imgThres = preProcessing(plate)

    #kernel = np.ones((1, 1), np.uint8)
    #edges = cv2.Canny(plate, 100, 200, apertureSize=3)
    #edges = cv2.dilate(plate, kernel, iterations=1)
    #edges = cv2.erode(edges, kernel, iterations=1)

    biggest = getContours(imgThres)

    if biggest.size != 0:
        imgWarped = getWarp(plate, biggest)

    else:
        imgWarped = plate.copy()  

    img_gray = cv2.cvtColor(imgWarped, cv2.COLOR_BGR2GRAY)

    (thresh, p2) = cv2.threshold(img_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    read = pytesseract.image_to_string(p2)
    read = ''.join(e for e in read if e.isalnum())
    stat = read[0:2]
    try:
        print('Car belongs to ', states[stat])
    except:
        print()

    print(read)
    cv2.imwrite("CleanedPlate.jpg", p2) 
    imgpath=os.path.join(os.getcwd(),'CleanedPlate.jpg')
    return FileResponse(imgpath)


@app.post("/img1")
def NumberPlateString(file:UploadFile):
    # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
    with open(f"{file.filename}","wb") as buf:
        shutil.copyfileobj(file.file,buf)

    img = cv2.imread(os.path.join(os.getcwd(),file.filename))
    temp=img

    cascade = cv2.CascadeClassifier(r'Files/haarcascade_russian_plate_number.xml')

    states = { "AN": "Andaman and Nicobar", "AP": "Andhra Pradesh", "AR": "AR",
    "CH": "Chandigarh" , "DN": "Dadra and Nagar Haveli", "DD": "Daman & Diu",
    "HR": "Haryana", "HP":"Himachal Pradesh", "JK" : " Jammu and Kashmir",
    "MP": "Madhya Pradesh", "MN": "Manipur", "PY": "Pondicherry", "PN": "Punjab", "RJ": "Rajasthan",
    "SK":"Sikkim", "WB": "West Bengal", "CG": "Chhattisgarh", "TS": "Telangana"}

    # img = cv2.imread(r"Files/num_plate.jpg")
    img = img.astype('uint8')



    plate = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    plate_orig = plate.copy()
    nplate = cascade.detectMultiScale(plate, 1.1,4)

    if len(nplate) != 0:

        for (x,y,w,h) in nplate:
            a,b = (int(0.02*img.shape[0]), int(0.01*img.shape[1]))
            #a,b = 0,0
            plate = img[y+a:y+h-a, x+b:x+w-b, :]



    imgThres = preProcessing(plate)

    #kernel = np.ones((1, 1), np.uint8)
    #edges = cv2.Canny(plate, 100, 200, apertureSize=3)
    #edges = cv2.dilate(plate, kernel, iterations=1)
    #edges = cv2.erode(edges, kernel, iterations=1)

    biggest = getContours(imgThres)

    if biggest.size != 0:
        imgWarped = getWarp(plate, biggest)

    else:
        imgWarped = plate.copy()

    img_gray = cv2.cvtColor(imgWarped, cv2.COLOR_BGR2GRAY)

    (thresh, p2) = cv2.threshold(img_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    read = pytesseract.image_to_string(p2)
    read = ''.join(e for e in read if e.isalnum())
    stat = read[0:2]
    try:
        print('Car belongs to ', states[stat])
    except:
        print()

    print(read)
    cv2.imwrite("CleanedPlate.jpg", p2)
    imgpath=os.path.join(os.getcwd(),'CleanedPlate.jpg')
    return read
    # image_bytes: bytes = temp
    # # media_type here sets the media type of the actual response sent to the client.
    # return Response(content=image_bytes, media_type="image/jpeg")
    
    # cv2.rectangle(img, (x,y), (x+w, y+h), (51,51,255), 5)
    # cv2.rectangle(img, (x, y - 40), (x + w, y) , (51,51,255), 3)
    # cv2.putText(img, read, (x+10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 3)

    # cv2.imshow("Cropped Plate", imgWarped)
    # cv2.imshow("Cleaned Plate", p2) 
    # #cv2.imshow("thresh",imgThres) 
    # cv2.imshow("Original", img)
    # cv2.waitKey(0)
def Slope(a,b,c,d):
    return (d - b)/(c - a)
@app.post("/seatbelt")
def SeatbeltInfo(file:UploadFile):
    with open(f"{file.filename}","wb") as buf:
        shutil.copyfileobj(file.file,buf)

    beltframe = cv2.imread(os.path.join(os.getcwd(),file.filename))

    
    beltframe = imutils.resize(beltframe, height=800)
    beltgray = cv2.cvtColor(beltframe, cv2.COLOR_BGR2GRAY)
    belt = False
    blur = cv2.blur(beltgray, (1, 1))
    edges = cv2.Canny(blur, 50, 400)
    ps = 0


    px1, py1, px2, py2 = 0, 0, 0, 0

    lines = cv2.HoughLinesP(edges, 1, np.pi/270, 30, maxLineGap = 20, minLineLength = 170)

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            s = Slope(x1,y1,x2,y2)
            if ((abs(s) > 0.7) and (abs (s) < 2)):
                if((abs(ps) > 0.7) and (abs(ps) < 2)):
                    if(((abs(x1 - px1) > 5) and (abs(x2 - px2) > 5)) or ((abs(y1 - py1) > 5) and (abs(y2 - py2) > 5))):
                        cv2.line(beltframe, (x1, y1), (x2, y2), (0, 0, 255), 3)
                        cv2.line(beltframe, (px1, py1), (px2, py2), (0, 0, 255), 3)
                        y="Belt Detected"
                        belt = True


            ps = s
            px1, py1, px2, py2 = line[0]


    if belt == False:
        y="No Seatbelt detected"
    return y
#     cv2.imshow("Seat Belt", beltframe)

