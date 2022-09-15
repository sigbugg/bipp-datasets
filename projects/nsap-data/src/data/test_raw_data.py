import json
import re
from pathlib import Path

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

"""This file is scraper for NSAP pension payment mode data. It involves three different processes:"""
"""1. Directory definitions and calling in the flat list of nested dictionaries."""
"""2. Scraping of data from the concerned webpages."""
"""3. Wrangling of data parsed from HTML of GP level webpage and saved as csv in concerend folders. This section is nested within step 2."""


# *****************************************************************************************************************************************************************************************#
"""PROCESS 1"""

# defining directories
dir_path = Path.cwd()
raw_path = Path.joinpath(dir_path, "data", "raw")
interim_path = Path.joinpath(dir_path, "data", "interim")
all_names_path = Path.joinpath(interim_path, "all_names.json")

with open(str(all_names_path), "r") as infile:
    all_names = json.load(infile)

# *****************************************************************************************************************************************************************************************#




# *****************************************************************************************************************************************************************************************#
"""PROCESS 2"""
"""The scraping of NSAP pension payment mode data begins here"""

# defining Chrome options
chrome_options = webdriver.ChromeOptions()
prefs = {"download.default_directory": str(dir_path), "profile.default_content_setting_values.automatic_downloads": 1,}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("--ignore-certificate-errors")
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
wait = WebDriverWait(driver, 30)
url = "https://nsap.nic.in/abstractdashboard.do?method=initialPage"

driver.get(url)
driver.implicitly_wait(10)
wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='btnpaymode']")))

#go inside the pension payment mode page-
view_payment_mode_button = driver.find_element(By.XPATH, "//*[@id='btnpaymode']")
driver.execute_script("arguments[0].click();", view_payment_mode_button)
print('Inside the view payment mode data site \n')

# looping across all names
for row in all_names:

    #Exclude devnagiri sub-districts
    if not str.isascii(row["sub_district_name"]):
        print("Excluded-", row["sub_district_name"], "Skipped it")
        continue

    state = row["state_name"]
    district = row["district_name"]
    sub_district = row["sub_district_name"]


    #Creating district folder to store sub-district level csv data file for all the sub-districts and each of the 3 schemes
    IGNOPAS_folder_path = Path.joinpath(raw_path, "IGNOPAS", state.strip().replace(" ", "_"), district.strip().replace(" ", "_"))
    IGNDPS_folder_path = Path.joinpath(raw_path, "IGNDPS", state.strip().replace(" ", "_"), district.strip().replace(" ", "_"))
    IGNWPS_folder_path = Path.joinpath(raw_path, "IGNWPS",state.strip().replace(" ", "_"), district.strip().replace(" ", "_"))

    sub_dist_name_corrected = re.sub(r"[^A-Za-z0-9_]", "", sub_district.strip().replace(" ", "_"))

    IGNOPAS_file_path = Path.joinpath(IGNOPAS_folder_path, f"{sub_dist_name_corrected}_IGNOPAS.csv")
    IGNDPS_file_path = Path.joinpath(IGNDPS_folder_path, f"{sub_dist_name_corrected}_IGNDPS.csv")
    IGNWPS_file_path = Path.joinpath(IGNWPS_folder_path, f"{sub_dist_name_corrected}_IGNWPS.csv")



