import cv2
from cv2 import face
import cv2.data
import os
import numpy as np
import threading
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def write_to_sheet(sheet_id, values):
    credentials = Credentials.from_service_account_file(
        'APIKEY/trabalhoDeIAAPIKEY.json',
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )

    service = build('sheets', 'v4', credentials=credentials)

    body = {
        'values': values
    }
    result = service.spreadsheets().values().append(
        spreadsheetId=sheet_id, range='Página1!A:A',
        valueInputOption='USER_ENTERED', body=body
    ).execute()

def write_to_sheet_async(sheet_id, values):
    thread = threading.Thread(target=write_to_sheet, args=(sheet_id, values))
    thread.start()

def prepare_training_data(data_folder_paths):
    faces = []
    labels = []
    label_names = {}

    label = 0
    for folder_path in data_folder_paths:
        for file_name in os.listdir(folder_path):
            if file_name.startswith("."):
                continue

            image_path = os.path.join(folder_path, file_name)
            image = cv2.imread(image_path)

            if image is None:
                print(f"Imagem não carregada corretamente: {image_path}")
                continue

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            face = face_cascade.detectMultiScale(gray, 1.3, 5)

            if len(face) != 1:
                continue

            (x, y, w, h) = face[0]
            faces.append(gray[y:y+w, x:x+h])
            labels.append(label)

        label_names[label] = folder_path.split('/')[-1]
        label += 1

    return faces, labels, label_names

def current_time():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

directories = ["datasets/Dani", "datasets/Jao", "datasets/SAM", "datasets/Vini"]
faces, labels, label_names = prepare_training_data(directories)

face_recognizer = face.LBPHFaceRecognizer_create()
face_recognizer.train(faces, np.array(labels))

def predict(test_img):
    img = test_img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray)

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        label, confidence = face_recognizer.predict(roi_gray)

        if confidence < 50:
            cv2.putText(img, label_names[label], (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            return img, True, label_names[label]

    return img, False, None

camera_active = True
validated_directories = set()

def run_face_recognition():
    global camera_active, validated_directories
    webcam = cv2.VideoCapture(0)

    while camera_active:
        ret, frame = webcam.read()
        if not ret:
            break

        processed_frame, is_face_found, directory = predict(frame)
        cv2.imshow("Reconhecimento Facial", processed_frame)

        if is_face_found and directory not in validated_directories:
            print(f"Rosto reconhecido do diretório: {directory}")
            time_stamp = current_time()
            data = [[directory, time_stamp]]
            write_to_sheet_async('1V3fBr3cHjpOuvMSCEDaapgZ8lpfKzIddYvj6aZ9TQVk', data)
            validated_directories.add(directory)

        if cv2.waitKey(1) == 27:
            break

    webcam.release()
    cv2.destroyAllWindows()

def get_sheet_data():
    credentials = Credentials.from_service_account_file(
        'APIKEY/trabalhoDeIAAPIKEY.json',
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    service = build('sheets', 'v4', credentials=credentials)

    spreadsheet_id = '1V3fBr3cHjpOuvMSCEDaapgZ8lpfKzIddYvj6aZ9TQVk'
    range_name = 'Página1!A1:E'

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    return result.get('values', [])

@app.route('/')
def home():
    alunos = [os.path.basename(directory) for directory in directories]
    sheet_data = get_sheet_data()
    return render_template('index.html', alunos=alunos, data=sheet_data)

@app.route('/start-face-recognition')
def start_face_recognition():
    thread = threading.Thread(target=run_face_recognition)
    thread.start()
    return jsonify({"message": "Reconhecimento facial iniciado."})

@app.route('/clear-sheet')
def clear_sheet():
    credentials = Credentials.from_service_account_file(
        'APIKEY/trabalhoDeIAAPIKEY.json',
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    service = build('sheets', 'v4', credentials=credentials)

    spreadsheet_id = '1V3fBr3cHjpOuvMSCEDaapgZ8lpfKzIddYvj6aZ9TQVk'
    range_to_clear = 'Página1!A1:E'

    request_body = {
        'ranges': [range_to_clear]
    }
    service.spreadsheets().values().batchClear(spreadsheetId=spreadsheet_id, body=request_body).execute()

    return jsonify({"message": "Planilha limpa com sucesso."})

@app.route('/get-sheet-data')
def get_sheet_data_route():
    sheet_data = get_sheet_data()
    return jsonify(sheet_data)

@app.route('/stop-camera')
def stop_camera():
    global camera_active
    camera_active = False
    return jsonify({"message": "Câmera desligada."})


if __name__ == '__main__':
    app.run(debug=True)
