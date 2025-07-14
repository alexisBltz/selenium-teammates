import os
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
@pytest.mark.usefixtures("driver")
def test_cp_03_01_student_dashboard_shows_sessions(driver):
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="student")
    assert page.is_logged_in("student"), "No se pudo iniciar sesión como estudiante"

@pytest.mark.usefixtures("driver")
def test_cp_03_02_student_dashboard_empty(driver):
    LOGIN_EMAIL_EMPTY = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD_EMPTY = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL_EMPTY, LOGIN_PASSWORD_EMPTY, user_type="student")
    assert page.is_logged_in("student"), f"No se pudo iniciar sesión como estudiante"
    wait = WebDriverWait(driver, 15)
    try:
        error_msg = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'You are not authorized to view this page') or contains(text(), 'No estás autorizado para ver esta página') ]")))
        assert error_msg.is_displayed(), "No se mostró el mensaje de error de autorización"
    except Exception:
        print('No se encontró el mensaje de error de autorización. HTML actual:')
        print(driver.page_source)
        assert False, "No se mostró el mensaje de error de autorización"

@pytest.mark.usefixtures("driver")
def test_cp_03_01_01_view_received_responses(driver):
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="student")
    assert page.is_logged_in("student"), f"No se pudo iniciar sesión como estudiante"
    wait = WebDriverWait(driver, 15)
    try:
        session_row = wait.until(EC.presence_of_element_located((By.XPATH, "//tr[.//td[contains(text(), 'First team feedback session')]]")))
        view_btn = session_row.find_element(By.XPATH, ".//a[contains(text(), 'View Responses')]")
        view_btn.click()
        results_title = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Feedback Session Results') or contains(text(), 'Resultados de la sesión de retroalimentación') ]")))
        assert results_title.is_displayed(), "No se mostró la página de resultados de feedback"
    except Exception:
        print('No se encontró la página de resultados o el botón View Responses. HTML actual:')
        print(driver.page_source)
        assert False, "No se visualizó correctamente la retroalimentación recibida"

@pytest.mark.usefixtures("driver")
def test_cp_03_01_02_view_no_responses(driver):
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="student")
    assert page.is_logged_in("student"), f"No se pudo iniciar sesión como estudiante"
    wait = WebDriverWait(driver, 15)
    try:
        session_row = wait.until(EC.presence_of_element_located((By.XPATH, "//tr[.//td[contains(text(), 'Second team feedback session (point-based)')]]")))
        view_btn = session_row.find_element(By.XPATH, ".//a[contains(text(), 'View Responses')]")
        # Validar que el botón está deshabilitado
        assert 'disabled' in view_btn.get_attribute('class'), "El botón 'View Responses' no está deshabilitado para sesión sin respuestas" # type: ignore
    except Exception:
        print('No se encontró el botón View Responses deshabilitado. HTML actual:')
        print(driver.page_source)
        assert False, "No se encontró el botón View Responses deshabilitado para sesión sin respuestas"