###################################################################### IGNOPAS ######################################################################################################################################################

    if not IGNOPAS_folder_path.exists():
        IGNOPAS_folder_path.mkdir(parents=True)

    if not IGNOPAS_file_path.exists():
        
        print(IGNOPAS_file_path, "doesn't exist and proceeding for scraping.")

        counter = 0
        while counter <= 5:
            try:
                counter += 1

                #click at the state
                driver.implicitly_wait(10)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='paymodedatatbody']//a")))
                state_link = driver.find_element(By.LINK_TEXT, state)
                state_link.click()
                print(f"Clicked {state} =>")

                #click at the district
                driver.implicitly_wait(10)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='paymodedatatbody']//a")))
                district_link = driver.find_element(By.LINK_TEXT, district)
                district_link.click()
                print(f"        Clicked {district}=>")

                #click at the sub-district
                driver.implicitly_wait(10)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='paymodedatatbody']//a")))
                sub_district_link = driver.find_element(By.LINK_TEXT, sub_district)
                sub_district_link.click()
                print(f"                     Clicked {sub_district}=>")

                #Grab the table header and get all the header columns
                table_header_ = driver.find_element(By.XPATH,'//*[@id="paymodedatathead"]/tr[2]')
                table_columns_ = table_header_.find_elements(By.TAG_NAME,'th')
                
                State_Name = table_columns_[1].text
                District_Name = table_columns_[2].text
                Sub_District_Name = table_columns_[3].text
                GP_Name = table_columns_[4].text
                State_Cap_A = table_columns_[5].text
                NSAP_Beneficiaries_B = table_columns_[6].text
                MIN_of_A_B = table_columns_[7].text
                Bank_Ac = table_columns_[8].text
                PO_Ac = table_columns_[9].text
                MO = table_columns_[10].text
                Cash = table_columns_[11].text

                #Grab the table body and get all the rows 
                table_body_ = driver.find_element(By.XPATH,'//*[@id="paymodedatatbody"]')
                table_rows_ = table_body_.find_elements(By.TAG_NAME,'tr')

                sub_district_IGNOPAS_data = []

                #Extract the table for each sub-district and each scheme seperately
                for x in table_rows_:
                    row_ = x.find_elements(By.TAG_NAME,'td')

                    temporary_IGNOPAS = {
                        "Scheme" : "IGNOPAS",
                        State_Name : row_[1].text,
                        District_Name : row_[2].text,
                        Sub_District_Name : row_[3].text,
                        GP_Name : row_[4].text,
                        State_Cap_A : row_[5].text,
                        NSAP_Beneficiaries_B : row_[6].text,
                        MIN_of_A_B : row_[7].text,
                        Bank_Ac : row_[8].text,
                        PO_Ac : row_[9].text,
                        MO : row_[10].text,
                        Cash : row_[11].text
                    }
                    #each_state_IGNOPAS_data = 
                    sub_district_IGNOPAS_data.append(temporary_IGNOPAS)
                
                #Convert to dataframe
                sub_district_IGNOPAS_data = pd.DataFrame(sub_district_IGNOPAS_data)
                print('sub_district_IGNOPAS_data length =>',sub_district_IGNOPAS_data.shape)
                sub_district_IGNOPAS_data.to_csv(IGNOPAS_file_path, index=False)

                BackButton = driver.find_element(By.XPATH,'//*[@id="btnpaymodeback"]').click()
                print(f'################################################ back to main starting page => {sub_district} IGNOPAS next sub-district ####################################################\n')

                break

            except(NoSuchElementException,
            TimeoutException,
            UnicodeEncodeError) as ex:
                print(
                    f"{ex}: Rasied at {state} {district} {sub_district}"
                )
                print("Relooping again")

                BackButton = driver.find_element(By.XPATH,'//*[@id="btnpaymodeback"]').click()

                if counter == 5:
                    break

            except WebDriverException as ex:
                print(
                    f"{ex}: Rasied at {state} {district} {sub_district}"
                )
                driver.close()
                print("Relooping again")
                # defining Chrome options
                chrome_options = webdriver.ChromeOptions()
                prefs = {
                    "download.default_directory": str(dir_path),
                    "profile.default_content_setting_values.automatic_downloads": 1,
                }
                chrome_options.add_experimental_option("prefs", prefs)
                chrome_options.add_argument("start-maximized")

                driver = webdriver.Chrome(
                    ChromeDriverManager().install(), options=chrome_options
                )

                driver.get(url)
                driver.implicitly_wait(10)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='btnpaymode']")))

                #go inside the pension payment mode page-
                view_payment_mode_button = driver.find_element(By.XPATH, "//*[@id='btnpaymode']")
                driver.execute_script("arguments[0].click();", view_payment_mode_button)
                print('Inside the view payment mode data site \n')

    else:
        print(IGNOPAS_file_path, "exists. Moving to next .")

