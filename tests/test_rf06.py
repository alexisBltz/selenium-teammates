from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

# CP-06-01
def test_cp_06_01_exact_name_search(driver):
    """
    CP-06-01: Búsqueda exacta por nombre completo

    Objetivo:
        Buscar estudiante por coincidencia exacta de nombre

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - Usuario instructor autenticado
        - Estudiante "Juan Pérez" registrado

    Entrada:
        "Juan Pérez"

    Resultado esperado:
        Solo "Juan Pérez" aparece con todos sus datos (nombre completo, correo, ID, etc.)
    """

    wait = WebDriverWait(driver, 10)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/search")
    time.sleep(2)

    objetivo = '\"Juan Pérez\"'
    nombre_buscado = 'Juan Pérez'

    # 1. Escribir en el input de búsqueda
    search_input = wait.until(EC.presence_of_element_located((By.ID, "search-keyword")))
    search_input.clear()
    search_input.send_keys(objetivo)

    # 2. Clic en el botón de búsqueda
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-search")))
    search_button.click()
    time.sleep(3)

    # 3. Verificar que aparece exactamente el nombre esperado
    try:
        nombre_td = wait.until(EC.presence_of_element_located((
            By.XPATH, "//table//tbody//tr/td[3]"
        )))

        nombre_encontrado = nombre_td.text.strip()
        assert nombre_encontrado == nombre_buscado, f"[X] Se encontró '{nombre_encontrado}', pero se esperaba '{nombre_buscado}'."
        print(f"[✓] Éxito CP-06-01: El nombre encontrado '{nombre_encontrado}', coincide con el buscado '{nombre_buscado}'.")

    except TimeoutException:
        raise AssertionError(f"[X] CP-06-01: No se encontró el nombre exacto '{nombre_buscado}' en los resultados.")

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


# CP-06-01b
def test_cp_06_01b_accent_insensitive_search(driver):
    """
    CP-06-01b: Búsqueda exacta con/sin tildes

    Objetivo:
        Verificar que la búsqueda encuentra nombres con o sin tildes

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - Usuario instructor autenticado
        - Estudiante "Luis Ángel" registrado

    Entrada:
        "Luis Angel"

    Resultado esperado:
        Solo "Luis Ángel" aparece con todos sus datos, a pesar de la falta de tilde
    """

    wait = WebDriverWait(driver, 10)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/search")
    time.sleep(2)

    nombre_objetivo = "Luis Ángel"
    nombre_buscado = "Luis Angel"

    # 1. Escribir en el input de búsqueda
    search_input = wait.until(EC.presence_of_element_located((By.ID, "search-keyword")))
    search_input.clear()
    search_input.send_keys(nombre_buscado)

    # 2. Clic en el botón de búsqueda
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-search")))
    search_button.click()
    time.sleep(3)

    # 3. Verificar que aparece exactamente el nombre esperado
    try:
        nombre_td = wait.until(EC.presence_of_element_located((
            By.XPATH, "//table//tbody//tr/td[3]"
        )))

        nombre_encontrado = nombre_td.text.strip()
        assert nombre_encontrado == nombre_objetivo, f"[X] CP-06-01b: Se encontró '{nombre_encontrado}', pero se esperaba '{nombre_objetivo}'."
        print(f"[✓] Éxito CP-06-01b: El nombre encontrado '{nombre_encontrado}' coincide con el esperado '{nombre_objetivo}'.")

    except TimeoutException:
        raise AssertionError(f"[X] CP-06-01b: No se encontró el nombre '{nombre_objetivo}' en los resultados.")


