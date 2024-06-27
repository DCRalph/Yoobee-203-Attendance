# importing the cv2 library
import cv2
import numpy as np
from imgbeddings import imgbeddings
from PIL import Image
import psycopg2
import os

import Secrets

conn = psycopg2.connect(Secrets.Secrets.PG_URI)

# loading the haar case algorithm file into alg variable
alg = "haarcascade_frontalface_default.xml"
# passing the algorithm to OpenCV
haar_cascade = cv2.CascadeClassifier(alg)
# loading the image path into file_name variable - replace <INSERT YOUR IMAGE NAME HERE> with the path to your image
file_name = "adam/1.jpg"
# reading the image
img = cv2.imread(file_name, 0)
# creating a black and white version of the image
gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
# detecting the faces
faces = haar_cascade.detectMultiScale(
    gray_img, scaleFactor=1.05, minNeighbors=2, minSize=(100, 100)
)

i = 0
# for each face detected
for x, y, w, h in faces:
    print(x, y, w, h)
    # crop the image to select only the face
    cropped_image = img[y : y + h, x : x + w]
    # loading the target image path into target_file_name variable  - replace <INSERT YOUR TARGET IMAGE NAME HERE> with the path to your target image
    target_file_name = 'faces/' + str(i) + '.jpg'
    cv2.imwrite(
        target_file_name,
        cropped_image,
    )

    img2 = Image.open(target_file_name)

    ibed = imgbeddings()
    embedding = ibed.to_embeddings(img2)
    cur = conn.cursor()
    cur.execute("INSERT INTO pictures values (%s,%s)", ("img:"+str(i), embedding[0].tolist()))
    i = i + 1
conn.commit()
