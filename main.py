import os
from time import sleep
from selenium.webdriver.common.by import By
import smtplib
from selenium import webdriver
from dotenv import load_dotenv
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException,TimeoutException

load_dotenv()

CHROME_USER_DATA_DIR = fr"C:\Users\{os.environ.get("CHROME_USER")}\AppData\Local\Google\Chrome\User Data"
CHROME_PROFILE_DIRECTORY = "Default"
CHROMEDRIVER_PATH = r"C:\path\to\chromedriver.exe"

def make_driver():
    options = Options()
    options.add_argument(r"--user-data-dir=C:\ChromeProfile")
    options.add_argument("--profile-directory=.")
    options.add_argument("--headless")
    # DECREASE BOT FEATURES + DevToolsActivePort fix
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    # WITH ChromeDriver Manager

    driver = webdriver.Chrome(options=options)
    return driver
drivers = make_driver()
drivers.get("https://www.pearson.com/en-us/higher-education/products-services/mylab/login-mylab.html?srsltid=AfmBOoopIwY9GyQ7VgGW4Y9xjOt0jcMpM9Kh1NEk5SXhrRZ7Rtpe_vHD")
sleep(5)

login_button = drivers.find_element(By.XPATH, value='//*[@id="main-content-starts"]/div[1]/div/section[1]/div[2]/div/div[2]/div/div/section/div/div/div/div[1]/div/div/div/div/p[2]/a' )
login_button.click()
sleep(5)
try:
    email_input = drivers.find_element(By.NAME, value="username")
    sleep(2)
    email_input.send_keys(f"{os.environ.get('MYL_LAB_EMAIL')}")
    sleep(4)
    password_input = drivers.find_element(By.NAME, value="password")
    sleep(2)
    password_input.send_keys(f"{os.environ.get('MY_LAB_PASSWORD')}")
    sleep(4)
except NoSuchElementException:
    pearson_popup = drivers.window_handles[1]
    drivers.switch_to.window(pearson_popup)
    close_button = drivers.find_element(By.XPATH , value='//*[@id="browserCheckerMessage"]/div[2]/div/div[1]/button')
    close_button.click()
    sleep(3)
    pearson_page = drivers.window_handles[0]
    drivers.switch_to.window(pearson_page)

submit_button = drivers.find_element(By.XPATH ,value='//*[@id="submitBttn"]')
submit_button.click()
sleep(10)
mis_button = drivers.find_element(By.XPATH , value='//*[@id="courseCardTitle-tuncali03545"]')
mis_button.click()
sleep(5)
assignment_button = drivers.find_element(By.XPATH , value='//*[@id="ov_leftnav"]/div[2]/div[3]/div/div/div/a/div[2]')
assignment_button.click()
sleep(4)
quiz_button = drivers.find_element(By.XPATH , value='//*[@id="ov_leftnav"]/div[2]/div[6]/div/div/div/a/div[1]')
quiz_button.click()
sleep(4)
drivers.switch_to.frame("contentFrame")
tr_attr = len(drivers.find_elements(By.XPATH , value='//*[@id="ctl00_ctl00_InsideForm_MasterContent_gridAssignments"]/tbody/tr'))
old_value = 6
progress = True
while progress:
    sleep(10)
    new_value = len(drivers.find_elements(By.XPATH , value='//*[@id="ctl00_ctl00_InsideForm_MasterContent_gridAssignments"]/tbody/tr'))
    if new_value is not None and old_value is not None:
        print(f"value is checked: {new_value}")
        if new_value > old_value:
            to_email = os.environ.get("TO_EMAIL")
            if to_email:
                emails = to_email.split(",")
                print(emails)
                with smtplib.SMTP("smtp.gmail.com") as connection:
                    connection.starttls()
                    connection.login(user=os.environ.get("MY_EMAIL"), password=os.environ.get("MY_PASSWORD"))
                    for email in emails:
                        connection.sendmail(from_addr=os.environ.get("MY_EMAIL"), to_addrs=email,msg="Subject: MIS homework notifications\n\n Teacher released new homework , please check your account!!")
            old_value = new_value
            progress = False
    sleep(30)






