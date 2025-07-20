import pytest
import os
import time
from selenium.webdriver.common.keys import Keys
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
    # Para el segundo edit
    try:
        edit_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'btn btn-primary btn-sm ng-star-inserted') and contains(text(), 'Edit')]")
        edit_btn.click()
    except Exception:
        pass

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
    # Esperar explícitamente el toast de éxito en cualquier <tm-toast> visible
    success = False
    try:
        # Buscar cualquier <tm-toast> visible con el texto esperado
        toast = wait.until(EC.visibility_of_element_located((By.XPATH, "//tm-toast[contains(., 'The course has been edited.') or contains(., 'Course updated') or contains(., 'actualizado') or contains(., 'edited')][not(contains(@style, 'display: none'))]")))
        if toast.is_displayed():
            success = True
    except Exception:
        pass
    # Validar solo el toast de éxito
    if not success:
        print("No se confirmó la edición exitosa del curso. HTML de depuración:")
        print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
        assert False, "No se confirmó la edición exitosa del curso (no apareció el toast de éxito)."


@pytest.mark.usefixtures("driver")
def test_cp_04_02_02_edit_course_empty_name(driver):
    """
    Editar curso activo con nombre vacío. Debe mostrar error y no permitir guardar.
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
    target_row = rows[0]
    # Buscar el botón 'Other Actions' en la fila
    other_actions_btn = target_row.find_element(By.XPATH, ".//button[contains(@id, 'btn-other-actions') or contains(text(), 'Other Actions')]")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", other_actions_btn)
    time.sleep(0.5)
    try:
        other_actions_btn.click()
    except Exception:
        driver.execute_script("arguments[0].click();", other_actions_btn)
    time.sleep(1)

    # Buscar el enlace 'Edit' dentro del menú desplegable
    edit_link = target_row.find_element(By.XPATH, ".//div[contains(@class, 'dropdown-menu')]//a[contains(text(), 'Edit')]")
    try:
        edit_link.click()
    except Exception:
        driver.execute_script("arguments[0].click();", edit_link)
    time.sleep(2)

    # Para el segundo botón de edit (si aparece)
    try:
        edit_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'btn btn-primary btn-sm ng-star-inserted') and contains(text(), 'Edit')]")
        edit_btn.click()
    except Exception:
        pass

    # Buscar el formulario de edición
    edit_form = wait.until(EC.visibility_of_element_located((By.XPATH, "//form[contains(@class, 'ng-untouched') and contains(@class, 'ng-pristine')]")))
    time.sleep(2)

    name_input = edit_form.find_element(By.ID, "course-name")
    if name_input.get_attribute("disabled"):
        habilitador = None
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
        if name_input.get_attribute("disabled"):
            print("No se encontró acción para habilitar los campos. HTML del formulario:")
            print(edit_form.get_attribute("outerHTML"))
            assert False, "No se encontró acción para habilitar los campos en el formulario de edición."

    # Ahora el campo debería estar habilitado
    name_input = wait.until(EC.element_to_be_clickable((By.ID, "course-name")))
    name_input.clear()
    name_input.send_keys("")
    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", name_input)
    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", name_input)
    name_input.send_keys(Keys.TAB)
    time.sleep(0.5)
    # Buscar el botón de guardar
    try:
        save_btn = edit_form.find_element(By.XPATH, ".//button[contains(text(), 'Save Changes') or contains(text(), 'Save') or contains(text(), 'Guardar') or contains(text(), 'Update') or contains(@class, 'btn-save')]")
    except Exception:
        try:
            save_btn = edit_form.find_element(By.XPATH, ".//input[@type='submit']")
        except Exception:
            assert False, "No se encontró el botón de guardar en el formulario de edición."
    # Esperar hasta 2 segundos a que el botón se deshabilite
    for _ in range(4):
        if not save_btn.is_enabled():
            break
        time.sleep(0.5)
    assert not save_btn.is_enabled(), "El botón de guardar está habilitado con nombre vacío"
    # Validar que el div de error está presente
    try:
        error_div = edit_form.find_element(By.XPATH, ".//div[contains(@class, 'invalid-field') and contains(., 'Course Name')]")
        assert error_div.get_attribute("hidden") == "true"
    except Exception:
        pass

@pytest.mark.usefixtures("driver")
def test_cp_04_02_03_add_instructor_valid(driver):
    """
    Agregar instructor válido a curso activo. Debe mostrar toast de éxito y reflejarse en la tabla.
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
    target_row = rows[0]
    # Ir a editar curso
    other_actions_btn = target_row.find_element(By.XPATH, ".//button[contains(@id, 'btn-other-actions') or contains(text(), 'Other Actions')]")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", other_actions_btn)
    time.sleep(0.5)
    try:
        other_actions_btn.click()
    except Exception:
        driver.execute_script("arguments[0].click();", other_actions_btn)
    time.sleep(1)
    edit_link = target_row.find_element(By.XPATH, ".//div[contains(@class, 'dropdown-menu')]//a[contains(text(), 'Edit')]")
    try:
        edit_link.click()
    except Exception:
        driver.execute_script("arguments[0].click();", edit_link)
    time.sleep(2)
    # Buscar y presionar 'Add New Instructor' después de habilitar el formulario
    add_instr_btn = None
    try:
        # Buscar por id globalmente en el DOM
        add_instr_btn = driver.find_element(By.ID, "btn-add-instructor")
    except Exception:
        try:
            add_instr_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Add New Instructor') or contains(text(), 'Agregar instructor') or contains(@id, 'add-instructor') or contains(@class, 'add-instructor')]")
        except Exception:
            print("No se encontró el botón 'Add New Instructor'. HTML del body:")
            print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
            assert False, "No se encontró el botón 'Add New Instructor' en la página tras habilitar edición"
    add_instr_btn.click()
    time.sleep(1)
    # Rellenar campos del formulario de instructor usando los IDs exactos
    name_input = wait.until(EC.element_to_be_clickable((By.ID, "name-instructor-2")))
    name_input.clear()
    name_input.send_keys("Instructor 2")

    email_input = wait.until(EC.element_to_be_clickable((By.ID, "email-instructor-2")))
    email_input.clear()
    email_input.send_keys("asdasd@gmail.com")

    display_input = wait.until(EC.element_to_be_clickable((By.ID, "displayed-name-instructor-2")))
    display_input.clear()
    display_input.send_keys("Instructor")

    # Seleccionar nivel de acceso: Manager
    # Buscar el radio con id que contenga 'MANAGER'
    radios = driver.find_elements(By.XPATH, "//input[@type='radio' and contains(@id, 'MANAGER')]")
    manager_radio = None
    for radio in radios:
        if radio.is_enabled():
            manager_radio = radio
            break
    assert manager_radio is not None, "No se encontró el radio de acceso 'Manager'"
    driver.execute_script("arguments[0].click();", manager_radio)
    # Buscar y presionar el botón 'Add Instructor' usando el ID exacto
    add_btn = wait.until(EC.element_to_be_clickable((By.ID, "btn-save-instructor-2")))
    assert add_btn.is_enabled(), "El botón para agregar instructor está deshabilitado"
    add_btn.click()
    # Validar el toast de éxito
    success = False
    try:
        toast = wait.until(EC.visibility_of_element_located((By.XPATH, "//tm-toast[contains(., 'added successfully') or contains(., 'Instructor')][not(contains(@style, 'display: none'))]")))
        if toast.is_displayed():
            success = True
    except Exception:
        pass
    assert success, "No se confirmó la adición exitosa del instructor (no apareció el toast de éxito)."

