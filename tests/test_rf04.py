import pytest
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.mark.usefixtures("driver")
def test_cp_04_01_instructor_courses_panel(driver):
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión como instructor"
    wait = WebDriverWait(driver, 15)
    # Ir a la sección de cursos en la navbar
    try:
        courses_nav = wait.until(EC.element_to_be_clickable((By.XPATH, "//nav//a[contains(@href, 'courses') or contains(text(), 'Courses') or contains(text(), 'Cursos')]")))
        courses_nav.click()
    except Exception:
        print('No se encontró el enlace de cursos en la navbar. HTML actual:')
        print(driver.page_source)
        assert False, "No se pudo navegar a la sección de cursos"
    # Validar que el título de la sección es 'Courses'
    try:
        title = wait.until(EC.presence_of_element_located((By.XPATH, "//*[text()='Courses']")))
        assert title.is_displayed(), "No se visualiza el título 'Courses' en la sección de cursos"
    except Exception:
        print("No se encontró el título 'Courses' en la sección. HTML actual:")
        print(driver.page_source)
        assert False, "No se visualizó el título 'Courses' en la sección de cursos"


@pytest.mark.usefixtures("driver")
def test_cp_04_02_create_course_valid(driver):
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión como instructor"
    wait = WebDriverWait(driver, 15)
    # Ir a la sección de cursos
    courses_nav = wait.until(EC.element_to_be_clickable((By.XPATH, "//nav//a[contains(@href, 'courses') or contains(text(), 'Courses') or contains(text(), 'Cursos')]")))
    courses_nav.click()
    # Abrir formulario de nuevo curso
    add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Añadir nuevo curso') or contains(text(), 'Add New Course')]")))
    add_btn.click()
    # Llenar campos
    wait.until(EC.visibility_of_element_located((By.XPATH, "//form")))
    course_id = "CS106119912321552312"
    try:
        courseid_input = wait.until(EC.visibility_of_element_located((By.NAME, "courseId")))
        courseid_input.send_keys(course_id)
    except Exception:
        print("No se encontró el campo 'courseId'. HTML actual:")
        print(driver.page_source)
        assert False, "No se encontró el campo 'courseId' en el formulario de nuevo curso"
    driver.find_element(By.NAME, "courseName").send_keys("Intro a la programación")
    # Instituto es un select
    institute_select = driver.find_element(By.NAME, "institute")
    from selenium.webdriver.support.ui import Select
    Select(institute_select).select_by_value("unsa")
    # Zona horaria es un select
    timezone_select = driver.find_element(By.NAME, "timeZone")
    Select(timezone_select).select_by_value("America/Lima")
    # Guardar
    submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Add Course') or contains(text(), 'Añadir curso')]")
    assert submit_btn.is_enabled(), "El botón para crear curso no está habilitado con datos válidos"
    submit_btn.click()
    # Validar que el curso aparece en la tabla de cursos activos
    active_table = wait.until(EC.presence_of_element_located((By.XPATH, "//table[contains(@id, 'active-courses-table')]") ))
    table_text = active_table.get_attribute("innerText")
    if table_text is None or course_id not in table_text:
        print("No se encontró el curso en la tabla. HTML del formulario tras submit:")
        try:
            form = driver.find_element(By.XPATH, "//form")
            print(form.get_attribute("innerHTML"))
        except Exception:
            print(driver.page_source)
        assert False, f"El curso creado no aparece en la tabla de cursos activos. Buscado: {course_id}"

@pytest.mark.usefixtures("driver")
def test_cp_04_03_create_course_empty_id(driver):
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión como instructor"
    wait = WebDriverWait(driver, 15)
    courses_nav = wait.until(EC.element_to_be_clickable((By.XPATH, "//nav//a[contains(@href, 'courses') or contains(text(), 'Courses') or contains(text(), 'Cursos')]")))
    courses_nav.click()
    add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Añadir nuevo curso') or contains(text(), 'Add New Course')]")))
    add_btn.click()
    wait.until(EC.visibility_of_element_located((By.XPATH, "//form")))
    driver.find_element(By.NAME, "courseId").clear()
    driver.find_element(By.NAME, "courseName").send_keys("Curso de Prueba")
    # Instituto y zona pueden ser predefinidos
    submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Add Course') or contains(text(), 'Añadir curso')]")
    assert not submit_btn.is_enabled(), "El botón para crear curso está habilitado con ID vacío"
    # Validar mensaje de error
    try:
        error = driver.find_element(By.XPATH, "//div[contains(@class, 'invalid-field') and contains(., 'The field Course ID should not be empty.')]")
        is_hidden = error.get_attribute("hidden")
        # El mensaje de error está oculto (hidden="true") cuando el botón está deshabilitado
        assert is_hidden == "true", f"El mensaje de error por ID vacío debería estar oculto (hidden={is_hidden}) según la lógica de la UI"
    except Exception:
        print("No se encontró el mensaje de error por ID vacío. HTML del formulario:")
        try:
            form = driver.find_element(By.XPATH, "//form")
            print(form.get_attribute("innerHTML"))
        except Exception:
            print(driver.page_source)
        assert False, "No se muestra el mensaje de error por ID vacío"

@pytest.mark.usefixtures("driver")
def test_cp_04_04_create_course_empty_name(driver):
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión como instructor"
    wait = WebDriverWait(driver, 15)
    courses_nav = wait.until(EC.element_to_be_clickable((By.XPATH, "//nav//a[contains(@href, 'courses') or contains(text(), 'Courses') or contains(text(), 'Cursos')]")))
    courses_nav.click()
    add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Añadir nuevo curso') or contains(text(), 'Add New Course')]")))
    add_btn.click()
    wait.until(EC.visibility_of_element_located((By.XPATH, "//form")))
    driver.find_element(By.NAME, "courseId").send_keys("CS102")
    driver.find_element(By.NAME, "courseName").clear()
    # Instituto y zona pueden ser predefinidos
    submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Add Course') or contains(text(), 'Añadir curso')]")
    assert not submit_btn.is_enabled(), "El botón para crear curso está habilitado con nombre vacío"
    try:
        error = driver.find_element(By.XPATH, "//div[contains(@class, 'invalid-field') and contains(., 'The field Course Name should not be empty.')]")
        is_hidden = error.get_attribute("hidden")
        # El mensaje de error está oculto (hidden="true") cuando el botón está deshabilitado
        assert is_hidden == "true", f"El mensaje de error por nombre vacío debería estar oculto (hidden={is_hidden}) según la lógica de la UI"
    except Exception:
        print("No se encontró el mensaje de error por nombre vacío. HTML del formulario:")
        try:
            form = driver.find_element(By.XPATH, "//form")
            print(form.get_attribute("innerHTML"))
        except Exception:
            print(driver.page_source)
        assert False, "No se muestra el mensaje de error por nombre vacío"

@pytest.mark.usefixtures("driver")
def test_cp_04_05_create_course_duplicate_id(driver):
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión como instructor"
    wait = WebDriverWait(driver, 15)
    courses_nav = wait.until(EC.element_to_be_clickable((By.XPATH, "//nav//a[contains(@href, 'courses') or contains(text(), 'Courses') or contains(text(), 'Cursos')]")))
    courses_nav.click()
    add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Añadir nuevo curso') or contains(text(), 'Add New Course')]")))
    add_btn.click()
    wait.until(EC.visibility_of_element_located((By.XPATH, "//form")))
    driver.find_element(By.NAME, "courseId").send_keys("CS106")
    driver.find_element(By.NAME, "courseName").send_keys("Curso Duplicado")
    # Instituto y zona pueden ser predefinidos
    submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Add Course') or contains(text(), 'Añadir curso')]")
    assert submit_btn.is_enabled(), "El botón para crear curso no está habilitado con datos duplicados (debería estarlo para enviar y mostrar error)"
    submit_btn.click()
    # Validar notificación de error por ID duplicado
    notif = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'The course ID CS106 has been used by another course') or contains(text(), 'Course ID already exists') or contains(@class, 'notification') or contains(@class, 'alert-danger') ]")))
    assert notif.is_displayed(), "No se mostró la notificación de error por ID duplicado"

