from flask import Flask, render_template, jsonify,redirect, url_for, request
import json 
import os
from gtts import gTTS
import speech_recognition as sr
from transformers import pipeline
import json
import random
import utils
from pydub import AudioSegment

app = Flask(__name__)

sentiment_model = pipeline('sentiment-analysis')


with open('details.json', 'r') as f:
    users = json.load(f)['login']


@app.route('/', methods=['GET', 'POST'])
def login():
  
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']

        print('user {username} password {password} ')
        
        if username in users.keys() and users[username] == password:
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


@app.route('/get_questions', methods=['GET'])
def get_questions():
    questions = [
        'Hi, How can I help you?',
        'Express your feelings to me, I\'m here to listen!',
        'My model is analyzing your texts, you want anything to add? If no please enter NA'
    ]
    return jsonify(questions)


@app.route('/chat', methods=['POST', 'GET'])
def chat():
    states = {0:'From your texts, our model estimates that you in a traumatic state. Please visit the doctor connect page and book a consultation',
              1:"From your texts, our model estimates that you are in a healthy state"}
       
    if request.method == 'POST':
        data = request.get_json()
        answers = data.get('answers')
        trauma_state_chat = utils.detect_trauma(" ".join(answers))
        response = {'msg': states.get(int(trauma_state_chat))}  
        return jsonify(response)  
       
    return render_template('Chat.html')


@app.route('/voice', methods=['POST', 'GET'])
def voice():

    states = {0:'From your audio feed, our model estimates that you in a traumatic state. Please visit the doctor connect page and book a consultation',
              1:"From your audio feed, our model estimates that you are in a healthy state"}

    if request.method == 'POST':
        # Check if the 'audioFile' field is in the request form data
        if 'audioFile' not in request.files:
            return redirect(request.url)
        
        audio_obj = request.files['audioFile']

        if audio_obj and audio_obj.filename:
            filename = os.path.join(r"C:\Users\SURYA S\210623\TraumaChat\ChatAssistance\uploads", audio_obj.filename)
            audio_obj.save(filename)

            sound = AudioSegment.from_mp3(filename)
            sound.export("transcript.wav", format="wav")

            audio_text = utils.audio_to_text("transcript.wav")

        trauma_state = utils.detect_trauma(audio_text)
        response = {'msg': states.get(int(trauma_state))}
        print(response)
        return jsonify(response)  # Return the response as JSON

    return render_template('Voice.html')  


@app.route('/doctor')
def doctor():
    #pass me a map in a html  and the doctor name address and distance
    lat, lng = utils.get_lat_lng() 
    res = utils.get_nearest(lat, lng)
    address = res['results'][0]['address']
    distance = "{0:.2f} Km".format(res['results'][0]['distance']/100)
    m = utils.create_map(res)
    dc_name, dc_email = utils.fetch_details()
    response = {'map':m._repr_html_(), 'name': dc_name, 'address':address, 'distance':distance}
    if response:
        send_email(dc_name, dc_email)

    return render_template('Doctor.html', map=response['map'], name = response['name'], address=address, distance=distance)


@app.route('/email')
def send_email(dc_name, dc_email):
    utils.send_email(dc_email)
    return


@app.route('/patient' , methods=['POST', 'GET'])
def patient():
    if request.method == 'POST':
        data = request.get_json()  # Get the JSON data from the request
        print("Data received from the form:")
        print(data)  

        with open('patient_data.json', 'w') as jfk:
            json.dump(data, jfk)

        response = {'message': 'Data received and saved  successfully'}
        return jsonify(response)
    
     
    #frontend will send the patient details
    return render_template('Patient.html')


if __name__ == '__main__':
    app.run(debug=True)