This is a short description of the files included in the Linux release of the VocalTractLab 2.1 API (as of 2014/9/10):

- VocalTractLabApi.so: 
    The library. This is the essential file you'll be working with.
- VocalTractLabApi.h, VocalTractLabApi.def:
    If you access VTL via Matlab, you'll need these files, which define the API entry points.
- VtlMatlabExample1.m, VtlMatlabExample2.m: 
    Matlab scripts that show you how to use various VTL functions from within Matlab.
- GesToWave_Example.py: 
    A small Python script that shows how to access the library and execute the function "vtlGesToWav" using Python 2.7.
- TractSeqToWave_Example.py:
    A Python 2.7 script that shows how to produce audio from a tract and glottis sequence (adapted from VtlMatlabExample1.m).
- repair_header.py: 
    vtlGesToWav produces wave files with corrupt headers. This Python script fixes those headers.
- child-1y.speaker:
    Speaker file, required for all examples.
- mama-child.ges: 
    Gestural score file, required for executing the vtlGesToWav examples.
