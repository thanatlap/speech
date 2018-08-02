#!/usr/bin/env python3

'''
This example generates the speech waveform directly from a gestural score.

Look into example1.py for more thorough comments on how to interface
vocaltractlab API from python3.

'''

import ctypes
import os
import shutil
import sys

# Use 'VocalTractLabApi32.dll' if you use a 32-bit python version.

if sys.platform == 'win32':
    VTL = ctypes.cdll.LoadLibrary('./VocalTractLabApi64.dll')
else:
    VTL = ctypes.cdll.LoadLibrary('./VocalTractLabApi64.so')


# get version / compile date
version = ctypes.c_char_p(b'                                ')
VTL.vtlGetVersion(version)
print('Compile date of the library: "%s"' % version.value.decode())


# Synthesize from a gestural score.
speaker_file_name = ctypes.c_char_p(b'JD2.speaker')
gesture_file_name = ctypes.c_char_p(b'example-hallo.ges')
wav_file_name = ctypes.c_char_p(b'example-hallo.wav')
feedback_file_name = ctypes.c_char_p(b'example-hallo.txt')

print('Calling gesToWav()...')

failure = VTL.vtlGesToWav(speaker_file_name,  # input
                          gesture_file_name,  # input
                          wav_file_name,  # output
                          feedback_file_name)  # output

if failure != 0:
    raise ValueError('Error in vtlGesToWav! Errorcode: %i' % failure)


print('Finished.')

print('Stored results in "%s" and "%s".' % (wav_file_name.value.decode(),
                                            feedback_file_name.value.decode()))


# fix wav header on non windows os
if sys.platform != 'win32':
    WAV_HEADER = (b'RIFF\x8c\x87\x00\x00WAVEfmt\x20\x10\x00\x00\x00\x01\x00\x01'
                  + b'\x00"V\x00\x00D\xac\x00\x00\x02\x00\x10\x00data')

    wav_file = wav_file_name.value.decode()
    with open(wav_file, 'rb') as file_:
        content = file_.read()

    shutil.move(wav_file, wav_file + '.bkup')

    with open(wav_file, 'wb') as newfile:
        newcontent = WAV_HEADER + content[68:]
        newfile.write(newcontent)

    os.remove(wav_file + '.bkup')

    print('Fixed header in %s.' % wav_file)

