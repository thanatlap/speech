#Python 3.6.3 on win32
#Train VTL to synthesize /nanana/ sequence by Anqi Xu (a.xu.17@ucl.ac.uk)
#Velum constraints included; Tongue constraints included
#1% resistance and 20% hard change link
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                          load packages                                                               #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
import os, ctypes, time, random; #no need to install
import xml.etree.ElementTree as et; #no need to install #among all packages that parse hml file, it is the fastest
import numpy as np, matplotlib.pyplot as plt, librosa; #install needed

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                                Initialization                                                             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#start timer
start = time.time();

#set working directory
os.chdir('C:/Users/a.xu/Desktop/VTLAPI2.2-Windows');

#Load VocalTractLab library
VTL = ctypes.cdll.LoadLibrary('./VocalTractLabApi.dll');

#initialize synthesis settings
speaker_file_name = ctypes.c_char_p('nanana.speaker'.encode());
gesture_file_name = ctypes.c_char_p('nanana.ges'.encode());
wav_file_name = ctypes.c_char_p('nanana.wav'.encode());
feedback_file_name = ctypes.c_char_p('feedback.txt'.encode());
#The range of vocal tract parameters (VTP)
VTP_max_min = np.array([[0,1],[-6,-3.5],[-0.5,0],[-7,0],[-1,1],[-2,4],[0,1],[-0.1,1],[0,0],[-3,4],[-3,1],[1.5,5.5],[-3,2.5],[-3,4],[-3,5],[-4,2],[-6,0],[-1.4,1.4],[-1.4,1.4],[-1.4,1.4],[-1.4,1.4],[-0.05,-0.05],[-0.05,-0.05],[-0.05,-0.05]]);

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                            tongue and velum constraints                                  #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#Constraints1: Tongue parameters constraints: whenever the tongue blade paramters (TBX/TBY) were adjusted, those of tongue tip and tongue body were also modified by 20% with 1% resistance
def constrained_parameterT(ii, TBX, TBY, current_VTP, VTP_max_min):
    if ii == 9 or 11: #TCX and TTX changes according to TBX; TCY and TTY changes according to TBY
        change = TBX - current_VTP[13];
    else: #TCY and TTY changes according to TBY
        change = TBY - current_VTP[14];
    #TCX constraints
    if current_VTP[ii]*0.99+change*0.2 == max(VTP_max_min[ii]): #make sure it stays within the VTP range
        constrained_parameter = max(VTP_max_min[ii]);
    elif current_VTP[ii]*0.99+change*0.2 == min(VTP_max_min[ii]):
        constrained_parameter = min(VTP_max_min[ii]);
    else:
        constrained_parameter = current_VTP[ii]*0.99+change*0.2;
    return  constrained_parameter

#Constraints2:tongue body and velum constraints; every time the TCY parameter changes, velum opening changes by 20% with 1% resistance
def constrained_parameterVO(ii, TCY, current_VTP, VTP_max_min):
    change = TCY - current_VTP[10];
    if current_VTP[ii]*0.99+change*0.2 == max(VTP_max_min[ii]):
        constrained_parameter = max(VTP_max_min[ii]);
    elif current_VTP[ii]*0.99+change*0.2 == min(VTP_max_min[ii]):
        constrained_parameter = min(VTP_max_min[ii]);
    else:
        constrained_parameter = current_VTP[ii]*0.99+change*0.2;
    return  constrained_parameter
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                          Generate random vocal tract parameters function                                 #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
def randomVTP_1():
    HX=random.uniform(0,1);# Generate random number from 0 to 1
    HY=random.uniform(-6,-3.5);
    JX=random.uniform(-0.5,0);
    JA=random.uniform(-7,0);
    LP=random.uniform(-1,1);
    LD=random.uniform(-2,4);
    VS=random.uniform(0,1);
    WC=0; #Not included in Prom-on et al., 2014, use netrual parameter instead
    TBX=random.uniform(-3,4);
    TBY=random.uniform(-3,5); 
    TRX=random.uniform(-4,2);
    TRY=random.uniform(-6,0); 
    TS1=random.uniform(-1.4,1.4); 
    TS2=random.uniform(-1.4,1.4); 
    TS3=random.uniform(-1.4,1.4); 
    TS4=random.uniform(-1.4,1.4); 
    MA1= -0.05;
    MA2= -0.05;
    MA3= -0.05;
	#Get VTP of tongue body (TCX, TCY), tongue tip (TTX,TTY) and velum opening (VO) by constraints
    TCX = constrained_parameterT(9, TBX, TBY, current_VTP_1, VTP_max_min);
    TCY = constrained_parameterT(10, TBX, TBY, current_VTP_1, VTP_max_min);
    TTX = constrained_parameterT(11, TBX, TBY, current_VTP_1, VTP_max_min);
    TTY = constrained_parameterT(12, TBX, TBY,current_VTP_1, VTP_max_min);
    VO = constrained_parameterVO(7, TCY, current_VTP_1, VTP_max_min);
    #
    random_params = np.array([HX,HY,JX,JA,LP,LD,VS,VO,WC,TCX,TCY,TTX,TTY,TBX,TBY,TRX,TRY,TS1,TS2,TS3,TS4,MA1,MA2,MA3]);
    return  random_params

