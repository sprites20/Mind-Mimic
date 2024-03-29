#!/usr/bin/env python3

import os
import sys
import wave
import json
import numpy as np

import argparse
import queue
import sys
import sounddevice as sd
from pydub.silence import split_on_silence
from pydub import AudioSegment

from vosk import Model, KaldiRecognizer, SpkModel

SPK_MODEL_PATH = "vosk-model-spk-0.4"
q = queue.Queue()


if not os.path.exists(SPK_MODEL_PATH):
    print("Please download the speaker model from "
        "https://alphacephei.com/vosk/models and unpack as {SPK_MODEL_PATH} "
        "in the current folder.")
    sys.exit(1)

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata)) 
    
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    "-l", "--list-devices", action="store_true",
    help="show list of audio devices and exit")
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    sys.exit(0)

parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    "-f", "--filename", type=str, metavar="FILENAME",
    help="audio file to store recording to")
parser.add_argument(
    "-d", "--device", type=int_or_str,
    help="input device (numeric ID or substring)")
parser.add_argument(
    "-r", "--samplerate", type=int, help="sampling rate")
parser.add_argument(
    "-m", "--model", type=str, help="language model; e.g. en-us, fr, nl; default is en-us")
args = parser.parse_args(remaining)
"""
wf = wave.open(sys.argv[1], "rb")
if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
    print("Audio file must be WAV format mono PCM.")
    sys.exit(1)
"""
# Large vocabulary free form recognition
model = Model("vosk-model-small-en-us-0.15")
spk_model = SpkModel(SPK_MODEL_PATH)
#rec = KaldiRecognizer(model, wf.getframerate(), spk_model)
#rec = KaldiRecognizer(model, wf.getframerate())


# We compare speakers with cosine distance.
# We can keep one or several fingerprints for the speaker in a database
# to distingusih among users.
spk_sig = [-0.645543, 1.267236, 1.739462, -0.717491, -0.157087, 0.147635, -1.308505, -0.446466, 0.116764, -0.115046, 0.376392, 0.62511, 0.554749, 0.871882, 1.705446, 1.346732, -0.237086, 0.554086, 0.171249, 0.035732, 0.079214, -0.577399, 1.605019, -0.872605, -0.80465, -0.402827, -0.621014, -0.13613, 1.766777, 1.253641, -1.048572, -1.723634, -0.525028, -0.512419, 0.979154, -0.29935, -1.11108, 1.460288, -0.492389, -0.165662, -0.274988, 0.458642, 1.453099, 1.092062, -0.856726, 0.724769, 0.423962, -0.774903, -0.434743, -0.083244, 0.685712, -0.579763, -0.160493, 0.699621, -0.95782, -1.056444, -0.218858, 0.508616, -0.441598, 0.140081, 0.870923, -1.356405, -0.179892, -0.495612, -0.165929, 0.162548, -0.490384, 0.044856, -0.585081, 2.214094, 0.511557, -2.132176, -0.329827, 1.419002, -1.156591, -0.265651, -1.553596, -0.50643, 0.627002, -1.194909, -0.253832, 0.115579, 0.164481, -0.543525, -0.657609, 0.529603, 0.917261, 1.276905, 2.072457, 0.501246, -0.229274, 0.554694, -1.703213, -0.693821, 0.768317, -0.404479, 2.06889, -1.26462, -0.019318, 0.715243, 1.138082, -1.728924, -0.714421, -1.267921, 1.681902, -1.716266, -0.074632, -2.936986, -2.350122, 0.001327, -0.382891, -0.688902, 1.322296, -0.987495, 1.975746, -0.44887, 0.185008, 0.067595, 0.665363, 0.246385, 0.719629, 0.506032, -0.988654, 0.606328, -1.949532, 1.727559, -1.032074, -0.772542]

def cosine_similarity_average(speaker_embeddings, target_speaker):
    lowest_similarity = {}

    for speaker, embeddings in speaker_embeddings.items():
        # Get the lowest similarity among the two embeddings for each speaker
        similarities = [cosine_dist(target_speaker, embedding) for embedding in embeddings]
        lowest_similarity[speaker] = min(similarities)

    return lowest_similarity