#deprecado por que se casi lo mismo que test_cp_04_02
@pytest.mark.usefixtures("driver")
def test_cp_04_06_create_course_valid_name(driver):
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión como instructor"
    wait = WebDriverWait(driver, 15)
    courses_nav = wait.until(EC.element_to_be_clickable((By.XPATH, "//nav//a[contains(@href, 'courses') or contains(text(), 'Courses') or contains(text(), 'Cursos')]")))
    courses_nav.click()
    add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Añadir nuevo curso') or contains(text(), 'Add New Course')]")))
    add_btn.click()
    wait.until(EC.visibility_of_element_located((By.XPATH, "//form")))
    course_id = "MATH2024gaa"
    driver.find_element(By.NAME, "courseId").send_keys(course_id)
    name_input = driver.find_element(By.NAME, "courseName")
    name_input.send_keys("Matemáticas Aplicadas")
    # Instituto es un select
    institute_select = driver.find_element(By.NAME, "institute")
    from selenium.webdriver.support.ui import Select
    Select(institute_select).select_by_value("unsa")
    # Zona horaria es un select
    timezone_select = driver.find_element(By.NAME, "timeZone")
    Select(timezone_select).select_by_value("America/Lima")
    # Validar que el campo limita la entrada a 64 caracteres
    value = name_input.get_attribute("value")
    assert len(value) <= 64, f"El nombre del curso excede el límite de 64 caracteres: {len(value)}"
    # Instituto y zona pueden ser auto-seleccionados
    submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Add Course') or contains(text(), 'Añadir curso')]")
    assert submit_btn.is_enabled(), "El botón para crear curso no está habilitado con nombre válido"
    submit_btn.click()
    active_table = wait.until(EC.presence_of_element_located((By.XPATH, "//table[contains(@id, 'active-courses-table')]") ))
    table_text = active_table.get_attribute("innerText")
    if table_text is None or course_id not in table_text:
        print("No se encontró el curso en la tabla. HTML del formulario tras submit:")
        try:
            form = driver.find_element(By.XPATH, "//form")
            print(form.get_attribute("innerHTML"))
        except Exception:
            print(driver.page_source)
        assert False, f"El curso creado no aparece en la tabla de cursos activos. Buscado: {course_id}"

@pytest.mark.usefixtures("driver")
def test_cp_04_07_create_course_name_exceeds_limit(driver):
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión como instructor"
    wait = WebDriverWait(driver, 15)
    courses_nav = wait.until(EC.element_to_be_clickable((By.XPATH, "//nav//a[contains(@href, 'courses') or contains(text(), 'Courses') or contains(text(), 'Cursos')]")))
    courses_nav.click()
    add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Añadir nuevo curso') or contains(text(), 'Add New Course')]")))
    add_btn.click()
    wait.until(EC.visibility_of_element_located((By.XPATH, "//form")))
    driver.find_element(By.NAME, "courseId").send_keys("HIST001")
    # Intentar enviar un nombre de curso de más de 80 caracteres
    long_name = "A" * 100
    name_input = driver.find_element(By.NAME, "courseName")
    name_input.send_keys(long_name)
    # Seleccionar instituto y zona horaria como en los otros tests
    institute_select = driver.find_element(By.NAME, "institute")
    from selenium.webdriver.support.ui import Select
    Select(institute_select).select_by_value("unsa")
    timezone_select = driver.find_element(By.NAME, "timeZone")
    Select(timezone_select).select_by_value("America/Lima")
    # Validar que el valor del campo se recorta a 80 caracteres
    value = name_input.get_attribute("value")
    assert len(value) == 80, f"El campo nombre no recorta correctamente a 80 caracteres: {len(value)}"
    # El botón debe estar habilitado si el nombre es válido (exactamente 80)
    submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Add Course') or contains(text(), 'Añadir curso')]")
    assert submit_btn.is_enabled(), "El botón para crear curso no está habilitado con nombre en el límite"

@pytest.mark.usefixtures("driver")
def test_cp_04_08_create_course_timezone_autodetect(driver):
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión como instructor"
    wait = WebDriverWait(driver, 15)
    courses_nav = wait.until(EC.element_to_be_clickable((By.XPATH, "//nav//a[contains(@href, 'courses') or contains(text(), 'Courses') or contains(text(), 'Cursos')]")))
    courses_nav.click()
    add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Añadir nuevo curso') or contains(text(), 'Add New Course')]")))
    add_btn.click()
    wait.until(EC.visibility_of_element_located((By.XPATH, "//form")))
    course_id = "GEO001"
    # Esperar que los campos estén habilitados
    courseid_input = wait.until(EC.visibility_of_element_located((By.NAME, "courseId")))
    name_input = wait.until(EC.visibility_of_element_located((By.NAME, "courseName")))
    institute_select = wait.until(EC.visibility_of_element_located((By.NAME, "institute")))
    timezone_select = wait.until(EC.visibility_of_element_located((By.NAME, "timeZone")))
    # Si algún campo está deshabilitado, imprimir HTML y fallar
    if courseid_input.get_attribute("disabled") or name_input.get_attribute("disabled") or institute_select.get_attribute("disabled") or timezone_select.get_attribute("disabled"):
        print("Algún campo está deshabilitado. HTML del formulario:")
        try:
            form = driver.find_element(By.XPATH, "//form")
            print(form.get_attribute("innerHTML"))
        except Exception:
            print(driver.page_source)
        assert False, "Algún campo del formulario está deshabilitado antes de interactuar"
    # Limpiar campos antes de enviar datos
    courseid_input.clear()
    name_input.clear()
    courseid_input.send_keys(course_id)
    name_input.send_keys("Geografía")
    from selenium.webdriver.support.ui import Select
    Select(institute_select).select_by_value("unsa")
    # Validar que la zona horaria se auto-detecta correctamente
    tz_value = timezone_select.get_attribute("value")
    assert tz_value == "America/Lima", f"La zona horaria detectada no es la esperada: {tz_value}"
    Select(timezone_select).select_by_value("America/Lima")
    # Guardar y validar curso creado
    submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Add Course') or contains(text(), 'Añadir curso')]")
    assert submit_btn.is_enabled(), "El botón para crear curso no está habilitado con zona horaria auto-detectada"
    submit_btn.click()
    active_table = wait.until(EC.presence_of_element_located((By.XPATH, "//table[contains(@id, 'active-courses-table')]")))
    table_text = active_table.get_attribute("innerText")
    if table_text is None or course_id not in table_text:
        print("No se encontró el curso en la tabla. HTML del formulario tras submit:")
        try:
            form = driver.find_element(By.XPATH, "//form")
            print(form.get_attribute("innerHTML"))
        except Exception:
            print(driver.page_source)
        assert False, f"El curso creado no aparece en la tabla de cursos activos. Buscado: {course_id}"

# =====================
# UTILIDAD PARA AGREGAR ESTUDIANTES EN TABLA "NEW STUDENTS"
def fill_new_student_row(driver, row_idx, section, team, name, email, comment):
    """
    Llena una fila de la tabla 'New Students' en la posición row_idx (1-indexed).
    """
    # Buscar el div del spreadsheet
    spreadsheet_div = driver.find_element(By.ID, "newStudentsHOT")
    ht_table = spreadsheet_div.find_element(By.CLASS_NAME, "ht_master")
    table = ht_table.find_element(By.CLASS_NAME, "htCore")
    rows = table.find_elements(By.TAG_NAME, "tr")
    if len(rows) <= row_idx:
        raise Exception(f"No hay suficientes filas en la tabla de estudiantes nuevos. Esperado al menos {row_idx+1}, encontrado {len(rows)}")
    row = rows[row_idx]
    cells = row.find_elements(By.TAG_NAME, "td")
    if len(cells) < 5:
        raise Exception(f"La fila de la tabla no tiene suficientes celdas. Esperado 5, encontrado {len(cells)}")
    # Simular doble clic y edición usando el textarea global de Handsontable
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.keys import Keys
    import time
    values = [section, team, name, email, comment]
    for i, value in enumerate(values):
        if value is not None:
            cell = cells[i]
            actions = ActionChains(driver)
            actions.double_click(cell).perform()
            time.sleep(0.5)
            # Esperar a que el textarea global esté visible
            textarea = None
            try:
                textarea = driver.find_element(By.CLASS_NAME, "handsontableInput")
                # Esperar a que esté visible y habilitado
                for _ in range(10):
                    if textarea.is_displayed() and textarea.is_enabled():
                        break
                    time.sleep(0.1)
            except Exception:
                pass
            if textarea:
                textarea.clear()
                textarea.send_keys(value)
                textarea.send_keys(Keys.ENTER)
                time.sleep(0.2)

