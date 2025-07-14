
import pytest
import os
from dotenv import load_dotenv
from pages.login_page import LoginPage

load_dotenv()
LOGIN_EMAIL = os.getenv("LOGIN_EMAIL")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD")

@pytest.mark.usefixtures("driver")
def test_cp_02_01_login_success(driver):
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD)
    assert page.is_logged_in()

@pytest.mark.usefixtures("driver")
def test_cp_02_02_login_denied_unregistered(driver):
    # Usar credenciales de cuenta no registrada
    email = "ehilacondob@unsa.edu.pe"
    password = "12345678"  # Puedes ajustar el password si hay una política específica
    page = LoginPage(driver)
    page.login(email, password)
    # Validar que no se ingresa al módulo del instructor
    assert not page.is_logged_in(), "El sistema permitió el ingreso con cuenta no registrada"