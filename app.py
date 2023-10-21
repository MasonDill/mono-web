from flask import Flask, request, render_template, send_file
import os
import sys
from datetime import datetime
import subprocess
import json

MODEL_PATH, CTC_PREDICT_PATH, S2M_PATH, VEROVIO_PATH, PYTHON_PATH, PYTHON3_PATH, VOCAB_PATH, SEMANTIC_PATH, IL_PATH, OUT_PATH, UPLOAD_PATH = None, None, None, None, None, None, None, None, None, None, None


app = Flask(__name__)

def tar_files(files):
    timestamp = get_timestamp()
    tar_file_path = "temp" +timestamp +".tar.gz"
    command = "tar -czvf " +tar_file_path +" " +(files[0]) + " " +(files[1])
    subprocess.call(command, shell=True)
    return tar_file_path

def remove_files(files):
    for file in files:
        os.remove(file)

@app.route('/')
def home():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    
    if 'file' not in request.files:
        return 'No file uploaded', 400

    file = request.files['file']
    print(file)

    if file.filename == '':
        return 'No selected file', 400

    if os.path.exists(file.filename):
        return 'File already exists', 400

    # check if uploads exist
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    # save the file
    input_file_path = os.path.join(UPLOAD_PATH, file.filename)
    
    file.save(input_file_path)

    # generate the output file
    results = image_to_out(input_file_path, 'mei', 'il')

    #tar ball the results    
    #tar_file_path = tar_files(results)

    #remove the files
    #remove_files(results)

    # return the files to the user
    #return send_file(tar_file_path, as_attachment=True)
    return 200

def get_timestamp():
    date_string =  datetime.now().strftime("%Y%m%d%H%M%S")
    return ''.join(filter(str.isdigit, date_string))

def predict(image_path):
    current_ts = get_timestamp()
    semantic_output_file = SEMANTIC_PATH + "temp" +current_ts + ".semantic"
    
    #run the prediction
    command = PYTHON3_PATH + " " + CTC_PREDICT_PATH + " -model " + MODEL_PATH + " -image " + image_path + " -vocabulary " + VOCAB_PATH + " > " + semantic_output_file
    print(subprocess.call(command, shell=True))
    return semantic_output_file

def semantic_to_IL(semantic_path, il):    
    il_output_file = IL_PATH + "temp" +get_timestamp()
    command = PYTHON3_PATH + " " + S2M_PATH + " " + semantic_path + " -type xml" +" -o " + il_output_file
    print(subprocess.call(command, shell=True))

    if il == "mei":
        command = VEROVIO_PATH + " -t mei -o " + il_output_file +" " + il_output_file +".xml"
        print(subprocess.call(command, shell=True))

    return il_output_file

def IL_to_out(IL_file, IL, out_type):    
    timestamp = get_timestamp()
    output_filepath = OUT_PATH + "temp" +timestamp

    #TODO: run the image to out command
    return output_filepath

def image_to_out(image_path, il="mei", out_type="wav"):
    semantic_file_path = predict(image_path)
    il_file_path = semantic_to_IL(semantic_file_path, il)

    #output_file_path = IL_to_out(il_file_path, il, out_type)

    return (semantic_file_path, il_file_path + '.' +il)

if __name__ == '__main__':
    # Read the file paths from config.json
    with open('config.json') as json_file:
        data = json.load(json_file)
        MODEL_PATH = data['model_path']
        CTC_PREDICT_PATH = data['ctc_predict_path']
        S2M_PATH = data['S2M_path']
        VEROVIO_PATH = data['verovio_path']
        PYTHON_PATH = data['python_path']
        PYTHON3_PATH = data['python3_path']
        VOCAB_PATH = data['vocab_path']
        temp_path = data['temp_path']
        UPLOAD_PATH = data['upload_path']

    SEMANTIC_PATH = temp_path + "/semantic/"
    IL_PATH = temp_path + "/il/"
    OUT_PATH = temp_path + "/out/"

    # Validate the file paths
    for path in [MODEL_PATH, CTC_PREDICT_PATH, S2M_PATH, PYTHON_PATH, PYTHON3_PATH, VOCAB_PATH, SEMANTIC_PATH, IL_PATH, OUT_PATH]:
        if not os.path.exists(path):
            print("Path does not exist: \"" +path +"\"")
            if(input("Would you like to make it an continue? [y/N] ") != 'y'):
                sys.exit(1)
            #os.makedirs(path)

    app.run(port=8890, debug=True)
