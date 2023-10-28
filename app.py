from flask import Flask, render_template, redirect, url_for, request
import json 
import os
from gtts import gTTS
import speech_recognition as sr
from transformers import pipeline
import json

app = Flask(__name__)

sentiment_model = pipeline('sentiment-analysis')

try:
    os.makedirs(app.instance_path)
except:
    pass


with open('details.json', 'r') as f:
    users = json.load(f)


UPLOAD_FOLDER = os.path.join(app.instance_path, '/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def audio_to_text(audio_file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file_path) as source:
        audio = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio)
            return text
        except:
            return 'Error'
        

def detect_trauma(text):
    result = sentiment_model(text)
    class_dict = {'POSITIVE':True, 'NEGATIVE':False}

    return class_dict[result[0]['label']]



@app.route('/', methods=['GET', 'POST'])
def login():
  
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        print('user {username} password {password} ')
        
        # if username in users.keys() and users[username] == password:
        return redirect(url_for('chat'))
        
        error = 'Invalid username or password'
        return render_template('Login.html', error=error)
    
    return render_template('Login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirmPassword = request.form['confirm-password']

        print('user {email} password {password} confirm passs {confirmPassword}')

        users[email] = password
        with open('details.json', 'w') as jf:
            json.dump(users, jf)

        return redirect(url_for('login'))
    
    return render_template('Signup.html')


@app.route('/chat')
def chat():
    return render_template('Chat.html', )

    #[1 ,2 ,3,4 ]

@app.route('/voice')
def voice():
    return render_template('Voice.html')

@app.route('/doctor')
def doctor():
    #pass me a map in a html  and the doctor name address and distance 
    return render_template('Doctor.html')

@app.route('/patient')
def patient():
    #frontend will send the patient details
    return render_template('Patient.html',)


@app.route('/analyze_audio')
def analyze_audio():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        
        audio_obj = request.files['file']

        if audio_obj and audio_obj.filename:
            filename = os.path.join(app.config['UPLOAD_FOLDER'], audio_obj.filename)

            audio_obj.save(filename)

            audio_text = audio_to_text(filename)

            trauma_state = detect_trauma(audio_text)

        #     return trauma_state (success , 1) (harmful ,0)

if __name__ == '__main__':
    app.run(debug=True)