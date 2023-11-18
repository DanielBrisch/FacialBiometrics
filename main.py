import cv2
from cv2 import face
import cv2.data
import os
import numpy as np

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def prepare_training_data(data_folder_path):
    faces = []
    labels = []

    for file_name in os.listdir("venv/img"):
        if file_name.startswith("."):
            continue

        image_path = data_folder_path + "/" + file_name
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        face = face_cascade.detectMultiScale(gray, 1.3, 5)
        if len(face) != 1:
            continue

        (x, y, w, h) = face[0]
        faces.append(gray[y:y+w, x:x+h])
        labels.append(1)  # 1 representa 'você'

    return faces, labels

faces, labels = prepare_training_data("venv/img")

# Criar e treinar o reconhecedor facial
face_recognizer = face.LBPHFaceRecognizer_create()
face_recognizer.train(faces, np.array(labels))

# Função para prever o rosto
def predict(test_img):
    img = test_img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray)

    face_found = False

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

        roi_gray = gray[y:y+h, x:x+w]
        label, confidence = face_recognizer.predict(roi_gray)

        if label == 1 and confidence < 50:
            face_found = True

    return img, face_found

webcam = cv2.VideoCapture(0)

while True:
    ret, frame = webcam.read()
    if not ret:
        break

    processed_frame, is_face_found = predict(frame)

    cv2.imshow("Reconhecimento Facial", processed_frame)

    if is_face_found:
        print("Acesso Liberado!!")
    else:
        print("Acesso Negado!!")

    if cv2.waitKey(1) == 27:  # Esc para sair
        break

webcam.release()
cv2.destroyAllWindows()