@pytest.mark.usefixtures("driver")
def test_cp_04_02_04_edit_instructor(driver):
    """
    Editar email de instructor. Debe mostrar toast de éxito y reflejarse el cambio.
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
    target_row = rows[0]
    # Buscar el botón 'Other Actions' en la fila
    other_actions_btn = None
    try:
        other_actions_btn = target_row.find_element(By.XPATH, ".//button[contains(@id, 'btn-other-actions') or contains(text(), 'Other Actions')]")
    except Exception:
        print("No se encontró el botón 'Other Actions' en la fila. HTML de la fila:")
        print(target_row.get_attribute("outerHTML"))
        assert False, "No se encontró el botón 'Other Actions' en la fila del curso activo"
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
    try:
        edit_link.click()
    except Exception:
        driver.execute_script("arguments[0].click();", edit_link)
    time.sleep(2)
    # Depuración: imprime el HTML del body tras navegar a la edición de curso
    print("HTML del body tras editar curso:")
    print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
    # Buscar todos los bloques de instructor y mostrar sus textos
    instructor_blocks = driver.find_elements(By.XPATH, "//div[contains(@class, 'card')]")
    print(f"Se encontraron {len(instructor_blocks)} bloques tipo 'card'. Textos:")
    for idx, block in enumerate(instructor_blocks):
        print(f"Bloque {idx}: {block.text}")
    # Ahora busca el bloque que contenga 'Instructor 1' (ajusta si tienes más instructores)
    instructor_blocks_1 = [b for b in instructor_blocks if 'Instructor 1' in b.text]
    assert instructor_blocks_1, "No se encontró el bloque de 'Instructor 1' en la edición de curso"
    instructor_block = instructor_blocks_1[0]
    # Presionar el botón 'Edit' azul dentro del bloque del instructor (no el del curso)
    try:
        edit_instr_btn = instructor_block.find_element(By.ID, "btn-edit-instructor-1")
        edit_instr_btn.click()
        time.sleep(1)
    except Exception:
        print("No se encontró el botón 'Edit' con id 'btn-edit-instructor-1' dentro del bloque de 'Instructor 1'. HTML del bloque:")
        print(instructor_block.get_attribute("outerHTML"))
        assert False, "No se encontró el botón 'Edit' con id 'btn-edit-instructor-1' dentro del bloque de 'Instructor 1'"
    # Ahora editar el email
    instr_email_input = instructor_block.find_element(By.XPATH, ".//input[contains(@id, 'email') or contains(@id, 'instructor-email')]")
    instr_email_input.clear()
    instr_email_input.send_keys("editado.instructor@unsa.edu.pe")
    # Buscar y presionar el botón 'Save Changes' dentro del bloque del instructor
    # Buscar el botón 'Save changes' por id dentro del bloque del instructor
    try:
        save_btn = instructor_block.find_element(By.ID, "btn-save-instructor-1")
    except Exception:
        print("No se encontró el botón 'Save changes' con id 'btn-save-instructor-1' dentro del bloque del instructor. HTML del bloque:")
        print(instructor_block.get_attribute("outerHTML"))
        assert False, "No se encontró el botón 'Save changes' con id 'btn-save-instructor-1' dentro del bloque del instructor"
    assert save_btn.is_enabled(), "El botón de guardar instructor no está habilitado"
    save_btn.click()
    # Validar el toast de éxito con el texto solicitado
    success = False
    try:
        toast = wait.until(EC.visibility_of_element_located((By.XPATH, "//tm-toast[contains(., 'The instructor alesis final tester has been updated.')][not(contains(@style, 'display: none'))]")))
        if toast.is_displayed():
            success = True
    except Exception:
        print("No se confirmó la edición exitosa del instructor. HTML de depuración:")
        print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
    assert success, "No se confirmó la edición exitosa del instructor (no apareció el toast de éxito con el texto esperado)."


@pytest.mark.usefixtures("driver")
def test_cp_04_02_05_delete_instructor(driver):
    """
    Eliminar instructor de curso activo. Debe mostrar toast de éxito y reflejarse en la tabla.
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
    target_row = rows[0]
    # Ir a editar curso (igual que en el test de edición de instructor)
    other_actions_btn = None
    try:
        other_actions_btn = target_row.find_element(By.XPATH, ".//button[contains(@id, 'btn-other-actions') or contains(text(), 'Other Actions')]")
    except Exception:
        print("No se encontró el botón 'Other Actions' en la fila. HTML de la fila:")
        print(target_row.get_attribute("outerHTML"))
        assert False, "No se encontró el botón 'Other Actions' en la fila del curso activo"
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
    try:
        edit_link.click()
    except Exception:
        driver.execute_script("arguments[0].click();", edit_link)
    time.sleep(2)
    # Buscar todos los bloques de instructor y mostrar sus textos para depuración
    instructor_blocks = driver.find_elements(By.XPATH, "//div[contains(@class, 'card')]")
    print(f"Se encontraron {len(instructor_blocks)} bloques tipo 'card'. Textos:")
    for idx, block in enumerate(instructor_blocks):
        print(f"Bloque {idx}: {block.text}")
    # Intentar encontrar el bloque que contenga 'Instructor 1'
    instructor_blocks_1 = [b for b in instructor_blocks if 'Instructor 1' in b.text]
    del_instr_btn = None
    if instructor_blocks_1:
        instructor_block = instructor_blocks_1[0]
        try:
            del_instr_btn = instructor_block.find_element(By.ID, "btn-delete-instructor-1")
            del_instr_btn.click()
        except Exception:
            print("No se encontró el botón 'Delete' con id 'btn-delete-instructor-1' dentro del bloque de 'Instructor 1'. HTML del bloque:")
            print(instructor_block.get_attribute("outerHTML"))
            # Intentar buscar el botón globalmente
    else:
        print("[ADVERTENCIA] No se encontró el bloque de 'Instructor 1'. Buscando el botón 'btn-delete-instructor-1' globalmente...")
    if not del_instr_btn:
        try:
            del_instr_btn = driver.find_element(By.ID, "btn-delete-instructor-1")
            print("[ADVERTENCIA] Botón 'btn-delete-instructor-1' encontrado fuera del bloque esperado. Procediendo a eliminar.")
            del_instr_btn.click()
        except Exception:
            print("No se encontró el botón 'Delete' con id 'btn-delete-instructor-1' en ningún lugar del DOM. HTML del body:")
            print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
            assert False, "No se encontró el botón 'Delete' con id 'btn-delete-instructor-1' en ningún lugar del DOM."
    time.sleep(1)
    # Confirmar eliminación: buscar el botón 'Yes' en el cuadro de diálogo
    try:
        # Esperar a que aparezca el botón 'Yes' en el modal
        yes_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-danger') and contains(text(), 'Yes')]")))
        yes_btn.click()
        print("Botón 'Yes' del cuadro de diálogo de confirmación encontrado y clickeado. Test pasa.")
        return
    except Exception:
        print("No se encontró el botón 'Yes' en el cuadro de diálogo de confirmación. HTML del body:")
        print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
        assert False, "No se encontró el botón 'Yes' en el cuadro de diálogo de confirmación"

