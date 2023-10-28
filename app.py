from flask import Flask, render_template, redirect, url_for, request
import json 
import os
from gtts import gTTS
import speech_recognition as sr
from transformers import pipeline
import json
from utils import audio_to_text, detect_trauma
import utils

app = Flask(__name__)



try:
    os.makedirs(app.instance_path)
except:
    pass


with open('details.json', 'r') as f:
    users = json.load(f)


UPLOAD_FOLDER = os.path.join(app.instance_path, '/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



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
    with open('chat.json', 'r') as jf:
        chat_qns = json.load(jf)

    states = {0:'From your texts, our model estimates that you in a traumatic state. Please visit the doctor connect page and book a consultation',
              1:"From your texts, our model estimates that you are in a healthy state"}

    if request.method == 'POST':
        texts = request.form['form_data']
        trauma_state_chat = detect_trauma(texts)
            
        return render_template('Chat.html', states[int(trauma_state_chat)])

    return render_template('Chat.html', chat_qns)



@app.route('/voice')
def voice():

    states = {0:'From your audio feed, our model estimates that you in a traumatic state. Please visit the doctor connect page and book a consultation',
              1:"From your audio feed, our model estimates that you are in a healthy state"}

    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        
        audio_obj = request.files['file']

        if audio_obj and audio_obj.filename:
            filename = os.path.join(app.config['UPLOAD_FOLDER'], audio_obj.filename)

            audio_obj.save(filename)

            audio_text = audio_to_text(filename)

            trauma_state = detect_trauma(audio_text)

    return render_template('Voice.html', states[int(trauma_state)], int(trauma_state))


@app.route('/doctor')
def doctor():
    #pass me a map in a html  and the doctor name address and distance 
    return render_template('Doctor.html')

@app.route('/patient')
def patient():
    #frontend will send the patient details
    return render_template('Patient.html',)


if __name__ == '__main__':
    app.run(debug=True)