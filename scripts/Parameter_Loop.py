# -*- coding: utf-8 -*-
"""
This will loop through all combinations of paramters for the online model and 
    save the average outputs as rasters, and pickle the time series for the 
    time series graphs

Created on Mon May  7 20:29:57 2018

@author: trwi0358
"""
runfile('C:/Users/trwi0358/Github/Pasture-Rangeland-Forage/functions_git.py', 
        wdir='C:/Users/trwi0358/Github/Pasture-Rangeland-Forage')
import warnings
warnings.filterwarnings("ignore") #This is temporary, toggle this on for presentation
os.chdir(r'C:\Users\trwi0358\Github\Pasture-Rangeland-Forage')
mask, geom, proj = readRaster("d:\\data\\droughtindices\\masks\\nad83\\mask4.tif",1,-9999)

# Drought Index
paths = [
         'D:\\data\\droughtindices\\noaa\\nad83\\indexvalues\\',
         'D:\\data\\droughtindices\\palmer\\pdsi\\nad83\\',
         'D:\\data\\droughtindices\\palmer\\pdsisc\\nad83\\',
         'D:\\data\\droughtindices\\palmer\\pdsiz\\nad83\\',
         'D:\\data\\droughtindices\\spei\\nad83\\1month\\',
         'D:\\data\\droughtindices\\spei\\nad83\\2month\\',
         'D:\\data\\droughtindices\\spei\\nad83\\3month\\',
         'D:\\data\\droughtindices\\spei\\nad83\\6month\\',
         'D:\\data\\droughtindices\\spi\\nad83\\1month\\',
         'D:\\data\\droughtindices\\spi\\nad83\\2month\\',
         'D:\\data\\droughtindices\\spi\\nad83\\3month\\',
         'D:\\data\\droughtindices\\spi\\nad83\\6month\\'
         ]

indices = ["noaa","pdsi","pdsisc","pdsiz","spei1","spei2","spei3","spei6","spi1","spi2","spi3","spi6"]

# Strike level
strikes = [.7,.75,.8,.85,.9]

# Info Type
# producerpremiums,indemnities,frequencies,pcfs,nets, lossratios,meanppremium,meanindemnity,frequencysum,meanpcf, net, lossratio
infotype = [i for i in range(6,12)]

# Actuarial Year
actuarialyears  = [2017,2018]

# Number of Acres....uh oh...better make this discrete
acres = [250,500,1000,2000]

# rasterpath, actuarialyear, studyears, baselineyears, productivity, strike,
 # acres, allocation,difference = 0, scale = True,plot = True