# CP-06-01c
def test_cp_06_01c_search_with_trailing_spaces(driver):
    """
    CP-06-01c: Búsqueda exacta con espacios antes/después

    Objetivo:
        Verificar que espacios extra son ignorados en la búsqueda exacta

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - Usuario instructor autenticado
        - Estudiante "Juan Pérez" registrado

    Entrada:
        " Juan Pérez ", "Juan Pérez ", " Juan Pérez"

    Resultado esperado:
        Solo "Juan Pérez" aparece con todos sus datos, ignorando los espacios adicionales
    """

    wait = WebDriverWait(driver, 10)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/search")
    time.sleep(2)

    nombre_objetivo = "Luis Ángel"
    nombre_buscado = "  Luis  Angel    "

    # 1. Escribir en el input de búsqueda
    search_input = wait.until(EC.presence_of_element_located((By.ID, "search-keyword")))
    search_input.clear()
    search_input.send_keys(nombre_buscado)

    # 2. Clic en el botón de búsqueda
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-search")))
    search_button.click()
    time.sleep(3)

    # 3. Verificar que aparece exactamente el nombre esperado
    try:
        nombre_td = wait.until(EC.presence_of_element_located((
            By.XPATH, "//table//tbody//tr/td[3]"
        )))

        nombre_encontrado = nombre_td.text.strip()
        assert nombre_encontrado == nombre_objetivo, f"[X] CP-06-01c: Se encontró '{nombre_encontrado}', pero se esperaba '{nombre_objetivo}'."
        print(f"[✓] Éxito CP-06-01c: El nombre encontrado '{nombre_encontrado}' coincide con el esperado '{nombre_objetivo}'.")

    except TimeoutException:
        raise AssertionError(f"[X] CP-06-01c: No se encontró el nombre '{nombre_objetivo}' en los resultados.")
    

# CP-06-01d
def test_cp_06_01d_single_character_search(driver):
    """
    CP-06-01d: Búsqueda con un solo carácter válido

    Objetivo:
        Verificar que el sistema acepta búsquedas con un solo carácter como límite mínimo válido

    Técnica utilizada:
        Análisis de Valores Límite

    Datos de prueba:
        - Sistema disponible
        - Usuario autenticado
        - Estudiantes registrados en el sistema

    Entrada:
        Texto de búsqueda: "A"

    Resultado esperado:
        Muestra todos los registros que contengan "A"
    """

    wait = WebDriverWait(driver, 10)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/search")
    time.sleep(2)

    objetivo = "A"

    # 1. Escribir en el input de búsqueda
    search_input = wait.until(EC.presence_of_element_located((By.ID, "search-keyword")))
    search_input.clear()
    search_input.send_keys(objetivo)

    # 2. Clic en el botón de búsqueda
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-search")))
    search_button.click()
    time.sleep(3)

    # 3. Contar los resultados con A
    try:
        filas = wait.until(EC.presence_of_all_elements_located((
            By.XPATH, "//table//tbody//tr"
        )))
        cantidad = len(filas)
        assert cantidad > 0, "[X] CP-06-01d: No se encontraron resultados en la tabla."
        print(f"[✓] Éxito CP-06-01d: Se encontraron {cantidad} resultados en la búsqueda con '{objetivo}'.")
    except TimeoutException:
        raise AssertionError("[X] CP-06-01d: No se encontraron resultados tras la búsqueda.")
    

# CP-06-02
def test_cp_06_02_partial_keyword_search_name(driver):
    """
    CP-06-02: Búsqueda por palabra clave parcial (nombre)

    Objetivo:
        Buscar estudiantes que contengan el fragmento en nombre

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - Instructor autenticado
        - Varios estudiantes con "Juan" registrados

    Entrada:
        "Juan"

    Resultado esperado:
        Todos los estudiantes con "Juan" en campos buscables aparecen listados
    """

    wait = WebDriverWait(driver, 10)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/search")
    time.sleep(2)

    objetivo = "Juan"

    # 1. Escribir en el input de búsqueda
    search_input = wait.until(EC.presence_of_element_located((By.ID, "search-keyword")))
    search_input.clear()
    search_input.send_keys(objetivo)

    # 2. Clic en el botón de búsqueda
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-search")))
    search_button.click()
    time.sleep(3)

    # 3. Contar los resultados con A
    try:
        filas = wait.until(EC.presence_of_all_elements_located((
            By.XPATH, "//table//tbody//tr"
        )))
        cantidad = len(filas)
        assert cantidad > 0, "[X] CP-06-02: No se encontraron resultados en la tabla."
        print(f"[✓] Éxito CP-06-02: Se encontraron {cantidad} coincidencas en la búsqueda con el nombre '{objetivo}'.")
    except TimeoutException:
        raise AssertionError("[X] CP-06-02: No se encontraron resultados tras la búsqueda.")


