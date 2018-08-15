%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This example simply shows how to obtain the voclume velocity transfer
% function of the vocal tract based on vocal tract parameters for a certain
% phone in the speaker file.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% File name of the dll and header file (they differ only in the extension).
% Use 'VocalTractLabApi32' if you have an old 32-bit Matlab version.

libName = 'VocalTractLabApi64';

if ~libisloaded(libName)
    % To load the library, specify the name of the DLL and the name of the
    % header file. If no file extensions are provided (as below)
    % LOADLIBRARY assumes that the DLL ends with .dll and the header file
    % ends with .h.
    loadlibrary(libName, libName);
    disp(['Loaded library: ' libName]);
    pause(1);
end

if ~libisloaded(libName)
    error(['Failed to load external library: ' libName]);
    success = 0;
    return;
end

% *****************************************************************************
% list the methods
% *****************************************************************************

libfunctions(libName);   

% *****************************************************************************
% Print the version (compile date) of the library.
%
% void vtlGetVersion(char *version);
% *****************************************************************************

% Init the variable version with enough characters for the version string
% to fit in.
version = '                                ';
version = calllib(libName, 'vtlGetVersion', version);

disp(['Compile date of the library: ' version]);

% *****************************************************************************
% Initialize the VTL synthesis with the given speaker file name.
%
% void vtlInitialize(const char *speakerFileName)
% *****************************************************************************

speakerFileName = 'JD2.speaker';

failure = calllib(libName, 'vtlInitialize', speakerFileName);
if (failure ~= 0)
    disp('Error in vtlInitialize()!');   
    return;
end

% *****************************************************************************
% Get some constants.
%
% void vtlGetConstants(int *audioSamplingRate, int *numTubeSections,
%   int *numVocalTractParams, int *numGlottisParams);
% *****************************************************************************

audioSamplingRate = 0;
numTubeSections = 0;
numVocalTractParams = 0;
numGlottisParams = 0;

[audioSamplingRate, numTubeSections, numVocalTractParams, numGlottisParams] = ...
    calllib(libName, 'vtlGetConstants', audioSamplingRate, numTubeSections, numVocalTractParams, numGlottisParams);

disp(['Audio sampling rate = ' num2str(audioSamplingRate)]);
disp(['Num. of tube sections = ' num2str(numTubeSections)]);
disp(['Num. of vocal tract parameters = ' num2str(numVocalTractParams)]);
disp(['Num. of glottis parameters = ' num2str(numGlottisParams)]);

% *****************************************************************************
% Get the vocal tract parameters for the phone /a/.
%
% int vtlGetTractParams(char *shapeName, double *param);
% *****************************************************************************

vocalTractParams = zeros(1, numVocalTractParams);
shapeName = 'a';

[failed, shapeName, vocalTractParams] = ...
  calllib(libName, 'vtlGetTractParams', shapeName, vocalTractParams);

% *****************************************************************************
% void vtlGetTransferFunction(double *tractParams, int numSpectrumSamples,
%  double *magnitude, double *phase_rad);
% *****************************************************************************

NUM_SPECTRUM_SAMPLES = 1024;
magSpectrum = zeros(1, NUM_SPECTRUM_SAMPLES);
phaseSpectrum = zeros(1, NUM_SPECTRUM_SAMPLES);

[vocalTractParams, magSpectrum, phaseSpectrum] = ...
  calllib(libName, 'vtlGetTransferFunction', vocalTractParams, ...
    NUM_SPECTRUM_SAMPLES, magSpectrum, phaseSpectrum);

% Plot the transfer function.

freqAxis = double(0:1:NUM_SPECTRUM_SAMPLES-1);
freqAxis = (double(audioSamplingRate) / double(NUM_SPECTRUM_SAMPLES)).*freqAxis;
plot(freqAxis, 20*log10(magSpectrum), freqAxis, phaseSpectrum);

xlabel('Frequency in Hz');
ylabel('Log. magnitude in dB, phase in rad');

% *****************************************************************************
% Close the VTL synthesis.
%
% void vtlClose();
% *****************************************************************************

calllib(libName, 'vtlClose');

unloadlibrary(libName);