for p in range(len(paths)):
    print(paths[p])
    for ay in actuarialyears:
        print(ay)
        for s in strikes:
            for a in acres:
                print(s)
                df = indexInsurance(paths[p], # Index Path
                                    ay, # Actuarial Year
                                    [1948,2017], # Study years
                                    [1948,2017], # Baseline
                                    1, # Productivity
                                    s, # Strike
                                    a, # Acres
                                    .5, # Allocation
                                    scale = True,
                                    plot = False)
                
                #  returns = producerpremiums,indemnities,frequencies,pcfs,nets, lossratios
                    #,meanppremium,meanindemnity,frequencysum,meanpcf, net, lossratio
                # Premiums
                array = df[6]
                np.savez_compressed( # Save this as an array, too 
                         "D:\\data\\prfpayouts\\onlinedata\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\premiums\\"+indices[p]+"\\array",array)
                
                # Instead of Pickling use a numpy specific file 
                arrays = df[0]            
                dates = pd.DataFrame([a[0] for a in arrays]) # Also, just to keep things solid, lets save the dates. 
                dates.columns = ["dates"]
                jarrays = np.array([a[1] for a in arrays])
                np.savez_compressed("D:\\data\\prfpayouts\\onlinedata\\AY"
                             +str(ay)+"\\"+str(int(s*100))+"\\premiums\\"+indices[p]+"\\arrays", jarrays)
                dates.to_csv("D:\\data\\prfpayouts\\onlinedata\\AY"
                             +str(ay)+"\\"+str(int(s*100))+"\\premiums\\"+indices[p]+"\\dates.csv", index = False)
                np.savez_compressed("D:\\data\\prfpayouts\\onlinedata\\testarrays", jarrays)
                dates.to_csv("D:\\data\\prfpayouts\\onlinedata\\testdates.csv", index = False)
    
                
                # Indemnities
                array = df[7]
                np.savez_compressed( # Save this as an array, too 
                         "D:\\data\\prfpayouts\\onlinedata\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\indemnities\\"+indices[p]+"\\array",array)
                
                # Instead of Pickling use a numpy specific file 
                arrays = df[1]            
                dates = pd.DataFrame([a[0] for a in arrays]) # Also, just to keep things solid, lets save the dates. 
                dates.columns = ["dates"]
                jarrays = np.array([a[1] for a in arrays])
                np.savez_compressed("D:\\data\\prfpayouts\\onlinedata\\AY"
                             +str(ay)+"\\"+str(int(s*100))+"\\indemnities\\"+indices[p]+"\\arrays", jarrays)
                dates.to_csv("D:\\data\\prfpayouts\\onlinedata\\AY"
                             +str(ay)+"\\"+str(int(s*100))+"\\indemnities\\"+indices[p]+"\\dates.csv", index = False)
    
                
                
                
                # frequencies
                array = df[8]
                np.savez_compressed( # Save this as an array, too 
                         "D:\\data\\prfpayouts\\onlinedata\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\frequencies\\"+indices[p]+"\\array",array)
                
                # Instead of Pickling use a numpy specific file 
                arrays = df[2]            
                dates = pd.DataFrame([a[0] for a in arrays]) # Also, just to keep things solid, lets save the dates. 
                dates.columns = ["dates"]
                jarrays = np.array([a[1] for a in arrays])
                np.savez_compressed("D:\\data\\prfpayouts\\onlinedata\\AY"
                             +str(ay)+"\\"+str(int(s*100))+"\\frequencies\\"+indices[p]+"\\arrays", jarrays)
                dates.to_csv("D:\\data\\prfpayouts\\onlinedata\\AY"
                             +str(ay)+"\\"+str(int(s*100))+"\\frequencies\\"+indices[p]+"\\dates.csv", index = False)
    
                
                
                
                
                
                # pcfs
                array = df[9]
                np.savez_compressed( # Save this as an array, too 
                         "D:\\data\\prfpayouts\\onlinedata\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\pcfs\\"+indices[p]+"\\array",array)
                
                # Instead of Pickling use a numpy specific file 
                arrays = df[3]            
                dates = pd.DataFrame([a[0] for a in arrays]) # Also, just to keep things solid, lets save the dates. 
                dates.columns = ["dates"]
                jarrays = np.array([a[1] for a in arrays])
                np.savez_compressed("D:\\data\\prfpayouts\\onlinedata\\AY"
                             +str(ay)+"\\"+str(int(s*100))+"\\pcfs\\"+indices[p]+"\\arrays", jarrays)
                dates.to_csv("D:\\data\\prfpayouts\\onlinedata\\AY"
                             +str(ay)+"\\"+str(int(s*100))+"\\pcfs\\"+indices[p]+"\\dates.csv", index = False)
    
    
    
    
    
                # nets
                array = df[10]
                np.savez_compressed( # Save this as an array, too 
                         "D:\\data\\prfpayouts\\onlinedata\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\nets\\"+indices[p]+"\\array",array)
                
                # Instead of Pickling use a numpy specific file 
                arrays = df[4]            
                dates = pd.DataFrame([a[0] for a in arrays]) # Also, just to keep things solid, lets save the dates. 
                dates.columns = ["dates"]
                jarrays = np.array([a[1] for a in arrays])
                np.savez_compressed("D:\\data\\prfpayouts\\onlinedata\\AY"
                             +str(ay)+"\\"+str(int(s*100))+"\\nets\\"+indices[p]+"\\arrays", jarrays)
                dates.to_csv("D:\\data\\prfpayouts\\onlinedata\\AY"
                             +str(ay)+"\\"+str(int(s*100))+"\\nets\\"+indices[p]+"\\dates.csv", index = False)
    
                
                
                
                # lossratios
                array = df[11]
                np.savez_compressed( # Save this as an array, too 
                         "D:\\data\\prfpayouts\\onlinedata\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\lossratios\\"+indices[p]+"\\array",array)
                
                # Instead of Pickling use a numpy specific file 
                arrays = df[5]            
                dates = pd.DataFrame([a[0] for a in arrays]) # Also, just to keep things solid, lets save the dates. 
                dates.columns = ["dates"]
                jarrays = np.array([a[1] for a in arrays])
                np.savez_compressed("D:\\data\\prfpayouts\\onlinedata\\AY"
                             +str(ay)+"\\"+str(int(s*100))+"\\lossratios\\"+indices[p]+"\\arrays", jarrays)
                dates.to_csv("D:\\data\\prfpayouts\\onlinedata\\AY"
                             +str(ay)+"\\"+str(int(s*100))+"\\lossratios\\"+indices[p]+"\\dates.csv", index = False)
    
    
    
    
    
## Numpy reading practice - pretty quick :D
#newarray = np.load("test.npy")
#arrays = [newarray[i] for i in range(len(newarray))]
#dates = pd.read_csv("dates.csv")
#arraylist = [[dates['dates'][i],arrays[i]] for i in range(len(arrays))]