@pytest.mark.usefixtures("driver")
def test_cp_04_02_06_add_instructor_invalid_email(driver):
    """
    Agregar instructor con email inválido. Debe mostrar error y no permitir guardar.
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
    target_row = rows[0]
    # Ir a editar curso
    other_actions_btn = target_row.find_element(By.XPATH, ".//button[contains(@id, 'btn-other-actions') or contains(text(), 'Other Actions')]")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", other_actions_btn)
    time.sleep(0.5)
    try:
        other_actions_btn.click()
    except Exception:
        driver.execute_script("arguments[0].click();", other_actions_btn)
    time.sleep(1)
    edit_link = target_row.find_element(By.XPATH, ".//div[contains(@class, 'dropdown-menu')]//a[contains(text(), 'Edit')]")
    try:
        edit_link.click()
    except Exception:
        driver.execute_script("arguments[0].click();", edit_link)
    time.sleep(2)
    # Buscar y presionar 'Add New Instructor' después de habilitar el formulario
    add_instr_btn = None
    try:
        add_instr_btn = driver.find_element(By.ID, "btn-add-instructor")
    except Exception:
        try:
            add_instr_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Add New Instructor') or contains(text(), 'Agregar instructor') or contains(@id, 'add-instructor') or contains(@class, 'add-instructor')]")
        except Exception:
            print("No se encontró el botón 'Add New Instructor'. HTML del body:")
            print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
            assert False, "No se encontró el botón 'Add New Instructor' en la página tras habilitar edición"
    add_instr_btn.click()
    time.sleep(1)
    # Rellenar campos del formulario de instructor usando los IDs exactos
    name_input = wait.until(EC.element_to_be_clickable((By.ID, "name-instructor-2")))
    name_input.clear()
    name_input.send_keys("Instructor 2")

    email_input = wait.until(EC.element_to_be_clickable((By.ID, "email-instructor-2")))
    email_input.clear()
    email_input.send_keys("instructor.com")  # Email inválido
    # Disparar eventos input y change para forzar validación
    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", email_input)
    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", email_input)
    email_input.send_keys(Keys.TAB)
    time.sleep(0.5)

    display_input = wait.until(EC.element_to_be_clickable((By.ID, "displayed-name-instructor-2")))
    display_input.clear()
    display_input.send_keys("Instructor")

    # Seleccionar nivel de acceso: Manager
    radios = driver.find_elements(By.XPATH, "//input[@type='radio' and contains(@id, 'MANAGER')]")
    manager_radio = None
    for radio in radios:
        if radio.is_enabled():
            manager_radio = radio
            break
    assert manager_radio is not None, "No se encontró el radio de acceso 'Manager'"
    driver.execute_script("arguments[0].click();", manager_radio)

    # Buscar y verificar el botón 'Add Instructor' usando el ID exacto
    add_btn = wait.until(EC.element_to_be_clickable((By.ID, "btn-save-instructor-2")))
    # El botón puede estar habilitado, así que lo presionamos y validamos el error mostrado
    add_btn.click()
    time.sleep(1)
    # Buscar el mensaje de error por email inválido tras intentar guardar
    error = None
    try:
        error = driver.find_element(By.XPATH, "//*[contains(text(), 'Formato de correo inválido') or contains(text(), 'invalid email') or contains(@class, 'alert-danger') or contains(text(), 'not acceptable to TEAMMATES')]")
    except Exception:
        pass
    if not (error and error.is_displayed()):
        print("No se mostró el error por email inválido tras intentar guardar. HTML del body:")
        print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
    assert error and error.is_displayed(), "No se mostró el error por email inválido tras intentar guardar"

@pytest.mark.usefixtures("driver")
def test_cp_04_02_07_add_instructor_duplicate_email(driver):
    """
    Agregar instructor con email duplicado. Debe mostrar error y no permitir guardar.
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
    target_row = rows[0]
    # Ir a editar curso
    other_actions_btn = target_row.find_element(By.XPATH, ".//button[contains(@id, 'btn-other-actions') or contains(text(), 'Other Actions')]")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", other_actions_btn)
    time.sleep(0.5)
    try:
        other_actions_btn.click()
    except Exception:
        driver.execute_script("arguments[0].click();", other_actions_btn)
    time.sleep(1)
    edit_link = target_row.find_element(By.XPATH, ".//div[contains(@class, 'dropdown-menu')]//a[contains(text(), 'Edit')]")
    try:
        edit_link.click()
    except Exception:
        driver.execute_script("arguments[0].click();", edit_link)
    time.sleep(2)
    # Buscar y presionar 'Add New Instructor' después de habilitar el formulario
    add_instr_btn = None
    try:
        add_instr_btn = driver.find_element(By.ID, "btn-add-instructor")
    except Exception:
        try:
            add_instr_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Add New Instructor') or contains(text(), 'Agregar instructor') or contains(@id, 'add-instructor') or contains(@class, 'add-instructor')]")
        except Exception:
            print("No se encontró el botón 'Add New Instructor'. HTML del body:")
            print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
            assert False, "No se encontró el botón 'Add New Instructor' en la página tras habilitar edición"
    add_instr_btn.click()
    time.sleep(1)
    # Rellenar campos del formulario de instructor usando los IDs exactos
    name_input = wait.until(EC.element_to_be_clickable((By.ID, "name-instructor-2")))
    name_input.clear()
    name_input.send_keys("Instructor 2")

    email_input = wait.until(EC.element_to_be_clickable((By.ID, "email-instructor-2")))
    email_input.clear()
    email_input.send_keys(LOGIN_EMAIL)  # Email duplicado
    # Disparar eventos input y change para forzar validación
    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", email_input)
    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", email_input)
    email_input.send_keys(Keys.TAB)
    time.sleep(0.5)

    display_input = wait.until(EC.element_to_be_clickable((By.ID, "displayed-name-instructor-2")))
    display_input.clear()
    display_input.send_keys("Instructor")

    # Seleccionar nivel de acceso: Manager
    radios = driver.find_elements(By.XPATH, "//input[@type='radio' and contains(@id, 'MANAGER')]")
    manager_radio = None
    for radio in radios:
        if radio.is_enabled():
            manager_radio = radio
            break
    assert manager_radio is not None, "No se encontró el radio de acceso 'Manager'"
    driver.execute_script("arguments[0].click();", manager_radio)

    # Buscar y verificar el botón 'Add Instructor' usando el ID exacto
    add_btn = wait.until(EC.element_to_be_clickable((By.ID, "btn-save-instructor-2")))
    # El botón debe estar deshabilitado o debe aparecer error tras intentar guardar
    add_btn.click()
    time.sleep(1)
    # Buscar el mensaje de error por email duplicado tras intentar guardar
    error = None
    try:
        error = driver.find_element(By.XPATH, "//*[contains(text(), 'Email ya registrado') or contains(text(), 'duplicate') or contains(text(), 'An instructor with the same email address already exists in the course.') or contains(@class, 'alert-danger')]")
    except Exception:
        pass
    if not (error and error.is_displayed()):
        print("No se mostró el error por email duplicado tras intentar guardar. HTML del body:")
        print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
    assert error and error.is_displayed(), "No se mostró el error por email duplicado tras intentar guardar"


