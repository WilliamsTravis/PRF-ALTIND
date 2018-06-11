# -*- coding: utf-8 -*-
"""
This will loop through all combinations of paramters for the online model and 
    save the average outputs as rasters, and pickle the time series for the 
    time series graphs

Created on Mon May  7 20:29:57 2018

@author: trwi0358
"""
runfile('C:/Users/user/Github/PRF-ALTIND/functions.py', 
        wdir='C:/Users/user/Github/PRF-ALTIND')
import warnings
warnings.filterwarnings("ignore") #This is temporary, toggle this on for presentation
os.chdir(r'C:\Users\user\Github')
#mask, geom, proj = readRaster("e:\\data\\droughtindices\\masks\\nad83\\mask4.tif",1,-9999)
homepath= ''
grid = readRaster("data/prfgrid.tif",1,-9999)[0]
########################## Load Index Arrays #################################################################################
# Actuarial Rates
indices = ['noaa','pdsi','pdsisc','pdsiz','spi1','spi2','spi3','spi6','spei1','spei2','spei3','spei6']

# Actuarial rate paths -- to be simplified
with np.load(homepath + 'data/actuarial/premium_arrays_2017.npz') as data:
    arrays = data.f.arr_0
    data.close()
with np.load(homepath + 'data/actuarial/premium_dates_2017.npz') as data:
    dates = data.f.arr_0
    data.close()
premiums2017 = [[str(dates[i]),arrays[i]] for i in range(len(arrays))]

with np.load(homepath + 'data/actuarial/premium_arrays_2018.npz') as data:
    arrays = data.f.arr_0
    data.close()
with np.load(homepath + 'data/actuarial/premium_dates_2018.npz') as data:
    dates = data.f.arr_0
    data.close()
premiums2018= [[str(dates[i]),arrays[i]] for i in range(len(arrays))]

with np.load(homepath + 'data/actuarial/base_arrays_2017.npz') as data:
    arrays = data.f.arr_0
    data.close()
with np.load(homepath + 'data/actuarial/base_dates_2017.npz') as data:
    dates = data.f.arr_0
    data.close()
bases2017 = [[str(dates[i]),arrays[i]] for i in range(len(arrays))]

with np.load(homepath + 'data/actuarial/base_arrays_2018.npz') as data:
    arrays = data.f.arr_0
    data.close()
with np.load(homepath + 'data/actuarial/base_dates_2018.npz') as data:
    dates = data.f.arr_0
    data.close()
bases2018 = [[str(dates[i]),arrays[i]] for i in range(len(arrays))]

# Indices
try:
    arraydict
except NameError:
    arraydict = []
    for i in tqdm(range(len(indices))):
        with np.load("data/indices/"+indices[i]+"_arrays.npz") as data:
            arrays = data.f.arr_0
            data.close()
        with np.load("data/indices/"+indices[i]+"_dates.npz") as data:
            names = data.f.arr_0
            data.close()
        timeseries = [[str(names[y]),arrays[y]] for y in range(len(arrays))]
        arraydict.append(timeseries)
    
        
    arraydict ={indices[i]:arraydict[i] for i in range(len(indices))}
    gc.collect(2)
# Strike level
strikes = [.7,.75,.8,.85,.9]

# Info Type
# producerpremiums,indemnities,frequencies,pcfs,nets, lossratios,meanppremium,meanindemnity,frequencysum,meanpcf, net, lossratio
infotype = [i for i in range(6,12)]

# Actuarial Year
actuarialyears  = [2017,2018]

# Number of Acres....uh oh...better make this discrete
acres = 500

# rasterpath, actuarialyear, studyears, baselineyears, productivity, strike,
 # acres, allocation,difference = 0, scale = True,plot = True
