#########################################################################################
#
# This script is essentially a Python 2.7 version of the VTL Matlab example 1
# Make sure these files are in the same directory as this script:
#   - VocalTractLabApi.so
#   - child-1y.speaker
# The output will be stored as:
#   - ai-child.wav (contains the simulated speech)
#
#########################################################################################

import ctypes			# for accessing C libraries 
import os			# for retrieving path names
import numpy  # for array operations
import scipy.io.wavfile # to write wav file


#########################################################################################
#
# Load Library
#
#########################################################################################

dllFile = os.path.abspath('VocalTractLabApi.so')
lib = ctypes.cdll.LoadLibrary(dllFile)



#########################################################################################
#
# Synthesize from a tract + glottis sequence.
#
#########################################################################################


speakerFileName = os.path.abspath('child-1y.speaker')
wavFileName = os.path.abspath('ai-child.wav')

lib.vtlInitialize(speakerFileName)

# get vtl constants
c_int_ptr = ctypes.c_int * 1 # type for int*
audioSamplingRate_ptr = c_int_ptr(0);
numTubeSections_ptr = c_int_ptr(0);
numVocalTractParams_ptr = c_int_ptr(0);
numGlottisParams_ptr = c_int_ptr(0);
lib.vtlGetConstants(audioSamplingRate_ptr, numTubeSections_ptr, numVocalTractParams_ptr, numGlottisParams_ptr);
audioSamplingRate = audioSamplingRate_ptr[0]
numTubeSections = numTubeSections_ptr[0]
numVocalTractParams = numVocalTractParams_ptr[0]
numGlottisParams = numGlottisParams_ptr[0]

# get tract info
c_numTractParam_ptr = ctypes.c_double * numVocalTractParams;
tractParamNames = ctypes.create_string_buffer(numVocalTractParams * 32);
tractParamMin = c_numTractParam_ptr(0);
tractParamMax = c_numTractParam_ptr(0);
tractParamNeutral = c_numTractParam_ptr(0);
lib.vtlGetTractParamInfo(tractParamNames, tractParamMin, tractParamMax, tractParamNeutral);

# get glottis info
c_numGlottisParam_ptr = ctypes.c_double * numGlottisParams;
glottisParamNames = ctypes.create_string_buffer(numGlottisParams * 32);
glottisParamMin = c_numGlottisParam_ptr(0);
glottisParamMax = c_numGlottisParam_ptr(0);
glottisParamNeutral = c_numGlottisParam_ptr(0);
lib.vtlGetGlottisParamInfo(glottisParamNames, glottisParamMin, glottisParamMax, glottisParamNeutral);

# get shape information from speaker
shapeName = 'a';
paramsA = c_numTractParam_ptr(0);
failure = lib.vtlGetTractParams(shapeName, paramsA);

if (failure != 0):
    print 'Error: Vocal tract shape "a" not in the speaker file!'

shapeName = 'i';
paramsI = c_numTractParam_ptr(0);
failure = lib.vtlGetTractParams(shapeName, paramsI);

if (failure != 0):
    print 'Error: Vocal tract shape "i" not in the speaker file!'

duration_s = 1.0;
frameRate_Hz = 200;
numFrames = round(duration_s * frameRate_Hz);
# 2000 samples more in the audio signal for safety.
c_audio_ptr = ctypes.c_double * int(duration_s * audioSamplingRate + 2000)
audio = c_audio_ptr(0);
numAudioSamples = c_int_ptr(0);

# Init the arrays.
tractParamFrame = [0] * numVocalTractParams;
glottisParamFrame = [0] * numGlottisParams;
c_tubeAreas_ptr = ctypes.c_double * int(numFrames * numTubeSections);
tubeAreas = c_tubeAreas_ptr(0);

tractParams = [];
glottisParams = [];

# Create the vocal tract shapes that slowly change from /a/ to /i/ from the
# first to the last frame.
for i in range(0, int(numFrames)):
    # The VT shape changes from /a/ to /i/.
    d = i / (numFrames-1)
    for j in range(0, len(paramsA)):
        tractParamFrame[j] = (1-d) * paramsA[j] + d * paramsI[j]

    # Set F0 in Hz.
    for j in range(0, numGlottisParams):
        # Take the neutral settings for the glottis here.    
        glottisParamFrame[j] = glottisParamNeutral[j]

    glottisParamFrame[0] = 300.0 - 20*(i/numFrames); # ONLY FOR CHILD VT
    
    glottisParamFrame[1] = 1000.0;
    
    # Append the parameters for the new frame to the parameter vectors.
    tractParams = tractParams + tractParamFrame
    glottisParams = glottisParams + glottisParamFrame
    

c_tractSequence_ptr = ctypes.c_double * int(numFrames * numVocalTractParams)
c_glottisSequence_ptr = ctypes.c_double * int(numFrames * numGlottisParams)

tractParams_ptr = c_tractSequence_ptr(*tractParams)
glottisParams_ptr = c_glottisSequence_ptr(*glottisParams)

lib.vtlSynthBlock(tractParams_ptr, glottisParams_ptr, tubeAreas, ctypes.c_int(int(numFrames)), ctypes.c_double(frameRate_Hz), audio, numAudioSamples);

copiedAudio = numpy.zeros(shape=(len(audio),1), dtype=numpy.float)
for i in range(0, len(audio)):
    copiedAudio[i] = audio[i]

# normalize audio and scale to int16 range
scaledAudio = numpy.int16(copiedAudio/numpy.max(numpy.abs(copiedAudio)) * 32767)
# write wave file
scipy.io.wavfile.write(wavFileName, 22050, scaledAudio)

lib.vtlClose()

print "done!"