@pytest.mark.usefixtures("driver")
def test_cp_04_01_01_add_valid_student_to_active_course(driver):
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión como instructor"
    wait = WebDriverWait(driver, 15)
    # Ir a la sección de cursos
    courses_nav = wait.until(EC.element_to_be_clickable((By.XPATH, "//nav//a[contains(@href, 'courses') or contains(text(), 'Courses') or contains(text(), 'Cursos')]")))
    courses_nav.click()
    # Tomar el primer curso activo (asume que hay al menos uno)
    active_table = wait.until(EC.presence_of_element_located((By.XPATH, "//table[contains(@id, 'active-courses-table')]")))
    # Buscar la primera fila de datos (ignorando encabezado)
    rows = active_table.find_elements(By.XPATH, ".//tr[not(th)]")
    if not rows or len(rows) < 1:
        print("No se encontraron filas de cursos activos. HTML de la tabla:")
        print(active_table.get_attribute("outerHTML"))
        assert False, "No hay filas de cursos activos para probar"
    first_row = rows[0]
    # Buscar el botón Enroll en la fila
    try:
        enroll_btn = first_row.find_element(By.XPATH, ".//button[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')] | .//a[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')] | .//span[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')]")
        enroll_btn.click()
    except Exception:
        print("No se encontró el botón de acción en la primera fila. HTML de la fila:")
        print(first_row.get_attribute("outerHTML"))
        assert False, "No se encontró el botón Enroll/Matricular/Agregar estudiantes en la primera fila de la tabla"
    # Esperar el div del spreadsheet de nuevos estudiantes
    try:
        spreadsheet_div = wait.until(EC.visibility_of_element_located((By.ID, "newStudentsHOT")))
    except Exception:
        print("No se encontró el div 'newStudentsHOT' tras hacer clic en el botón. HTML del contenedor principal:")
        try:
            main = driver.find_element(By.TAG_NAME, "main")
            print(main.get_attribute("outerHTML"))
        except Exception:
            print(driver.page_source)
        assert False, "No se encontró el div 'newStudentsHOT' tras hacer clic en el botón de inscripción. Ajusta el selector según el HTML impreso."
    # Agregar una fila vacía antes de llenar datos
    add_row_btn = driver.find_element(By.ID, "btn-add-empty-rows")
    add_row_btn.click()
    import time
    time.sleep(1)  # Espera breve para que se agregue la fila
    # Llenar la primera fila con datos válidos
    fill_new_student_row(driver, 1, section="A1", team="Alpha", name="Juan Pérez", email="juan.perez@unsa.edu.pe", comment="")
    # Click en Enroll students (por id)
    enroll_students_btn = driver.find_element(By.ID, "btn-enroll")
    enroll_students_btn.click()
    # Esperar mensaje de confirmación
    import time
    time.sleep(2)  # Breve espera para que se procese la inscripción
    # Buscar notificación de éxito
    success = False
    try:
        notif = driver.find_element(By.XPATH, "//*[contains(text(), 'Student added') or contains(text(), 'agregado') or contains(@class, 'alert-success')]")
        if notif.is_displayed():
            success = True
    except Exception:
        pass
    # Expandir el panel 'Existing Students' y buscar al estudiante en la tabla
    found = False
    try:
        # Expandir el panel si está colapsado
        toggle_panel = driver.find_element(By.ID, "toggle-existing-students")
        chevron_btn = toggle_panel.find_element(By.CLASS_NAME, "chevron")
        aria_expanded = chevron_btn.get_attribute("aria-expanded")
        if aria_expanded == "false":
            chevron_btn.click()
            import time
            time.sleep(1)
        # Esperar a que el hot-table de estudiantes existentes esté visible
        wait = WebDriverWait(driver, 10)
        existing_hot = wait.until(EC.visibility_of_element_located((By.ID, "existingStudentsHOT")))
        ht_table = existing_hot.find_element(By.CLASS_NAME, "ht_master")
        table = ht_table.find_element(By.CLASS_NAME, "htCore")
        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 5:
                name = cells[2].text.strip() if cells[2].text else ""
                email = cells[3].text.strip() if cells[3].text else ""
                if "Juan Pérez" in name and "juan.perez@unsa.edu.pe" in email:
                    found = True
                    break
    except Exception:
        pass
    # Imprimir HTML de todas las tablas y divs con 'student' o 'enroll' en id o clase, y el body completo para depuración
    # Guardar HTML de depuración en archivo
    html_debug = []
    html_debug.append("========== DEPURACIÓN: HTML tras inscripción ==========")
    # Tablas relevantes
    tables = driver.find_elements(By.XPATH, "//table[contains(@id, 'student') or contains(@class, 'student') or contains(@id, 'enroll') or contains(@class, 'enroll')]")
    if tables:
        html_debug.append("--- Tablas con 'student' o 'enroll' en id o clase ---")
        for t in tables:
            html_debug.append(t.get_attribute("outerHTML"))
    else:
        html_debug.append("No se encontró ninguna tabla relevante.\n")
    # Divs relevantes
    divs = driver.find_elements(By.XPATH, "//div[contains(@id, 'student') or contains(@class, 'student') or contains(@id, 'enroll') or contains(@class, 'enroll')]")
    if divs:
        html_debug.append("--- Divs con 'student' o 'enroll' en id o clase ---")
        for d in divs:
            html_debug.append(d.get_attribute("outerHTML"))
    else:
        html_debug.append("No se encontró ningún div relevante.\n")
    # Body completo
    html_debug.append("--- Body completo tras inscripción ---")
    html_debug.append(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
    html_debug.append("========== FIN DEPURACIÓN ==========")
    # Escribir en archivo
    with open("depuracion_estudiante.html", "w", encoding="utf-8") as f:
        f.write("\n".join(html_debug))
    # También imprimir en consola para quien use -s
    for line in html_debug:
        print(line)
    if not (success or found):
        assert False, "No se confirmó que el estudiante fue agregado correctamente (ni por notificación ni en la tabla de estudiantes)."


#GAAAAAAAAAAAAAA a partir de aca no probe aun xd 
@pytest.mark.usefixtures("driver")
def test_cp_04_01_02_add_student_with_duplicate_email(driver):
    """
    Agregar estudiante con email duplicado a curso activo. Debe mostrar error y no agregar.
    """
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión como instructor"
    wait = WebDriverWait(driver, 15)
    # Ir a la sección de cursos
    courses_nav = wait.until(EC.element_to_be_clickable((By.XPATH, "//nav//a[contains(@href, 'courses') or contains(text(), 'Courses') or contains(text(), 'Cursos')]")))
    courses_nav.click()
    active_table = wait.until(EC.presence_of_element_located((By.XPATH, "//table[contains(@id, 'active-courses-table')]")))
    rows = active_table.find_elements(By.XPATH, ".//tr[not(th)]")
    first_row = rows[0]
    enroll_btn = first_row.find_element(By.XPATH, ".//button[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')] | .//a[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')] | .//span[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')]")
    enroll_btn.click()
    spreadsheet_div = wait.until(EC.visibility_of_element_located((By.ID, "newStudentsHOT")))
    add_row_btn = driver.find_element(By.ID, "btn-add-empty-rows")
    add_row_btn.click()
    import time
    time.sleep(1)
    # Usar email ya existente en el curso (debe estar en la tabla de existentes)
    # Para robustez, tomar el email de la primera fila de existentes
    toggle_panel = driver.find_element(By.ID, "toggle-existing-students")
    chevron_btn = toggle_panel.find_element(By.CLASS_NAME, "chevron")
    aria_expanded = chevron_btn.get_attribute("aria-expanded")
    # Verificar si el panel ya está visible antes de expandir
    panel_visible = False
    try:
        existing_hot = driver.find_element(By.ID, "existingStudentsHOT")
        if existing_hot.is_displayed():
            panel_visible = True
    except Exception:
        pass
    if not panel_visible and aria_expanded == "false":
        # Hacer scroll al botón antes de hacer clic
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", chevron_btn)
        import time
        time.sleep(0.5)
        try:
            chevron_btn.click()
        except Exception:
            # Si el clic es interceptado, usar JavaScript como fallback
            driver.execute_script("arguments[0].click();", chevron_btn)
        time.sleep(1)
    # Esperar a que el panel esté visible
    try:
        existing_hot = wait.until(EC.visibility_of_element_located((By.ID, "existingStudentsHOT")))
    except Exception:
        # Imprimir HTML relevante para depuración
        print("No se encontró el panel de estudiantes existentes tras expandir. HTML del contenedor principal:")
        try:
            main = driver.find_element(By.TAG_NAME, "main")
            print(main.get_attribute("outerHTML"))
        except Exception:
            print(driver.page_source)
        assert False, "No se encontró el panel de estudiantes existentes tras expandir. Ajusta el selector o la lógica según el HTML impreso."
    ht_table = existing_hot.find_element(By.CLASS_NAME, "ht_master")
    table = ht_table.find_element(By.CLASS_NAME, "htCore")
    rows_exist = table.find_elements(By.TAG_NAME, "tr")
    email_exist = ""
    for row in rows_exist:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) >= 4:
            email_exist = cells[3].text.strip() if cells[3].text else ""
            if email_exist:
                break
    # Si no hay email, usar uno de ejemplo
    if not email_exist:
        email_exist = "maria.lopez@unsa.edu.pe"
    fill_new_student_row(driver, 1, section="B2", team="Beta", name="María López", email=email_exist, comment="")
    enroll_students_btn = driver.find_element(By.ID, "btn-enroll")
    enroll_students_btn.click()
    time.sleep(2)
    # Validar mensaje de error
    error = None
    try:
        error = driver.find_element(By.XPATH, "//*[contains(text(), 'Email ya registrado') or contains(text(), 'duplicate') or contains(@class, 'alert-danger')]")
    except Exception:
        pass
    assert error and error.is_displayed(), "No se mostró el error por email duplicado"
    # Validar que no se agregó
    found = False
    for row in rows_exist:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) >= 5:
            name = cells[2].text.strip() if cells[2].text else ""
            email = cells[3].text.strip() if cells[3].text else ""
            if "María López" in name and email_exist in email:
                found = True
                break
    assert not found, "El estudiante con email duplicado fue agregado, pero no debería"