###################################################################### IGNDPS ######################################################################################################################################################

    if not IGNDPS_folder_path.exists():
        IGNDPS_folder_path.mkdir(parents=True)

    if not IGNDPS_file_path.exists():
        
        print(IGNDPS_file_path, "doesn't exist and proceeding for scraping.")

        counter = 0
        while counter <= 5:
            try:
                counter += 1

                #click at the state
                driver.implicitly_wait(10)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='paymodedatatbody']//a")))
                state_link = driver.find_element(By.LINK_TEXT, state)
                state_link.click()
                print(f"Clicked {state} =>")

                #click at the district
                driver.implicitly_wait(10)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='paymodedatatbody']//a")))
                district_link = driver.find_element(By.LINK_TEXT, district)
                district_link.click()
                print(f"        Clicked {district}=>")

                #click at the sub-district
                driver.implicitly_wait(10)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='paymodedatatbody']//a")))
                sub_district_link = driver.find_element(By.LINK_TEXT, sub_district)
                sub_district_link.click()
                print(f"                     Clicked {sub_district}=>")

                #Grab the table header and get all the header columns
                table_header_ = driver.find_element(By.XPATH,'//*[@id="paymodedatathead"]/tr[2]')
                table_columns_ = table_header_.find_elements(By.TAG_NAME,'th')
                
                State_Name = table_columns_[1].text
                District_Name = table_columns_[2].text
                Sub_District_Name = table_columns_[3].text
                GP_Name = table_columns_[4].text
                State_Cap_A = table_columns_[5].text
                NSAP_Beneficiaries_B = table_columns_[6].text
                MIN_of_A_B = table_columns_[7].text
                Bank_Ac = table_columns_[8].text
                PO_Ac = table_columns_[9].text
                MO = table_columns_[10].text
                Cash = table_columns_[11].text

                #Grab the table body and get all the rows 
                table_body_ = driver.find_element(By.XPATH,'//*[@id="paymodedatatbody"]')
                table_rows_ = table_body_.find_elements(By.TAG_NAME,'tr')

                sub_district_IGNDPS_data = []

                #Extract the table for each sub-district and each scheme seperately
                for x in table_rows_:
                    row_ = x.find_elements(By.TAG_NAME,'td')

                    temporary_IGNDPS = {
                        "Scheme" : "IGNDPS",
                        State_Name : row_[1].text,
                        District_Name : row_[2].text,
                        Sub_District_Name : row_[3].text,
                        GP_Name : row_[4].text,
                        State_Cap_A : row_[12].text,
                        NSAP_Beneficiaries_B : row_[13].text,
                        MIN_of_A_B : row_[14].text,
                        Bank_Ac : row_[15].text,
                        PO_Ac : row_[16].text,
                        MO : row_[17].text,
                        Cash : row_[18].text
                    }
                    #each_state_IGNDPS_data = 
                    sub_district_IGNDPS_data.append(temporary_IGNDPS)
                
                #Convert to dataframe
                sub_district_IGNDPS_data = pd.DataFrame(sub_district_IGNDPS_data)
                print('sub_district_IGNDPS_data length=>',sub_district_IGNDPS_data.shape)
                sub_district_IGNDPS_data.to_csv(IGNDPS_file_path, index=False)

                BackButton = driver.find_element(By.XPATH,'//*[@id="btnpaymodeback"]').click()
                print(f'################################################ back to main starting page => {sub_district} IGNDPS next sub-district ####################################################\n')

                break

            except(NoSuchElementException,
            TimeoutException,
            UnicodeEncodeError) as ex:
                print(
                    f"{ex}: Rasied at {state} {district} {sub_district}"
                )
                print("Relooping again")

                BackButton = driver.find_element(By.XPATH,'//*[@id="btnpaymodeback"]').click()

                if counter == 5:
                    break

            except WebDriverException as ex:
                print(
                    f"{ex}: Rasied at {state} {district} {sub_district}"
                )
                driver.close()
                print("Relooping again")
                # defining Chrome options
                chrome_options = webdriver.ChromeOptions()
                prefs = {
                    "download.default_directory": str(dir_path),
                    "profile.default_content_setting_values.automatic_downloads": 1,
                }
                chrome_options.add_experimental_option("prefs", prefs)
                chrome_options.add_argument("start-maximized")

                driver = webdriver.Chrome(
                    ChromeDriverManager().install(), options=chrome_options
                )

                driver.get(url)
                driver.implicitly_wait(10)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='btnpaymode']")))

                #go inside the pension payment mode page-
                view_payment_mode_button = driver.find_element(By.XPATH, "//*[@id='btnpaymode']")
                driver.execute_script("arguments[0].click();", view_payment_mode_button)
                print('Inside the view payment mode data site \n')

    else:
        print(IGNDPS_file_path, "exists. Moving to next .")