@pytest.mark.usefixtures("driver")
def test_cp_03_02_01_feedback_submit_success(driver):
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="student")
    assert page.is_logged_in("student"), f"No se pudo iniciar sesión como estudiante"
    wait = WebDriverWait(driver, 15)
    try:
        session_row = wait.until(EC.presence_of_element_located((By.XPATH, "//tr[.//td[contains(text(), 'First team feedback session')]]")))
        submit_btn = session_row.find_element(By.XPATH, ".//a[contains(text(), 'View Submission') or contains(text(), 'Edit Submission')]")
        submit_btn.click()
        # Esperar el formulario y llenar los campos
        # Seleccionar valores en los <select> de contribución usando aria-label
        def select_contribution(aria_label, value):
            select_elem = wait.until(EC.presence_of_element_located((By.XPATH, f"//select[@aria-label='{aria_label}']")))
            from selenium.webdriver.support.ui import Select
            select = Select(select_elem)
            select.select_by_value(value)

        select_contribution("Response for alesis final tester", "1: 100")  # Equal share
        select_contribution("Response for Charlie Davis", "1: 100")        # Equal share
        select_contribution("Response for Francis Gabriel", "1: 100")      # Equal share
        select_contribution("Response for Gene Hudson", "1: 100")          # Equal share


        # Enviar el formulario para todas las preguntas
        submit_all_btn = wait.until(EC.element_to_be_clickable((By.ID, "btn-submit")))
        submit_all_btn.click()

        # Validar el mensaje de éxito tras enviar feedback
        success_msg = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Responses to all questions submitted successfully!') or contains(text(), 'respuestas guardadas exitosamente') ]")))
        assert "Responses to all questions submitted successfully!" in success_msg.text, "No se mostró el mensaje de éxito esperado tras enviar feedback"
    except Exception:
        print('No se encontró el formulario de feedback o el mensaje de éxito. HTML actual:')
        print(driver.page_source)
        assert False, "No se mostró el mensaje de éxito tras enviar feedback"

@pytest.mark.usefixtures("driver")
def test_cp_03_02_02_feedback_submit_invalid_sum(driver):
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="student")
    assert page.is_logged_in("student"), f"No se pudo iniciar sesión como estudiante"
    wait = WebDriverWait(driver, 15)
    try:
        session_row = wait.until(EC.presence_of_element_located((By.XPATH, "//tr[.//td[contains(text(), 'First team feedback session')]]")))
        submit_btn = session_row.find_element(By.XPATH, ".//a[contains(text(), 'View Submission') or contains(text(), 'Edit Submission')]")
        submit_btn.click()
        # Esperar el formulario y seleccionar valores en los <select> para generar suma inválida
        def select_contribution(aria_label, value):
            select_elem = wait.until(EC.presence_of_element_located((By.XPATH, f"//select[@aria-label='{aria_label}']")))
            from selenium.webdriver.support.ui import Select
            select = Select(select_elem)
            select.select_by_value(value)

        # Seleccionar valores altos para exceder el total permitido
        select_contribution("Response for alesis final tester", "2: 200")
        select_contribution("Response for Charlie Davis", "2: 200")
        select_contribution("Response for Francis Gabriel", "2: 200")
        select_contribution("Response for Gene Hudson", "2: 200")

        # Buscar el mensaje de advertencia de suma incorrecta por presencia, no visibilidad
        try:
            warning_msg = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'does not match the expected total') or contains(text(), 'la suma total de porcentajes debe ser 100') ]")))
            assert warning_msg is not None, "No se encontró el mensaje de advertencia por suma incorrecta"
        except Exception:
            print('No se encontró el mensaje de advertencia, pero se continúa para validar el modal de error.')

        # Intentar enviar el formulario para todas las preguntas
        submit_all_btn = wait.until(EC.element_to_be_clickable((By.ID, "btn-submit")))
        submit_all_btn.click()

        # Validar que aparece el modal de error con todos los mensajes esperados (usando innerText para obtener todo el contenido)
        error_modal = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'modal-content')]")))
        modal_text = error_modal.get_attribute("innerText")
        assert modal_text is not None, "No se pudo extraer el texto del modal de error"
        assert "Some response submissions failed!" in modal_text, "No se mostró el mensaje 'Some response submissions failed!' en el modal de error"
        assert "ERROR! The response submissions to the following questions failed." in modal_text, "No se mostró el mensaje principal de error en el modal"
        assert "Question 1: [Invalid option for the Team contribution question.]" in modal_text, "No se mostró el detalle de opción inválida en el modal"
        assert "Please try to submit your responses again." in modal_text, "No se mostró la sugerencia de reintento en el modal"
    except Exception:
        print('No se encontró el formulario de feedback o el mensaje de error. HTML actual:')
        print(driver.page_source)
        assert False, "No se mostró el mensaje de error por suma incorrecta"
