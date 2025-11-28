import os
import json
import smtplib
from time import sleep
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

# --- Memory docs settings ---
MEMORY_FILE = "memory.json"

def get_saved_count():
    """Önceki çalıştırmadan kalan ödev sayısını dosyadan okur."""
    if not os.path.exists(MEMORY_FILE):
        return 0 
    try:
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
            return data.get("count", 0)
    except:
        return 0

def save_new_count(count):
    """Yeni ödev sayısını dosyaya kaydeder."""
    with open(MEMORY_FILE, "w") as f:
        json.dump({"count": count}, f)

def make_driver():
    chrome_options = Options()
    # cloud arrangments
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    return driver

def main():
    driver = make_driver()
    try:
        print("Siteye gidiliyor...")
        driver.get("https://www.pearson.com/en-us/higher-education/products-services/mylab/login-mylab.html?srsltid=AfmBOoopIwY9GyQ7VgGW4Y9xjOt0jcMpM9Kh1NEk5SXhrRZ7Rtpe_vHD")
        sleep(5)

        # Login process
        login_button = driver.find_element(By.XPATH, value='//*[@id="main-content-starts"]/div[1]/div/section[1]/div[2]/div/div[2]/div/div/section/div/div/div/div[1]/div/div/div/div/p[2]/a' )
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
                close_button = driver.find_element(By.XPATH , value='//*[@id="browserCheckerMessage"]/div[2]/div/div[1]/button')
                close_button.click()
                sleep(3)
                driver.switch_to.window(driver.window_handles[0])

        # click the login button
        submit_button = driver.find_element(By.XPATH ,value='//*[@id="submitBttn"]')
        driver.execute_script("arguments[0].click();", submit_button)
        sleep(10)

        # Navigation (subject -> homework -> Quiz)
        mis_button = driver.find_element(By.XPATH , value='//*[@id="courseCardTitle-tuncali03545"]')
        driver.execute_script("arguments[0].click();", mis_button)
        sleep(5)
        
        assignment_button = driver.find_element(By.XPATH , value='//*[@id="ov_leftnav"]/div[2]/div[3]/div/div/div/a/div[2]')
        driver.execute_script("arguments[0].click();", assignment_button)
        sleep(4)
        
        quiz_button = driver.find_element(By.XPATH , value='//*[@id="ov_leftnav"]/div[2]/div[6]/div/div/div/a/div[1]')
        driver.execute_script("arguments[0].click();", quiz_button)
        sleep(4)
        
        driver.switch_to.frame("contentFrame")
        
        
        # 1. find the homework numbers
        current_count = len(driver.find_elements(By.XPATH , value='//*[@id="ctl00_ctl00_InsideForm_MasterContent_gridAssignments"]/tbody/tr'))
        print(f"Sitedeki güncel ödev sayısı: {current_count}")

        # 2. Eski (kayıtlı) ödev sayısını dosyadan oku
        saved_count = get_saved_count()
        print(f"Hafızadaki eski ödev sayısı: {saved_count}")

        # 3. compare
        if current_count > saved_count:
            print("YENİ ÖDEV TESPİT EDİLDİ! Mail atılıyor...")
            to_email = os.environ.get("TO_EMAIL")
            if to_email:
                emails = to_email.split(",")
                with smtplib.SMTP("smtp.gmail.com") as connection:
                    connection.starttls()
                    connection.login(user=os.environ.get("MY_EMAIL"), password=os.environ.get("MY_PASSWORD"))
                    for email in emails:
                        connection.sendmail(
                            from_addr=os.environ.get("MY_EMAIL"), 
                            to_addrs=email,
                            msg="Subject: MIS homework notifications\n\n Teacher released new homework , please check your account!!"
                        )
            
            # Yeni sayıyı hafızaya kaydet
            save_new_count(current_count)
        
        elif current_count < saved_count:
             print("Ödev sayısı azalmış, hafıza güncelleniyor.")
             save_new_count(current_count)
             
        else:
            print("Değişiklik yok. Mail atılmadı.")

    except Exception as e:
        print(f"Bir hata oluştu: {e}")
    finally:
        driver.quit()
        print("Driver kapatıldı.")

if __name__ == "__main__":
    main()
