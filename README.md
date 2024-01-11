<h2>Introduction</h2>
  <p>This project was my senior project for the University of Pittsburgh, completed Fall 2023. The purpose of this project is to leverage a convolution recurrent nueral network to perform optical music recognition (OMR) on images of sheet music and synthesize an audio playback from the recognized musical symbols. The end goal is to facilitate the accessibility of music, allowing users to effortlessly convert sheet music into audio files, enhancing the overall learning and listening experience.
  </p>
<h2>Acknowledgments</h2>
  <p>I extend my gratitude to Calvo-Zaragoza, J. and Rizo, D., the Authors of End-to-End Neural Optical Music Recognition of Monophonic Scores. The ideas outlined in the paper, as well as the contributions to the primus dataset and the tf-end-to-end open-source code-base laid the groundwork for this exploration. This project builds upon their work extensively.</p>
  <p>I would also like to thank my teammate throughout the semester, Margeret Kilmeyer (<a href=https://github.com/mak453>https://github.com/mak453</a>) for her work on the audio synthesizer. </p>
<h2>Original OMR Source Code</h2>
  <p>The foundation of this project is based on the open-source TensorFlow code available at <a href="https://github.com/OMR-Research/tf-end-to-end">https://github.com/OMR-Research/tf-end-to-end</a>. The original code provided a starting point for my exploration into optical music recognition, and significant modifications have been made to enhance its utility.</p>
  <h2>Modified OMR Source Code</h2>
  <p>The modified source code, located at <a href="https://github.com/OMR-Research/tf-end-to-end">https://github.com/OMR-Research/tf-end-to-end</a>, reflects the tailored enhancements made to the original TensorFlow OMR model. The code has been modified to be compatible with TensorFlow 2. The addition of a data augmentation layer to the training algorithm is a notable improvement.</p>
 <h2>Published OMR Models</h2>
  <p>The trained and improved OMR model is accessible through the Hugging Face model hub at <a href="https://huggingface.co/MasonDill/Monophonic_OMR">https://huggingface.co/MasonDill/Monophonic_OMR</a>.</p>
  <h2>Transcoder: Semantic to MEI</h2>
  <p>To facilitate the transition from the output of the OMR model (semantic representation) to the input of an audio synthesizer, a transcoder was developed. This component converts the semantic representation of musical notations to the Music Encoding Initiative (MEI) format. The transcoder's code can be found at <a href="https://github.com/MasonDill/semantic21">https://github.com/MasonDill/semantic21</a>.</p>

  <h2>Audio Synthesizer: MEI to Wav</h2>
  <p>Completing the project's pipeline, an audio synthesizer has been implemented to convert MEI files to audible WAV files. The synthesizer takes the MEI representation of musical scores and produces high-quality audio output. The code for the audio synthesizer is available at <a href="https://github.com/mak453/AudioGenerator">https://github.com/mak453/AudioGenerator</a>.</p>
