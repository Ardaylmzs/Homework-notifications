import os
import json
import smtplib
from time import sleep
from dotenv import load_dotenv
from selenium import webdriver
from datetime import datetime as dt
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

# --- Memory docs settings ---
MEMORY_FILE = "memory.json"

# email
to_email = os.environ.get("TO_EMAIL")

def get_saved_count():
    if not os.path.exists(MEMORY_FILE):
        return 0
    try:
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
            return data.get("count", 0)
    except:
        return 0


def save_new_count(count):
    with open(MEMORY_FILE, "w") as f:
        json.dump({"count": count}, f)


def make_driver():
    chrome_options = Options()
    # cloud arrangements
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    return driver


def main():
    global to_email
    driver = make_driver()
    try:
        print("going to website...")
        driver.get(os.environ.get('URL'))
        sleep(5)

        # Login process
        login_button = driver.find_element(By.XPATH,
                                           value='//*[@id="main-content-starts"]/div[1]/div/section[1]/div[2]/div/div[2]/div/div/section/div/div/div/div[1]/div/div/div/div/p[2]/a')
        driver.execute_script("arguments[0].click();", login_button)
        sleep(5)

        try:
            email_input = driver.find_element(By.NAME, value="username")
            sleep(2)
            email_input.send_keys(f"{os.environ.get('MYL_LAB_EMAIL')}")
            sleep(2)
            password_input = driver.find_element(By.NAME, value="password")
            sleep(2)
            password_input.send_keys(f"{os.environ.get('MY_LAB_PASSWORD')}")
            sleep(2)
        except NoSuchElementException:
            # Popup
            if len(driver.window_handles) > 1:
                pearson_popup = driver.window_handles[1]
                driver.switch_to.window(pearson_popup)
                close_button = driver.find_element(By.XPATH,
                                                   value='//*[@id="browserCheckerMessage"]/div[2]/div/div[1]/button')
                close_button.click()
                sleep(3)
                driver.switch_to.window(driver.window_handles[0])

        # click the login button
        submit_button = driver.find_element(By.XPATH, value='//*[@id="submitBttn"]')
        driver.execute_script("arguments[0].click();", submit_button)
        sleep(10)

        # Navigation (subject -> homework -> Quiz)
        quiz_path = os.environ.get('QUIZ_PATH')
        mis_button = driver.find_element(By.XPATH, value=f'//*[@id="{quiz_path}"]')
        driver.execute_script("arguments[0].click();", mis_button)
        sleep(5)

        assignment_button = driver.find_element(By.XPATH,
                                                value='//*[@id="ov_leftnav"]/div[2]/div[3]/div/div/div/a/div[2]')
        driver.execute_script("arguments[0].click();", assignment_button)
        sleep(4)

        quiz_button = driver.find_element(By.XPATH, value='//*[@id="ov_leftnav"]/div[2]/div[6]/div/div/div/a/div[1]')
        driver.execute_script("arguments[0].click();", quiz_button)
        sleep(4)

        driver.switch_to.frame("contentFrame")

        # 1. find the homework numbers
        current_count = len(driver.find_elements(By.XPATH,
                                                 value='//*[@id="ctl00_ctl00_InsideForm_MasterContent_gridAssignments"]/tbody/tr'))
        try:
            h_date = driver.find_elements(By.XPATH,value='//*[@class=" nowrap"]')[-1]
        except NoSuchElementException:
            h_date = driver.find_element(By.XPATH, value='//*[@class=" nowrap"]')
        print(h_date.text)
        print(f"actual number of homework in website: {current_count}")
        print(f"homework deadline is :{h_date.text}")

         #2. read the old number in the previous process
        saved_count = get_saved_count()
        print(f"old number of homework in the memory: {saved_count}")

        # -- last day notification data !!
        on_last_day = dt.timetuple(dt.today()).tm_mday
        last_day_hour = dt.timetuple(dt.today()).tm_hour
        new_year = 31
        print(on_last_day)

        try:
            dates = driver.find_elements(By.XPATH,value='//*[@class=" nowrap"]')[0].text
            last_day = int(dates[3] + dates[4])
            if last_day == on_last_day and last_day_hour == 10:
                print("today is last day for math homework!!!")
                if to_email:
                    _emails = to_email.split(",")
                    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
                        connection.starttls()
                        connection.login(user=os.environ.get("MY_EMAIL"), password=os.environ.get("MY_PASSWORD"))
                        for email in _emails:
                            connection.sendmail(
                                from_addr=os.environ.get("MY_EMAIL"),
                                to_addrs=email,
                                msg=f"Subject: MIS homework notifications\n\n PAY ATTENTION!! LAST DAY FOR THE {current_count}. HOMEWORK \n\n you should complete your homework until {h_date.text[9:16]} :) !!\n\n\n pearson link :\n {os.environ.get('URL')}"
                            )
        except NoSuchElementException:
            last_day = int(h_date.text[3] + h_date.text[4])
            if last_day == on_last_day and last_day_hour == 10:
                print("today is last day for math homework!!!")
                if to_email:
                    _emails = to_email.split(",")
                    with smtplib.SMTP("smtp.gmail.com",port=587) as connection:
                        connection.starttls()
                        connection.login(user=os.environ.get("MY_EMAIL"), password=os.environ.get("MY_PASSWORD"))
                        for email in _emails:
                            connection.sendmail(
                                from_addr=os.environ.get("MY_EMAIL"),
                                to_addrs=email,
                                msg=f"Subject: Math homework notifications\n\n PAY ATTENTION!! LAST DAY FOR THE {actual_count}. HOMEWORK \n\n you should complete your homework until {h_date.text[9:16]} :) !!\n\n\n pearson link :\n {os.environ.get('URL')}"
                            )
        # Happy New Year

        if on_last_day == new_year  and last_day_hour == 21:
            print("today is last day for 2025 ")
            if to_email:
                _emails = to_email.split(",")
                with smtplib.SMTP("smtp.gmail.com",port=587) as connection:
                    connection.starttls()
                    connection.login(user=os.environ.get("MY_EMAIL"), password=os.environ.get("MY_PASSWORD"))
                    for email in _emails:
                        connection.sendmail(
                            from_addr=os.environ.get("MY_EMAIL"),
                            to_addrs=email,
                            msg=f"Subject: HAPPY NEW YEARS !!! \n\n Happy new year and I hope the new year brings you happiness and health :) \n\n by the way you don't miss the final exams , is coming :/"
                        )
        #  4. compare
        if current_count > saved_count:
            print("we determined a new homework , are sending the emails!!")
            if to_email:
                emails = to_email.split(",")
                with smtplib.SMTP("smtp.gmail.com",port=587) as connection:
                    connection.starttls()
                    connection.login(user=os.environ.get("MY_EMAIL"), password=os.environ.get("MY_PASSWORD"))
                    for email in emails:
                        connection.sendmail(
                            from_addr=os.environ.get("MY_EMAIL"),
                            to_addrs=email,
                            msg=f"Subject: MIS homework notifications\n\n Teacher released the {current_count}. homework , you dont MISS that :) please check your MyLab account!!\n\n Homework deadline is : {h_date.text[:8]}  {h_date.text[9:16]} \n\n\n pearson link :\n {os.environ.get('URL')}"
                        )

            # save the new count
            save_new_count(current_count)


        elif current_count < saved_count:
            print("the homework number is decreased , is updating now !! .")
            save_new_count(current_count)

        else:
            print("there is no any new homework!!.")

    except Exception as e:
        print(f"we received the error : {e}:(")
    finally:
        driver.quit()
        print("is ended the process.")


if __name__ == "__main__":
    main()