def recognize_speaker(target_speaker):
    speakers = {
        "speaker1": [[-0.645543, 1.267236, 1.739462, -0.717491, -0.157087, 0.147635, -1.308505, -0.446466, 0.116764, -0.115046, 0.376392, 0.62511, 0.554749, 0.871882, 1.705446, 1.346732, -0.237086, 0.554086, 0.171249, 0.035732, 0.079214, -0.577399, 1.605019, -0.872605, -0.80465, -0.402827, -0.621014, -0.13613, 1.766777, 1.253641, -1.048572, -1.723634, -0.525028, -0.512419, 0.979154, -0.29935, -1.11108, 1.460288, -0.492389, -0.165662, -0.274988, 0.458642, 1.453099, 1.092062, -0.856726, 0.724769, 0.423962, -0.774903, -0.434743, -0.083244, 0.685712, -0.579763, -0.160493, 0.699621, -0.95782, -1.056444, -0.218858, 0.508616, -0.441598, 0.140081, 0.870923, -1.356405, -0.179892, -0.495612, -0.165929, 0.162548, -0.490384, 0.044856, -0.585081, 2.214094, 0.511557, -2.132176, -0.329827, 1.419002, -1.156591, -0.265651, -1.553596, -0.50643, 0.627002, -1.194909, -0.253832, 0.115579, 0.164481, -0.543525, -0.657609, 0.529603, 0.917261, 1.276905, 2.072457, 0.501246, -0.229274, 0.554694, -1.703213, -0.693821, 0.768317, -0.404479, 2.06889, -1.26462, -0.019318, 0.715243, 1.138082, -1.728924, -0.714421, -1.267921, 1.681902, -1.716266, -0.074632, -2.936986, -2.350122, 0.001327, -0.382891, -0.688902, 1.322296, -0.987495, 1.975746, -0.44887, 0.185008, 0.067595, 0.665363, 0.246385, 0.719629, 0.506032, -0.988654, 0.606328, -1.949532, 1.727559, -1.032074, -0.772542],
                [-0.683516, 0.722179, 1.651159, -0.311776, -0.35272, -0.542711, -0.169784, 0.146419, 0.639174, 0.260786, 0.512685, -0.567375, 0.510885, 1.081993, 0.730045, 1.644301, -0.388575, 0.594761, 0.580934, 1.701163, 0.542753, -0.030902, 0.940672, -0.681181, -0.961269, -0.953732, 0.342842, 0.212761, 1.010038, 0.789226, -0.440633, -1.639356, 0.098124, -0.453873, -0.1269, -0.831008, -1.336311, 1.838328, -1.500506, 0.398561, -0.139225, 0.602066, 1.217693, -0.28669, -1.240536, 0.828214, -0.385781, -1.585939, -0.253948, 0.6254, -1.144157, -1.09649, -1.247936, -0.164992, -1.131125, -0.827816, 1.595752, 1.22196, -0.260766, -0.053225, 0.372862, -0.496685, 0.559101, 0.313831, 0.906749, -0.911119, -0.718342, 0.731359, -0.060828, 0.889468, 0.870002, -1.046849, 0.358473, 1.403957, -0.55995, 0.544278, 0.252579, 0.176449, -0.973618, -1.316356, -1.39273, -0.397281, -1.244906, -2.552846, -0.056479, 0.00252, -0.071661, 0.549343, -0.563582, 0.298601, -1.599536, 0.060805, -1.131684, -0.236406, 0.10192, -0.05143, 2.822287, 0.298605, 0.027687, 1.805171, 0.535367, -0.750344, 0.195215, -2.74342, -0.240448, -1.853602, 0.667115, -1.152912, -1.458451, -0.463823, -1.081316, 1.07476, 1.69582, 0.083853, 0.208222, -0.203687, -0.761975, 2.021879, 2.07578, 0.214109, 1.010975, -0.535104, -1.102454, 1.422523, -1.389488, 2.282245, 0.526214, -0.289677],
                [-0.645543, 1.267236, 1.739462, -0.717491, -0.157087, 0.147635, -1.308505, -0.446466, 0.116764, -0.115046, 0.376392, 0.62511, 0.554749, 0.871882, 1.705446, 1.346732, -0.237086, 0.554086, 0.171249, 0.035732, 0.079214, -0.577399, 1.605019, -0.872605, -0.80465, -0.402827, -0.621014, -0.13613, 1.766777, 1.253641, -1.048572, -1.723634, -0.525028, -0.512419, 0.979154, -0.29935, -1.11108, 1.460288, -0.492389, -0.165662, -0.274988, 0.458642, 1.453099, 1.092062, -0.856726, 0.724769, 0.423962, -0.774903, -0.434743, -0.083244, 0.685712, -0.579763, -0.160493, 0.699621, -0.95782, -1.056444, -0.218858, 0.508616, -0.441598, 0.140081, 0.870923, -1.356405, -0.179892, -0.495612, -0.165929, 0.162548, -0.490384, 0.044856, -0.585081, 2.214094, 0.511557, -2.132176, -0.329827, 1.419002, -1.156591, -0.265651, -1.553596, -0.50643, 0.627002, -1.194909, -0.253832, 0.115579, 0.164481, -0.543525, -0.657609, 0.529603, 0.917261, 1.276905, 2.072457, 0.501246, -0.229274, 0.554694, -1.703213, -0.693821, 0.768317, -0.404479, 2.06889, -1.26462, -0.019318, 0.715243, 1.138082, -1.728924, -0.714421, -1.267921, 1.681902, -1.716266, -0.074632, -2.936986, -2.350122, 0.001327, -0.382891, -0.688902, 1.322296, -0.987495, 1.975746, -0.44887, 0.185008, 0.067595, 0.665363, 0.246385, 0.719629, 0.506032, -0.988654, 0.606328, -1.949532, 1.727559, -1.032074, -0.772542],
            
        ],
    }
    #Iterate in speakers and get average cosine similarity and return average cosine similarity for each and the lowest
    lowest_similarity = cosine_similarity_average(speakers, target_speaker)

    # Print the results
    print("Lowest Similarities:")
    dspeaker, thesim = None, None
    for speaker, lowest_sim in lowest_similarity.items():
        print(f"{speaker}: {lowest_sim}")
        dspeaker, thesim = speaker, lowest_sim
        break
    
    #print(cosine_similarity_average(speakers, target_speaker))
    if thesim > 0.55:
        dspeaker = "Unknown User"
    return dspeaker
