###import important libraries
import os, re, sys
import glob
import parselmouth
import argparse
from IPython.display import Audio
from parselmouth.praat import call
import seaborn as sns
import pandas as pd
import csv

###parameters to calculate
minPitch = []
maxPitch =[]
meanPitch = []
sdPitch = []
minIn = []
maxIn = []
meanIn = []
sdIn = []
jitter = []
shimmer = []
hnr = []
speakingRate = []


###extract the different features
class feature_extraction:

    def getPitch(self,audio):
    	pitch = call(audio,"To Pitch", 0.0, 75, 600)
    	minpitch = call(pitch,"Get minimum",0.0, 0.0,"Hertz","Parabolic")
    	maxpitch = call(pitch,"Get maximum",0.0, 0.0,"Hertz","Parabolic")
    	meanpitch = call(pitch,"Get mean",0.0, 0.0,"Hertz")
    	sdpitch = call(pitch,"Get standard deviation",0.0,0.0,"Hertz")
    	minPitch.append(minpitch)
    	maxPitch.append(maxpitch)
    	meanPitch.append(meanpitch)
    	sdPitch.append(sdpitch)
   
    def getIntensity(self,audio):
        intensity = call(audio,"To Intensity",100,0.0,600)
        intensity_min = call(intensity,"Get minimum",0.0,0.0,"parabolic")
        intensity_max = call(intensity,"Get maximum",0.0,0.0,"parabolic")
        intensity_mean = call(intensity,"Get mean",0.0,0.0,"energy")
        intensity_sd = call(intensity,"Get standard deviation",0.0,0.0)  
        minIn.append(intensity_min)
        maxIn.append(intensity_max)
        meanIn.append(intensity_mean)
        sdIn.append(intensity_sd)
    
    def getJitter(self,audio):
        ps = call(audio,"To PointProcess (periodic, cc)",75.0,600.0)
        jt = call(ps,"Get jitter (local)",0.0,0.0,0.0001,0.02,1.3)
        jitter.append(jt)
   
    def getShimmer(self,audio):
        ps  = call(audio,"To PointProcess (periodic, cc)",75.0,600.0)
        smr = call([audio,ps],"Get shimmer (local)",0.0,0.0,0.0001,0.02,1.3,1.6)
        shimmer.append(smr)

    def getHNR(self,audio):
        harmony = call(audio,"To Harmonicity (cc)",0.01,75.0,0.1,1.0)
        ratio = call(harmony,"Get mean",0.0,0.0)
        hnr.append(ratio)

    def getSpeakingrate_my_features(self,audio,n,swords,emotion_list):
        time = call(audio,"Get total duration")
        print("Time taken by this audio file", time)
        speakingRate.append(swords/time)
        emotion_list.append(n.capitalize())

    def getSpeakingrate_msp(self,audio,n,mwords,emotion_list):
        time = call(audio,"Get total duration")
        print("Time taken by this audio file", time)
        speakingRate.append(mwords/time)
        emotion_list.append(n.capitalize())


###process audio, create final dictionary
    def get_audio(self,args):

        ###words in the sentence and sentence's emotion to calculate the speaking rate
        mwords = {"afraid" : 30, "angry" : 11, "disgusted" : 26, "happy" : 17, "neutral" : 9, "sad" : 16, "surprised" : 16}
        swords = {"afraid" : 7, "angry" : 8, "disgusted" : 7, "happy" : 4, "neutral" : 5, "sad" : 4, "surprised" : 7}
        self.path = args.input
        self.dict = args.dict
        print(self.dict)
        os.chdir(self.path)
        emotion_list = []
        out= {}
        for i in glob.glob("*.wav"):
            print("File name", i)
            audio = parselmouth.Sound(i)
            n = i.split(".")[0]
            n = n.lower()
            #call all the self functions for all the files
            self.getPitch(audio)
            self.getIntensity(audio)
            self.getJitter(audio)
            self.getShimmer(audio)
            self.getHNR(audio)
            if self.dict == mwords:
                print("pass")
                self.getSpeakingrate_msp(audio,n,mwords[n],emotion_list)
            else:
                self.getSpeakingrate_my_features(audio,n,swords[n],emotion_list)
        print("All files processed")
        out = {"Speech File": emotion_list,"Min Pitch" : minPitch,"Max Pitch" : maxPitch,"Mean Pitch" : meanPitch,"Sd Pitch": sdPitch,
                "Min Intensity": minIn,"Max Intensity": maxIn,"Mean Intensity": meanIn,"Sd Intensity" : sdIn, "Speaking Rate": speakingRate,
                "Jitter" : jitter,"Shimmer": shimmer,"HNR": hnr}
        return out
        

###add the argparse method to pass in the directory for the user input
parser = argparse.ArgumentParser(description="get the feature values")
parser.add_argument('--input', help='audio file directory', required = True)
parser.add_argument('--dict', help='name of dictionary', required = True)
parser.add_argument('--output', help='name of csv', required = True)
args = parser.parse_args()

features = feature_extraction()
out = features.get_audio(args)

###write the file based on the user given path and name
file_out = args.output
df = pd.DataFrame.from_dict(data=out, orient = 'index')
df = df.transpose()
df.to_csv(file_out)