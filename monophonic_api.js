path_to_model = "/models/semantic_model.meta"
path_to_ctc_predict = "/tf-end-to-end/ctc_predict.py"
python_path = "/usr/bin/python"
vocabulary_path = "/tf-end-to-end/Data/vocabulary_semantic.txt"
//Use Node js and listen to port 8889
//This is the API for the monophonic synthesizer

var express = require('express');
var app = express();
var multer = require('multer');
var bodyParser = require('body-parser');
var fs = require('fs');
var path = require('path');
var config = require("./config.json")

// Set up Multer to handle file uploads
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
      // Specify the directory where uploaded files will be saved
      cb(null, 'uploads/');
    },
    filename: (req, file, cb) => {
      // Rename the uploaded file (you can customize the naming logic)
      cb(null, Date.now() + '-' + file.originalname);
    },
  });
const upload = multer({ storage: storage });

// Serve static files in the 'uploads' directory
app.use(express.static('uploads'));

//Create a server
port = 8890
var server = app.listen(port, function () {
    console.log('Server is listening on port ', port);
}
);
app.get('/', function (req, res) {
    res.sendFile(__dirname + '/index.html');
});

// Define a route to handle file uploads
app.post('/upload', upload.single('file'), (req, res) => {
    if (!req.file) {
      return res.status(400).json({ message: 'No file uploaded.' });
    }
    //#python ctc_predict.py -image Data/Example/000051652-1_2_1.png -model Models/semantic_model.meta -vocabulary Data/vocabulary_semantic.txt
    //ctc_predict with the uploaded file
    command = python_path + " " +path_to_ctc_predict + " -image " +path_input +" -model "+path_to_model +" -vocabulary " +vocabulary_path + " > /log.txt"
    console.log(command);

    //turn the semantic into midi file

    //return the midi file to the client
  
    // You can perform further processing on the uploaded file here
  
    res.status(200).json({ message: 'File uploaded successfully.' });
});
  


// //Create a socket
// var io = require('socket.io').listen(server);

// //Create a MIDI file
// var midi = require('midi-file');
// var output = midi.writer();

// //Create a MIDI file
// var midi = require('midi-file');
// var output = midi.writer();

