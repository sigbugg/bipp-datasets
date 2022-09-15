import json
import time
from pathlib import Path

#pip install selenium
#pip install webdrivermanager
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# defining directories

dir_path = Path.cwd()
raw_path = Path.joinpath(dir_path, "data", "raw", "jsons")
interim_path = Path.joinpath(dir_path, "data", "interim")
external_path = Path.joinpath(dir_path, "data", "external")


"""Scraping Begins Here"""

# defining Chrome options
chrome_options = webdriver.ChromeOptions()
prefs = {"download.default_directory": str(dir_path),"profile.default_content_setting_values.automatic_downloads": 1,}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("start-maximized")

driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)


# fectching URL
url = "https://nsap.nic.in/abstractdashboard.do?method=initialPage"
driver.get(url)
wait = WebDriverWait(driver, 30)

driver.implicitly_wait(10)
wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='btnpaymode']")))
view_payment_mode_button = driver.find_element(By.XPATH, "//*[@id='btnpaymode']")
driver.execute_script("arguments[0].click();", view_payment_mode_button)
print('Inside the view payment mode data site \n')


driver.implicitly_wait(10)
wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='paymodedatatbody']//a")))
state_link_tags = driver.find_elements(By.XPATH, "//*[@id='paymodedatatbody']//a")
state_names = [x.get_attribute("text") for x in state_link_tags]
state_hrefs = [x.get_attribute("href") for x in state_link_tags]
#print(state_names,state_hrefs)
#print(len(state_hrefs))

for state, st_href in zip(state_names, state_hrefs):
    state_link = driver.find_element(By.LINK_TEXT, state)
    state_link.click()
    print(f"Clicked {state} =>")
    driver.implicitly_wait(10)



    #Take care of DADRA N HAVELI DAMAN & DIU which has no district records
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='paymodedatatbody']//a")))
    except:
        BackButton = driver.find_element(By.XPATH,'//*[@id="btnpaymodeback"]').click()
        print(f"No data for {state} !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print('Back to main starting page')
        print('########################################################################################################################## \n \n')
        driver.implicitly_wait(10)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='paymodedatatbody']//a")))
        continue
    

    #get the district <a> tags
    district_a_tags = driver.find_elements(By.XPATH, "//*[@id='paymodedatatbody']//a")
    district_names = [x.get_attribute("text") for x in district_a_tags]
    district_hrefs = [x.get_attribute("href") for x in district_a_tags]
    #print(district_names, '\n')



    for district, dist_href in zip(district_names, district_hrefs):

        try:
            #### If there comes an error, handle it => now checking
            district_list = []
            
            #json file for each district 
            state_path = Path.joinpath(raw_path, state)
            district_json_name = ".".join([district, "json"])
            district_json_path = Path.joinpath(state_path, district_json_name)

            #check if the path to state folder exists to store the district json files
            if not state_path.exists():
                Path.mkdir(state_path, parents=True)
            
            #check if the district json file already exists in the state folder
            if not district_json_path.exists():
                print(f"{district}.json file doesn't exist and proceeding for scraping")

                #Facing problem with south west delhi#####################
                try:
                    link_district = driver.find_element(By.LINK_TEXT, district)
                except:
                    print(f"Cannot find element - {district} by link text !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! \n")
                    continue

                link_district.click()
                print(f"Clicked {state} => {district} =>")
                driver.implicitly_wait(10)

                #Havent checked if all the links can be found using the link text attribute       
                         
                wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='paymodedatatbody']//a")))
                #get the sub-district <a> tags

                #Himachal pradesh has devnagiri sub-district names

                sub_district_a_tags = driver.find_elements(By.XPATH, "//*[@id='paymodedatatbody']//a")
                sub_district_names = [x.get_attribute("text") for x in sub_district_a_tags]
                sub_district_hrefs = [x.get_attribute("href") for x in sub_district_a_tags]
                print(sub_district_names)

                #Append all the sub-district dictionary to the district list
                for sub_district, sub_district_href in zip(sub_district_names, sub_district_hrefs):
                    #create dictionary for each sub-district
                    sub_district_dict = {}
                    sub_district_dict = {
                        "state_name": state,
                        "district_name": district,
                        "sub_district_name": sub_district,
                    }
                    district_list.append(sub_district_dict)

                with open(str(district_json_path), "w") as nested_out_file:
                    json.dump(
                        district_list, nested_out_file, ensure_ascii=False
                    )            

            else:
                print(f"{district}.json file already exists and skipped. Moving to next district. \n")
                continue

            BackButton = driver.find_element(By.XPATH,'//*[@id="btnpaymodeback"]').click()
            #print('back to main starting page')
            driver.implicitly_wait(10)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='paymodedatatbody']//a")))

            state_link = driver.find_element(By.LINK_TEXT, state)
            state_link.click()
            driver.implicitly_wait(10)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='paymodedatatbody']//a")))
            print('Next district \n####################################################\n')
        
        except (
            NoSuchElementException,
            TimeoutException,
            UnicodeEncodeError,
        ) as ex:

            while True:
                try:
                    print(f"{ex} raised at {state} {district} {sub_district} !!!!!!!!!!!!!!!")

                    #go back to the district page to iterate through the next sub-district
                    driver.get(url)
                    driver.implicitly_wait(20)

                    #go inside the pension payment mode page-
                    view_payment_mode_button = driver.find_element(By.XPATH, "//*[@id='btnpaymode']")
                    driver.execute_script("arguments[0].click();", view_payment_mode_button)
                    driver.implicitly_wait(10)
                    wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='paymodedatatbody']//a")))

                    link_state = driver.find_element(By.LINK_TEXT, state)
                    link_state.click()
                    driver.implicitly_wait(10)
                    wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='paymodedatatbody']//a")))
                    break

                except (NoSuchElementException, TimeoutException):
                    continue

        except WebDriverException as ex:

            while True:
                try:
                    print(f"{ex} raised at {state} {district} {sub_district}")

                    driver.close()

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

                   #go back to the district page to iterate through the next sub-district
                    driver.get(url)
                    driver.implicitly_wait(20)

                    #go inside the pension payment mode page-
                    view_payment_mode_button = driver.find_element(By.XPATH, "//*[@id='btnpaymode']")
                    driver.execute_script("arguments[0].click();", view_payment_mode_button)
                    driver.implicitly_wait(10)
                    wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='paymodedatatbody']//a")))

                    link_state = driver.find_element(By.LINK_TEXT, state)
                    link_state.click()
                    driver.implicitly_wait(10)
                    wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='paymodedatatbody']//a")))
    
                    break

                except (NoSuchElementException, TimeoutException):
                    continue

    BackButton = driver.find_element(By.XPATH,'//*[@id="btnpaymodeback"]').click()
    print('Back to main starting page')
    print('###################################################################################################################################################### \n \n')
    driver.implicitly_wait(10)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='paymodedatatbody']//a")))

time.sleep(15)