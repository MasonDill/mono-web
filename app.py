from flask import Flask, request, render_template
import os

app = Flask(__name__)


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

    file.save(os.path.join('uploads', file.filename))

    return 'File uploaded successfully', 200




if __name__ == '__main__':
    app.run(port=8890, debug=True)
