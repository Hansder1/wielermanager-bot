import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configuratie
SPORZA_LOGIN_URL = "https://wielermanager.sporza.be/home"
SPORZA_TEAM_URL = "https://wielermanager.sporza.be/team/685775"
SPORZA_USERNAME = os.getenv("SPORZA_USERNAME", "JOUW_GEBRUIKERSNAAM")
SPORZA_PASSWORD = os.getenv("SPORZA_PASSWORD", "JOUW_WACHTWOORD")

@pytest.fixture
def driver():
    """ Setup en teardown voor de WebDriver """
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    yield driver
    driver.quit()

def close_cookie_banner(driver):
    """ Klikt op de cookie-melding als deze verschijnt """
    try:
        wait = WebDriverWait(driver, 5)
        cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Akkoord')]")))
        cookie_button.click()
        print("🍪 Cookie-melding weggeklikt!")
    except Exception:
        print("✅ Geen cookie-melding gevonden.")

def test_login(driver):
    """ Test of de login correct werkt """
    driver.get(SPORZA_LOGIN_URL)
    time.sleep(5)
    
    close_cookie_banner(driver)

    wait = WebDriverWait(driver, 10)

    # Klik op eerste 'Aanmelden'-knop
    first_login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "sso-login")))
    driver.execute_script("arguments[0].shadowRoot.querySelector('.loginButton').click();", first_login_button)
    print("🟢 Eerste 'Aanmelden'-knop gevonden en geklikt!")

    time.sleep(2)

    # Klik op tweede 'Aanmelden'-knop
    second_login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "sso-login")))
    driver.execute_script("arguments[0].shadowRoot.querySelector('.realAanmelden').click();", second_login_button)
    print("🟢 Tweede 'Aanmelden'-knop gevonden en geklikt!")

    time.sleep(5)

    # Vul inloggegevens in
    username_input = wait.until(EC.presence_of_element_located((By.NAME, "email")))
    password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Aanmelden')]")))

    username_input.send_keys(SPORZA_USERNAME)
    password_input.send_keys(SPORZA_PASSWORD)
    login_button.click()
    print("✅ Inloggegevens ingevuld en login-knop geklikt!")

    time.sleep(5)

    # Verifieer of login geslaagd is
    assert "login" not in driver.current_url, "❌ Login is niet gelukt!"
    print("✅ Login succesvol!")

def test_team_page(driver):
    """ Test of de ploegopstellingspagina correct opent """
    driver.get(SPORZA_TEAM_URL)
    time.sleep(5)

    wait = WebDriverWait(driver, 10)

    # Controleer of de pagina correct is geladen
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "team-container")))
        print("✅ Ploegopstellingspagina correct geopend!")
    except:
        assert False, "⚠️ Ploegopstellingspagina lijkt niet correct te laden!"

def test_get_team(driver):
    """ Test of de ploegopstelling correct wordt opgehaald """
    driver.get(SPORZA_TEAM_URL)
    time.sleep(5)

    wait = WebDriverWait(driver, 10)

    try:
        rider_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "rider-name")))
        current_team = [rider.text for rider in rider_elements]
        print(f"🏆 Huidige ploeg: {current_team}")
        assert len(current_team) > 0, "⚠️ Geen renners gevonden in de ploegopstelling!"
    except:
        assert False, "❌ Kon de ploegopstelling niet ophalen!"