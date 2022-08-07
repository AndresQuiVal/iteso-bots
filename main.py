from lib2to3.pgen2 import driver
import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup

def dummy_send(driver, element, word, delay):    
    for c in word:
        driver.find_element_by_id(element).send_keys(c)
        time.sleep(delay)

def login(driver, email, password):
    driver.get("https://sso.iteso.mx/sso/XUI/#login/&goto=https://servicios.iteso.mx/j_spring_security_check")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "idToken1")))
    submit_btn = driver.find_element_by_id("loginButton_0")
    dummy_send(driver, "idToken1", email, 0.05)
    dummy_send(driver, "idToken2", password, 0.05)

    submit_btn.click()
    time.sleep(10)

    return driver

def login_and_create_driver(email, password):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    login(driver, email, password)

    return driver


def notify_discord(amount):
    IMAGE = "https://cdn-icons-png.flaticon.com/512/4712/4712010.png"
    WEBHOOK = "https://discord.com/api/webhooks/1002268247221088268/4YcgIvdScK_Rdg62nx9EcNwq7yG9Sbk94f31wz1aytN4qTUAxN6PMjf8IwbBBV6b3bDv"

    try:
        data = {
            "avatar_url":
            IMAGE,
            "username":
            "Notificador de pagos",
            "embeds": [{
                "description": f"Tienes que pagar mendigo pobre \nTotal de adeudos: {amount}\n\nLink para pagar: https://servicios.iteso.mx/apps/alumno/estado_cuenta/",
                "color": 16753152,
                "thumbnail": {
                    "url": IMAGE
                },
                "footer": {
                    "text": "botsito epico",
                    "icon_url": IMAGE
                }
            }]
        }
        response = requests.post(WEBHOOK,
                                 json=data,
                                 headers={"Content-Type": "application/json"})
        response.raise_for_status()
    except requests.exceptions.HTTPError as ex:
        print(f"Error al notificar!: {ex}")

def check_finances(driver):
    driver.get("https://servicios.iteso.mx/apps/alumno/estado_cuenta/")
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    payment_info_divs = soup.find_all("div", {"class": "ng-tns-c9-4 ng-star-inserted"})
    total_payment_div = payment_info_divs[1] 
    money_delayed = float(total_payment_div.text)

    if money_delayed == 0.0:
        notify_discord(money_delayed)

    print("Awaiting...")
    time.sleep(60 * 60 * 24) # await one day


def main():
    email, password = input("Introduce correo contraseña: ").split()
    driver = login_and_create_driver(email, password)
    check_finances(driver)
    

if __name__ == "__main__":
    main()