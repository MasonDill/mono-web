path_to_model = "/models/semantic_model.meta"
path_to_ctc_predict = "/tf-end-to-end/ctc_predict.py"
path_to_s2m = "/semantic_to_mei/semantic_to_mei.py"
python_path = "/usr/bin/python"
vocabulary_path = "/tf-end-to-end/Data/vocabulary_semantic.txt"

const OUTPUT_PATH = "/temp/out/"
const IL_OUTPUT_PATH = "/temp/IL/"


var express = require('express');
var app = express();
var bodyParser = require('body-parser');
var fs = require('fs');
var path = require('path');
var config = require("./config.json");
var cors = require('cors')

const { toUnicode } = require('punycode');
const { exec } = require('child_process');
const fileUpload = require('express-fileupload');

//https://mono-web.dill.digital/index

function check_file_exists(file_path){
  if (!fs.existsSync(file_paasth)) {
    throw "File does not exist " + file_path;
  }
}

//Take an image file and turn it into a semantic file using the model
async function predict(image_file_path){
  check_file_exists(image_file_path);
  check_file_exists(path_to_model);
  check_file_exists(path_to_ctc_predict);
  check_file_exists(python_path);
  check_file_exists(vocabulary_path);
  

  command = python_path + " " +path_to_ctc_predict + " -image " +image_file_path +" -model "+path_to_model +" -vocabulary " +vocabulary_path + " > /log.txt"
  console.log(command);
}

//Take a semantic file and turn it into a intermediate language
async function semantic_to_IL(semantic_file_path, IL){
  var il_output_file = "temp." + IL
  il_output_file = IL_OUTPUT_PATH +il_output_file

  //Use semantic_to_mei
  command = `${python_path} ${path_to_s2m} ${semantic_file_path} +type ${IL} +o ${il_output_file}`

   exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error: ${error}`);
      return;
    }
  });
  
  return il_output_file;
}


async function IL_to_out(IL_file, IL, out_type){
  var output_filepath = OUTPUT_PATH + "temp." + out_type
  //TODO
  //var command = 
  return output_filepath;
} 

async function image_to_out(image_file_path, IL, out_type){
  semantic_file_path = await predict(image_file_path)
  il_file_path = await semantic_to_IL(semantic_file_path, IL)
  output_filepath = IL_to_out(il_file_path, IL, out_type)
  return (semantic_file_path, il_file_path, output_filepath)
}