@pytest.mark.usefixtures("driver")
def test_cp_04_01_03_add_student_with_invalid_email_format(driver):
    """
    Agregar estudiante con formato incorrecto en correo. Debe mostrar error y no agregar.
    """
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión como instructor"
    wait = WebDriverWait(driver, 15)
    courses_nav = wait.until(EC.element_to_be_clickable((By.XPATH, "//nav//a[contains(@href, 'courses') or contains(text(), 'Courses') or contains(text(), 'Cursos')]")))
    courses_nav.click()
    active_table = wait.until(EC.presence_of_element_located((By.XPATH, "//table[contains(@id, 'active-courses-table')]")))
    rows = active_table.find_elements(By.XPATH, ".//tr[not(th)]")
    first_row = rows[0]
    enroll_btn = first_row.find_element(By.XPATH, ".//button[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')] | .//a[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')] | .//span[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')]")
    enroll_btn.click()
    spreadsheet_div = wait.until(EC.visibility_of_element_located((By.ID, "newStudentsHOT")))
    add_row_btn = driver.find_element(By.ID, "btn-add-empty-rows")
    add_row_btn.click()
    import time
    time.sleep(1)
    fill_new_student_row(driver, 1, section="C1", team="Gamma", name="Luis Ramos", email="luis.ramos.com", comment="")
    enroll_students_btn = driver.find_element(By.ID, "btn-enroll")
    enroll_students_btn.click()
    time.sleep(2)
    error = None
    try:
        error = driver.find_element(By.XPATH, "//*[contains(text(), 'Formato de correo inválido') or contains(text(), 'invalid email') or contains(@class, 'alert-danger')]")
    except Exception:
        pass
    if error and error.is_displayed():
        return
    # Si no se encontró el error flotante, buscar en la tabla de resultados de inscripción
    found_error_in_table = False
    try:
        # Buscar el toast de error de inscripción
        toast = driver.find_element(By.XPATH, "//div[contains(@class, 'toast') and contains(., 'Some students failed to be enrolled')]")
        if toast and toast.is_displayed():
            found_error_in_table = True
        # Buscar el div de resultados de inscripción con encabezado bg-danger
        results_panel = driver.find_element(By.ID, "results-panel")
        error_panels = results_panel.find_elements(By.XPATH, ".//div[contains(@class, 'enroll-results-panel') and .//div[contains(@class, 'bg-danger')]]")
        for panel in error_panels:
            table = panel.find_element(By.TAG_NAME, "table")
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 6:
                    name = cells[2].text.strip() if cells[2].text else ""
                    email = cells[3].text.strip() if cells[3].text else ""
                    error_msg = cells[5].text.strip() if cells[5].text else ""
                    if "Luis Ramos" in name and "luis.ramos.com" in email and ("not acceptable" in error_msg or "Formato" in error_msg or "email" in error_msg):
                        found_error_in_table = True
                        break
            if found_error_in_table:
                break
    except Exception:
        pass
    if not found_error_in_table:
        print("No se encontró el mensaje de error por email inválido ni en alerta, toast ni en la tabla de resultados. HTML del body tras intentar inscribir:")
        print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
        assert False, "No se mostró el error por formato de email inválido ni en alerta, toast ni en la tabla de resultados"