def cosine_dist(x, y):
    nx = np.array(x)
    ny = np.array(y)
    return 1 - np.dot(nx, ny) / np.linalg.norm(nx) / np.linalg.norm(ny)
def save_audio(filename, audio_data, samplerate):
    audio_segment = AudioSegment(
        data=audio_data, sample_width=2, frame_rate=samplerate, channels=1
    )
    audio_segment.export(filename, format="wav")
# Function to modify already saved audio file
def modify_saved_audio(input_filename, output_filename, samplerate):
    audio_segment = AudioSegment.from_wav(input_filename)

    # Split the audio based on silence
    # Adjust silence detection parameters as needed
    segments = split_on_silence(audio_segment, silence_thresh=-40, keep_silence=100)

    # Concatenate non-silent segments
    concatenated_audio = AudioSegment.silent()
    for i, segment in enumerate(segments):
        concatenated_audio += segment

    # Save the concatenated audio
    concatenated_audio.export(output_filename, format="wav")

try:
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, "input")
        args.samplerate = int(device_info["default_samplerate"])


    with sd.RawInputStream(samplerate=args.samplerate, blocksize=8000, device=args.device,
            dtype="int16", channels=1, callback=callback):
        print("#" * 80)
        print("Press Ctrl+C to stop the recording")
        print("#" * 80)

        rec = KaldiRecognizer(model, args.samplerate)
        rec.SetSpkModel(spk_model)
        recording_started = False
        audio_data = b""

        while True:
            data = q.get()

            if rec.PartialResult() != "":
                if not recording_started:
                    print("Recording started.")
                    recording_started = True

            if recording_started:
                audio_data += data

            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                print("Text:", res["text"])
                print("Recording stopped.")
                result = json.loads(rec.Result()).get("text")
                print(result)
                #self.change_text_input(result)
                save_audio("output_audio.wav", audio_data, args.samplerate)

                # After recording is done and you have an output audio file
                input_audio_filename = "output_audio.wav"
                output_audio_filename = "modified_output_audio.wav"

                modify_saved_audio(input_audio_filename, output_audio_filename, args.samplerate)

                recording_started = False
                audio_data = b""
                if "spk" in res:
                    recognize_speaker(res["spk"])
                    print("X-vector:", res["spk"])
                    print("Speaker distance:", cosine_dist(spk_sig, res["spk"]),
                        "based on", res["spk_frames"], "frames")
                
except KeyboardInterrupt:
    print("\nDone")
except Exception as e:
    print(type(e).__name__ + ": " + str(e))
"""
while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        res = json.loads(rec.Result())
        print("Text:", res["text"])
        if "spk" in res:
            print("X-vector:", res["spk"])
            print("Speaker distance:", cosine_dist(spk_sig, res["spk"]),
                "based on", res["spk_frames"], "frames")
"""
print("Note that second distance is not very reliable because utterance is too short. "
    "Utterances longer than 4 seconds give better xvector")
"""
res = json.loads(rec.FinalResult())
print("Text:", res["text"])
if "spk" in res:
    print("X-vector:", res["spk"])
    print("Speaker distance:", cosine_dist(spk_sig, res["spk"]),
        "based on", res["spk_frames"], "frames")
"""
