"""
Get RMA Summary of Business report for the PRF
Created on Thu Nov 15 08:34:36 2018

@author: User
"""
import glob
import os
import pandas as pd
from selenium import webdriver
from tqdm import tqdm
import zipfile
os.chdir("C:/users/user/github/data/rma/summary_of_business_reports/")

options = webdriver.ChromeOptions()
options.add_experimental_option("prefs", {
  "download.default_directory":
      "C:/users/user/github/data/rma/summary_of_business_reports/",
  "download.prompt_for_download": False,
  "download.directory_upgrade": True,
  "safebrowsing.enabled": True
})

url = "https://prodwebnlb.rma.usda.gov/apps/SummaryofBusiness/DataFiles"
path_to_chromedriver = "C:\\Drivers\\chrome\\chromedriver.exe"
driver = webdriver.Chrome(executable_path=path_to_chromedriver,
                          chrome_options=options)
driver.set_window_position(975, 0)
driver.get(url)
driver.implicitly_wait(30)

# Get to the list of zipped files
list_path = '//*[@id="content"]/div/table/tbody/tr/td[1]/ul[2]/li/a'
lp_link = driver.find_element_by_xpath(list_path)
lp_link.click()

# Find links in the 'divDataFiles' div
elements = driver.find_element_by_id('divDataFiles')
links = elements.find_elements_by_class_name('DownLoadFileLink')
for l in links:
    l.click()

# Unzip everythin
zfiles = glob.glob("*zip")  # Check that all were included in this...?
for zf in tqdm(zfiles, position=0):
    targetfile = os.path.splitext(zf)[0]
    zfile = zipfile.ZipFile(zf)
    zfile.extractall('txt')
    zfile.close()
    os.remove(zf)

# Build singular dataset
tfiles = glob.glob("txt/*txt")
df_list = []
for t in tqdm(tfiles, position=0):
    try:
        df = pd.read_table(t, sep="|", header=None, low_memory=False)
        df_list.append(df)
    except Exception as e:
        print(e)
        pass

# Merge
df = pd.concat(df_list)

# Add Columns
# This dataset is apparently a work in progress, no easy field names
# They do have a pdf, but the pdf table readers can't handle the multiline
# text boxes, so...
columns = ['Commodity Year', 'State Code', 'State Name', 'State Abbreviation',
           'County Code', 'County Name', 'Commodity Code', 'Commodity Name',
           'Insurance Plan Code', 'Insurance Plan Abbreviation',
           'Coverage Type Code', 'Coverage Level Percent', 'Delivery ID',
           'Type Code', 'Type Name', 'Practice Code', 'Practice Name',
           'Unit Structure Code', 'Unit Structure Name',
           'Net Commodity Reporting Level Amount',
           'Commodity Report Level Type', 'Liability Amount',
           'Total Premium Amount', 'Subsidy Amount', 'Indemnity Amount',
           'Loss Ratio', 'Endorsed Commodity']

df.columns = columns
df.to_csv("sob_master.csv", index=False)
