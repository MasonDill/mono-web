from flask import Flask, request, render_template, send_file
import os
import sys
import time
from datetime import datetime
import subprocess
import json

from PIL import Image
import io
import base64

IMAGE_PATH, MODEL_DIRECTORY, CTC_PREDICT_PATH, S2M_PATH, VEROVIO_PATH, AUDIO_GENERATOR_PATH, PYTHON3_PATH, VOCAB_PATH, SEMANTIC_PATH, IL_PATH, OUT_PATH, UPLOAD_PATH = None, None, None, None, None, None, None, None, None, None, None, None
HOME_PATH = os.path.dirname(os.path.realpath(__file__))

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
    # Get the models from the model directory
    models = []
    for file in os.listdir(MODEL_DIRECTORY):
        if file.endswith(".meta"):
            models.append(file)

    # Order the models by name
    # models.sort()

    # Order the models by date
    models.sort(key=lambda x: os.path.getmtime(os.path.join(MODEL_DIRECTORY, x)), reverse=True)
    

    dates = []
    for model in models:
        date = time.ctime(os.path.getmtime(os.path.join(MODEL_DIRECTORY, model)))
        dates.append(date)

    return render_template('upload.html', models=models, dates=dates)

@app.route('/retrieve/<path:path>')
def generate_image(path):
    return send_file("/" +path)

@app.route('/delete/<path:path>')
def delete_file(path):
    os.remove("/" +path)
    return "Deleted", 200

@app.route('/upload', methods=['POST'])
def upload_file():
    # Access the data URL from the form
    data_url = request.form.get('image_data')
    model_file_name = request.form.get('model_data')

    if model_file_name is None or model_file_name == "":
        return "No model selected.", 400
    
    model_path = MODEL_DIRECTORY + "/" + model_file_name

    if data_url:
        try:
            # Decode the base64 data URL to bytes
            image_data = base64.b64decode(data_url.split(',')[1])

            # Create a PIL (Pillow) image from the decoded bytes
            image = Image.open(io.BytesIO(image_data))

        except Exception as e:
            return "Error while processing the image: " + str(e), 400
    else:
        return "No image data received.", 400
    
    # clean up old files
    os.chdir(HOME_PATH)
    for old_file in os.listdir('uploads'):
        os.remove(os.path.join('uploads', old_file))
    for old_file in os.listdir('temp/semantic'):
        os.remove(os.path.join('temp/semantic', old_file))
    for old_file in os.listdir('temp/il'):
        os.remove(os.path.join('temp/il', old_file))
    for old_file in os.listdir('temp/out'):
        os.remove(os.path.join('temp/out', old_file))
    for old_file in os.listdir('temp/images'):
        os.remove(os.path.join('temp/images', old_file))

     # Save the image to a file
    temp_image_filepath = str(UPLOAD_PATH) + "/temp"
    temp_image_filepath += get_timestamp() + ".png"
    image.save(temp_image_filepath)  # Adjust the filename and format as needed

    # generate the output file
    results = image_to_out(temp_image_filepath, model_path, 'mei', 'wav')
    
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
    return render_template('output.html', input_image_path=temp_image_filepath, output_image_path=results[2], output_audio_path=results[3], semantic=semantic, mei=mei)

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

def predict(image_path, model_path):
    current_ts = get_timestamp()
    semantic_output_file = SEMANTIC_PATH + "temp" +current_ts + ".semantic"
    
    #run the prediction
    command = PYTHON3_PATH + " " + CTC_PREDICT_PATH + " -model " + model_path + " -image " + image_path + " -vocabulary " + VOCAB_PATH + " > " + semantic_output_file
    print(">" +command)
    subprocess.call(command, shell=True)
    print("---\n")

    return semantic_output_file

def semantic_to_IL(semantic_path, il, model_path=None):   
    if model_path is None:
        model_path = "unknown"

    il_output_file = IL_PATH + "temp" +get_timestamp()
    command = PYTHON3_PATH + " " + S2M_PATH + " " + semantic_path + " -type xml" +" -o " + il_output_file +" --title " +get_timestamp() + " --artist " +(model_path.split("/")[-1].split(".")[0])
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

def image_to_out(image_path, model_path, il="mei", out_type="wav"):
    semantic_file_path = predict(image_path, model_path)
    if not os.path.exists(semantic_file_path): 
        return (None, None, None, None)
    
    il_file_path = semantic_to_IL(semantic_file_path, il, model_path)
    if not os.path.exists(il_file_path+".mei"): 
        return (semantic_file_path, None, None, None)
    
    image_file_path = IL_to_image(il_file_path, il)
    if not os.path.exists(image_file_path):
        return (semantic_file_path, il_file_path + '.' +il, None, None)
    
    output_file_path = IL_to_out(il_file_path, il, out_type)
    if not os.path.exists(output_file_path):
        return (semantic_file_path, il_file_path + '.' +il, image_file_path, None)

    return (semantic_file_path, il_file_path + '.' +il, image_file_path, output_file_path)

if __name__ == '__main__':
    # Read the file paths from config.json
    with open(HOME_PATH +'/config.json') as json_file:
        data = json.load(json_file)
        MODEL_DIRECTORY = data['model_path']
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
    for path in [MODEL_DIRECTORY, CTC_PREDICT_PATH, S2M_PATH, VEROVIO_PATH, AUDIO_GENERATOR_PATH, PYTHON3_PATH, VOCAB_PATH, SEMANTIC_PATH, IL_PATH, IMAGE_PATH, OUT_PATH, temp_path, UPLOAD_PATH ]:
        if not os.path.exists(path):
            print("Path does not exist: \"" +path +"\"")
            if(input("Would you like to continue? [y/N] ") != 'y'):
                sys.exit(1)

    app.run(host='0.0.0.0', port=8890, debug=False)