# CP-06-02a
def test_cp_06_02a_partial_keyword_search_section(driver):
    """
    CP-06-02a: Búsqueda por palabra clave parcial (sección)

    Objetivo:
        Buscar estudiantes por fragmento en el nombre de la sección

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - Instructor autenticado
        - Sección "A" registrada

    Entrada:
        "A"

    Resultado esperado:
        Todos los estudiantes de la sección "A" aparecen listados
    """

    wait = WebDriverWait(driver, 10)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/search")
    time.sleep(2)

    objetivo = "A"

    # 1. Escribir en el input de búsqueda
    search_input = wait.until(EC.presence_of_element_located((By.ID, "search-keyword")))
    search_input.clear()
    search_input.send_keys(objetivo)

    # 2. Clic en el botón de búsqueda
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-search")))
    search_button.click()
    time.sleep(3)

    # 3. Contar los resultados con A
    try:
        filas = wait.until(EC.presence_of_all_elements_located((
            By.XPATH, "//table//tbody//tr"
        )))
        cantidad = len(filas)
        assert cantidad > 0, "[X] CP-06-02a: No se encontraron resultados en la tabla."
        print(f"[✓] Éxito CP-06-02a: Se encontraron {cantidad} coincidencas en la búsqueda con el nombre '{objetivo}'.")
    except TimeoutException:
        raise AssertionError("[X] CP-06-02a: No se encontraron resultados tras la búsqueda.")
    

# CP-06-02b
def test_cp_06_02b_partial_keyword_search_team(driver):
    """
    CP-06-02b: Búsqueda por palabra clave parcial (equipo)

    Objetivo:
        Buscar estudiantes por fragmento en el nombre del equipo

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - Instructor autenticado
        - Equipo "Tiburones"

    Entrada:
        "Tiburones"

    Resultado esperado:
        Todos los estudiantes del equipo "Tiburones" aparecen listados
    """

    wait = WebDriverWait(driver, 10)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/search")
    time.sleep(2)

    objetivo = "Tiburones"

    # 1. Escribir en el input de búsqueda
    search_input = wait.until(EC.presence_of_element_located((By.ID, "search-keyword")))
    search_input.clear()
    search_input.send_keys(objetivo)

    # 2. Clic en el botón de búsqueda
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-search")))
    search_button.click()
    time.sleep(3)

    # 3. Contar los resultados con A
    try:
        filas = wait.until(EC.presence_of_all_elements_located((
            By.XPATH, "//table//tbody//tr"
        )))
        cantidad = len(filas)
        assert cantidad > 0, "[X] CP-06-02b: No se encontraron resultados en la tabla."
        print(f"[✓] Éxito CP-06-02b: Se encontraron {cantidad} coincidencas en la búsqueda con el nombre '{objetivo}'.")
    except TimeoutException:
        raise AssertionError("[X] CP-06-02b: No se encontraron resultados tras la búsqueda.")
    

# CP-06-02c
def test_cp_06_02c_partial_keyword_search_email(driver):
    """
    CP-06-02c: Búsqueda por palabra clave parcial (correo)

    Objetivo:
        Buscar estudiantes por fragmento en el correo electrónico

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - Instructor autenticado
        - Correo con dominio "@unsa.edu.pe"

    Entrada:
        "unsa.edu.pe"

    Resultado esperado:
        Todos los estudiantes con correo "@unsa.edu.pe" aparecen listados
    """

    wait = WebDriverWait(driver, 10)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/search")
    time.sleep(2)

    objetivo = "@unsa.edu.pe"

    # 1. Escribir en el input de búsqueda
    search_input = wait.until(EC.presence_of_element_located((By.ID, "search-keyword")))
    search_input.clear()
    search_input.send_keys(objetivo)

    # 2. Clic en el botón de búsqueda
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-search")))
    search_button.click()
    time.sleep(3)

    # 3. Contar los resultados con A
    try:
        filas = wait.until(EC.presence_of_all_elements_located((
            By.XPATH, "//table//tbody//tr"
        )))
        cantidad = len(filas)
        assert cantidad > 0, "[X] CP-06-02b: No se encontraron resultados en la tabla."
        print(f"[✓] Éxito CP-06-02b: Se encontraron {cantidad} coincidencas en la búsqueda con el nombre '{objetivo}'.")
    except TimeoutException:
        raise AssertionError("[X] CP-06-02b: No se encontraron resultados tras la búsqueda.")