def randomVTP_2():
    HX=random.uniform(0,1);# Generate random number from 0 to 1
    HY=random.uniform(-6,-3.5);
    JX=random.uniform(-0.5,0);
    JA=random.uniform(-7,0);
    LP=random.uniform(-1,1);
    LD=random.uniform(-2,4);
    VS=random.uniform(0,1);
    WC=0; #Not included in Prom-on et al., 2014, use netrual parameter instead
    TBX=random.uniform(-3,4);
    TBY=random.uniform(-3,5);
    TRX=random.uniform(-4,2);
    TRY=random.uniform(-6,0);
    TS1=random.uniform(-1.4,1.4);
    TS2=random.uniform(-1.4,1.4); 
    TS3=random.uniform(-1.4,1.4); 
    TS4=random.uniform(-1.4,1.4); 
    MA1= -0.05;
    MA2= -0.05;
    MA3= -0.05;
	#Get VTP of tongue body (TCX, TCY), tongue tip (TTX,TTY) and velum opening (VO) by constraints
    TCX = constrained_parameterT(9, TBX, TBY, current_VTP_2, VTP_max_min);
    TCY = constrained_parameterT(10, TBX, TBY, current_VTP_2, VTP_max_min);
    TTX = constrained_parameterT(11, TBX, TBY, current_VTP_2, VTP_max_min);
    TTY = constrained_parameterT(12, TBX, TBY,current_VTP_2, VTP_max_min);
    VO = constrained_parameterVO(7, TCY, current_VTP_2, VTP_max_min);
    #
    random_params = np.array([HX,HY,JX,JA,LP,LD,VS,VO,WC,TCX,TCY,TTX,TTY,TBX,TBY,TRX,TRY,TS1,TS2,TS3,TS4,MA1,MA2,MA3])
    return  random_params

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                                MFCC function                                                     #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#The function takes sound file name as input; returns MFCC Matrix
def get_MFCC(sound_file_name):
    y, sr = librosa.load(sound_file_name, sr= 16000); #resample to 16000 Hz
    #details of MFCC
    n_mfcc = 40;
    n_mels = 40;
    n_fft = 512;
    win_length = int(0.025*sr); #window time is 0.025
    hop_length = int(0.010*sr); #hop time is 0.01 
    window = 'hamming';
    fmin = 0;
    fmax = 8000;
    stft_setting = librosa.stft(y, window=window, n_fft=n_fft, win_length=win_length, hop_length=hop_length);
    S = librosa.feature.melspectrogram(S=stft_setting, y=y, n_mels=n_mels, fmin=fmin, fmax=fmax);
    MFCC = librosa.feature.mfcc(S=librosa.power_to_db(S), n_mfcc=n_mfcc);
    return MFCC
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                              Update speaker file function                                                     #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#This function takes two sets of vocal tract parameters (numpy arrays)
def update_speaker_file(params_1, params_2):
    tree = et.parse("nanana.speaker");
    for i in range(23):
    #use getchildren to find the node that stores vocal tract parameter
        tree.getroot().getchildren()[0].getchildren()[1].getchildren()[0].getchildren()[i].set('value', str(params_1[i]));# /a/ parameter in the speaker file
        tree.getroot().getchildren()[0].getchildren()[1].getchildren()[40].getchildren()[i].set('value', str(params_2[i]));# /n/ parameter in the speaker file
    tree.write("nanana.speaker")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                             training session                                                         #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#The optimization is done by comparing the error of MFCC between the target and synthetic audio.