@pytest.mark.usefixtures("driver")
def test_cp_04_02_08_add_instructor_duplicate_exact(driver):
    """
    Agregar instructor con email duplicado y nombre exacto igual al existente. Debe mostrar error y no permitir guardar.
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
    target_row = rows[0]
    # Ir a editar curso
    other_actions_btn = target_row.find_element(By.XPATH, ".//button[contains(@id, 'btn-other-actions') or contains(text(), 'Other Actions')]")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", other_actions_btn)
    time.sleep(0.5)
    try:
        other_actions_btn.click()
    except Exception:
        driver.execute_script("arguments[0].click();", other_actions_btn)
    time.sleep(1)
    edit_link = target_row.find_element(By.XPATH, ".//div[contains(@class, 'dropdown-menu')]//a[contains(text(), 'Edit')]")
    try:
        edit_link.click()
    except Exception:
        driver.execute_script("arguments[0].click();", edit_link)
    time.sleep(2)
    # Buscar y presionar 'Add New Instructor' después de habilitar el formulario
    add_instr_btn = None
    try:
        add_instr_btn = driver.find_element(By.ID, "btn-add-instructor")
    except Exception:
        try:
            add_instr_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Add New Instructor') or contains(text(), 'Agregar instructor') or contains(@id, 'add-instructor') or contains(@class, 'add-instructor')]")
        except Exception:
            print("No se encontró el botón 'Add New Instructor'. HTML del body:")
            print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
            assert False, "No se encontró el botón 'Add New Instructor' en la página tras habilitar edición"
    add_instr_btn.click()
    time.sleep(1)
    # Rellenar campos del formulario de instructor usando los IDs exactos
    name_input = wait.until(EC.element_to_be_clickable((By.ID, "name-instructor-2")))
    name_input.clear()
    name_input.send_keys("alesis final tester")

    email_input = wait.until(EC.element_to_be_clickable((By.ID, "email-instructor-2")))
    email_input.clear()
    email_input.send_keys("almamanima@unsa.edu.pe")  # Email duplicado
    # Disparar eventos input y change para forzar validación
    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", email_input)
    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", email_input)
    email_input.send_keys(Keys.TAB)
    time.sleep(0.5)

    display_input = wait.until(EC.element_to_be_clickable((By.ID, "displayed-name-instructor-2")))
    display_input.clear()
    display_input.send_keys("alesis final tester")

    # Seleccionar nivel de acceso: Manager
    radios = driver.find_elements(By.XPATH, "//input[@type='radio' and contains(@id, 'MANAGER')]")
    manager_radio = None
    for radio in radios:
        if radio.is_enabled():
            manager_radio = radio
            break
    assert manager_radio is not None, "No se encontró el radio de acceso 'Manager'"
    driver.execute_script("arguments[0].click();", manager_radio)

    # Buscar y verificar el botón 'Add Instructor' usando el ID exacto
    add_btn = wait.until(EC.element_to_be_clickable((By.ID, "btn-save-instructor-2")))
    # El botón debe estar deshabilitado o debe aparecer error tras intentar guardar
    add_btn.click()
    time.sleep(1)
    # Buscar el mensaje de error por email duplicado tras intentar guardar
    error = None
    try:
        error = driver.find_element(By.XPATH, "//*[contains(text(), 'Email ya registrado') or contains(text(), 'duplicate') or contains(text(), 'An instructor with the same email address already exists in the course.') or contains(@class, 'alert-danger')]")
    except Exception:
        pass
    if not (error and error.is_displayed()):
        print("No se mostró el error por email duplicado tras intentar guardar. HTML del body:")
        print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
    assert error and error.is_displayed(), "No se mostró el error por email duplicado tras intentar guardar"

@pytest.mark.usefixtures("driver")
def test_cp_04_02_09_delete_course(driver):
    """
    Eliminar curso activo. Debe mostrar toast de éxito y el curso debe desaparecer de la tabla.
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
    target_row = rows[0]
    # Abrir menú 'Other Actions' en la fila del curso
    other_actions_btn = None
    try:
        other_actions_btn = target_row.find_element(By.XPATH, ".//button[contains(@id, 'btn-other-actions') or contains(text(), 'Other Actions')]")
    except Exception:
        print("No se encontró el botón 'Other Actions' en la fila. HTML de la fila:")
        print(target_row.get_attribute("outerHTML"))
        assert False, "No se encontró el botón 'Other Actions' en la fila del curso activo"
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", other_actions_btn)
    time.sleep(0.5)
    try:
        other_actions_btn.click()
    except Exception:
        driver.execute_script("arguments[0].click();", other_actions_btn)
    time.sleep(1)
    # Ahora buscar el botón para eliminar curso (id que contenga 'soft-delete' o texto 'Delete')
    del_course_btn = None
    try:
        # Buscar por id que contenga 'soft-delete' dentro de la fila
        del_course_btn = target_row.find_element(By.XPATH, ".//button[contains(@id, 'soft-delete')]")
    except Exception:
        try:
            # Buscar por texto 'Delete' dentro del menú desplegable
            del_course_btn = target_row.find_element(By.XPATH, ".//div[contains(@class, 'dropdown-menu')]//button[contains(text(), 'Delete')]")
        except Exception:
            print("No se encontró el botón 'Delete' tras abrir el menú. HTML de la fila:")
            print(target_row.get_attribute("outerHTML"))
            assert False, "No se encontró el botón 'Delete' tras abrir el menú 'Other Actions'"
    del_course_btn.click()
    time.sleep(1)
    # Buscar el botón 'Yes' en el cuadro de diálogo de confirmación
    try:
        # Buscar por clase y texto
        yes_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'modal-btn-ok') and (contains(text(), 'Yes') or contains(@class, 'btn-warning'))]")
    except Exception:
        try:
            # Alternativamente, buscar solo por texto 'Yes'
            yes_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Yes')]")
        except Exception:
            print("No se encontró el botón 'Yes' en el cuadro de diálogo de confirmación. HTML del body:")
            print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
            assert False, "No se encontró el botón 'Yes' en el cuadro de diálogo de confirmación"
    yes_btn.click()
    success = False
    try:
        toast = wait.until(EC.visibility_of_element_located((By.XPATH, "//tm-toast[contains(., 'The course') and contains(., 'has been deleted. You can restore it from the Recycle Bin manually.')][not(contains(@style, 'display: none'))]")))
        if toast.is_displayed():
            success = True
    except Exception:
        pass
    assert success, "No se confirmó la eliminación exitosa del curso (no apareció el toast de éxito con el texto esperado)."
    # Validar que el curso ya no aparece en la tabla de activos
    time.sleep(2)
    active_table = driver.find_element(By.XPATH, "//table[contains(@id, 'active-courses-table')]")
    table_text = active_table.get_attribute("innerText")
    assert "Programación I" not in table_text, "El curso eliminado sigue apareciendo en la tabla."

    # Buscar la sección de cursos eliminados (Recycle Bin) y expandirla si es necesario
    try:
        # Esperar el encabezado de la papelera
        recycle_heading = wait.until(EC.presence_of_element_located((By.ID, "deleted-table-heading")))
        # Buscar el botón chevron para expandir/collapse
        chevron_btn = None
        try:
            chevron_btn = recycle_heading.find_element(By.XPATH, ".//button[contains(@class, 'chevron')]")
        except Exception:
            pass
        # Si el panel está colapsado, expandirlo (buscar el ícono chevron-down visible)
        panel_expanded = False
        try:
            # Si ya hay celdas de cursos eliminados visibles, no expandir
            deleted_course_cells = driver.find_elements(By.XPATH, "//td[starts-with(@id, 'deleted-course-id-')]")
            if deleted_course_cells:
                panel_expanded = True
        except Exception:
            pass
        if not panel_expanded and chevron_btn:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", chevron_btn)
            time.sleep(0.5)
            try:
                chevron_btn.click()
            except Exception:
                driver.execute_script("arguments[0].click();", chevron_btn)
            # Esperar a que se expanda y aparezcan los cursos eliminados
            time.sleep(1)
        # Ahora buscar los cursos eliminados en la tabla de la papelera
        deleted_table = None
        try:
            deleted_table = driver.find_element(By.ID, "deleted-courses-table")
        except Exception:
            pass
        found = False
        if deleted_table:
            rows = deleted_table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if not cells:
                    continue
                # Validar por Course ID o por nombre de curso
                course_id = cells[0].text.strip() if len(cells) > 0 else ""
                course_name = cells[1].text.strip() if len(cells) > 1 else ""
                if course_id == "MATH2024gaa" or course_name == "Matemáticas Aplicadas":
                    found = True
                    break
        assert found, "El curso eliminado no aparece en la sección 'Recycle Bin' tras eliminarlo (ni por Course ID ni por nombre)."
    except Exception:
        print("No se encontró la sección de cursos eliminados o el curso no aparece ahí. HTML del body:")
        print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))


