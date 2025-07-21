from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

# CP-07-01
def test_cp_07_01_recover_links_valid_email_valid_captcha_recent_sessions(driver):
    """
    CP-07-01: Recuperar enlaces con correo válido, CAPTCHA válido y sesiones recientes

    Objetivo:
        Verificar que el sistema envía enlaces activos cuando todas las condiciones son válidas

    Técnica utilizada:
        Tabla de decisión (Regla R1)

    Datos de prueba:
        - Email: usuario@ejemplo.com
        - CAPTCHA: correcto
        - Usuario con sesiones en últimos 90 días

    Resultado esperado:
        El sistema confirma en pantalla y envía al correo los enlaces activos (últimos 90 días)
    """

    driver.get("https://teammatesv4.appspot.com/web/front/help/session-links-recovery")

    
    
# CP-07-02
def test_cp_07_02_recover_links_valid_email_valid_captcha_no_recent_sessions(driver):
    """
    CP-07-02: Recuperar enlaces con correo válido, CAPTCHA válido y sin sesiones recientes

    Objetivo:
        Verificar que el sistema informa adecuadamente cuando no hay sesiones recientes

    Técnica utilizada:
        Tabla de decisión (Regla R2)

    Datos de prueba:
        - Email: usuario@ejemplo.com
        - CAPTCHA: correcto
        - Usuario sin sesiones en últimos 90 días

    Resultado esperado:
        El sistema confirma en pantalla y envía correo indicando que no hay sesiones recientes
    """

    driver.get("https://teammatesv4.appspot.com/web/front/help/session-links-recovery")

# CP-07-03
def test_cp_07_03_recover_links_valid_email_invalid_captcha(driver):
    """
    CP-07-03: Intentar recuperar enlaces con correo válido y CAPTCHA inválido

    Objetivo:
        Verificar que el sistema valida correctamente el CAPTCHA

    Técnica utilizada:
        Tabla de decisión (Regla R3)

    Datos de prueba:
        - Email: usuario@ejemplo.com
        - CAPTCHA: incorrecto
        - Usuario registrado en el sistema

    Resultado esperado:
        El sistema muestra un mensaje de error: "CAPTCHA inválido"
    """


# CP-07-04
def test_cp_07_04_recover_links_unregistered_email_valid_captcha(driver):
    """
    CP-07-04: Intentar recuperar enlaces con correo no registrado y CAPTCHA válido

    Objetivo:
        Verificar que el sistema valida la existencia del correo en el sistema

    Técnica utilizada:
        Tabla de decisión (Regla R4)

    Datos de prueba:
        - Email: noexiste@ejemplo.com
        - CAPTCHA: correcto
        - Correo no existe en base de datos

    Resultado esperado:
        El sistema muestra un mensaje de error: "Correo no registrado"
    """


# CP-07-05
def test_cp_07_05_recover_links_unregistered_email_invalid_captcha(driver):
    """
    CP-07-05: Intentar recuperar enlaces con correo no registrado y CAPTCHA inválido

    Objetivo:
        Verificar que el sistema maneja múltiples errores de validación

    Técnica utilizada:
        Tabla de decisión (Regla R5)

    Datos de prueba:
        - Email: noexiste@ejemplo.com
        - CAPTCHA: incorrecto
        - Correo no existe en base de datos

    Resultado esperado:
        El sistema muestra un mensaje de error: "Correo no registrado y CAPTCHA inválido"
    """