# CP-06-02d
def test_cp_06_02d_combined_search_section_team(driver):
    """
    CP-06-02d: Búsqueda combinada por sección/equipo

    Objetivo:
        Filtrar por varias palabras clave en distintos campos

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - Estudiantes en sección "A"
        - Estudiantes en equipo "Tiburones"

    Entrada:
        "A Tiburones"

    Resultado esperado:
        Solo estudiantes de sección A y equipo Tiburones aparecen listados
    """

    wait = WebDriverWait(driver, 10)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/search")
    time.sleep(2)

    objetivo = "A Tiburones"

    # 1. Escribir en el input de búsqueda
    search_input = wait.until(EC.presence_of_element_located((By.ID, "search-keyword")))
    search_input.clear()
    search_input.send_keys(objetivo)

    # 2. Clic en el botón de búsqueda
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-search")))
    search_button.click()
    time.sleep(3)

    # 3. Contar los resultados con A
    try:
        filas = wait.until(EC.presence_of_all_elements_located((
            By.XPATH, "//table//tbody//tr"
        )))
        cantidad = len(filas)
        assert cantidad > 0, "[X] CP-06-02b: No se encontraron resultados en la tabla."
        print(f"[✓] Éxito CP-06-02b: Se encontraron {cantidad} coincidencas en la búsqueda con el nombre '{objetivo}'.")
    except TimeoutException:
        raise AssertionError("[X] CP-06-02b: No se encontraron resultados tras la búsqueda.")
    

# CP-06-03
def test_cp_06_03_exact_email_search(driver):
    """
    CP-06-03: Búsqueda por correo electrónico exacto

    Objetivo:
        Buscar por coincidencia exacta de correo electrónico

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - "carlos.rosas@unsa.edu.pe" registrado

    Entrada:
        "carlos.rosas@unsa.edu.pe"

    Resultado esperado:
        Solo "Carlos Rosas" aparece
    """

    wait = WebDriverWait(driver, 10)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/search")
    time.sleep(2)

    objetivo = "carlos.rosas@unsa.edu.pe"

    # 1. Escribir en el input de búsqueda
    search_input = wait.until(EC.presence_of_element_located((By.ID, "search-keyword")))
    search_input.clear()
    search_input.send_keys(objetivo)

    # 2. Clic en el botón de búsqueda
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-search")))
    search_button.click()
    time.sleep(3)

    # 3. Contar los resultados (debería haber solo uno)
    try:
        filas = wait.until(EC.presence_of_all_elements_located((
            By.XPATH, "//table//tbody//tr"
        )))
        cantidad = len(filas)
        assert cantidad == 1, f"[X] CP-06-03: Se esperaban 1 coincidencia, pero se encontraron {cantidad}."
        print(f"[✓] Éxito CP-06-03: Se encontró exactamente una coincidencia para el correo '{objetivo}'.")
    except TimeoutException:
        raise AssertionError("[X] CP-06-03: No se encontraron resultados tras la búsqueda.")


# CP-06-03a
def test_cp_06_03a_email_search_with_whitespace(driver):
    """
    CP-06-03a: Búsqueda por correo con espacios antes/después

    Objetivo:
        Verificar que espacios extra son ignorados en la búsqueda por correo exacto

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - "carlos.rosas@unsa.edu.pe" registrado

    Entrada:
        "  carlos.rosas@unsa.edu.pe  "

    Resultado esperado:
        Solo "Carlos Rosas" aparece
    """

    wait = WebDriverWait(driver, 10)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/search")
    time.sleep(2)

    objetivo = "    carlos.rosas@unsa.edu.pe    "

    # 1. Escribir en el input de búsqueda
    search_input = wait.until(EC.presence_of_element_located((By.ID, "search-keyword")))
    search_input.clear()
    search_input.send_keys(objetivo)

    # 2. Clic en el botón de búsqueda
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-search")))
    search_button.click()
    time.sleep(3)

    # 3. Contar los resultados (debería haber solo uno)
    try:
        filas = wait.until(EC.presence_of_all_elements_located((
            By.XPATH, "//table//tbody//tr"
        )))
        cantidad = len(filas)
        assert cantidad == 1, f"[X] CP-06-03a: Se esperaban 1 coincidencia, pero se encontraron {cantidad}."
        print(f"[✓] Éxito CP-06-03a: Se encontró exactamente una coincidencia para el correo '{objetivo}' (con espacios).")
    except TimeoutException:
        raise AssertionError("[X] CP-06-03a: No se encontraron resultados tras la búsqueda.")


