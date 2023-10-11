MODEL_PATH = "/models/semantic_model.meta"
CTC_PREDICT_PATH = "/tf-end-to-end/ctc_predict.py"
S2M_PATH = "/semantic_to_mei/semantic_to_mei.py"
PYTHON_PATH = "/usr/bin/python"
VOCAB_PATH = "/tf-end-to-end/Data/vocabulary_semantic.txt"

SEMANTIC_PATH = "/temp/semantic/"
IL_PATH = "/temp/IL/"
OUT_PATH = "/temp/out/"

from flask import Flask, request, render_template
import os
import sys
import datetime
import asyncio
import subprocess

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file uploaded', 400

    file = request.files['file']

    if file.filename == '':
        return 'No selected file', 400

    if os.path.exists(file.filename):
        return 'File already exists', 400

    # check if uploads exist
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    # save the file
    input_file_path = os.path.join('uploads', file.filename)

    file.save(input_file_path)

    # generate the output file
    output_file_path = image_to_out(input_file_path, 'xml', 'il')

    return 'File uploaded successfully', 200

def predict(image_path):
    #check that the constant file paths exist
    if not os.path.exists(MODEL_PATH):
        return 'Model path does not exist', 400
    if not os.path.exists(CTC_PREDICT_PATH):
        return 'CTC predict path does not exist', 400
    if not os.path.exists(S2M_PATH):
        return 'Semantic to MEI path does not exist', 400
    if not os.path.exists(PYTHON_PATH):
        return 'Python path does not exist', 400
    if not os.path.exists(VOCAB_PATH):
        return 'Vocabulary path does not exist', 400
    if not os.path.exists(image_path):
        return 'Image file does not exist', 400
    
    current_ts = datetime.datetime.now().timestamp()
    semantic_output_file = SEMANTIC_PATH + "temp" +current_ts + ".semantic"
    
    #run the prediction
    command = PYTHON_PATH + " " + CTC_PREDICT_PATH + " " + MODEL_PATH + " " + image_path + " " + VOCAB_PATH + " > " + semantic_output_file
    process =  os.system(command)
    process.wait()

    return semantic_output_file

def semantic_to_IL(semantic_path, il):
    if not os.path.exists(semantic_path):
        return 'Semantic file does not exist', 400
    if not os.path.exists(S2M_PATH):
        return 'Semantic to MEI path does not exist', 400
    if not os.path.exists(PYTHON_PATH):
        return 'Python path does not exist', 400
    
    current_ts = datetime.datetime.now().timestamp()
    il_output_file = IL_PATH + "temp" +current_ts + "." + il
    command = PYTHON_PATH + " " + S2M_PATH + " " + semantic_path + " " + il_output_file
    process = os.system(command)
    process.wait()

    return il_output_file

def IL_to_out(IL_file, IL, out_type):
    if not os.path.exists(IL_file):
        return 'IL file does not exist', 400
    if not os.path.exists(PYTHON_PATH):
        return 'Python path does not exist', 400
    
    timestamp = datetime.datetime.now().timestamp()
    output_filepath = OUT_PATH + "temp" +timestamp +"." + out_type

    #TODO: run the image to out command

    return output_filepath

def image_to_out(image_path, il, out_type):
    semantic_file_path = predict(image_path)
    il_file_path = semantic_to_IL(semantic_file_path, il)
    output_file_path = IL_to_out(il_file_path, il, out_type)

    return (output_file_path, semantic_file_path, il_file_path)

if __name__ == '__main__':
    app.run(port=8890, debug=True)