#Every time there is an improvement in MFCC, the set of VTP will be adopted and recorded.
#In every iteration, the VTP is random except for tongue tip (TTX/TTY), tongue body (TCX,TCY) and velum opening (V0), which are constrained by certain rules (see the tongue and velum constraints function).
iteration = 100000;
target_mfcc =  get_MFCC('target_nanana.wav'); #get target mfcc
current_sum_of_squares =  562844.7591388852;#the mfcc difference between the netrual sequence and target sequence
#start from vocal tract parameters of schwas
current_VTP_1=np.array([1.0,  -4.75,  0.0,   -2.0,  -0.07,  0.95,   0.0,   -0.1,   0.0,   -0.4,   -1.46,    3.5,   -1.0,    2.0,    0.5,     0.0,    0.0,    0.0,   0.06,    0.15,    0.15,   -0.05,  -0.05,  -0.05]);# VTP of schwa
current_VTP_2=np.array([1.0,  -4.75,  0.0,   -2.0,  -0.07,  0.95,   0.0,   -0.1,   0.0,   -0.4,   -1.46,    3.5,   -1.0,    2.0,    0.5,     0.0,    0.0,    0.0,   0.06,    0.15,    0.15,   -0.05,  -0.05,  -0.05]);# VTP of schwa
#
params_1 = np.array([1.0,  -4.75,  0.0,   -2.0,  -0.07,  0.95,   0.0,   -0.1,   0.0,   -0.4,   -1.46,    3.5,   -1.0,    2.0,    0.5,     0.0,    0.0,    0.0,   0.06,    0.15,    0.15,   -0.05,  -0.05,  -0.05]);# VTP of schwa
params_2 =np.array([1.0,  -4.75,  0.0,   -2.0,  -0.07,  0.95,   0.0,   -0.1,   0.0,   -0.4,   -1.46,    3.5,   -1.0,    2.0,    0.5,     0.0,    0.0,    0.0,   0.06,    0.15,    0.15,   -0.05,  -0.05,  -0.05]);# VTP of schwa
#
Every_SSQ = np.zeros(shape=[iteration+1, 1]);  Every_SSQ[0,:] = current_sum_of_squares; #empty array for taking a record of every sum of squares; the first value in the array is the initial ssq
#
Every_VTP_1 = np.zeros(shape=[iteration+1, 24]); Every_VTP_1[0,:] = params_1; #empty array for taking a record of every set of VTP; the first value in the array is VTP of a schwa
Every_VTP_2 = np.zeros(shape=[iteration+1, 24]); Every_VTP_2[0,:] = params_2;
#
counter = 0;
for i in range(iteration):
    counter += 1;
    #
    params_1=randomVTP_1();#get a random set of vocal tract parameters with tongue constraints
    params_2=randomVTP_2();
    #
    update_speaker_file(params_1, params_2);
    VTL.vtlGesToWav(speaker_file_name, gesture_file_name, wav_file_name, feedback_file_name);#synthesis by VTL
    #VTL.vtlClose()
    #caculate the MFCC of the synthesized audio
    mfcc = get_MFCC('nanana.wav');
    #caculate the sum of squares
    residual = mfcc - target_mfcc;
    sum_of_squares = np.sum(residual**2);
    Every_SSQ[counter,:] = sum_of_squares; # Take a record of the SSQ of every synthetic sequence
    Every_VTP_1[counter,:] = params_1; # Take a record of every set of VTP
    Every_VTP_2[counter,:] = params_2;
    if sum_of_squares < current_sum_of_squares:
        current_sum_of_squares = sum_of_squares;
        current_VTP_1=params_1;
        current_VTP_2=params_2;
        os.rename('nanana.wav','nanana%i.wav'%counter);
        np.savetxt("Every_SSQ.csv", Every_SSQ, delimiter=","); #every sum of squares
        np.savetxt("Every_VTP_1.csv", Every_VTP_1, delimiter=",");
        np.savetxt("Every_VTP_2.csv", Every_VTP_2, delimiter=",");
    #report the progress every 1000 iterations
    if (counter % 1000==0):
        print('Progress report');
        print('Current_sum_of_sqaures: %i' % current_sum_of_squares);
        np.savetxt("Every_SSQ.csv", Every_SSQ, delimiter=","); #every sum of squares
        np.savetxt("Every_VTP_1.csv", Every_VTP_1, delimiter=",");
        np.savetxt("Every_VTP_2.csv", Every_VTP_2, delimiter=",");
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                      Training results                                                   #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#timer
end = time.time();
time = end-start;
print('Time: %i' % time);
#save the output
np.savetxt("Every_SSQ.csv", Every_SSQ, delimiter=",");
np.savetxt("Every_VTP_1.csv", Every_VTP_1, delimiter=",");
np.savetxt("Every_VTP_2.csv", Every_VTP_2, delimiter=",");