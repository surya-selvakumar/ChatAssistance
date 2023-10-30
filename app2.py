from flask import Flask, render_template, jsonify,redirect, url_for, request
import json 
import os
from gtts import gTTS
import speech_recognition as sr
from transformers import pipeline
import json
import random
import utils

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
        'My model is analyzing your texts, you want anything to add?'
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
            print("**********Inside IF")
            filename = os.path.join(r"C:\Users\SURYA S\210623\TraumaChat\ChatAssistance\uploads", audio_obj.filename)
            print("**********", filename)
            audio_obj.save(filename)

            audio_text = utils.audio_to_text(filename)

        trauma_state = utils.detect_trauma(audio_text)
        response = {'msg': states.get(int(trauma_state))}
        return jsonify(response)  # Return the response as JSON

    return render_template('Voice.html')  


@app.route('/doctor')
def doctor():
    #pass me a map in a html  and the doctor name address and distance 
    res = utils.get_nearest(13.075393, 80.214797)
    address = res['results'][0]['address']
    distance = "{0:.2f} Km".format(res['results'][0]['distance']/100)
    m = utils.create_map(res)
    # print(m)
    m.save('map.html')
    with open('map.html', 'r') as mp:
        map_html = mp.read()

    response = {'map':map_html, 'name':utils.fetch_details(), 'address':address, 'distance':distance}

    return render_template('Doctor.html')


@app.route('/patient' , methods=['POST', 'GET'])
def patient():
    if request.method == 'POST':
        data = request.get_json()  # Get the JSON data from the request
        print("Data received from the form:")
        print(data)  # Print the received data

        # You can process and store the data as needed

        response = {'message': 'Data received successfully'}
        return jsonify(response)
    
     
    #frontend will send the patient details
    return render_template('Patient.html')


if __name__ == '__main__':
    app.run(debug=True)