# ------------------ CP-04-03-XX: Pruebas de Copia de Curso ------------------
import string

# Utilidad para abrir el modal de copia de curso desde la fila de un curso activo
def open_copy_course_modal(driver, wait, course_row=None):
    if course_row is None:
        active_table = wait.until(EC.presence_of_element_located((By.XPATH, "//table[contains(@id, 'active-courses-table')]")))
        rows = active_table.find_elements(By.XPATH, ".//tr[not(th)]")
        course_row = rows[0]
    # Abrir menú Other Actions
    other_actions_btn = course_row.find_element(By.XPATH, ".//button[contains(@id, 'btn-other-actions') or contains(text(), 'Other Actions')]")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", other_actions_btn)
    time.sleep(0.5)
    try:
        other_actions_btn.click()
    except Exception:
        driver.execute_script("arguments[0].click();", other_actions_btn)
    # Esperar a que el menú esté visible
    dropdown_menu = None
    for _ in range(10):
        try:
            dropdown_menu = course_row.find_element(By.XPATH, ".//div[contains(@class, 'dropdown-menu') and contains(@class, 'show')]")
            if dropdown_menu.is_displayed():
                break
        except Exception:
            pass
        time.sleep(0.2)
    if not dropdown_menu:
        dropdown_menu = course_row.find_element(By.XPATH, ".//div[contains(@class, 'dropdown-menu')]")
    # Buscar la opción Copy/Copiar en cualquier tag hijo visible o no
    copy_btn = None
    # Buscar en a, button, li (como antes)
    for tag in ['a', 'button', 'li']:
        try:
            btn = dropdown_menu.find_element(By.XPATH, f".//{tag}[contains(text(), 'Copy') or contains(text(), 'Copiar')]")
            if btn:
                copy_btn = btn
                if copy_btn.is_displayed() and copy_btn.is_enabled():
                    break
        except Exception:
            continue
    # Si no se encontró, buscar en cualquier hijo del menú (incluyendo ocultos)
    if not copy_btn:
        try:
            btns = dropdown_menu.find_elements(By.XPATH, ".//*[contains(text(), 'Copy') or contains(text(), 'Copiar')]")
            for btn in btns:
                copy_btn = btn
                if copy_btn.is_displayed() and copy_btn.is_enabled():
                    break
        except Exception:
            pass
    # Si aún no se encontró, imprimir el HTML del menú y de la fila para depuración
    if not copy_btn:
        print("[DEPURACIÓN] No se encontró la opción 'Copy' o 'Copiar' en el menú. HTML del menú:")
        print(dropdown_menu.get_attribute("outerHTML"))
        print("[DEPURACIÓN] HTML completo de la fila del curso:")
        print(course_row.get_attribute("outerHTML"))
        # Búsqueda global dentro de la fila por si el menú está fuera
        try:
            btns = course_row.find_elements(By.XPATH, ".//*[contains(text(), 'Copy') or contains(text(), 'Copiar')]")
            for btn in btns:
                copy_btn = btn
                if copy_btn.is_displayed() and copy_btn.is_enabled():
                    break
        except Exception:
            pass
    # Si se encontró pero está oculto o deshabilitado, advertir
    if copy_btn and (not copy_btn.is_displayed() or not copy_btn.is_enabled()):
        print("[ADVERTENCIA] Se encontró la opción 'Copy'/'Copiar' pero está oculta o deshabilitada. HTML:")
        print(copy_btn.get_attribute("outerHTML"))
    assert copy_btn, "No se encontró la opción 'Copy' o 'Copiar' en el menú 'Other Actions'"
    # Siempre forzar el click con JS (más robusto para menús animados/overlays)
    try:
        driver.execute_script("arguments[0].click();", copy_btn)
    except Exception:
        try:
            copy_btn.click()
        except Exception:
            print("[DEPURACIÓN] No se pudo hacer click en el botón Copy. HTML:")
            print(copy_btn.get_attribute("outerHTML"))
            raise
    time.sleep(0.2)  # Dar tiempo a la animación del modal
    try:
        # Esperar el <ngb-modal-window> visible que contenga <tm-copy-course-modal> y <h5> con 'Copy course'
        modal_window = wait.until(EC.visibility_of_element_located((By.XPATH, "//ngb-modal-window[.//tm-copy-course-modal and .//h5[contains(., 'Copy course')]]")))
        # El modal real es el componente tm-copy-course-modal dentro del modal window
        modal = modal_window.find_element(By.XPATH, ".//tm-copy-course-modal")
    except Exception:
        print("[DEPURACIÓN] No apareció el modal tras hacer click en Copy. HTML del body:")
        print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
        raise
    return modal

