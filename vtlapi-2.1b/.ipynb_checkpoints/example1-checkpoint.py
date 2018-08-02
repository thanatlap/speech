#!/usr/bin/env python3

'''
This example generates the transition from /a/ to /i/ using the vocal tract
model and the function vtlSynthBlock(...).

.. note::

    This example uses ``ctypes`` and is very close to the vocaltractlab API.
    This comes with breaking with some standard assumptions one have in python.
    If one wants a more pythonic experience use the ``pyvtl`` wrapper in order
    to use vocaltractlab from python. (pyvtl does not exist yet)

If you are not aware of ``ctypes`` read the following introduction
https://docs.python.org/3/library/ctypes.html

For an in-depth API description look at the `VocalTractLabApi64.h`.

For plotting and saving results you need to install ``matplotlib``, ``numpy``,
and ``scipy``.

'''

import ctypes
import sys

# try to load some non-essential packages
try:
    import numpy as np
except ImportError:
    np = None
try:
    from scipy.io import wavfile
except ImportError:
    wavefile = None
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


# load vocaltractlab binary
# Use 'VocalTractLabApi32.dll' if you use a 32-bit python version.
if sys.platform == 'win32':
    VTL = ctypes.cdll.LoadLibrary('./VocalTractLabApi64.dll')
else:
    VTL = ctypes.cdll.LoadLibrary('./VocalTractLabApi64.so')


# get version / compile date
version = ctypes.c_char_p(b'                                ')
VTL.vtlGetVersion(version)
print('Compile date of the library: "%s"' % version.value.decode())


# initialize vtl
speaker_file_name = ctypes.c_char_p('JD2.speaker'.encode())

failure = VTL.vtlInitialize(speaker_file_name)
if failure != 0:
    raise ValueError('Error in vtlInitialize! Errorcode: %i' % failure)


# get some constants
audio_sampling_rate = ctypes.c_int(0)
number_tube_sections = ctypes.c_int(0)
number_vocal_tract_parameters = ctypes.c_int(0)
number_glottis_parameters = ctypes.c_int(0)

VTL.vtlGetConstants(ctypes.byref(audio_sampling_rate),
                    ctypes.byref(number_tube_sections),
                    ctypes.byref(number_vocal_tract_parameters),
                    ctypes.byref(number_glottis_parameters))

print('Audio sampling rate = %i' % audio_sampling_rate.value)
print('Num. of tube sections = %i' % number_tube_sections.value)
print('Num. of vocal tract parameters = %i' % number_vocal_tract_parameters.value)
print('Num. of glottis parameters = %i' % number_glottis_parameters.value)


# get information about the parameters of the vocal tract model
# Hint: Reserve 32 chars for each parameter.
TRACT_PARAM_TYPE = ctypes.c_double * number_vocal_tract_parameters.value
tract_param_names = ctypes.c_char_p((' ' * 32 * number_vocal_tract_parameters.value).encode())
tract_param_min = TRACT_PARAM_TYPE()
tract_param_max = TRACT_PARAM_TYPE()
tract_param_neutral = TRACT_PARAM_TYPE()

VTL.vtlGetTractParamInfo(tract_param_names,
                         ctypes.byref(tract_param_min),
                         ctypes.byref(tract_param_max),
                         ctypes.byref(tract_param_neutral))

print('Vocal tract parameters: "%s"' % tract_param_names.value.decode())
print('Vocal tract parameter minima: ' + str(list(tract_param_min)))
print('Vocal tract parameter maxima: ' + str(list(tract_param_max)))
print('Vocal tract parameter neutral: ' + str(list(tract_param_neutral)))

# get information about the parameters of glottis model
# Hint: Reserve 32 chars for each parameter.
GLOTTIS_PARAM_TYPE = ctypes.c_double * number_glottis_parameters.value
glottis_param_names = ctypes.c_char_p((' ' * 32 * number_glottis_parameters.value).encode())
glottis_param_min = GLOTTIS_PARAM_TYPE()
glottis_param_max = GLOTTIS_PARAM_TYPE()
glottis_param_neutral = GLOTTIS_PARAM_TYPE()

VTL.vtlGetGlottisParamInfo(glottis_param_names,
                           ctypes.byref(glottis_param_min),
                           ctypes.byref(glottis_param_max),
                           ctypes.byref(glottis_param_neutral))

print('Glottis parameters: "%s"' % glottis_param_names.value.decode())
print('Glottis parameter minima: ' + str(list(glottis_param_min)))
print('Glottis parameter maxima: ' + str(list(glottis_param_max)))
print('Glottis parameter neutral: ' + str(list(glottis_param_neutral)))


# Get the vocal tract parameter values for the vocal tract shapes of /i/
# and /a/, which are saved in the speaker file.

