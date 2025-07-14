import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from pages.login_page import LoginPage


REGISTRATION_URL = "https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/front/home"

@pytest.mark.usefixtures("driver")
def test_cp_01_01_register_valid_instructor(driver):
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    # Realizar login primero
    import os
    LOGIN_EMAIL = os.environ.get("LOGIN_EMAIL")
    LOGIN_PASSWORD = os.environ.get("LOGIN_PASSWORD")
    assert LOGIN_EMAIL, "No se encontró la variable de entorno LOGIN_EMAIL"
    assert LOGIN_PASSWORD, "No se encontró la variable de entorno LOGIN_PASSWORD"
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión correctamente"
    # Presionar el icono de 'Teammates' (ajusta el selector si es necesario)
    wait = WebDriverWait(driver, 15)
    # Click directo al icono de Teammates usando el selector validado
    try:
        icon = wait.until(EC.element_to_be_clickable((By.XPATH, "//img[contains(@src, 'logo')]")))
        icon.click()
    except Exception:
        assert False, "No se pudo hacer click en el icono de Teammates"
    # Continuar con el flujo de registro
    driver.get(REGISTRATION_URL)
    time.sleep(2)
    request_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'request a free instructor account')]")))
    request_btn.click()
    instructor_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'i am an instructor')]")))
    instructor_btn.click()
    wait.until(EC.presence_of_element_located((By.ID, "name")))
    driver.find_element(By.ID, "name").send_keys("Andre Hilacondo Begazo")
    driver.find_element(By.ID, "institution").send_keys("Universidad Nacional de San Agustín de Arequipa")
    driver.find_element(By.ID, "country").send_keys("Perú")
    driver.find_element(By.ID, "email").send_keys("juan@unsa.edu.pe")
    driver.find_element(By.ID, "comments").send_keys("")
    driver.find_element(By.XPATH, "//button[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')]").click()
    try:
        # Espera hasta 20 segundos por los mensajes de éxito, usando un XPath más flexible
        wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'your request has been submitted successfully')]")))
        wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'we have sent an acknowledgement email')]")))
        success = True
    except Exception as e:
        print('No se encontraron los mensajes de éxito. HTML actual:')
        print(driver.page_source)
        success = False
    assert success

@pytest.mark.usefixtures("driver")
def test_cp_01_02_register_invalid_instructor(driver):
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    # Realizar login primero
    import os
    LOGIN_EMAIL = os.environ.get("LOGIN_EMAIL")
    LOGIN_PASSWORD = os.environ.get("LOGIN_PASSWORD")
    assert LOGIN_EMAIL, "No se encontró la variable de entorno LOGIN_EMAIL"
    assert LOGIN_PASSWORD, "No se encontró la variable de entorno LOGIN_PASSWORD"
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión correctamente"
    wait = WebDriverWait(driver, 15)
    # Click directo al icono de Teammates usando el selector validado
    try:
        icon = wait.until(EC.element_to_be_clickable((By.XPATH, "//img[contains(@src, 'logo')]")))
        icon.click()
    except Exception:
        assert False, "No se pudo hacer click en el icono de Teammates"
    # Continuar con el flujo de registro fallido
    driver.get(REGISTRATION_URL)
    time.sleep(2)
    request_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'request a free instructor account')]")))
    request_btn.click()
    instructor_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'i am an instructor')]")))
    instructor_btn.click()
    wait.until(EC.presence_of_element_located((By.ID, "name")))
    driver.find_element(By.ID, "name").send_keys("Andre Hilacondo Bega zo")
    driver.find_element(By.ID, "institution").send_keys("Universidad Nacional de San Agustín de Arequipa")
    driver.find_element(By.ID, "country").send_keys("Perú")
    driver.find_element(By.ID, "email").send_keys("jose@gmail.com")
    driver.find_element(By.ID, "comments").send_keys("")
    driver.find_element(By.XPATH, "//button[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')]").click()
    try:
        wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'correo no autorizado para registro')]")))
        error_found = True
    except Exception:
        print('No se encontró el mensaje de correo no autorizado. HTML actual:')
        print(driver.page_source)
        error_found = False
    assert error_found, "No se mostró el mensaje de correo no autorizado para registro"

@pytest.mark.usefixtures("driver")
def test_cp_01_03_register_missing_name(driver):
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    # Realizar login primero
    import os
    LOGIN_EMAIL = os.environ.get("LOGIN_EMAIL")
    LOGIN_PASSWORD = os.environ.get("LOGIN_PASSWORD")
    assert LOGIN_EMAIL, "No se encontró la variable de entorno LOGIN_EMAIL"
    assert LOGIN_PASSWORD, "No se encontró la variable de entorno LOGIN_PASSWORD"
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión correctamente"
    wait = WebDriverWait(driver, 15)
    # Click directo al icono de Teammates usando el selector validado
    try:
        icon = wait.until(EC.element_to_be_clickable((By.XPATH, "//img[contains(@src, 'logo')]")))
        icon.click()
    except Exception:
        assert False, "No se pudo hacer click en el icono de Teammates"
    # Continuar con el flujo de registro fallido
    driver.get(REGISTRATION_URL)
    time.sleep(2)
    request_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'request a free instructor account')]")))
    request_btn.click()
    instructor_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'i am an instructor')]")))
    instructor_btn.click()
    wait.until(EC.presence_of_element_located((By.ID, "name")))
    # Llenar el formulario con el nombre vacío
    driver.find_element(By.ID, "name").send_keys("")
    driver.find_element(By.ID, "institution").send_keys("Universidad Nacional de San Agustín de Arequipa")
    driver.find_element(By.ID, "country").send_keys("Perú")
    driver.find_element(By.ID, "email").send_keys("jose@unsa.edu.pe")
    driver.find_element(By.ID, "comments").send_keys("")
    driver.find_element(By.XPATH, "//button[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')]" ).click()
    # Esperar los mensajes de error por campo obligatorio faltante
    try:
        wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'please enter your name')]")))
        wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'there was a problem with your submission')]")))
        error_found = True
    except Exception:
        print('No se encontraron los mensajes de error esperados. HTML actual:')
        print(driver.page_source)
        error_found = False
    assert error_found, "No se mostraron los mensajes de error por campos obligatorios faltantes"