@pytest.mark.usefixtures("driver")
def test_cp_04_01_04_team_required(driver):
    """
    Validación de campo obligatorio Team vacío. Debe mostrar error y no permitir operación.
    """
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión como instructor"
    wait = WebDriverWait(driver, 15)
    courses_nav = wait.until(EC.element_to_be_clickable((By.XPATH, "//nav//a[contains(@href, 'courses') or contains(text(), 'Courses') or contains(text(), 'Cursos')]")))
    courses_nav.click()
    active_table = wait.until(EC.presence_of_element_located((By.XPATH, "//table[contains(@id, 'active-courses-table')]")))
    rows = active_table.find_elements(By.XPATH, ".//tr[not(th)]")
    first_row = rows[0]
    enroll_btn = first_row.find_element(By.XPATH, ".//button[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')] | .//a[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')] | .//span[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')]")
    enroll_btn.click()
    spreadsheet_div = wait.until(EC.visibility_of_element_located((By.ID, "newStudentsHOT")))
    add_row_btn = driver.find_element(By.ID, "btn-add-empty-rows")
    add_row_btn.click()
    import time
    time.sleep(1)
    fill_new_student_row(driver, 1, section="", team="", name="Carlos Mejía", email="carlos.mejia@unsa.edu.pe", comment="")
    enroll_students_btn = driver.find_element(By.ID, "btn-enroll")
    enroll_students_btn.click()
    time.sleep(2)
    error = None
    try:
        error = driver.find_element(By.XPATH, "//*[contains(text(), 'Team es obligatorio') or contains(text(), 'team required') or contains(@class, 'alert-danger') or contains(text(), 'Found empty compulsory fields and/or sections with more than 100 students.')]")
    except Exception:
        pass
    if error and error.is_displayed():
        return
    # Si no se encontró el error flotante, buscar en la tabla de resultados de inscripción
    found_error_in_table = False
    try:
        # Buscar el toast de error de inscripción
        toast = driver.find_element(By.XPATH, "//div[contains(@class, 'toast') and contains(., 'Some students failed to be enrolled')]")
        if toast and toast.is_displayed():
            found_error_in_table = True
        # Buscar el div de resultados de inscripción con encabezado bg-danger
        results_panel = driver.find_element(By.ID, "results-panel")
        error_panels = results_panel.find_elements(By.XPATH, ".//div[contains(@class, 'enroll-results-panel') and .//div[contains(@class, 'bg-danger')]]")
        for panel in error_panels:
            table = panel.find_element(By.TAG_NAME, "table")
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 6:
                    name = cells[2].text.strip() if cells[2].text else ""
                    email = cells[3].text.strip() if cells[3].text else ""
                    error_msg = cells[5].text.strip() if cells[5].text else ""
                    if (
                        "Carlos Mejía" in name and "carlos.mejia@unsa.edu.pe" in email and (
                            "Team" in error_msg or "team" in error_msg or "obligatorio" in error_msg or "Found empty compulsory fields" in error_msg
                        )
                    ) or (
                        "Found empty compulsory fields and/or sections with more than 100 students." in error_msg
                    ):
                        found_error_in_table = True
                        break
            if found_error_in_table:
                break
    except Exception:
        pass
    if not found_error_in_table:
        print("No se encontró el mensaje de error por Team vacío ni en alerta, toast ni en la tabla de resultados. HTML del body tras intentar inscribir:")
        print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
        assert False, "No se mostró el error por Team vacío ni en alerta, toast ni en la tabla de resultados"

@pytest.mark.usefixtures("driver")
def test_cp_04_01_05_name_required(driver):
    """
    Validación de campo Name vacío. Debe mostrar error y no permitir operación.
    """
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión como instructor"
    wait = WebDriverWait(driver, 15)
    courses_nav = wait.until(EC.element_to_be_clickable((By.XPATH, "//nav//a[contains(@href, 'courses') or contains(text(), 'Courses') or contains(text(), 'Cursos')]")))
    courses_nav.click()
    add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Añadir nuevo curso') or contains(text(), 'Add New Course')]")))
    add_btn.click()
    wait.until(EC.visibility_of_element_located((By.XPATH, "//form")))
    driver.find_element(By.NAME, "courseId").send_keys("CS102")
    driver.find_element(By.NAME, "courseName").clear()
    # Instituto y zona pueden ser predefinidos
    submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Add Course') or contains(text(), 'Añadir curso')]")
    assert not submit_btn.is_enabled(), "El botón para crear curso está habilitado con nombre vacío"
    try:
        error = driver.find_element(By.XPATH, "//div[contains(@class, 'invalid-field') and contains(., 'The field Course Name should not be empty.')]")
        is_hidden = error.get_attribute("hidden")
        # El mensaje de error está oculto (hidden="true") cuando el botón está deshabilitado
        assert is_hidden == "true", f"El mensaje de error por nombre vacío debería estar oculto (hidden={is_hidden}) según la lógica de la UI"
    except Exception:
        print("No se encontró el mensaje de error por nombre vacío. HTML del formulario:")
        try:
            form = driver.find_element(By.XPATH, "//form")
            print(form.get_attribute("innerHTML"))
        except Exception:
            print(driver.page_source)
        assert False, "No se muestra el mensaje de error por nombre vacío"

@pytest.mark.usefixtures("driver")
def test_cp_04_01_06_email_required(driver):
    """
    Validación de campo Email vacío. Debe mostrar error y no permitir operación.
    """
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión como instructor"
    wait = WebDriverWait(driver, 15)
    courses_nav = wait.until(EC.element_to_be_clickable((By.XPATH, "//nav//a[contains(@href, 'courses') or contains(text(), 'Courses') or contains(text(), 'Cursos')]")))
    courses_nav.click()
    active_table = wait.until(EC.presence_of_element_located((By.XPATH, "//table[contains(@id, 'active-courses-table')]")))
    rows = active_table.find_elements(By.XPATH, ".//tr[not(th)]")
    first_row = rows[0]
    enroll_btn = first_row.find_element(By.XPATH, ".//button[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')] | .//a[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')] | .//span[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')]")
    enroll_btn.click()
    spreadsheet_div = wait.until(EC.visibility_of_element_located((By.ID, "newStudentsHOT")))
    add_row_btn = driver.find_element(By.ID, "btn-add-empty-rows")
    add_row_btn.click()
    import time
    time.sleep(1)
    fill_new_student_row(driver, 1, section="C1", team="Echo", name="Pedro Ruiz", email="", comment="")
    enroll_students_btn = driver.find_element(By.ID, "btn-enroll")
    enroll_students_btn.click()
    time.sleep(2)
    error = None
    try:
        error = driver.find_element(By.XPATH, "//*[contains(text(), 'Email es obligatorio') or contains(text(), 'email required') or contains(@class, 'alert-danger') or contains(text(), 'Found empty compulsory fields and/or sections with more than 100 students.')]")
    except Exception:
        pass
    if error and error.is_displayed():
        return
    # Si no se encontró el error flotante, buscar en la tabla de resultados de inscripción
    found_error_in_table = False
    try:
        # Buscar el toast de error de inscripción
        toast = driver.find_element(By.XPATH, "//div[contains(@class, 'toast') and contains(., 'Some students failed to be enrolled')]")
        if toast and toast.is_displayed():
            found_error_in_table = True
        # Buscar el div de resultados de inscripción con encabezado bg-danger
        results_panel = driver.find_element(By.ID, "results-panel")
        error_panels = results_panel.find_elements(By.XPATH, ".//div[contains(@class, 'enroll-results-panel') and .//div[contains(@class, 'bg-danger')]]")
        for panel in error_panels:
            table = panel.find_element(By.TAG_NAME, "table")
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 6:
                    name = cells[2].text.strip() if cells[2].text else ""
                    email = cells[3].text.strip() if cells[3].text else ""
                    error_msg = cells[5].text.strip() if cells[5].text else ""
                    if (
                        "Pedro Ruiz" in name and (
                            "Email" in error_msg or "email" in error_msg or "obligatorio" in error_msg or "Found empty compulsory fields" in error_msg
                        )
                    ) or (
                        "Found empty compulsory fields and/or sections with more than 100 students." in error_msg
                    ):
                        found_error_in_table = True
                        break
            if found_error_in_table:
                break
    except Exception:
        pass
    if not found_error_in_table:
        print("No se encontró el mensaje de error por Email vacío ni en alerta, toast ni en la tabla de resultados. HTML del body tras intentar inscribir:")
        print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
        assert False, "No se mostró el error por Email vacío ni en alerta, toast ni en la tabla de resultados"

#FALLO PO QUE IGUAL ACEPTA EL NOMBRE DEL TEAM 1TEAM
@pytest.mark.usefixtures("driver")
def test_cp_04_01_07_team_must_start_with_letter(driver):
    """
    Validar Team que no inicia con letra. Debe mostrar error y no permitir operación.
    """
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión como instructor"
    wait = WebDriverWait(driver, 15)
    courses_nav = wait.until(EC.element_to_be_clickable((By.XPATH, "//nav//a[contains(@href, 'courses') or contains(text(), 'Courses') or contains(text(), 'Cursos')]")))
    courses_nav.click()
    active_table = wait.until(EC.presence_of_element_located((By.XPATH, "//table[contains(@id, 'active-courses-table')]")))
    rows = active_table.find_elements(By.XPATH, ".//tr[not(th)]")
    first_row = rows[0]
    enroll_btn = first_row.find_element(By.XPATH, ".//button[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')] | .//a[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')] | .//span[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')]")
    enroll_btn.click()
    spreadsheet_div = wait.until(EC.visibility_of_element_located((By.ID, "newStudentsHOT")))
    add_row_btn = driver.find_element(By.ID, "btn-add-empty-rows")
    add_row_btn.click()
    import time
    time.sleep(1)
    fill_new_student_row(driver, 1, section="A1", team="1Alpha", name="Sandra Cruz", email="sandra.cruz@unsa.edu.pe", comment="")
    enroll_students_btn = driver.find_element(By.ID, "btn-enroll")
    enroll_students_btn.click()
    time.sleep(2)
    error = None
    try:
        error = driver.find_element(By.XPATH, "//*[contains(text(), 'Team debe iniciar con una letra') or contains(text(), 'team must start with a letter') or contains(@class, 'alert-danger')]")
    except Exception:
        pass
    assert error and error.is_displayed(), "No se mostró el error por Team que no inicia con letra"