shape_name = ctypes.c_char_p(b'a')
params_a = TRACT_PARAM_TYPE()
failure = VTL.vtlGetTractParams(shape_name, ctypes.byref(params_a))
if failure != 0:
    raise ValueError('Error in vtlGetTractParams! Errorcode: %i' % failure)

shape_name = ctypes.c_char_p(b'i')
params_i = TRACT_PARAM_TYPE()
failure = VTL.vtlGetTractParams(shape_name, ctypes.byref(params_i))
if failure != 0:
    raise ValueError('Error in vtlGetTractParams! Errorcode: %i' % failure)

del shape_name


# Synthesize a transition from /a/ to /i/.
##########################################

duration_s = 1.0  # seconds
frame_rate = 200.0  # Hz
number_frames = int(duration_s * frame_rate)
# within first parenthesis type definition, second initialisation
# 2000 samples more in the audio signal for safety
audio = (ctypes.c_double * int(duration_s * audio_sampling_rate.value + 2000))()
number_audio_samples = ctypes.c_int(0)

# init the arrays
tract_params = (ctypes.c_double * (number_frames * number_vocal_tract_parameters.value))()
glottis_params = (ctypes.c_double * (number_frames * number_glottis_parameters.value))()
tube_areas = (ctypes.c_double * (number_frames * number_tube_sections.value))()
tube_articulators = ctypes.c_char_p(b' ' * number_frames * number_tube_sections.value)

# Create the vocal tract shapes that slowly change from /a/ to /i/ from the
# first to the last frame.

for ii in range(number_frames):
    # transition linearly from /a/ to /i/
    dd = ii / (number_frames - 1)
    for jj in range(number_vocal_tract_parameters.value):
        tract_params[ii * number_vocal_tract_parameters.value + jj] =\
                (1 - dd) * params_a[jj] + dd * params_i[jj]

    offset_glottis = ii * number_glottis_parameters.value
    # transition F0 in Hz going from 120 Hz down to 100 Hz
    glottis_params[offset_glottis + 0] = 120.0 - 20.0 * (ii / number_frames)

    # Start with zero subglottal pressure and then go to 1000 Pa.
    # Somehow, P_sub must stay at zero for the first two frames - otherwise
    # we get an annoying transient at the beginning of the audio signal,
    # and I (Peter) don't know why this is so at the moment.
    if ii <= 1:
        glottis_params[offset_glottis + 1] = 0.0
    elif ii == 2:
        glottis_params[offset_glottis + 1] = 500.0
    else:
        glottis_params[offset_glottis + 1] = 1000.0

    # use the neutral settings for the rest of glottis parameters
    for jj in range(2, number_glottis_parameters.value):
        glottis_params[offset_glottis + jj] = glottis_param_neutral[jj]


# Call the synthesis function. It may calculate a few seconds.
failure = VTL.vtlSynthBlock(ctypes.byref(tract_params),  # input
                            ctypes.byref(glottis_params),  # input
                            ctypes.byref(tube_areas),  # output
                            tube_articulators,  # output
                            number_frames,  # input
                            ctypes.c_double(frame_rate),  # input
                            ctypes.byref(audio),  # output
                            ctypes.byref(number_audio_samples))  # output

if failure != 0:
    raise ValueError('Error in vtlSynthBlock! Errorcode: %i' % failure)

print('First 40 data points for every vector:')
print('  tube_areas: %s' % str(list(tube_areas)[:40]))
print('  tube_articulators: %s' % tube_articulators.value[:40])
print('  audio: %s' % str(list(audio)[:40]))
print('  number_audio_samples: %i' % number_audio_samples.value)

# destroy current state of VTL and free memory
VTL.vtlClose()


# plot and save the audio signal
################################

if np is not None:
    wav = np.array(audio)

if plt is not None and np is not None:
    time_wav = np.arange(len(wav)) / frame_rate
    plt.plot(time_wav, wav, c='black', alpha=0.75)
    plt.ylabel('amplitude')
    plt.ylim(-1, 1)
    plt.xlabel('time [s]')
    print('\nClose the plot in order to continue.')
    plt.show()
else:
    print('plotting not available; matplotlib needed')
    print('skip plotting')


if wavfile is not None and np is not None:
    wav_int = np.int16(wav  * (2 ** 15 - 1))
    wavfile.write('ai_test.wav', audio_sampling_rate.value, wav_int)
    print('saved audio to "ai_test.wav"')
else:
    print('scipy not available')
    print('skip writing out wav file')

# Plot the area function of the first and the last frame.
# TODO
# Matlab code:
#figure;
#plot(1:1:numTubeSections, tubeAreas(1:numTubeSections), ...
#    1:1:numTubeSections,
#    tubeAreas(1+(numFrames-1)*numTubeSections:(numFrames-1)*numTubeSections +
#    numTubeSections));
#xlabel('Position in cm');
#ylabel('Tube section index');