@pytest.mark.usefixtures("driver")
def test_cp_01_04_register_name_too_long(driver):
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    # Realizar login primero
    import os
    LOGIN_EMAIL = os.environ.get("LOGIN_EMAIL")
    LOGIN_PASSWORD = os.environ.get("LOGIN_PASSWORD")
    assert LOGIN_EMAIL, "No se encontró la variable de entorno LOGIN_EMAIL"
    assert LOGIN_PASSWORD, "No se encontró la variable de entorno LOGIN_PASSWORD"
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión correctamente"
    wait = WebDriverWait(driver, 15)
    # Click directo al icono de Teammates usando el selector validado
    try:
        icon = wait.until(EC.element_to_be_clickable((By.XPATH, "//img[contains(@src, 'logo')]")))
        icon.click()
    except Exception:
        assert False, "No se pudo hacer click en el icono de Teammates"
    # Continuar con el flujo de registro fallido
    driver.get(REGISTRATION_URL)
    time.sleep(2)
    request_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'request a free instructor account')]")))
    request_btn.click()
    instructor_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'i am an instructor')]")))
    instructor_btn.click()
    wait.until(EC.presence_of_element_located((By.ID, "name")))
    # Llenar el formulario con nombre de 256 caracteres
    long_name = "A" * 256
    driver.find_element(By.ID, "name").send_keys(long_name)
    driver.find_element(By.ID, "institution").send_keys("Universidad Nacional de San Agustín de Arequipa")
    driver.find_element(By.ID, "country").send_keys("Perú")
    driver.find_element(By.ID, "email").send_keys("jose@unsa.edu.pe")
    driver.find_element(By.ID, "comments").send_keys("")
    driver.find_element(By.XPATH, "//button[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')]" ).click()
    # Esperar los mensajes de error por longitud de nombre
    try:
        wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'name must be shorter than 100 characters')]")))
        wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'there was a problem with your submission')]")))
        error_found = True
    except Exception:
        print('No se encontraron los mensajes de error esperados. HTML actual:')
        print(driver.page_source)
        error_found = False
    assert error_found, "No se mostraron los mensajes de error por longitud de nombre"

@pytest.mark.usefixtures("driver")
def test_cp_01_05_register_invalid_email_format(driver):
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    # Realizar login primero
    import os
    LOGIN_EMAIL = os.environ.get("LOGIN_EMAIL")
    LOGIN_PASSWORD = os.environ.get("LOGIN_PASSWORD")
    assert LOGIN_EMAIL, "No se encontró la variable de entorno LOGIN_EMAIL"
    assert LOGIN_PASSWORD, "No se encontró la variable de entorno LOGIN_PASSWORD"
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión correctamente"
    wait = WebDriverWait(driver, 15)
    # Click directo al icono de Teammates usando el selector validado
    try:
        icon = wait.until(EC.element_to_be_clickable((By.XPATH, "//img[contains(@src, 'logo')]")))
        icon.click()
    except Exception:
        assert False, "No se pudo hacer click en el icono de Teammates"
    # Continuar con el flujo de registro fallido
    driver.get(REGISTRATION_URL)
    time.sleep(2)
    request_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'request a free instructor account')]")))
    request_btn.click()
    instructor_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'i am an instructor')]")))
    instructor_btn.click()
    wait.until(EC.presence_of_element_located((By.ID, "name")))
    # Llenar el formulario con e-mail inválido
    driver.find_element(By.ID, "name").send_keys("Jorge")
    driver.find_element(By.ID, "institution").send_keys("UNSA")
    driver.find_element(By.ID, "country").send_keys("Perú")
    driver.find_element(By.ID, "email").send_keys("jorgeunsa.edu.pe")
    driver.find_element(By.ID, "comments").send_keys("")
    driver.find_element(By.XPATH, "//button[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')]" ).click()
    # Esperar y verificar que el campo de e-mail se marque en rojo (clase is-invalid)
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='email' and contains(@class, 'is-invalid')]")))
        error_found = True
    except Exception:
        print('No se encontró el campo de e-mail marcado en rojo. HTML actual:')
        print(driver.page_source)
        error_found = False
    assert error_found, "El campo de e-mail no se marcó como inválido para formato incorrecto"