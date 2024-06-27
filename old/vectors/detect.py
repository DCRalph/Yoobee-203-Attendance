# importing the cv2 library
import cv2
import numpy as np
from imgbeddings import imgbeddings
from PIL import Image
import psycopg2
import os
# import IPython.display

import Secrets


conn = psycopg2.connect(Secrets.Secrets.PG_URI)


# loading the face image path into file_name variable
file_name = "adam/3.jpg"  # replace <INSERT YOUR FACE FILE NAME> with the path to your image
# opening the image
img = Image.open(file_name)
# loading the `imgbeddings`
ibed = imgbeddings()
# calculating the embeddings
embedding = ibed.to_embeddings(img)


cur = conn.cursor()
string_representation = "["+ ",".join(str(x) for x in embedding[0].tolist()) +"]"
cur.execute("SELECT * FROM pictures ORDER BY embedding <-> %s LIMIT 1;", (string_representation,))
rows = cur.fetchall()
for row in rows:
    # display(display.Image(filename="stored-faces/"+row[0]))
    # IPython.display.display(IPython.display.Image(filename="stored-faces/"+row[0]))
    detected = cv2.imread("adam/"+row[0].split(":")[1]+".jpg")

    cv2.imshow("Detected", detected)

cur.close()

while True:
    key = cv2.waitKey(1)
    if key == 27:
        break