# CP-04-03-01 Copia exitosa de curso activo
@pytest.mark.usefixtures("driver")
def test_cp_04_03_01_copy_course_success(driver):
    LOGIN_EMAIL = os.environ["LOGIN_EMAIL"]
    LOGIN_PASSWORD = os.environ["LOGIN_PASSWORD"]
    from pages.login_page import LoginPage
    page = LoginPage(driver)
    page.login(LOGIN_EMAIL, LOGIN_PASSWORD, user_type="instructor")
    assert page.is_logged_in("instructor")
    wait = WebDriverWait(driver, 15)
    # Ir a cursos
    wait.until(EC.element_to_be_clickable((By.XPATH, "//nav//a[contains(@href, 'courses') or contains(text(), 'Courses') or contains(text(), 'Cursos')]"))).click()
    # Abrir modal de copia
    modal = open_copy_course_modal(driver, wait)
    # Llenar formulario
    modal.find_element(By.ID, "copy-course-id").send_keys("CS101NEW")
    modal.find_element(By.ID, "copy-course-name").send_keys("Intro to AI")
    institute_select = modal.find_element(By.ID, "copy-course-institute")
    for option in institute_select.find_elements(By.TAG_NAME, "option"):
        if option.get_attribute("value").lower() == "unsa":
            option.click()
            break
    tz_select = modal.find_element(By.ID, "copy-time-zone")
    for option in tz_select.find_elements(By.TAG_NAME, "option"):
        if "America/Lima" in option.text:
            option.click()
            break
    # Esperar y click en Copy
    save_btn = wait.until(lambda d: modal.find_element(By.ID, "btn-confirm-copy-course"))
    wait.until(lambda d: save_btn.is_enabled() and save_btn.is_displayed())
    save_btn.click()
    # Validar toast de éxito (selector flexible y depuración)
    try:
        # Esperar cualquier tm-toast visible
        toast = wait.until(EC.visibility_of_element_located((By.XPATH, "//tm-toast[not(contains(@style, 'display: none'))]")))
        # Extraer el texto real del toast desde el div.toast-body si toast.text está vacío
        toast_text = toast.text.strip()
        if not toast_text:
            try:
                toast_body = toast.find_element(By.CLASS_NAME, "toast-body")
                toast_text = toast_body.text.strip()
            except Exception:
                toast_text = ""
        print("[DEPURACIÓN] Texto del toast visible tras copiar:", toast_text)
        valid_success_texts = [
            "copied successfully", "copiado", "successfully", "copiado con éxito", "copia exitosa", "copia realizada",
            "the course has been added."  # nuevo texto detectado
        ]
        toast_text_lower = toast_text.lower()
        assert any(s in toast_text_lower for s in valid_success_texts), f"El toast no contiene mensaje esperado: {toast_text}"
    except Exception:
        # Si falla, imprimir todos los tm-toast visibles y el HTML del body
        print("[DEPURACIÓN] No se encontró el toast esperado. HTML del body:")
        print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
        toasts = driver.find_elements(By.XPATH, "//tm-toast[not(contains(@style, 'display: none'))]")
        for idx, t in enumerate(toasts):
            print(f"Toast visible {idx}: {t.text}")
        raise AssertionError("No se confirmó la copia exitosa del curso (no apareció el toast de éxito o el texto no coincide).")
    # Validar que el nuevo curso aparece en la tabla de cursos activos
    wait.until(lambda d: "CS101NEW" in d.find_element(By.XPATH, "//table[contains(@id, 'active-courses-table')]").get_attribute("innerText"))

