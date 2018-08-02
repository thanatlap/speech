#########################################################################################
#
# This script is essentially a Python 2.7 version of the VTL Matlab example 2,
#   section "Synthesize from a gestural score"
# Make sure these files are in the same directory as this script:
#   - VocalTractLabApi.so
#   - child-1y.speaker
#   - mama-child.ges
# The output will be stored as:
#   - mama-child.wav (contains the simulated speech)
#   - mama-child-areas.txt (contains various simulation parameters)
# Repair the wave file with the script "repair_header.py".
#
#########################################################################################

import ctypes			# for accessing C libraries 
import os			# for retrieving path names


#########################################################################################
#
# Load Library
#
#########################################################################################

dllFile = os.path.abspath('VocalTractLabApi.so')
                    # get path to library
lib = ctypes.cdll.LoadLibrary(dllFile)
                    # load library


#########################################################################################
#
# Synthesize from a gestural score
#
#########################################################################################


speakerFileName = os.path.abspath('child-1y.speaker')
gestureFileName = os.path.abspath('mama-child.ges')
                    # get paths to input files
wavFileName = os.path.abspath('mama-child.wav')
areaFileName = os.path.abspath('mama-child-areas.txt')
                    # get paths to output files

print 'Calling gesToWav()...'

failure = lib.vtlGesToWav(speakerFileName, gestureFileName, wavFileName, areaFileName)
                    # execute library function and receive return value

if (failure != 0):
    print 'Error in vtlGesToWav()!'

print 'Finished.'
