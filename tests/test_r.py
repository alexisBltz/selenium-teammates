from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

# CP-06-01a
def test_cp_06_01a_case_insensitive_search(driver):
    """
    CP-06-01a: Búsqueda exacta insensible a mayúsculas/minúsculas

    Objetivo:
        Confirmar que mayúsculas/minúsculas no afectan la búsqueda exacta

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - Usuario instructor autenticado
        - Estudiante "Juan Pérez" registrado

    Entradas:
        "juan pérez", "JUAN PÉREZ"

    Resultado esperado:
        Solo "Juan Pérez" aparece con todos sus datos en ambos casos
    """

    wait = WebDriverWait(driver, 10)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/search")
    time.sleep(2)

    nombre_real = 'Juan Pérez'
    nombres_prueba = ['\"JUAN PÉREZ\"', '\"juan pérez\"']

    for nombre_input in nombres_prueba:
        # Buscar el nombre con distinta capitalización
        search_input = wait.until(EC.presence_of_element_located((By.ID, "search-keyword")))
        search_input.clear()
        search_input.send_keys(nombre_input)

        search_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-search")))
        search_button.click()
        time.sleep(3)

        try:
            nombre_td = wait.until(EC.presence_of_element_located((
                By.XPATH, "//table//tbody//tr/td[3]"
            )))

            nombre_encontrado = nombre_td.text.strip()

            assert nombre_encontrado.lower() == nombre_real.lower(), (
                f"[X] Se encontró '{nombre_encontrado}' al buscar '{nombre_input}', "
                f"pero se esperaba '{nombre_real}'."
            )
            print(f"\t[!] Éxito CP-06-01a: Búsqueda con '{nombre_input}' exitosa. Nombre encontrado: '{nombre_encontrado}'")

        except TimeoutException:
            raise AssertionError(
                f"\t[!] CP-06-01a: No se encontró el nombre '{nombre_real}' al buscar '{nombre_input}'."
            )

        time.sleep(0.5)

    print(f"[✓] Éxito CP-06-01a: Ambos nombres fueron encontrados.'")
    