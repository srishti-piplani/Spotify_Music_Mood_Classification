import os
import pandas as pd 
import numpy as np 
import flask
import pickle
from flask import Flask, render_template, request
from SpotifyUtils.utility_functions import *
from IPython.display import Image
from IPython.core.display import HTML

app=Flask(__name__)

@app.route('/')
def index():
 return flask.render_template('index.html')

def MoodPredictor(to_predict_list):
 model_type = pickle.load(open("knn_model.pkl","rb"))
 scaler = pickle.load(open("scaler.pkl","rb"))
 print(get_track_image(to_predict_list[0]))
 x = predict_new_song_flask(to_predict_list[0], model_type, scaler)
 return x

@app.route('/predict',methods = ['POST'])
def result():
 if request.method == 'POST':
    to_predict_list = request.form.to_dict()
    to_predict_list=list(to_predict_list.values())

    result = MoodPredictor(to_predict_list)
    result = "The MOOD for the song " + result[0] + " is " + result[1]
    prediction = str(result)
    url = get_track_image(to_predict_list[0])
    return render_template('index.html', prediction_text=prediction, url = url)
if __name__ == "__main__":
 app.run(debug=True)