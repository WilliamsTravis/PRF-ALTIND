# -*- coding: utf-8 -*-
"""
Created on Tue Apr 24 20:43:15 2018

@author: trwi0358
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 16:32:09 2018

@author: trwi0358
"""
runfile('C:/Users/User/Github/Pasture-Rangeland-Forage/functions_git.py', 
        wdir='C:/Users/User/Github/Pasture-Rangeland-Forage')
import warnings
warnings.filterwarnings("ignore") #This is temporary, toggle this on for presentation

noaapath = 'E:\\data\\droughtindices\\noaa\\nad83\\indexvalues\\'

# Paths
paths= ['E:\\data\\droughtindices\\noaa\\nad83\\indexvalues\\',
        'E:\\data\\droughtindices\\palmer\\pdsi\\nad83\\',
         'E:\\data\\droughtindices\\palmer\\pdsisc\\nad83\\',
         'E:\\data\\droughtindices\\palmer\\pdsiz\\nad83\\',
         'E:\\data\\droughtindices\\spi\\nad83\\1month\\',
         'E:\\data\\droughtindices\\spi\\nad83\\2month\\',
         'E:\\data\\droughtindices\\spi\\nad83\\3month\\',
         'E:\\data\\droughtindices\\spi\\nad83\\6month\\',
         'E:\\data\\droughtindices\\spei\\nad83\\1month\\',
         'E:\\data\\droughtindices\\spei\\nad83\\2month\\',
         'E:\\data\\droughtindices\\spei\\nad83\\3month\\',
         'E:\\data\\droughtindices\\spei\\nad83\\6month\\']

# Just names
indices= ['noaa',
          'pdsi',
          'pdsisc',
          'pdsiz',
          'spi1',
          'spi2',
          'spi3',
          'spi6',
          'spei1',
          'spei2',
          'spei3',
          'spei6']
                                
############### Argument Definitions ##########################################
actuarialyear = 2018
baselineyears = [1948,2016] 
studyears = [2000,2017]  
productivity = 1 
strikes = [.7,.75,.8,.85,.9]
acres = 500
allocation = .5
difference = 0 # 0 = indemnities, 1 = net payouts, 2 = lossratios 

############################ Normal NOAA Method ###############################
noaas = []
for i in range(len(strikes)):
    [producerpremiums, indemnities, frequencies, pcfs, nets, 
     lossratios, meanppremium, meanindemnity, frequencysum,
     meanpcf, net, lossratio] = indexInsurance(noaapath, actuarialyear, 
     studyears, baselineyears, productivity, strikes[i], acres, allocation,
     difference,scale = True,plot = False) 
    payments = [n[1] for n in indemnities]
    noaas.append(np.nanmean(payments))

noaamean = np.mean(noaas)

####################### Test methods for drought indices ######################
# Step one, scalar one
levels = []
for i in range(len(paths)):   
    print(indices[i])  
    # Step one, scalar one -- strike level ratios   
    for s in range(len(strikes)):
        # Get payouts at this strike level
        [producerpremiums, indemnities, frequencies, pcfs, nets, 
             lossratios, meanppremium, meanindemnity, frequencysum,
             meanpcf, net, lossratio] = indexInsurance(paths[i], 
             actuarialyear, studyears, baselineyears, productivity, 
             strikes[s], acres, allocation,difference,
             scale = False,plot = False) 
        
        # Get just the payouts at this strike level
        payments = [n[1] for n in indemnities]
        
        # Get the ratio between payouts at this strike level and the rainfall one
        ratio = noaas[s] / np.nanmean(payments)
        
        # Add the indexname, strike level and total ratio to the full levels set
        levels.append([indices[i],strikes[s], ratio])
        

scalars = pd.DataFrame(levels)
scalars.columns = ["index","strike","ratio"]
scalars.to_csv("G:\\My Drive\\THESIS\\data\\Index Project\\index_ratios_bystrike.csv",index=False)

################### Step two, overall scaling #############################
ratios = []
for i in range(len(paths)):   
    print(indices[i])  
    # Step one, scalar one -- strike level ratios   
    allstrikes = []
    for s in range(len(strikes)):
        # Get payouts at this strike level
        [producerpremiums, indemnities, frequencies, pcfs, nets, 
             lossratios, meanppremium, meanindemnity, frequencysum,
             meanpcf, net, lossratio] = indexInsurance(paths[i], 
             actuarialyear, studyears, baselineyears, productivity, 
             strikes[s], acres, allocation,difference,
             scale = True,plot = False) 
        
        # Get just the payouts at this strike level
        payments = [n[1] for n in indemnities]
        
        # Get the ratio between payouts at this strike level and the rainfall one
        allstrikes.append(np.nanmean(payments))
        
    # Find overall mean payment
    indexmean = np.mean(allstrikes) 
    overallratio = noaamean/indexmean
    ratios.append([indices[i],overallratio])

# Get the Strikewise ratios           
scalars1 = pd.read_csv("G:\\My Drive\\THESIS\\data\\Index Project\\index_ratios_bystrike.csv")
scalars1.columns = ['index','strike','ratio1']

#Get the overall ratios
scalars2 = pd.DataFrame(ratios)
scalars2.columns = ['index','ratio2']

# Join and generate the composite ratio
scalars3 = pd.merge(scalars1,scalars2,on = 'index')
scalars3['ratio'] = scalars3['ratio1'] * scalars3['ratio2']
scalars3.to_csv("G:\\My Drive\\THESIS\\data\\Index Project\\index_ratios_bystrike.csv",index=False)