@pytest.mark.usefixtures("driver")
def test_cp_04_01_08_team_with_forbidden_characters(driver):
    """
    Validar Team con caracteres prohibidos. Debe mostrar error y no permitir operación.
    """
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión como instructor"
    wait = WebDriverWait(driver, 15)
    courses_nav = wait.until(EC.element_to_be_clickable((By.XPATH, "//nav//a[contains(@href, 'courses') or contains(text(), 'Courses') or contains(text(), 'Cursos')]")))
    courses_nav.click()
    active_table = wait.until(EC.presence_of_element_located((By.XPATH, "//table[contains(@id, 'active-courses-table')]")))
    rows = active_table.find_elements(By.XPATH, ".//tr[not(th)]")
    first_row = rows[0]
    enroll_btn = first_row.find_element(By.XPATH, ".//button[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')] | .//a[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')] | .//span[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')]")
    enroll_btn.click()
    spreadsheet_div = wait.until(EC.visibility_of_element_located((By.ID, "newStudentsHOT")))
    add_row_btn = driver.find_element(By.ID, "btn-add-empty-rows")
    add_row_btn.click()
    import time
    time.sleep(1)
    fill_new_student_row(driver, 1, section="B1", team="Alpha|Beta", name="Roberto Silva", email="roberto.silva@unsa.edu.pe", comment="")
    enroll_students_btn = driver.find_element(By.ID, "btn-enroll")
    enroll_students_btn.click()
    time.sleep(2)
    error = None
    try:
        error = driver.find_element(By.XPATH, "//*[contains(text(), 'Team no puede contener | o %') or contains(text(), 'forbidden character') or contains(@class, 'alert-danger')]")
    except Exception:
        pass
    if error and error.is_displayed():
        return
    # Si no se encontró el error flotante, buscar en la tabla de resultados de inscripción
    found_error_in_table = False
    try:
        # Buscar el toast de error de inscripción
        toast = driver.find_element(By.XPATH, "//div[contains(@class, 'toast') and contains(., 'Some students failed to be enrolled')]")
        if toast and toast.is_displayed():
            found_error_in_table = True
        # Buscar el div de resultados de inscripción con encabezado bg-danger
        results_panel = driver.find_element(By.ID, "results-panel")
        error_panels = results_panel.find_elements(By.XPATH, ".//div[contains(@class, 'enroll-results-panel') and .//div[contains(@class, 'bg-danger')]]")
        for panel in error_panels:
            table = panel.find_element(By.TAG_NAME, "table")
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 6:
                    name = cells[2].text.strip() if cells[2].text else ""
                    email = cells[3].text.strip() if cells[3].text else ""
                    error_msg = cells[5].text.strip() if cells[5].text else ""
                    if (
                        "Roberto Silva" in name and "roberto.silva@unsa.edu.pe" in email and (
                            "Team" in error_msg or "team" in error_msg or "forbidden" in error_msg or "no puede contener" in error_msg or "|" in error_msg or "%" in error_msg
                        )
                    ):
                        found_error_in_table = True
                        break
            if found_error_in_table:
                break
    except Exception:
        pass
    if not found_error_in_table:
        print("No se encontró el mensaje de error por caracteres prohibidos en Team ni en alerta, toast ni en la tabla de resultados. HTML del body tras intentar inscribir:")
        print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
        assert False, "No se mostró el error por caracteres prohibidos en Team ni en alerta, toast ni en la tabla de resultados"

@pytest.mark.usefixtures("driver")
def test_cp_04_01_09_team_with_email_format(driver):
    """
    Validar Team con formato de email. Debe mostrar error y no permitir operación.
    """
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión como instructor"
    wait = WebDriverWait(driver, 15)
    courses_nav = wait.until(EC.element_to_be_clickable((By.XPATH, "//nav//a[contains(@href, 'courses') or contains(text(), 'Courses') or contains(text(), 'Cursos')]")))
    courses_nav.click()
    active_table = wait.until(EC.presence_of_element_located((By.XPATH, "//table[contains(@id, 'active-courses-table')]")))
    rows = active_table.find_elements(By.XPATH, ".//tr[not(th)]")
    first_row = rows[0]
    enroll_btn = first_row.find_element(By.XPATH, ".//button[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')] | .//a[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')] | .//span[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')]")
    enroll_btn.click()
    spreadsheet_div = wait.until(EC.visibility_of_element_located((By.ID, "newStudentsHOT")))
    add_row_btn = driver.find_element(By.ID, "btn-add-empty-rows")
    add_row_btn.click()
    import time
    time.sleep(1)
    fill_new_student_row(driver, 1, section="C1", team="team@example.com", name="Laura Mendoza", email="laura.mendoza@unsa.edu.pe", comment="")
    enroll_students_btn = driver.find_element(By.ID, "btn-enroll")
    enroll_students_btn.click()
    time.sleep(2)
    error = None
    try:
        error = driver.find_element(By.XPATH, "//*[contains(text(), 'Team no puede tener formato de email') or contains(text(), 'team cannot be email') or contains(@class, 'alert-danger')]")
    except Exception:
        pass
    if error and error.is_displayed():
        return
    # Si no se encontró el error flotante, buscar en la tabla de resultados de inscripción
    found_error_in_table = False
    try:
        # Buscar el toast de error de inscripción
        toast = driver.find_element(By.XPATH, "//div[contains(@class, 'toast') and contains(., 'Some students failed to be enrolled')]")
        if toast and toast.is_displayed():
            found_error_in_table = True
        # Buscar el div de resultados de inscripción con encabezado bg-danger
        results_panel = driver.find_element(By.ID, "results-panel")
        error_panels = results_panel.find_elements(By.XPATH, ".//div[contains(@class, 'enroll-results-panel') and .//div[contains(@class, 'bg-danger')]]")
        for panel in error_panels:
            table = panel.find_element(By.TAG_NAME, "table")
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 6:
                    name = cells[2].text.strip() if cells[2].text else ""
                    email = cells[3].text.strip() if cells[3].text else ""
                    error_msg = cells[5].text.strip() if cells[5].text else ""
                    if (
                        "Laura Mendoza" in name and "laura.mendoza@unsa.edu.pe" in email and (
                            "Team" in error_msg or "team" in error_msg or "formato de email" in error_msg or "cannot be email" in error_msg or "@" in error_msg
                        )
                    ):
                        found_error_in_table = True
                        break
            if found_error_in_table:
                break
    except Exception:
        pass
    if not found_error_in_table:
        print("No se encontró el mensaje de error por formato de email en Team ni en alerta, toast ni en la tabla de resultados. HTML del body tras intentar inscribir:")
        print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
        assert False, "No se mostró el error por formato de email en Team ni en alerta, toast ni en la tabla de resultados"

