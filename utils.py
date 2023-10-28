import requests
import folium
from geopy.geocoders import Nominatim
import pandas as pd
import os
from gtts import gTTS
import speech_recognition as sr
from transformers import pipeline
import json

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
    mls = response.json()['route']['geometry']['coordinates']
    points = [(mls[i][0], mls[i][1]) for i in range(len(mls))]
    m = folium.Map()
    for point in [points[0], points[-1]]:
        folium.Marker(point).add_to(m)
    folium.PolyLine(points, weight=5, opacity=1).add_to(m)
    df = pd.DataFrame(mls).rename(columns={0: 'Lon', 1: 'Lat'})[['Lat', 'Lon']]
    sw = df[['Lon', 'Lat']].min().values.tolist()
    ne = df[['Lon', 'Lat']].max().values.tolist()
    m.fit_bounds([sw, ne])
    return m


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