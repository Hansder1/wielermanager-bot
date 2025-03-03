import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configuratie
SPORZA_LOGIN_URL = "https://wielermanager.sporza.be/home"
SPORZA_TEAM_URL = "https://wielermanager.sporza.be/team/685775"  # Correcte URL
SPORZA_USERNAME = os.getenv("SPORZA_USERNAME", "JOUW_GEBRUIKERSNAAM")
SPORZA_PASSWORD = os.getenv("SPORZA_PASSWORD", "JOUW_WACHTWOORD")

def close_cookie_banner(driver):
    """ Klikt op de cookie-melding als deze verschijnt """
    try:
        wait = WebDriverWait(driver, 5)
        cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Akkoord')]")))
        cookie_button.click()
        print("🍪 Cookie-melding weggeklikt!")
    except Exception:
        print("✅ Geen cookie-melding gevonden.")

def login_to_sporza(driver):
    """ Log in op Sporza Wielermanager """
    driver.get(SPORZA_LOGIN_URL)
    time.sleep(5)
    
    close_cookie_banner(driver)

    try:
        wait = WebDriverWait(driver, 10)

        # Zoek en klik op de eerste 'Aanmelden'-knop in de header
        first_login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "sso-login")))
        driver.execute_script("arguments[0].shadowRoot.querySelector('.loginButton').click();", first_login_button)
        print("🟢 Eerste 'Aanmelden'-knop gevonden en geklikt!")

        time.sleep(2)

        # Zoek en klik op de tweede 'Aanmelden'-knop in het dropdown-menu
        second_login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "sso-login")))
        driver.execute_script("arguments[0].shadowRoot.querySelector('.realAanmelden').click();", second_login_button)
        print("🟢 Tweede 'Aanmelden'-knop gevonden en geklikt!")

        time.sleep(5)

        # Vul de inloggegevens in
        username_input = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Aanmelden')]")))

        username_input.send_keys(SPORZA_USERNAME)
        password_input.send_keys(SPORZA_PASSWORD)
        login_button.click()
        print("✅ Inloggegevens ingevuld en login-knop geklikt!")

        time.sleep(5)

        # Controleren of login is geslaagd
        if "login" in driver.current_url:
            print("⚠️ Login lijkt niet gelukt!")
            return False
        
        print("✅ Login geslaagd!")
        return True
    except Exception as e:
        print(f"❌ Kon niet inloggen op Sporza: {e}")
        return False

def open_team_page(driver):
    """ Opent de ploegopstellingspagina en controleert of deze geladen is """
    try:
        print("📂 Ploegpagina openen...")
        driver.get(SPORZA_TEAM_URL)
        time.sleep(5)  # Extra wachttijd voor de zekerheid
        
        wait = WebDriverWait(driver, 10)
        
        # Probeer meerdere manieren om te detecteren of de pagina geladen is
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "team-container")))
            print("✅ Ploegopstellingspagina geopend!")
            return True
        except:
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, "//h1[contains(text(),'Ploegopstelling')]")))
                print("✅ Ploegopstellingspagina gevonden op alternatieve manier!")
                return True
            except:
                print("⚠️ Ploegopstellingspagina lijkt niet volledig geladen!")

        return False
    except Exception as e:
        print(f"⚠️ Kon de ploegopstellingspagina niet openen: {e}")
        return False

def get_current_team(driver):
    """ Haalt de huidige ploegopstelling op """
    try:
        wait = WebDriverWait(driver, 10)
        rider_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "rider-name")))
        current_team = [rider.text for rider in rider_elements]
        print(f"🏆 Huidige ploeg: {current_team}")
        return current_team
    except Exception as e:
        print(f"⚠️ Kon de huidige ploeg niet ophalen: {e}")
        return []

def main():
    """ Hoofdprogramma """
    print("🚀 Script gestart...")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        if login_to_sporza(driver):
            if open_team_page(driver):
                current_team = get_current_team(driver)
                print(f"✅ Ploeg opgehaald: {current_team}")
    finally:
        print("❌ Browser gesloten.")
        driver.quit()

if __name__ == "__main__":
    main()