from flask import Flask, request, render_template, send_file
import os
import sys
import time
from datetime import datetime
import subprocess
import json

IMAGE_PATH, MODEL_PATH, CTC_PREDICT_PATH, S2M_PATH, VEROVIO_PATH, AUDIO_GENERATOR_PATH, PYTHON3_PATH, VOCAB_PATH, SEMANTIC_PATH, IL_PATH, OUT_PATH, UPLOAD_PATH = None, None, None, None, None, None, None, None, None, None, None, None


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

@app.route('/retrieve/<path:path>')
def generate_image(path):
    return send_file("/" +path)

@app.route('/delete/<path:path>')
def delete_file(path):
    os.remove("/" +path)
    return "Deleted", 200

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
    input_file_path = os.path.join(UPLOAD_PATH, file.filename)
    
    file.save(input_file_path)

    # generate the output file
    results = image_to_out(input_file_path, 'mei', 'wav')

    if results is None:
        return 'Error generating output', 500
    
    # read the semantic file
    semantic_file = open(results[0], 'r')
    semantic = semantic_file.read()
    semantic_file.close()
    semantic = semantic.strip()
    semantic = semantic.replace('\n', '\t')

    #read the mei file
    mei_file = open(results[1], 'r')
    mei = mei_file.read()
    mei_file.close()

    # Render the output html
    return render_template('output.html', input_image_path=input_file_path, output_image_path=results[2], output_audio_path=results[3], semantic=semantic, mei=mei)

def get_timestamp():
    date_string =  datetime.now().strftime("%Y%m%d%H%M%S")
    return ''.join(filter(str.isdigit, date_string))

def xml_to_mei(xml_file_path, mei_file_path=None, remove_xml=False):
    if not xml_file_path.endswith(".xml"):
        xml_file_path += ".xml"
    if mei_file_path is None:
        mei_file_path = xml_file_path.replace(".xml", ".mei")

    command = VEROVIO_PATH + " -t mei -o " + mei_file_path +" " + xml_file_path
    print(">" +command)
    subprocess.call(command, shell=True)
    print("---\n")

    if remove_xml:
        os.remove(xml_file_path)

def predict(image_path):
    current_ts = get_timestamp()
    semantic_output_file = SEMANTIC_PATH + "temp" +current_ts + ".semantic"
    
    #run the prediction
    command = PYTHON3_PATH + " " + CTC_PREDICT_PATH + " -model " + MODEL_PATH + " -image " + image_path + " -vocabulary " + VOCAB_PATH + " > " + semantic_output_file
    print(">" +command)
    subprocess.call(command, shell=True)
    print("---\n")

    return semantic_output_file

def semantic_to_IL(semantic_path, il):    
    il_output_file = IL_PATH + "temp" +get_timestamp()
    command = PYTHON3_PATH + " " + S2M_PATH + " " + semantic_path + " -type xml" +" -o " + il_output_file +" --title " +get_timestamp() + " --artist " +(MODEL_PATH.split("/")[-1].split(".")[0])
    print(">" +command)
    subprocess.call(command, shell=True)
    print("---\n")

    if il == "mei":
        xml_to_mei(il_output_file, remove_xml=False)

    return il_output_file

def IL_to_out(IL_file, IL, out_type):    
    timestamp = get_timestamp()
    output_filepath = OUT_PATH + "temp" +timestamp + "." +out_type

    command = PYTHON3_PATH + " " +AUDIO_GENERATOR_PATH + " " + IL_file + "." + IL + " -out " + output_filepath
    print(">" +command)
    subprocess.call(command, shell=True)
    print("---\n")

    return output_filepath

def IL_to_image(IL_file, IL):
    timestamp = get_timestamp()
    image_filepath = IMAGE_PATH + "temp" +timestamp + ".svg"

    command = VEROVIO_PATH + " -t svg -o " + image_filepath +" --page-height 500 " + IL_file + "." + IL
    print(">" +command)
    subprocess.call(command, shell=True)
    print("---\n")

    return image_filepath

def image_to_out(image_path, il="mei", out_type="wav"):
    semantic_file_path = predict(image_path)
    if not os.path.exists(semantic_file_path): 
        return None
    
    il_file_path = semantic_to_IL(semantic_file_path, il)
    if not os.path.exists(il_file_path+".mei"): 
        return None
    
    image_file_path = IL_to_image(il_file_path, il)
    if not os.path.exists(image_file_path):
        return None
    
    output_file_path = IL_to_out(il_file_path, il, out_type)
    if not os.path.exists(output_file_path):
        return None

    return (semantic_file_path, il_file_path + '.' +il, image_file_path, output_file_path)

if __name__ == '__main__':
    # Read the file paths from config.json
    with open('config.json') as json_file:
        data = json.load(json_file)
        MODEL_PATH = data['model_path']
        CTC_PREDICT_PATH = data['ctc_predict_path']
        S2M_PATH = data['S2M_path']
        VEROVIO_PATH = data['verovio_path']
        AUDIO_GENERATOR_PATH = data['audio_generator_path']
        PYTHON3_PATH = data['python3_path']
        VOCAB_PATH = data['vocab_path']
        temp_path = data['temp_path']
        UPLOAD_PATH = data['upload_path']

    SEMANTIC_PATH = temp_path + "/semantic/"
    IL_PATH = temp_path + "/il/"
    OUT_PATH = temp_path + "/out/"
    IMAGE_PATH = temp_path + "/images/"

    # Validate the file paths
    for path in [MODEL_PATH, CTC_PREDICT_PATH, S2M_PATH, VEROVIO_PATH, AUDIO_GENERATOR_PATH, PYTHON3_PATH, VOCAB_PATH, SEMANTIC_PATH, IL_PATH, IMAGE_PATH, OUT_PATH, temp_path, UPLOAD_PATH ]:
        if not os.path.exists(path):
            print("Path does not exist: \"" +path +"\"")
            if(input("Would you like to continue? [y/N] ") != 'y'):
                sys.exit(1)

    app.run(host='0.0.0.0', port=8890)