# CP-06-03b
def test_cp_06_03b_partial_email_fragment_search(driver):
    """
    CP-06-03b: Búsqueda por fragmento de correo

    Objetivo:
        Buscar estudiantes por fragmento de correo electrónico

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - "carlos.rosas@unsa.edu.pe" registrado

    Entrada:
        "rosas"

    Resultado esperado:
        Todos los estudiantes con "rosas" en el correo aparecen
    """

    wait = WebDriverWait(driver, 10)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/search")
    time.sleep(2)

    objetivo = '\"rosas\"'

    # 1. Escribir en el input de búsqueda
    search_input = wait.until(EC.presence_of_element_located((By.ID, "search-keyword")))
    search_input.clear()
    search_input.send_keys(objetivo)

    # 2. Clic en el botón de búsqueda
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-search")))
    search_button.click()
    time.sleep(3)

    # 3. Contar los resultados con A
    try:
        filas = wait.until(EC.presence_of_all_elements_located((
            By.XPATH, "//table//tbody//tr"
        )))
        cantidad = len(filas)
        assert cantidad > 0, "[X] CP-06-03b: No se encontraron resultados en la tabla."
        print(f"[✓] Éxito CP-06-03b: Se encontraron {cantidad} coincidencas en la búsqueda con el nombre '{objetivo}'.")
    except TimeoutException:
        raise AssertionError("[X] CP-06-03b: No se encontraron resultados tras la búsqueda.")


# CP-06-04
def test_cp_06_04_combined_search_section_team_alt(driver):
    """
    CP-06-04: Búsqueda combinada por sección/equipo diferente

    Objetivo:
        Filtrar por varias palabras clave en distintos campos (otro ejemplo)

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - Estudiantes en sección "B"
        - Estudiantes en equipo "Leones"

    Entrada:
        "B Leones"

    Resultado esperado:
        Solo estudiantes de sección B y equipo Leones aparecen
    """

    wait = WebDriverWait(driver, 10)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/search")
    time.sleep(2)

    objetivo = 'B Leones'

    # 1. Escribir en el input de búsqueda
    search_input = wait.until(EC.presence_of_element_located((By.ID, "search-keyword")))
    search_input.clear()
    search_input.send_keys(objetivo)

    # 2. Clic en el botón de búsqueda
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-search")))
    search_button.click()
    time.sleep(3)

    # 3. Contar los resultados con A
    try:
        filas = wait.until(EC.presence_of_all_elements_located((
            By.XPATH, "//table//tbody//tr"
        )))
        cantidad = len(filas)
        assert cantidad > 0, "[X] CP-06-04: No se encontraron resultados en la tabla."
        print(f"[✓] Éxito CP-06-04: Se encontraron {cantidad} coincidencas en la búsqueda con el nombre '{objetivo}'.")
    except TimeoutException:
        raise AssertionError("[X] CP-06-04: No se encontraron resultados tras la búsqueda.")


# CP-06-05
def test_cp_06_05_exact_phrase_search_with_quotes(driver):
    """
    CP-06-05: Búsqueda exacta usando comillas

    Objetivo:
        Confirmar interpretación de comillas para búsqueda exacta

    Técnica utilizada:
        Valores límite / Decisión

    Datos de prueba:
        - Al menos un estudiante "Luis Ángel"

    Entrada:
        "\"Luis Ángel\""

    Resultado esperado:
        Solo "Luis Ángel", no coincidencias parciales
    """

    wait = WebDriverWait(driver, 10)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/search")
    time.sleep(2)

    objetivo = '\"Luis Ángel\"'

    # 1. Escribir en el input de búsqueda
    search_input = wait.until(EC.presence_of_element_located((By.ID, "search-keyword")))
    search_input.clear()
    search_input.send_keys(objetivo)

    # 2. Clic en el botón de búsqueda
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-search")))
    search_button.click()
    time.sleep(3)

    # 3. Contar los resultados con A
    try:
        filas = wait.until(EC.presence_of_all_elements_located((
            By.XPATH, "//table//tbody//tr"
        )))
        cantidad = len(filas)
        assert cantidad > 0, "[X] CP-06-05: No se encontraron resultados en la tabla."
        print(f"[✓] Éxito CP-06-05: Se encontraron {cantidad} coincidencas en la búsqueda con el nombre '{objetivo}'.")
    except TimeoutException:
        raise AssertionError("[X] CP-06-05: No se encontraron resultados tras la búsqueda.")


