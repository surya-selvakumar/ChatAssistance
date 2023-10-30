import requests
import folium
from geopy.geocoders import Nominatim
import pandas as pd
import os
from gtts import gTTS
import speech_recognition as sr
from transformers import pipeline
import json
import random

sentiment_model = pipeline('sentiment-analysis')


def get_lat_long_from_address(address):
    locator = Nominatim(user_agent='myGeocoder')
    location = locator.geocode(address)
    return location.latitude, location.longitude


def get_route(lat1, long1, lat2, long2):
    url = "https://trueway-directions2.p.rapidapi.com/FindDrivingRoute"

    querystring = {"stops":"{0},{1}; {2},{3}".format(lat1, long1, lat2, long2)}

    headers = {
        "X-RapidAPI-Key": "d136a898admsh769a12d85806a56p1d0f24jsna19b023692ae",
        "X-RapidAPI-Host": "trueway-directions2.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response


def create_map(response):
    location = response['results'][0]['location']
    lat, lng = location['lat'], location['lng']

    # Create a map centered on the given location with a starting zoom level of, say, 15.
    m = folium.Map(location=(lat, lng), zoom_start=15)

    folium.Marker((lat, lng)).add_to(m)

    return m


def fetch_details():
    with open('details.json', 'r') as fd:
        jf = json.load(fd)

    dc_details = jf['doctor_names']
    return dc_details[random.randint(0, len(dc_details))]


def get_nearest(my_lat, my_long):
    url = "https://trueway-places.p.rapidapi.com/FindPlacesNearby"

    querystring = {"location": "{}, {}".format(my_lat, my_long), "type": "hospital", "radius": "2000", "language": "en"}

    headers = {
        "X-RapidAPI-Key": "d136a898admsh769a12d85806a56p1d0f24jsna19b023692ae",
        "X-RapidAPI-Host": "trueway-places.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.json()



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