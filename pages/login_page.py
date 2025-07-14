from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
class LoginPage:
    def __init__(self, driver):
        self.driver = driver

    # CP-02-01: Inicio de sesión exitoso con cuenta registrada
    def login(self, email, password, user_type="student"):
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        self.driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/front/home")
        wait = WebDriverWait(self.driver, 15)
        # Hacer clic en el botón Login de la barra superior
        login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'login')]")))
        login_btn.click()
        if user_type == "instructor":
            # Hacer clic en 'Instructor Login' del menú desplegable
            instructor_login = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'instructor login')]")))
            instructor_login.click()
        else:
            # Hacer clic en 'Student Login' del menú desplegable
            student_login = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'student login')]")))
            student_login.click()
        # Esperar redirección a Google
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='email']")))
        self.driver.find_element(By.XPATH, "//input[@type='email']").send_keys(email)
        # Esperar y hacer clic en el botón 'Siguiente' (puede ser <span> o <button>)
        next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[self::span or self::button][contains(text(), 'Siguiente')]")))
        next_btn.click()
        # Esperar campo de contraseña
        password_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='password']")))
        while not password_input.is_enabled():
            time.sleep(0.1)
        password_input.send_keys(password)
        next_btn2 = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[self::span or self::button][contains(text(), 'Siguiente')]")))
        next_btn2.click()
        # Esperar y hacer clic en el botón final de 'Iniciar sesión' si aparece
        try:
            final_login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[self::span or self::button][contains(text(), 'Iniciar sesión')]")))
            final_login_btn.click()
        except Exception:
            pass  # Si no aparece, continuar normalmente
        for _ in range(30):
            if self.is_logged_in(user_type):
                break
            time.sleep(1)
        if self.is_logged_in(user_type):
            time.sleep(1)
            from selenium.webdriver.common.action_chains import ActionChains
            body = self.driver.find_element(By.TAG_NAME, "body")
            ActionChains(self.driver).move_to_element(body).click().send_keys(Keys.ESCAPE).perform()

    # CP-02-01: Verifica si el login fue exitoso
    def is_logged_in(self, user_type="student"):
        # Verifica si el login fue exitoso buscando el módulo o el texto correspondiente
        if user_type == "instructor":
            if self.driver.find_elements(By.ID, "instructor-module"):
                return True
            try:
                home_element = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Home')]")
                return home_element.is_displayed()
            except Exception:
                return False
        else:
            try:
                student_home_element = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Student Home')]")
                return student_home_element.is_displayed()
            except Exception:
                return False
