import configparser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import json

class Disney():
    def __init__(self, username, password):
        self.options = Options()
##        options.add_argument("--headless")
        self.options.add_argument("window-size=1980,1080")
        current_dir = os.getcwd()#.replace('\\','/')
        self.download_folder = '{}\\attendance2\\'.format(current_dir)
        prefs = {'download.default_directory' : self.download_folder}
        self.options.add_experimental_option('prefs', prefs)
        self.options.add_argument("--proxy-server='direct://'")
        self.options.add_argument("--proxy-bypass-list=*")
        self.username = username
        self.password = password
        self.data_file = 'data.csv'
        
    def login(self):
        self.driver = webdriver.Chrome(options=options)
        self.driver.get('https://www.disneyplus.com/login')
        user = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.ID, 'email'))
                )
        user.send_keys(self.username)
        self.driver.find_element_by_name('dssLoginSubmit').click()
        time.sleep(2)
        password = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'password'))
                )
        time.sleep(5)
        password.send_keys(self.password)
        self.driver.find_element_by_name('dssLoginSubmit').click()

    def run_scraper(self):
        # creates progress.txt file if it does not exist
        progress_file = 'progress.txt'
        if progress_file not in os.listdir():
            with open(progress_file, 'w') as new_file:
                new_file.write('0')
        # depending on progress number, the script will pick up where it left off, 
        # if it happened to time out or fail
        with open(progress_file, 'r') as progress_file:
            current_progress = int(progress_file.read())
        # opens csv file in which the data will be saved
        with open(self.data_file, 'a') as f:
            sliders = self.driver.find_elements_by_class_name('sc-chPdSV')
            num_sliders = len(sliders)
            for i in range(num_sliders)[current_progress:]:
                sliders = self.driver.find_elements_by_class_name('sc-chPdSV')
                next_button = sliders[i].find_element_by_class_name('slick-next')
                # clicks next button to open all data for all movie tiles
                for c in range(5):
                    try:
                        next_button.click()
                        time.sleep(0.5)
                    except:
                        pass
                previous_button = sliders[i].find_element_by_class_name('slick-prev')
                # clicks the previous button to go back to beginning of tiles, so that they can 
                # be interacted with
                for cc in range(5):
                    try:
                        previous_button.click()
                        time.sleep(0.5)
                    except:
                        pass
                slider_title = sliders[i].find_element_by_class_name('sc-bxivhb').text
                tiles = sliders[i].find_elements_by_class_name('image-container')
                num_tiles = len(tiles)
                for t in range(num_tiles):
                    sliders = self.driver.find_elements_by_class_name('sc-chPdSV')
                    next_button = sliders[i].find_element_by_class_name('slick-next')
                    # determine amount of times to click the next button
                    if t < 6:
                        num_range = 0
                    elif t < 11:
                        num_range = 1
                    elif t < 16:
                        num_range = 2
                    elif t < 21:
                        num_range = 3
                    else:
                        num_range = 4
                    for c in range(num_range):
                        try:
                            next_button.click()
                            time.sleep(1.5)
                        except:
                            try:
                                time.sleep(1.5)
                                next_button.click()
                                time.sleep(1.5)
                            except:
                                pass
                    tiles = sliders[i].find_elements_by_class_name('sc-dxgOiQ')
                    movie_tile = tiles[t]
                    movie_image = movie_tile.find_element_by_tag_name('img').get_attribute('src')
                    movie_title = movie_tile.find_element_by_tag_name('img').get_attribute('alt')
                    try:
                        # click the movie tab and save URL along with other data to CSV
                        movie_tile.click()
                        movie_url = self.driver.current_url
                        self.driver.back()
                        f.write('\t'.join([slider_title, movie_title, movie_image, movie_url]))
                        f.write('\n')
                        data.append([slider_title, movie_title, movie_image, movie_url])
                        progress = str(i)
                        with open('progress.txt', 'w') as file:
                            file.write(progress)
                    except:
                        try: 
                            # if error box shows that max amount of devices are being used, clicks the 'ok' button and continues script
                            self.driver.find_element_by_class_name('jmtqAJ').click()
                            time.sleep(0.5)
                        except:
                            pass
                    time.sleep(2)
                    try:    
                        # second fail safe if error message takes too long to load
                        self.driver.find_element_by_class_name('jmtqAJ').click()
                        time.sleep(0.5)
                    except:
                        pass
        # delete the progress file
        os.remove(progress_file)
        # close chrome driver
        self.driver.close()

    def clean_save_json(self):
        # data cleaning & save to JSON file
        with open(self.data_file) as f:
            list_data = [line.split('\t') for line in f.read().split('\n') if line != '']

        sections = {}
        for item in list_data:
            if item[0] in sections:
                sections[item[0]].append([{'Name':item[1], 'Image':item[2], 'URL':item[3]}])
            else:
                sections[item[0]] = [{'Name':item[1], 'Image':item[2], 'URL':item[3]}]
        
        # save to json file
        json_save_file = 'disney_data.json'
        with open(json_save_file, 'w') as f:
            f.write(json.dumps(sections))
            
        # remove csv file
        os.remove(self.data_file)
            
        print ('Data saved to file: ' + json_save_file)

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('dl.cfg')
    
    username = config['DISNEY']['USERNAME']
    password = config['DISNEY']['PASSWORD']
    disney = Disney(username, password)
    disney.login()
    disney.run_scraper()
    disney.clean_save_json()