# CP-06-05a
def test_cp_06_05a_non_exact_fragment_with_quotes(driver):
    """
    CP-06-05a: Búsqueda exacta con comillas en fragmento no exacto

    Objetivo:
        Verificar que comillas limitan la búsqueda a coincidencias exactas por fragmento

    Técnica utilizada:
        Valores límite / Decisión

    Datos de prueba:
        - Estudiantes registrados: "Luis Ángel", "Luis Angel", "Luis"

    Entrada:
        "\"Luis\""

    Resultado esperado:
        Solo coincidencias exactas, no parciales
    """

    wait = WebDriverWait(driver, 10)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/search")
    time.sleep(2)

    objetivo = '\"Luis\"'

    # 1. Escribir en el input de búsqueda
    search_input = wait.until(EC.presence_of_element_located((By.ID, "search-keyword")))
    search_input.clear()
    search_input.send_keys(objetivo)

    # 2. Clic en el botón de búsqueda
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-search")))
    search_button.click()
    time.sleep(3)

    # 3. Contar los resultados con A
    try:
        filas = wait.until(EC.presence_of_all_elements_located((
            By.XPATH, "//table//tbody//tr"
        )))
        cantidad = len(filas)
        assert cantidad > 0, "[X] CP-06-05a: No se encontraron resultados en la tabla."
        print(f"[✓] Éxito CP-06-05a: Se encontraron {cantidad} coincidencas en la búsqueda con el nombre '{objetivo}'.")
    except TimeoutException:
        raise AssertionError("[X] CP-06-05a: No se encontraron resultados tras la búsqueda.")


# CP-06-06
def test_cp_06_06_search_no_results(driver):
    """
    CP-06-06: Búsqueda sin resultados

    Objetivo:
        Verificar mensajes claros ante búsquedas sin coincidencias

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - No existe “Pepito Grillo”

    Entrada:
        "Pepito Grillo"

    Resultado esperado:
        Mensaje: “No se encontraron resultados”
    """
    wait = WebDriverWait(driver, 10)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/search")
    time.sleep(2)

    objetivo = 'Pepito Grillo'

    # 1. Escribir en el input de búsqueda
    search_input = wait.until(EC.presence_of_element_located((By.ID, "search-keyword")))
    search_input.clear()
    search_input.send_keys(objetivo)

    # 2. Clic en el botón de búsqueda
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-search")))
    search_button.click()
    time.sleep(3)

    # 3. Contar los resultados con A
    try:
        filas = wait.until(EC.presence_of_all_elements_located((
            By.XPATH, "//table//tbody//tr"
        )))
        cantidad = len(filas)
        assert cantidad > 0, "[X] CP-06-05a: No se encontraron resultados en la tabla."
        print(f"[✓] Éxito CP-06-05a: Se encontraron {cantidad} coincidencas en la búsqueda con el nombre '{objetivo}'.")
    except TimeoutException:
        raise AssertionError("[X] CP-06-05a: No se encontraron resultados tras la búsqueda.")
    

# CP-06-07
def test_cp_06_07_empty_or_special_characters_input(driver):
    """
    CP-06-07: Búsqueda con campo vacío o caracteres especiales

    Objetivo:
        Validar manejo de entrada vacía o con caracteres especiales

    Técnica utilizada:
        Valores Límite

    Datos de prueba:
        - Sistema funcionando, usuario autenticado

    Entrada:
        "" (vacío), "%%%"

    Resultado esperado:
        Mensaje de advertencia o “No se encontraron resultados”
    """

    wait = WebDriverWait(driver, 10)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/search")
    time.sleep(2)

    objetivo = ' '

    # 1. Escribir en el input de búsqueda
    search_input = wait.until(EC.presence_of_element_located((By.ID, "search-keyword")))
    search_input.clear()
    search_input.send_keys(objetivo)

    # 2. Clic en el botón de búsqueda
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-search")))
    search_button.click()
    time.sleep(3)

    # 3. Esperar al toast
    try:
        # Espera el mensaje de toast: "No results found."
        toast = wait.until(EC.presence_of_element_located((
            By.XPATH, "//div[contains(@class, 'toast-body') and contains(text(), 'No results found.')]"
        )))
        print(f"[✓] Éxito CP-06-07: No se encontraron resultados.'")
    except TimeoutException:
        raise AssertionError("[X] CP-06-07: Se encontraron resultados.")