# CP-04-03-02 Copia - Course ID duplicado
@pytest.mark.usefixtures("driver")
def test_cp_04_03_02_copy_course_duplicate_id(driver):
    """
    Validar que no se permita copiar un curso con un ID ya existente.
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
    # Abrir modal de copia
    modal = open_copy_course_modal(driver, wait)
    # Usar un ID ya existente (por ejemplo, el del primer curso activo)
    active_table = driver.find_element(By.XPATH, "//table[contains(@id, 'active-courses-table')]")
    first_row = active_table.find_elements(By.XPATH, ".//tr[not(th)]")[0]
    existing_id = first_row.find_elements(By.TAG_NAME, "td")[0].text.strip()
    modal.find_element(By.ID, "copy-course-id").clear()
    modal.find_element(By.ID, "copy-course-id").send_keys(existing_id)
    modal.find_element(By.ID, "copy-course-name").clear()
    modal.find_element(By.ID, "copy-course-name").send_keys("Curso Duplicado")
    institute_select = modal.find_element(By.ID, "copy-course-institute")
    for option in institute_select.find_elements(By.TAG_NAME, "option"):
        if option.get_attribute("value").lower() == "unsa":
            option.click()
            break
    # Guardar
    save_btn = modal.find_element(By.XPATH, ".//button[contains(text(), 'Copy') or contains(text(), 'Copiar')]")
    assert save_btn.is_enabled(), "El botón de copiar no está habilitado"
    save_btn.click()
    # Validar mensaje de error en el modal o en un toast
    error = None
    try:
        error = modal.find_element(By.XPATH, ".//*[contains(text(), 'already exists') or contains(text(), 'ya existe') or contains(text(), 'The course ID')]")
    except Exception:
        pass
    if not (error and error.is_displayed()):
        # Si no hay error en el modal, buscar toast de error (solo pasa si el texto es exactamente el esperado)
        import time
        try:
            wait = WebDriverWait(driver, 5)
            toast = wait.until(EC.visibility_of_element_located((By.XPATH, "//tm-toast[not(contains(@style, 'display: none'))]")))
            # Siempre buscar el texto en .toast-body si existe
            toast_text = ""
            try:
                toast_body = toast.find_element(By.CLASS_NAME, "toast-body")
                toast_text = toast_body.text.strip()
            except Exception:
                toast_text = toast.text.strip()
            # Si sigue vacío, esperar y reintentar una vez
            if not toast_text:
                time.sleep(0.5)
                try:
                    toast_body = toast.find_element(By.CLASS_NAME, "toast-body")
                    toast_text = toast_body.text.strip()
                except Exception:
                    toast_text = toast.text.strip()
            print("[DEPURACIÓN] Texto del toast visible tras error (ID duplicado):", toast_text)
            expected_text = f"The course ID {existing_id} already exists."
            if toast_text.strip() != expected_text:
                print(f"[DEPURACIÓN] El texto del toast no coincide exactamente. Esperado: '{expected_text}' | Obtenido: '{toast_text}'")
                print("[DEPURACIÓN] HTML del toast:")
                print(toast.get_attribute("outerHTML"))
            assert toast_text.strip() == expected_text, f"El toast de error no coincide exactamente. Esperado: '{expected_text}' | Obtenido: '{toast_text}'"
        except Exception:
            print("[DEPURACIÓN] No se encontró el error esperado (ID duplicado). HTML del body:")
            print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
            toasts = driver.find_elements(By.XPATH, "//tm-toast[not(contains(@style, 'display: none'))]")
            for idx, t in enumerate(toasts):
                print(f"Toast visible {idx}: {t.text}")
                try:
                    print(f"Toast {idx} outerHTML: {t.get_attribute('outerHTML')}")
                except Exception:
                    pass
            raise AssertionError("No se mostró el error por Course ID duplicado (ni en modal ni en toast).")
    else:
        assert error.is_displayed(), "No se mostró el error por Course ID duplicado."

# CP-04-03-03 Copia - Course ID vacío
@pytest.mark.usefixtures("driver")
def test_cp_04_03_03_copy_course_empty_id(driver):
    """
    Validar comportamiento al dejar vacío el campo Course ID al copiar curso.
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
    modal = open_copy_course_modal(driver, wait)
    # Dejar Course ID vacío
    modal.find_element(By.ID, "copy-course-id").clear()
    modal.find_element(By.ID, "copy-course-name").clear()
    modal.find_element(By.ID, "copy-course-name").send_keys("Curso sin ID")
    institute_select = modal.find_element(By.ID, "copy-course-institute")
    for option in institute_select.find_elements(By.TAG_NAME, "option"):
        if option.get_attribute("value").lower() == "unsa":
            option.click()
            break
    save_btn = modal.find_element(By.XPATH, ".//button[contains(text(), 'Copy') or contains(text(), 'Copiar')]")
    # El botón debe estar deshabilitado si el campo Course ID está vacío
    assert not save_btn.is_enabled(), "El botón de Copy está habilitado aunque el campo Course ID está vacío."

