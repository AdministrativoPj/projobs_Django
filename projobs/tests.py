from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
import time
import random

class RegistroYLoginTest(LiveServerTestCase):

    def setUp(self):
        chrome_options = Options()
        #chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        path = os.path.join(os.getcwd(), 'chromedriver.exe')
        service = Service(executable_path=path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)

        # Datos aleatorios válidos
        numero_random = random.randint(1000, 9999)
        self.correo_prueba = f"test{numero_random}@gmail.com"  # solo gmail/hotmail/outlook
        self.password_prueba = "Test1234"  # debe tener letras y números

    def test_registro_y_login(self):
        # Registro
        self.driver.get(f'{self.live_server_url}/formulario/')

        self.driver.find_element(By.NAME, 'nombre').send_keys('Selenium')
        self.driver.find_element(By.NAME, 'apellido').send_keys('Test')
        self.driver.find_element(By.NAME, 'correo').send_keys(self.correo_prueba)
        self.driver.find_element(By.NAME, 'password').send_keys(self.password_prueba)

        rol_select = self.driver.find_element(By.NAME, 'rol')
        for option in rol_select.find_elements(By.TAG_NAME, 'option'):
            if option.get_attribute('value') == '3':
                option.click()
                break

        # Cargar foto si existe
        foto_path = os.path.join(os.getcwd(), 'default.png')
        if os.path.exists(foto_path):
            self.driver.find_element(By.ID, 'foto').send_keys(foto_path)

        self.driver.find_element(By.CSS_SELECTOR, 'button[type=\"submit\"]').click()
        time.sleep(2)

        # Login
        self.driver.get(f'{self.live_server_url}/inicioSesion/')
        self.driver.find_element(By.NAME, 'correo').send_keys(self.correo_prueba)
        self.driver.find_element(By.NAME, 'password').send_keys(self.password_prueba)
        self.driver.find_element(By.CSS_SELECTOR, 'button[type=\"submit\"]').click()
        time.sleep(2)

        # Validar acceso exitoso
        body_text = self.driver.find_element(By.TAG_NAME, 'body').text
        self.assertIn('Bienvenido', body_text)

    def tearDown(self):
        self.driver.quit()