# CP-06-07a
def test_cp_06_07a_maximum_allowed_characters(driver):
    """
    CP-06-07a: Búsqueda con máximo permitido de caracteres

    Objetivo:
        Buscar usando exactamente el límite máximo de caracteres permitido

    Técnica utilizada:
        Valores Límite

    Datos de prueba:
        - Límite: 100 caracteres

    Entrada:
        Cadena de 100 caracteres

    Resultado esperado:
        Resultados válidos o advertencia si excede
    """

    wait = WebDriverWait(driver, 10)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/search")
    time.sleep(2)

    objetivo = "a" * 100

    # 1. Escribir en el input de búsqueda
    search_input = wait.until(EC.presence_of_element_located((By.ID, "search-keyword")))
    search_input.clear()
    search_input.send_keys(objetivo)

    # 2. Clic en el botón de búsqueda
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-search")))
    search_button.click()
    time.sleep(3)

    # 3. Esperar al toast
    try:
        # Espera el mensaje de toast: "No results found."
        toast = wait.until(EC.presence_of_element_located((
            By.XPATH, "//div[contains(@class, 'toast-body') and contains(text(), 'No results found.')]"
        )))
        print(f"[✓] Éxito CP-06-07a: Se insertaron 100 caracteres, realizo la busqueda pero no se encontraron resultados.")
    except TimeoutException:
        raise AssertionError("[X] CP-06-07a: Se encontraron resultados.")


# CP-06-07b
def test_cp_06_07b_exceeding_maximum_characters(driver):
    """
    CP-06-07b: Búsqueda superando el máximo de caracteres

    Objetivo:
        Buscar usando más caracteres de los permitidos

    Técnica utilizada:
        Valores Límite

    Datos de prueba:
        - Límite: 101 caracteres

    Entrada:
        Cadena de 101 caracteres

    Resultado esperado:
        Mensaje: “Máximo de X caracteres permitidos”
    """

    wait = WebDriverWait(driver, 10)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/search")
    time.sleep(2)

    objetivo = "a" * 101

    # 1. Escribir en el input de búsqueda
    search_input = wait.until(EC.presence_of_element_located((By.ID, "search-keyword")))
    search_input.clear()
    search_input.send_keys(objetivo)

    # 2. Clic en el botón de búsqueda
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-search")))
    search_button.click()
    time.sleep(3)

    # 3. Esperar al toast
    try:
        # Espera el mensaje de toast: "No results found."
        toast = wait.until(EC.presence_of_element_located((
            By.XPATH, "//div[contains(@class, 'toast-body') and contains(text(), 'No results found.')]"
        )))
        print(f"[✓] Éxito CP-06-07b: Se insertaron 101 caracteres, realizo la busqueda pero no se encontraron resultados.'")
    except TimeoutException:
        raise AssertionError("[X] CP-06-07b: Se encontraron resultados.")


# CP-06-07c
def test_cp_06_07c_one_less_than_max_characters(driver):
    """
    CP-06-07c: Búsqueda con un carácter menos del máximo permitido

    Objetivo:
        Buscar usando uno menos de los caracteres de los permitidos

    Técnica utilizada:
        Valores Límite

    Datos de prueba:
        - Límite: 99 caracteres

    Entrada:
        Cadena de 99 caracteres

    Resultado esperado:
        Resultados válidos
    """

    wait = WebDriverWait(driver, 10)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/search")
    time.sleep(2)

    objetivo = "a" * 99

    # 1. Escribir en el input de búsqueda
    search_input = wait.until(EC.presence_of_element_located((By.ID, "search-keyword")))
    search_input.clear()
    search_input.send_keys(objetivo)

    # 2. Clic en el botón de búsqueda
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-search")))
    search_button.click()
    time.sleep(3)

    # 3. Esperar al toast
    try:
        # Espera el mensaje de toast: "No results found."
        toast = wait.until(EC.presence_of_element_located((
            By.XPATH, "//div[contains(@class, 'toast-body') and contains(text(), 'No results found.')]"
        )))
        print(f"[✓] Éxito CP-06-07c: Se insertaron 99 caracteres, realizo la busqueda pero no se encontraron resultados.'")
    except TimeoutException:
        raise AssertionError("[X] CP-06-07c: Se encontraron resultados.")