@pytest.mark.usefixtures("driver")
def test_cp_04_01_10_forbidden_characters_in_optional_fields(driver):
    """
    Validar caracteres prohibidos en campos opcionales. Debe mostrar error y no permitir operación.
    """
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión como instructor"
    wait = WebDriverWait(driver, 15)
    courses_nav = wait.until(EC.element_to_be_clickable((By.XPATH, "//nav//a[contains(@href, 'courses') or contains(text(), 'Courses') or contains(text(), 'Cursos')]")))
    courses_nav.click()
    active_table = wait.until(EC.presence_of_element_located((By.XPATH, "//table[contains(@id, 'active-courses-table')]")))
    rows = active_table.find_elements(By.XPATH, ".//tr[not(th)]")
    first_row = rows[0]
    enroll_btn = first_row.find_element(By.XPATH, ".//button[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')] | .//a[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')] | .//span[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')]")
    enroll_btn.click()
    spreadsheet_div = wait.until(EC.visibility_of_element_located((By.ID, "newStudentsHOT")))
    add_row_btn = driver.find_element(By.ID, "btn-add-empty-rows")
    add_row_btn.click()
    import time
    time.sleep(1)
    fill_new_student_row(driver, 1, section="C|2", team="Zeta", name="Isabel Vargas", email="isabel.vargas@unsa.edu.pe", comment="Estudiante|destacado")
    enroll_students_btn = driver.find_element(By.ID, "btn-enroll")
    enroll_students_btn.click()
    time.sleep(2)
    error = None
    try:
        error = driver.find_element(By.XPATH, "//*[contains(text(), 'Los campos no pueden contener | o %') or contains(text(), 'forbidden character') or contains(@class, 'alert-danger')]")
    except Exception:
        pass
    if error and error.is_displayed():
        return
    # Si no se encontró el error flotante, buscar en la tabla de resultados de inscripción y toast
    found_error_in_table = False
    try:
        # Buscar el toast de error de inscripción
        toast = driver.find_element(By.XPATH, "//div[contains(@class, 'toast') and contains(., 'Some students failed to be enrolled')]")
        if toast and toast.is_displayed():
            found_error_in_table = True
        # Buscar el div de resultados de inscripción con encabezado bg-danger
        results_panel = driver.find_element(By.ID, "results-panel")
        error_panels = results_panel.find_elements(By.XPATH, ".//div[contains(@class, 'enroll-results-panel') and .//div[contains(@class, 'bg-danger')]]")
        for panel in error_panels:
            table = panel.find_element(By.TAG_NAME, "table")
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 6:
                    name = cells[2].text.strip() if cells[2].text else ""
                    email = cells[3].text.strip() if cells[3].text else ""
                    error_msg = cells[5].text.strip() if cells[5].text else ""
                    if (
                        "Isabel Vargas" in name and "isabel.vargas@unsa.edu.pe" in email and (
                            "forbidden" in error_msg or "no pueden contener" in error_msg or "|" in error_msg or "%" in error_msg
                        )
                    ):
                        found_error_in_table = True
                        break
            if found_error_in_table:
                break
    except Exception:
        pass
    if not found_error_in_table:
        print("No se encontró el mensaje de error por caracteres prohibidos en campos opcionales ni en alerta, toast ni en la tabla de resultados. HTML del body tras intentar inscribir:")
        print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
        assert False, "No se mostró el error por caracteres prohibidos en campos opcionales ni en alerta, toast ni en la tabla de resultados"

@pytest.mark.usefixtures("driver")
def test_cp_04_01_11_team_max_length(driver):
    """
    Validar Team en límite superior de caracteres (60). Debe permitir y agregar exitosamente.
    """
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión como instructor"
    wait = WebDriverWait(driver, 15)
    courses_nav = wait.until(EC.element_to_be_clickable((By.XPATH, "//nav//a[contains(@href, 'courses') or contains(text(), 'Courses') or contains(text(), 'Cursos')]")))
    courses_nav.click()
    active_table = wait.until(EC.presence_of_element_located((By.XPATH, "//table[contains(@id, 'active-courses-table')]")))
    rows = active_table.find_elements(By.XPATH, ".//tr[not(th)]")
    first_row = rows[0]
    enroll_btn = first_row.find_element(By.XPATH, ".//button[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')] | .//a[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')] | .//span[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')]")
    enroll_btn.click()
    spreadsheet_div = wait.until(EC.visibility_of_element_located((By.ID, "newStudentsHOT")))
    add_row_btn = driver.find_element(By.ID, "btn-add-empty-rows")
    add_row_btn.click()
    import time
    time.sleep(1)
    team_60 = "A" * 60
    fill_new_student_row(driver, 1, section="A1", team=team_60, name="Fernando López", email="fernando.lopez@unsa.edu.pe", comment="")
    enroll_students_btn = driver.find_element(By.ID, "btn-enroll")
    enroll_students_btn.click()
    time.sleep(2)
    # Validar éxito
    success = False
    try:
        notif = driver.find_element(By.XPATH, "//*[contains(text(), 'Student added') or contains(text(), 'agregado') or contains(@class, 'alert-success')]")
        if notif.is_displayed():
            success = True
    except Exception:
        pass
    # Validar que el estudiante aparece en la tabla de estudiantes existentes
    found = False
    try:
        toggle_panel = driver.find_element(By.ID, "toggle-existing-students")
        chevron_btn = toggle_panel.find_element(By.CLASS_NAME, "chevron")
        aria_expanded = chevron_btn.get_attribute("aria-expanded")
        if aria_expanded == "false":
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", chevron_btn)
            import time
            time.sleep(0.5)
            try:
                chevron_btn.click()
            except Exception:
                driver.execute_script("arguments[0].click();", chevron_btn)
            time.sleep(1)
        wait2 = WebDriverWait(driver, 10)
        existing_hot = wait2.until(EC.visibility_of_element_located((By.ID, "existingStudentsHOT")))
        ht_table = existing_hot.find_element(By.CLASS_NAME, "ht_master")
        table = ht_table.find_element(By.CLASS_NAME, "htCore")
        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 5:
                name = cells[2].text.strip() if cells[2].text else ""
                email = cells[3].text.strip() if cells[3].text else ""
                if "Fernando López" in name and "fernando.lopez@unsa.edu.pe" in email:
                    found = True
                    break
    except Exception:
        pass
    if not (success and found):
        print("No se confirmó que el estudiante fue agregado exitosamente con Team de 60 caracteres. HTML de depuración:")
        print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
        assert False, "No se confirmó que el estudiante fue agregado exitosamente con Team de 60 caracteres (ni por notificación ni en la tabla de estudiantes)."