for p in range(len(indices)):
    print(indices[p])
    indexlist = arraydict.get(indexnames[p])
    for ay in actuarialyears:
        if ay == 2017:
            bases = bases2017
            premiums = premiums2017
        elif ay == 2018:
            bases = bases2018
            premiums = premiums2018            
        print(ay)
        for s in strikes:
            print(s)
            df = indexInsurance(indexlist, # Index Path
                                grid,
                                premiums,
                                bases,
                                ay, # Actuarial Year
                                [2000,2017], # Study years
                                [1948,2016], # Baseline
                                1, # Productivity
                                s, # Strike
                                500, # Acres
                                .5, # Allocation
                                scale = True,
                                plot = False)
            
            #  returns = producerpremiums,indemnities,frequencies,pcfs,nets, lossratios
                #,meanppremium,meanindemnity,frequencysum,meanpcf, net, lossratio
            # Premiums
            array = df[6]
            np.savez_compressed( # Save this as an array, too 
                     "data\\onlinedata\\AY"
                     +str(ay)+"\\"+str(int(s*100))+"\\premiums\\"+indices[p]+"\\array",array)
            
            # Instead of Pickling use a numpy specific file 
            arrays = df[0]            
            dates = pd.DataFrame([a[0] for a in arrays]) # Also, just to keep things solid, lets save the dates. 
            dates.columns = ["dates"]
            jarrays = np.array([a[1] for a in arrays])
            np.savez_compressed("data\\onlinedata\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\premiums\\"+indices[p]+"\\arrays", jarrays)
            dates.to_csv("data\\onlinedata\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\premiums\\"+indices[p]+"\\dates.csv", index = False)

            # Indemnities
            array = df[7]
            np.savez_compressed( # Save this as an array, too 
                     "data\\onlinedata\\AY"
                     +str(ay)+"\\"+str(int(s*100))+"\\indemnities\\"+indices[p]+"\\array",array)
            
            # Instead of Pickling use a numpy specific file 
            arrays = df[1]            
            dates = pd.DataFrame([a[0] for a in arrays]) # Also, just to keep things solid, lets save the dates. 
            dates.columns = ["dates"]
            jarrays = np.array([a[1] for a in arrays])
            np.savez_compressed("data\\onlinedata\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\indemnities\\"+indices[p]+"\\arrays", jarrays)
            dates.to_csv("data\\onlinedata\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\indemnities\\"+indices[p]+"\\dates.csv", index = False)

            
            
            
            # frequencies
            array = df[8]
            np.savez_compressed( # Save this as an array, too 
                     "data\\onlinedata\\AY"
                     +str(ay)+"\\"+str(int(s*100))+"\\frequencies\\"+indices[p]+"\\array",array)
            
            # Instead of Pickling use a numpy specific file 
            arrays = df[2]            
            dates = pd.DataFrame([a[0] for a in arrays]) # Also, just to keep things solid, lets save the dates. 
            dates.columns = ["dates"]
            jarrays = np.array([a[1] for a in arrays])
            np.savez_compressed("data\\onlinedata\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\frequencies\\"+indices[p]+"\\arrays", jarrays)
            dates.to_csv("data\\onlinedata\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\frequencies\\"+indices[p]+"\\dates.csv", index = False)

            
            
            
            
            
            # pcfs
            array = df[9]
            np.savez_compressed( # Save this as an array, too 
                     "data\\onlinedata\\AY"
                     +str(ay)+"\\"+str(int(s*100))+"\\pcfs\\"+indices[p]+"\\array",array)
            
            # Instead of Pickling use a numpy specific file 
            arrays = df[3]            
            dates = pd.DataFrame([a[0] for a in arrays]) # Also, just to keep things solid, lets save the dates. 
            dates.columns = ["dates"]
            jarrays = np.array([a[1] for a in arrays])
            np.savez_compressed("data\\onlinedata\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\pcfs\\"+indices[p]+"\\arrays", jarrays)
            dates.to_csv("data\\onlinedata\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\pcfs\\"+indices[p]+"\\dates.csv", index = False)





            # nets
            array = df[10]
            np.savez_compressed( # Save this as an array, too 
                     "data\\onlinedata\\AY"
                     +str(ay)+"\\"+str(int(s*100))+"\\nets\\"+indices[p]+"\\array",array)
            
            # Instead of Pickling use a numpy specific file 
            arrays = df[4]            
            dates = pd.DataFrame([a[0] for a in arrays]) # Also, just to keep things solid, lets save the dates. 
            dates.columns = ["dates"]
            jarrays = np.array([a[1] for a in arrays])
            np.savez_compressed("data\\onlinedata\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\nets\\"+indices[p]+"\\arrays", jarrays)
            dates.to_csv("data\\onlinedata\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\nets\\"+indices[p]+"\\dates.csv", index = False)

            
            
            
            # lossratios
            array = df[11]
            np.savez_compressed( # Save this as an array, too 
                     "data\\onlinedata\\AY"
                     +str(ay)+"\\"+str(int(s*100))+"\\lossratios\\"+indices[p]+"\\array",array)
            
            # Instead of Pickling use a numpy specific file 
            arrays = df[5]            
            dates = pd.DataFrame([a[0] for a in arrays]) # Also, just to keep things solid, lets save the dates. 
            dates.columns = ["dates"]
            jarrays = np.array([a[1] for a in arrays])
            np.savez_compressed("data\\onlinedata\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\lossratios\\"+indices[p]+"\\arrays", jarrays)
            dates.to_csv("data\\onlinedata\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\lossratios\\"+indices[p]+"\\dates.csv", index = False)


    
    
    
## Numpy reading practice - pretty quick :D
#newarray = np.load("test.npy")
#arrays = [newarray[i] for i in range(len(newarray))]
#dates = pd.read_csv("dates.csv")
#arraylist = [[dates['dates'][i],arrays[i]] for i in range(len(arrays))]