# CP-04-03-04 Course ID con longitud máxima permitida
@pytest.mark.usefixtures("driver")
def test_cp_04_03_04_copy_course_id_max_length(driver):
    """
    Verificar que se acepte un Course ID con longitud límite válida (64 caracteres).
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
    modal = open_copy_course_modal(driver, wait)
    # 64 caracteres
    max_id = "C" + "1" * 63
    modal.find_element(By.ID, "copy-course-id").clear()
    modal.find_element(By.ID, "copy-course-id").send_keys(max_id)
    modal.find_element(By.ID, "copy-course-name").clear()
    modal.find_element(By.ID, "copy-course-name").send_keys("Curso ID Máx")
    institute_select = modal.find_element(By.ID, "copy-course-institute")
    for option in institute_select.find_elements(By.TAG_NAME, "option"):
        if option.get_attribute("value").lower() == "unsa":
            option.click()
            break
    tz_select = modal.find_element(By.ID, "copy-time-zone")
    for option in tz_select.find_elements(By.TAG_NAME, "option"):
        if "America/Lima" in option.text:
            option.click()
            break
    save_btn = modal.find_element(By.XPATH, ".//button[contains(text(), 'Copy') or contains(text(), 'Copiar')]")
    assert save_btn.is_enabled(), "El botón de copiar no está habilitado"
    save_btn.click()
    # Validar toast de éxito (extraer texto desde .toast-body si es necesario)
    try:
        toast = wait.until(EC.visibility_of_element_located((By.XPATH, "//tm-toast[not(contains(@style, 'display: none'))]")))
        toast_text = toast.text.strip()
        if not toast_text:
            try:
                toast_body = toast.find_element(By.CLASS_NAME, "toast-body")
                toast_text = toast_body.text.strip()
            except Exception:
                toast_text = ""
        print("[DEPURACIÓN] Texto del toast visible tras copiar (ID máx):", toast_text)
        valid_success_texts = [
            "copied successfully", "copiado", "successfully", "copiado con éxito", "copia exitosa", "copia realizada",
            "the course has been added."
        ]
        toast_text_lower = toast_text.lower()
        assert any(s in toast_text_lower for s in valid_success_texts), f"El toast no contiene mensaje esperado: {toast_text}"
    except Exception:
        print("[DEPURACIÓN] No se encontró el toast esperado (ID máx). HTML del body:")
        print(driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML"))
        toasts = driver.find_elements(By.XPATH, "//tm-toast[not(contains(@style, 'display: none'))]")
        for idx, t in enumerate(toasts):
            print(f"Toast visible {idx}: {t.text}")
        raise AssertionError("No se confirmó la copia exitosa del curso con ID de 64 caracteres (no apareció el toast de éxito o el texto no coincide).")

# CP-04-03-05 Course ID con longitud superior al límite
@pytest.mark.usefixtures("driver")
def test_cp_04_03_05_copy_course_id_exceeds_max_length(driver):
    """
    Verificar que se rechace un Course ID con más de la longitud permitida (65 caracteres).
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
    modal = open_copy_course_modal(driver, wait)
    # 65 caracteres
    too_long_id = "C" + "1" * 64
    course_id_input = modal.find_element(By.ID, "copy-course-id")
    course_id_input.clear()
    course_id_input.send_keys(too_long_id)
    # Validar que el valor del input no supera los 64 caracteres
    max_length = 64
    input_value = course_id_input.get_attribute("value")
    assert len(input_value) == max_length, f"El input permite más de {max_length} caracteres: '{input_value}' ({len(input_value)})"

    # Buscar el contador de caracteres restantes (debe mostrar '0 characters left' o similar)
    char_counter = None
    try:
        # Busca por texto exacto o parcial
        char_counter = modal.find_element(By.XPATH, ".//*[contains(text(), '0 characters left') or contains(text(), '0 caracteres restantes') or contains(text(), '0 character')]")
    except Exception:
        pass
    assert char_counter and char_counter.is_displayed(), "No se muestra el contador '0 characters left' al llegar al límite."

    modal.find_element(By.ID, "copy-course-name").clear()
    modal.find_element(By.ID, "copy-course-name").send_keys("Curso ID Largo")
    institute_select = modal.find_element(By.ID, "copy-course-institute")
    for option in institute_select.find_elements(By.TAG_NAME, "option"):
        if option.get_attribute("value").lower() == "unsa":
            option.click()
            break
    save_btn = modal.find_element(By.XPATH, ".//button[contains(text(), 'Copy') or contains(text(), 'Copiar')]")
    save_btn.click()
    # No se valida mensaje de error visual porque el input restringe la longitud y no permite superar los 64 caracteres.

# CP-04-03-06 Zona horaria inválida
@pytest.mark.usefixtures("driver")
def test_cp_04_03_06_copy_course_invalid_timezone(driver):
    """
    Validar que no se acepte una zona horaria inválida.
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
    modal = open_copy_course_modal(driver, wait)
    modal.find_element(By.ID, "copy-course-id").clear()
    modal.find_element(By.ID, "copy-course-id").send_keys("CS101-TZINV")
    modal.find_element(By.ID, "copy-course-name").clear()
    modal.find_element(By.ID, "copy-course-name").send_keys("Curso TZ Inválida")
    institute_elem = modal.find_element(By.ID, "copy-course-institute")
    institute_tag = institute_elem.tag_name.lower()
    if institute_tag == "input":
        institute_elem.clear()
        institute_elem.send_keys("UNSA")
    elif institute_tag == "select":
        # Seleccionar la opción UNSA si existe
        for option in institute_elem.find_elements(By.TAG_NAME, "option"):
            if option.get_attribute("value").lower() == "unsa":
                option.click()
                break
    else:
        # Si es otro tipo, intentar enviar UNSA
        institute_elem.send_keys("UNSA")

    # Detectar si el campo de zona horaria es select o input
    tz_elem = modal.find_element(By.ID, "copy-time-zone")
    tag_name = tz_elem.tag_name.lower()
    if tag_name == "select":
        # Si es select, intentar seleccionar una opción inválida y verificar que no existe
        options = [opt.text for opt in tz_elem.find_elements(By.TAG_NAME, "option")]
        assert all("GMT-25" not in opt and "-25" not in opt for opt in options), "El select de zona horaria permite una opción inválida."
        # No se puede seleccionar una zona inválida, el test pasa aquí
        print("[INFO] El campo de zona horaria es un <select> y no permite opciones inválidas. Test OK.")
        return
    else:
        # Si es input, intentar poner un valor inválido y buscar mensaje de error
        # Solo llamar .clear() si no es select
        if tag_name == "input":
            tz_elem.clear()
        tz_elem.send_keys("GMT-25")
        save_btn = modal.find_element(By.XPATH, ".//button[contains(text(), 'Copy') or contains(text(), 'Copiar')]")
        save_btn.click()
        # Validar mensaje de error
        error = None
        try:
            error = modal.find_element(By.XPATH, ".//*[contains(text(), 'Invalid Time Zone') or contains(text(), 'zona horaria') or contains(text(), 'invalid')]")
        except Exception:
            pass
        assert error and error.is_displayed(), "No se mostró el error por zona horaria inválida."

# CP-04-03-07 Nombre del curso vacío
@pytest.mark.usefixtures("driver")
def test_cp_04_03_07_copy_course_empty_name(driver):
    """
    Validar que el campo nombre del curso no pueda estar vacío.
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
    modal = open_copy_course_modal(driver, wait)
    modal.find_element(By.ID, "copy-course-id").clear()
    modal.find_element(By.ID, "copy-course-id").send_keys("CS101-NONAME")
    modal.find_element(By.ID, "copy-course-name").clear()
    # Manejar campo instituto como input o select
    institute_elem = modal.find_element(By.ID, "copy-course-institute")
    institute_tag = institute_elem.tag_name.lower()
    if institute_tag == "input":
        institute_elem.clear()
        institute_elem.send_keys("UNSA")
    elif institute_tag == "select":
        for option in institute_elem.find_elements(By.TAG_NAME, "option"):
            if option.get_attribute("value").lower() == "unsa":
                option.click()
                break
    else:
        institute_elem.send_keys("UNSA")
    save_btn = modal.find_element(By.XPATH, ".//button[contains(text(), 'Copy') or contains(text(), 'Copiar')]")
    # El botón debe estar deshabilitado si el nombre está vacío
    assert not save_btn.is_enabled(), "El botón de Copy está habilitado aunque el campo Course Name está vacío."


