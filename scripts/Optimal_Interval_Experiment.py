"""
Created on Fri Nov 17 22:19:03 2017
This script allows you to change parameters and call the functions. The working directory is set in the functions script while this is being tinkered with. 
    
"""
runfile('C:/Users/user/Github/Pasture-Rangeland-Forage/functions_git.py', wdir='C:/Users/user/Github/Pasture-Rangeland-Forage')
import warnings
warnings.filterwarnings("ignore") #This is temporary, toggle this on for presentation
os.chdir(r'C:\Users\user\Github\Pasture-Rangeland-Forage')

########################### Some Instruction ##################################
# For informing info and target info choose an index number for this list:
### 0: producerpremiums, 1: indemnities, 2: frequencies, 3: pcfs, 4: nets, 
#        5: lossratios, 6: meanppremium, 7: meanindemnity, 8: frequencysum,
#            9: meanpcf, 10: net, 11: lossratio
    
# Arguments:
#       rasterpath, targetinfo, targetarrayname, studyears, informinginfo, 
#                                   informingarrayname, informingyears,savename

rows = list()
paths = ["e:\\data\\droughtindices\\noaa\\nad83\\indexvalues\\",   
         'e:\\data\\droughtindices\\palmer\\pdsi\\nad83\\', 
        'e:\\data\\droughtindices\\palmer\\pdsisc\\nad83\\', 
        'e:\\data\\droughtindices\\palmer\\pdsiz\\nad83\\',
        'e:\\data\\droughtindices\\spi\\nad83\\1month\\',
        'e:\\data\\droughtindices\\spi\\nad83\\2month\\',
        'e:\\data\\droughtindices\\spi\\nad83\\3month\\', 
        'e:\\data\\droughtindices\\spi\\nad83\\6month\\', 
        'e:\\data\\droughtindices\\spei\\nad83\\1month\\',
        'e:\\data\\droughtindices\\spei\\nad83\\2month\\', 
        'e:\\data\\droughtindices\\spei\\nad83\\3month\\', 
        'e:\\data\\droughtindices\\spei\\nad83\\6month\\']

indices = ["noaa","pdsi","pdsisc","pdsiz","spi1","spi2","spi3","spi6","spei1","spei2","spei3","spei6"]
strikes = [.7,.75,.8,.85,.9]


for i in range(len(paths)):
    for s in range(len(strikes)):
        print("#####################################")
        print(paths[i])
        print("##################################")
        rows.append(optimalIntervalExperiment(rasterpath = paths[i],
                                              targetinfo = 4,
                                              targetarrayname = indices[i],
                                              studyears = [2000,2016], 
                                              informinginfo = 3,
                                              informingarrayname = "PCF",
                                              informingyears = [1948,2016],
                                              strike = strikes[s],
                                              savename = indices[i]))

dfrm = pd.DataFrame(rows)
dfrm.to_csv("G:\\My Drive\\THESIS\\data\\Index Project\\PRFOptimals_nets.csv")
