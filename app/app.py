from flask import Flask, request, jsonify, send_file
import replicate
import os
from dotenv import load_dotenv
from deepface import DeepFace
from werkzeug.utils import secure_filename
import requests
from pydub import AudioSegment
import io
import time
import random

load_dotenv()
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')

def audio_continuation(song_link, count):
    audio_files_links = []
    audio_files_links.append(song_link)
    for i in range(count):
        contination_params = {"model_version": "melody", "input_audio": song_link, "continuation": True, "duration": 24, "continuation_start": 25, "continuation_end": 30}
        song_link = replicate.run("meta/musicgen:7a76a8258b23fae65c5a22debb8841d1d7e816b75c2f24218cd2bd8573787906",input=contination_params)
        audio_files_links.append(song_link)
        print(song_link)
    return audio_files_links

def combine_audio_files(files_list):
    current_time = int(time.time())
    rand_num = random.randint(1000,9999)
    audio_file_name = str(current_time) + "_" + str(rand_num) + ".wav"
    combined_audio = AudioSegment.empty()
    for link in files_list:
        try:
            response = requests.get(link)
            if response.status_code == 200:
                audio_segment = AudioSegment.from_wav(io.BytesIO(response.content))
                combined_audio += audio_segment
            else:
                print(f"Failed to download {link}. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error while processing {link}: {str(e)}")
    file_path = "G:\\vibestation\\vibestation-backend\\app\\audio\\" + audio_file_name
    combined_audio.export(file_path, format="wav")
    return file_path

app = Flask(__name__)

@app.route('/api/data/query')
def fetch_song():
    prompt = request.args.get('prompt')
    #gpt prompt
    params = {"model_version": "melody", "prompt": prompt, "duration": 30}
    output = replicate.run(
    "meta/musicgen:7a76a8258b23fae65c5a22debb8841d1d7e816b75c2f24218cd2bd8573787906",
    input=params)
    print(output)
    return output

@app.route('/api/data/song')
def fetch_full_song():
    count = 1
    prompt = request.args.get('prompt')
    params = {"model_version": "melody", "prompt": prompt, "duration": 30}
    audio_files_links = []
    song_link = replicate.run(
    "meta/musicgen:7a76a8258b23fae65c5a22debb8841d1d7e816b75c2f24218cd2bd8573787906",
    input=params)
    audio_files_links = audio_continuation(song_link, count)
    combined_file_path = combine_audio_files(audio_files_links)
    return send_file(combined_file_path, as_attachment=False)

@app.route('/api/data/detect_emotion', methods=("POST", "GET"))
def fetch_song_from_emotion():
    uploaded_img = request.files['uploaded-img']
    img_filename = secure_filename(uploaded_img.filename)
    uploaded_img.save("G:\\vibestation\\vibestation-backend\\app\img\\" + img_filename)
    img_path = "G:\\vibestation\\vibestation-backend\\app\img\\" + img_filename
    result = DeepFace.analyze(img_path, actions=["emotion"])
    emotion = result[0]["dominant_emotion"]
    prompt = emotion
    params = {"model_version": "melody", "prompt": prompt, "duration": 30}
    audio_files_links = []
    song_link = replicate.run(
    "meta/musicgen:7a76a8258b23fae65c5a22debb8841d1d7e816b75c2f24218cd2bd8573787906",
    input=params)
    audio_files_links = audio_continuation(song_link, 1)
    combined_file_path = combine_audio_files(audio_files_links)
    return send_file(combined_file_path, as_attachment=False)
if __name__ == '__main__':
    app.run()