###################################################################### IGNWPS ######################################################################################################################################################

    if not IGNWPS_folder_path.exists():
        IGNWPS_folder_path.mkdir(parents=True)

    if not IGNWPS_file_path.exists():
        
        print(IGNWPS_file_path, "doesn't exist and proceeding for scraping.")

        counter = 0
        while counter <= 5:
            try:
                counter += 1

                #click at the state
                driver.implicitly_wait(10)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='paymodedatatbody']//a")))
                state_link = driver.find_element(By.LINK_TEXT, state)
                state_link.click()
                print(f"Clicked {state} =>")

                #click at the district
                driver.implicitly_wait(10)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='paymodedatatbody']//a")))
                district_link = driver.find_element(By.LINK_TEXT, district)
                district_link.click()
                print(f"        Clicked {district}=>")

                #click at the sub-district
                driver.implicitly_wait(10)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='paymodedatatbody']//a")))
                sub_district_link = driver.find_element(By.LINK_TEXT, sub_district)
                sub_district_link.click()
                print(f"                     Clicked {sub_district}=>")

                #Grab the table header and get all the header columns
                table_header_ = driver.find_element(By.XPATH,'//*[@id="paymodedatathead"]/tr[2]')
                table_columns_ = table_header_.find_elements(By.TAG_NAME,'th')
                
                State_Name = table_columns_[1].text
                District_Name = table_columns_[2].text
                Sub_District_Name = table_columns_[3].text
                GP_Name = table_columns_[4].text
                State_Cap_A = table_columns_[5].text
                NSAP_Beneficiaries_B = table_columns_[6].text
                MIN_of_A_B = table_columns_[7].text
                Bank_Ac = table_columns_[8].text
                PO_Ac = table_columns_[9].text
                MO = table_columns_[10].text
                Cash = table_columns_[11].text

                #Grab the table body and get all the rows 
                table_body_ = driver.find_element(By.XPATH,'//*[@id="paymodedatatbody"]')
                table_rows_ = table_body_.find_elements(By.TAG_NAME,'tr')

                sub_district_IGNWPS_data = []

                #Extract the table for each sub-district and each scheme seperately
                for x in table_rows_:
                    row_ = x.find_elements(By.TAG_NAME,'td')

                    temporary_IGNWPS = {
                        "Scheme" : "IGNWPS",
                        State_Name : row_[1].text,
                        District_Name : row_[2].text,
                        Sub_District_Name : row_[3].text,
                        GP_Name : row_[4].text,
                        State_Cap_A : row_[19].text,
                        NSAP_Beneficiaries_B : row_[20].text,
                        MIN_of_A_B : row_[21].text,
                        Bank_Ac : row_[22].text,
                        PO_Ac : row_[23].text,
                        MO : row_[24].text,
                        Cash : row_[25].text
                    }
                    #each_state_IGNWPS_data = 
                    sub_district_IGNWPS_data.append(temporary_IGNWPS)
                
                #Convert to dataframe
                sub_district_IGNWPS_data = pd.DataFrame(sub_district_IGNWPS_data)
                print('sub_district_IGNWPS_data length=>',sub_district_IGNWPS_data.shape)
                sub_district_IGNOPAS_data.to_csv(IGNWPS_file_path, index=False)

                BackButton = driver.find_element(By.XPATH,'//*[@id="btnpaymodeback"]').click()
                print(f'################################################ back to main starting page => {sub_district} IGNWPS next sub-district ####################################################\n')

                break

            except(NoSuchElementException,
            TimeoutException,
            UnicodeEncodeError) as ex:
                print(
                    f"{ex}: Rasied at {state} {district} {sub_district}"
                )
                print("Relooping again")

                BackButton = driver.find_element(By.XPATH,'//*[@id="btnpaymodeback"]').click()

                if counter == 5:
                    break

            except WebDriverException as ex:
                print(
                    f"{ex}: Rasied at {state} {district} {sub_district}"
                )
                driver.close()
                print("Relooping again")
                # defining Chrome options
                chrome_options = webdriver.ChromeOptions()
                prefs = {
                    "download.default_directory": str(dir_path),
                    "profile.default_content_setting_values.automatic_downloads": 1,
                }
                chrome_options.add_experimental_option("prefs", prefs)
                chrome_options.add_argument("start-maximized")

                driver = webdriver.Chrome(
                    ChromeDriverManager().install(), options=chrome_options
                )

                driver.get(url)
                driver.implicitly_wait(10)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='btnpaymode']")))

                #go inside the pension payment mode page-
                view_payment_mode_button = driver.find_element(By.XPATH, "//*[@id='btnpaymode']")
                driver.execute_script("arguments[0].click();", view_payment_mode_button)
                print('Inside the view payment mode data site \n')

    else:
        print(IGNWPS_file_path, "exists. Moving to next .")
                
                

                

                

            
            

    
