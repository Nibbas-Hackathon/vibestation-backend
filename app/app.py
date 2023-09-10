from flask import Flask, request, jsonify
import replicate
import os
from dotenv import load_dotenv

load_dotenv()
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')

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
    count = 3
    prompt = request.args.get('prompt')
    params = {"model_version": "melody", "prompt": prompt, "duration": 30}
    audio_files_links = []
    song_link = replicate.run(
    "meta/musicgen:7a76a8258b23fae65c5a22debb8841d1d7e816b75c2f24218cd2bd8573787906",
    input=params)
    audio_files_links.append(song_link)
    for i in range(count):
        contination_params = {"model_version": "melody", "input_audio": song_link, "continuation": True, "duration": 24, "continuation_start": 25, "continuation_end": 30}
        song_link = replicate.run("meta/musicgen:7a76a8258b23fae65c5a22debb8841d1d7e816b75c2f24218cd2bd8573787906",input=contination_params)
        audio_files_links.append(song_link)
        print(song_link)
    print(audio_files_links)
    return jsonify(audio_files_links)

if __name__ == '__main__':
    app.run()