@pytest.mark.usefixtures("driver")
def test_cp_04_01_12_team_exceeds_max_length(driver):
    """
    Validar Team excediendo límite de caracteres (>60). Debe mostrar error y no permitir operación.
    """
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión como instructor"
    wait = WebDriverWait(driver, 15)
    courses_nav = wait.until(EC.element_to_be_clickable((By.XPATH, "//nav//a[contains(@href, 'courses') or contains(text(), 'Courses') or contains(text(), 'Cursos')]")))
    courses_nav.click()
    active_table = wait.until(EC.presence_of_element_located((By.XPATH, "//table[contains(@id, 'active-courses-table')]")))
    rows = active_table.find_elements(By.XPATH, ".//tr[not(th)]")
    first_row = rows[0]
    enroll_btn = first_row.find_element(By.XPATH, ".//button[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')] | .//a[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')] | .//span[contains(text(), 'Enroll') or contains(text(), 'Matricular') or contains(text(), 'Agregar estudiantes')]")
    enroll_btn.click()
    spreadsheet_div = wait.until(EC.visibility_of_element_located((By.ID, "newStudentsHOT")))
    add_row_btn = driver.find_element(By.ID, "btn-add-empty-rows")
    add_row_btn.click()
    import time
    time.sleep(1)
    team_61 = "A" * 61
    fill_new_student_row(driver, 1, section="B1", team=team_61, name="Patricia Ruiz", email="patricia.ruiz@unsa.edu.pe", comment="")
    enroll_students_btn = driver.find_element(By.ID, "btn-enroll")
    enroll_students_btn.click()
    time.sleep(2)
    error = None
    try:
        error = driver.find_element(By.XPATH, "//*[contains(text(), 'Team excede 60 caracteres') or contains(text(), 'team exceeds 60') or contains(@class, 'alert-danger')]")
    except Exception:
        pass
    if error and error.is_displayed():
        return
    # Si no se encontró el error flotante, buscar en la tabla de resultados de inscripción y toast
    found_error_in_table = False
    try:
        # Buscar el toast de error de inscripción
        toast = driver.find_element(By.XPATH, "//div[contains(@class, 'toast') and contains(., 'Some students failed to be enrolled')]")
        if toast and toast.is_displayed():
            found_error_in_table = True
        # Buscar el div de resultados de inscripción con encabezado bg-danger
        results_panel = driver.find_element(By.ID, "results-panel")
        error_panels = results_panel.find_elements(By.XPATH, ".//div[contains(@class, 'enroll-results-panel') and .//div[contains(@class, 'bg-danger')]]")
        for panel in error_panels:
            table = panel.find_element(By.TAG_NAME, "table")
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 6:
                    name = cells[2].text.strip() if cells[2].text else ""
                    email = cells[3].text.strip() if cells[3].text else ""
                    error_msg = cells[5].text.strip() if cells[5].text else ""
                    if (
                        "Patricia Ruiz" in name and "patricia.ruiz@unsa.edu.pe" in email and (
                            "excede" in error_msg or "exceeds" in error_msg or "Team" in error_msg or "team" in error_msg or "60" in error_msg
                        )
                    ):
                        found_error_in_table = True
                        break
            if found_error_in_table:
                break
    except Exception:
        pass
    if not found_error_in_table:
        print("No se encontró el mensaje de error por Team excediendo el límite de caracteres ni en alerta, toast ni en la tabla de resultados. HTML del body tras intentar inscribir:")
        print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
        assert False, "No se mostró el error por Team excediendo el límite de caracteres ni en alerta, toast ni en la tabla de resultados"


@pytest.mark.usefixtures("driver")
def test_cp_04_02_01_edit_active_course_name(driver):
    """
    Editar nombre de curso activo: Modificar nombre de curso activo y validar éxito y visibilidad del nuevo nombre.
    """
    import os
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor"), "No se pudo iniciar sesión como instructor"
    wait = WebDriverWait(driver, 15)
    # Ir a la sección de cursos
    courses_nav = wait.until(EC.element_to_be_clickable((By.XPATH, "//nav//a[contains(@href, 'courses') or contains(text(), 'Courses') or contains(text(), 'Cursos')]")))
    courses_nav.click()
    active_table = wait.until(EC.presence_of_element_located((By.XPATH, "//table[contains(@id, 'active-courses-table')]")))
    rows = active_table.find_elements(By.XPATH, ".//tr[not(th)]")
    # Buscar el curso "Programación I" en la tabla
    target_row = None
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if cells and "Programación I" in cells[1].text:
            target_row = row
            break
    if not target_row:
        # Si no se encuentra, usar el primero
        target_row = rows[0]
    import time
    # Buscar el botón 'Other Actions' en la fila
    other_actions_btn = None
    try:
        other_actions_btn = target_row.find_element(By.XPATH, ".//button[contains(@id, 'btn-other-actions') or contains(text(), 'Other Actions')]")
    except Exception:
        print("No se encontró el botón 'Other Actions' en la fila. HTML de la fila:")
        print(target_row.get_attribute("outerHTML"))
        assert False, "No se encontró el botón 'Other Actions' en la fila del curso activo"

    # Hacer clic para desplegar el menú
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", other_actions_btn)
    time.sleep(0.5)
    try:
        other_actions_btn.click()
    except Exception:
        driver.execute_script("arguments[0].click();", other_actions_btn)
    time.sleep(1)

    # Buscar el enlace 'Edit' dentro del menú desplegable
    edit_link = None
    try:
        edit_link = target_row.find_element(By.XPATH, ".//div[contains(@class, 'dropdown-menu')]//a[contains(text(), 'Edit')]")
    except Exception:
        print("No se encontró el enlace 'Edit' en el menú 'Other Actions'. HTML de la fila:")
        print(target_row.get_attribute("outerHTML"))
        assert False, "No se encontró el enlace 'Edit' en el menú 'Other Actions' de la fila del curso activo"

    # Hacer clic en el enlace 'Edit'
    try:
        edit_link.click()
    except Exception:
        driver.execute_script("arguments[0].click();", edit_link)
    time.sleep(2)
    print("========== HTML tras presionar 'Edit' ==========")
    print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
    print("========== FIN HTML ==========")
    # Depuración: imprimir HTML tras presionar 'Edit'
    time.sleep(2)
    print("========== HTML tras presionar 'Edit' ==========")
    print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
    print("========== FIN HTML ==========")

    # Si se abrió una nueva ventana/pestaña, cambiar el foco
    if len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(1)

    # Buscar el formulario de edición
    edit_form = wait.until(EC.visibility_of_element_located((By.XPATH, "//form[contains(@class, 'ng-untouched') and contains(@class, 'ng-pristine')]")))

    # Esperar unos segundos por si los campos se habilitan automáticamente
    time.sleep(2)

    name_input = edit_form.find_element(By.ID, "course-name")
    if name_input.get_attribute("disabled"):
        # Buscar cualquier botón, ícono o enlace que permita habilitar los campos
        habilitador = None
        # Buscar botón o enlace con texto 'Edit', 'Editar', o ícono de lápiz cerca del formulario
        try:
            habilitador = edit_form.find_element(By.XPATH, ".//button[contains(text(), 'Edit') or contains(text(), 'Editar') or contains(@class, 'fa-pen')]")
        except Exception:
            try:
                habilitador = edit_form.find_element(By.XPATH, ".//a[contains(text(), 'Edit') or contains(text(), 'Editar') or contains(@class, 'fa-pen')]")
            except Exception:
                pass
        if habilitador:
            habilitador.click()
            time.sleep(1)
        # Verificar nuevamente si el campo está habilitado
        if name_input.get_attribute("disabled"):
            print("No se encontró acción para habilitar los campos. HTML del formulario:")
            print(edit_form.get_attribute("outerHTML"))
            assert False, "No se encontró acción para habilitar los campos en el formulario de edición."

    # Ahora el campo debería estar habilitado
    name_input = wait.until(EC.element_to_be_clickable((By.ID, "course-name")))
    name_input.clear()
    name_input.send_keys("Programación Básica I")

    # Guardar cambios (buscar botón Save/Guardar/Update)
    save_btn = None
    try:
        save_btn = edit_form.find_element(By.XPATH, ".//button[contains(text(), 'Save') or contains(text(), 'Guardar') or contains(text(), 'Update') or contains(@class, 'btn-save')]")
    except Exception:
        # Buscar input tipo submit
        try:
            save_btn = edit_form.find_element(By.XPATH, ".//input[@type='submit']")
        except Exception:
            print("No se encontró el botón de guardar. HTML del formulario:")
            print(edit_form.get_attribute("outerHTML"))
            assert False, "No se encontró el botón de guardar en el formulario de edición."
    assert save_btn.is_enabled(), "El botón de guardar no está habilitado"
    save_btn.click()
    # Esperar explícitamente el banner verde de éxito
    try:
        notif = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success') or contains(@class, 'toast-success') or contains(@class, 'bg-success') or contains(@class, 'alert')][contains(., 'edited') or contains(., 'actualizado') or contains(., 'Course updated') or contains(., 'has been edited')]")))
        success = notif.is_displayed()
    except Exception:
        success = False
    # Validar que el nuevo nombre aparece en la tabla de cursos activos
    active_table = wait.until(EC.presence_of_element_located((By.XPATH, "//table[contains(@id, 'active-courses-table')]")))
    table_text = active_table.get_attribute("innerText")
    found = "Programación Básica I" in table_text if table_text else False
    if not (success and found):
        print("No se confirmó la edición exitosa del nombre del curso. HTML de depuración:")
        print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
        assert False, "No se confirmó la edición exitosa del nombre del curso (ni por notificación ni en la tabla de cursos)."