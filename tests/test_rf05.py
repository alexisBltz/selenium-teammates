from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

# CP-05-01-09
def test_cp_05_01_09_edit_session_empty_instructions(driver):
    """
    CP-05-01-09: Editar sesión con instrucciones vacías

    Objetivo:
        Verificar que el sistema acepta instrucciones vacías como valor límite mínimo válido.

    Técnica utilizada:
        Análisis de valores límite.

    Datos de prueba:
        - Time Zone: "America/Lima"
        - Session Name: "First team feedback session"
        - Instrucciones: ""
        - Fecha apertura: "2025-08-01"
        - Fecha cierre: "2025-08-01"
        - Período de gracia: 15 minutos
        - Visibilidad sesión: "2025-08-01"
        - Visibilidad respuesta: "2025-08-05"
        - Correos activados: Sin apertura, Sin cierre, Con resultados

    Resultado esperado:
        Edición exitosa: el sistema debe aceptar las instrucciones vacías y guardar correctamente la sesión editada.
    """
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")
    wait = WebDriverWait(driver, 15)

    # --- 1. Buscar la sesión del curso específico ---
    session_row = wait.until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'example-course-012')]/following-sibling::td[contains(text(), 'First team feedback session')]/.."
    )))

    edit_button = session_row.find_element(By.XPATH, ".//button[contains(text(), 'Edit')]")
    edit_button.click()
    wait.until(EC.url_contains("/web/instructor/sessions/edit"))
    time.sleep(1)

    # --- 2. Limpiar instrucciones ---
    driver.switch_to.default_content()
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return typeof tinymce !== 'undefined' && tinymce.activeEditor !== null")
    )
    driver.execute_script("tinymce.activeEditor.setContent(''); tinymce.activeEditor.save();")

    # --- 3. Seleccionar radios para visibilidad personalizada ---
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "btn-change-visibility"))
        ).click()
    except TimeoutException:
        print("Botón 'btn-change-visibility' no apareció, continuando porque ya se tocaron sus atributos en alguna edición previa.")
    time.sleep(1)

    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "session-visibility-custom"))
    ).click()

    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "response-visibility-custom"))
    ).click()

    # --- 3.1. Esperar a que aparezcan los 4 inputs de fecha ---
    WebDriverWait(driver, 10).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, 'input[ngbdatepicker][aria-label="Date"]')) >= 4
    )

    # --- 3.2. Mapear todos los inputs y selects ---
    date_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[ngbdatepicker][readonly][aria-label="Date"]')
    time_selects = driver.find_elements(By.CSS_SELECTOR, 'select[aria-label="Select time"]')

    assert len(date_inputs) >= 4, "Faltan inputs de fecha"
    assert len(time_selects) >= 4, "Faltan selects de hora"

    # --- 4. Insertar fechas y horas ---
    fechas = ["Fri, 29 Aug, 2025", "Fri, 29 Aug, 2025", "Fri, 29 Aug, 2025", "Fri, 29 Aug, 2025"]
    horas = ["02:00", "12:00", "02:00", "12:00"]

    # Insertar fechas
    for input_el, valor in zip(date_inputs, fechas):
        driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """, input_el, valor)

    # Establecer horas
    for select_el, valor in zip(time_selects, horas):
        for option in select_el.find_elements(By.TAG_NAME, 'option'):
            if valor in option.text:
                option.click()
                break

    # --- 5. Ajustar período de gracia ---
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "grace-period"))
    ).click()
        
    grace_period_select = driver.find_element(By.CSS_SELECTOR, 'select#grace-period')
    grace_period_select.click()
    option_grace_period = grace_period_select.find_element(By.XPATH, './/option[@value="1: 5"]')
    option_grace_period.click()

    # --- 6. Ajustar correos ---
    try:
        # Esperar hasta 5 segundos si aparece el botón
        change_email_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "btn-change-email"))
        )
        change_email_button.click()
    except TimeoutException:
        print(" Botón de cambio de correo no apareció, continuando porque ya se tocaron sus atributos en alguna edición previa.")

    # Esperar a que los checkboxes sean visibles y clicables
    wait = WebDriverWait(driver, 10)

    # Checkbox: Cierre (desmarcar si está activo)
    checkbox_close = wait.until(EC.element_to_be_clickable((By.ID, "email-closing")))
    if checkbox_close.is_selected():
        checkbox_close.click()

    # Checkbox: Resultados (marcar si no está activo)
    checkbox_result = wait.until(EC.element_to_be_clickable((By.ID, "email-published")))
    if not checkbox_result.is_selected():
        checkbox_result.click()

    # --- 7. Guardar cambios ---
    save_button = driver.find_element(By.CSS_SELECTOR, 'button.btn-success')
    save_button.click()

    try:
        toast = WebDriverWait(driver, 100).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//*[contains(text(), 'The feedback session has been updated')]"
            ))
        )
        assert toast.is_displayed(), "Toast encontrado pero no visible"
        print(" [✓] Éxito CP-05-01-09: Se edito la sesion con instrucciones vacías.")
    except TimeoutException:
        raise AssertionError(" [X] CP-05-01-09: No se aplicaron los cambios con éxito.")


# CP-05-01-10
def test_cp_05_01_10_edit_session_max_instruction_length(driver):
    """
    CP-05-01-10: Editar sesión con 2000 caracteres de instrucciones

    Objetivo:
        Verificar que el sistema acepta instrucciones con exactamente 2000 caracteres como límite superior válido

    Técnica utilizada:
        Análisis de valores límite.

    Datos de prueba:
        - Time Zone: "America/Lima"
        - Session Name: "First team feedback session"
        - Instrucciones: 2000 carácteres
        - Fecha apertura: "2025-08-01"
        - Fecha cierre: "2025-08-01"
        - Período de gracia: 15 minutos
        - Visibilidad sesión: "2025-08-01"
        - Visibilidad respuesta: "2025-08-05"
        - Correos activados: Sin apertura, Sin cierre, Con resultados

    Resultado esperado:
        Edición exitosa: el sistema debe aceptar las instrucciones vacías y guardar correctamente la sesión editada.
    """

    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")
    wait = WebDriverWait(driver, 15)

    # --- 1. Buscar la sesión del curso específico ---
    session_row = wait.until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'example-course-012')]/following-sibling::td[contains(text(), 'First team feedback session')]/.."
    )))

    edit_button = session_row.find_element(By.XPATH, ".//button[contains(text(), 'Edit')]")
    edit_button.click()
    wait.until(EC.url_contains("/web/instructor/sessions/edit"))
    time.sleep(1)
    
    # --- 2. Limpiar instrucciones ---
    driver.switch_to.default_content()
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return typeof tinymce !== 'undefined' && tinymce.activeEditor !== null")
    )
    driver.execute_script("tinymce.activeEditor.setContent('Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Nam quam nunc, blandit vel, luctus pulvinar, hendrerit id, lorem. Maecenas nec odio et ante tincidunt tempus. Donec vitae sapien ut libero venenatis faucibus. Nullam quis ante. Etiam sit amet orci eget eros faucibus tincidunt. Duis leo. Sed fringilla mauris sit amet nibh. Donec sodales sagittis magna. Sed consequat, leo eget bibendum sodales, augue velit cursus nunc, quis gravida magna mi a libero. Fusce vulputate eleifend sapien. Vestibulum purus quam, scelerisque ut, mollis sed, nonummy id, metus. Nullam accumsan lorem in dui. Cras ultricies mi eu turpis hendrerit fringilla. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; In ac dui quis mi consectetuer lacinia. Nam pretium turpis et arcu. Duis arcu tortor, suscipit eget, imperdiet nec, imperdiet iaculis, ipsum. Sed aliquam ultrices mauris. Integer ante arcu, accumsan a, consectetuer eget, posuere ut, mauris. Praesent adipiscing. Phasellus ullamcorper ipsum rutrum nunc. Nunc nonummy metus. Vestib123456789a123456789a123456789a12345678'); tinymce.activeEditor.save();")

    # --- 3. Seleccionar radios para visibilidad personalizada ---
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "btn-change-visibility"))
        ).click()
    except TimeoutException:
        print("Botón 'btn-change-visibility' no apareció, continuando porque ya se tocaron sus atributos en alguna edición previa.")
    time.sleep(1)

    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "session-visibility-custom"))
    ).click()

    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "response-visibility-custom"))
    ).click()

    # --- 3.1. Esperar a que aparezcan los 4 inputs de fecha ---
    WebDriverWait(driver, 10).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, 'input[ngbdatepicker][aria-label="Date"]')) >= 4
    )

    # --- 3.2. Mapear todos los inputs y selects ---
    date_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[ngbdatepicker][readonly][aria-label="Date"]')
    time_selects = driver.find_elements(By.CSS_SELECTOR, 'select[aria-label="Select time"]')

    assert len(date_inputs) >= 4, "Faltan inputs de fecha"
    assert len(time_selects) >= 4, "Faltan selects de hora"

    # --- 4. Insertar fechas y horas ---
    fechas = ["Fri, 29 Aug, 2025", "Fri, 29 Aug, 2025", "Fri, 29 Aug, 2025", "Fri, 29 Aug, 2025"]
    horas = ["02:00", "12:00", "02:00", "12:00"]

    # Insertar fechas
    for input_el, valor in zip(date_inputs, fechas):
        driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """, input_el, valor)

    # Establecer horas
    for select_el, valor in zip(time_selects, horas):
        for option in select_el.find_elements(By.TAG_NAME, 'option'):
            if valor in option.text:
                option.click()
                break

    # --- 5. Ajustar período de gracia ---
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "grace-period"))
    ).click()
        
    grace_period_select = driver.find_element(By.CSS_SELECTOR, 'select#grace-period')
    grace_period_select.click()
    option_grace_period = grace_period_select.find_element(By.XPATH, './/option[@value="1: 5"]')
    option_grace_period.click()

    # --- 6. Ajustar correos ---
    try:
        # Esperar hasta 5 segundos si aparece el botón
        change_email_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "btn-change-email"))
        )
        change_email_button.click()
    except TimeoutException:
        print(" Botón de cambio de correo no apareció, continuando porque ya se tocaron sus atributos en alguna edición previa.")

    # Esperar a que los checkboxes sean visibles y clicables
    wait = WebDriverWait(driver, 10)

    # Checkbox: Cierre (desmarcar si está activo)
    checkbox_close = wait.until(EC.element_to_be_clickable((By.ID, "email-closing")))
    if checkbox_close.is_selected():
        checkbox_close.click()

    # Checkbox: Resultados (marcar si no está activo)
    checkbox_result = wait.until(EC.element_to_be_clickable((By.ID, "email-published")))
    if not checkbox_result.is_selected():
        checkbox_result.click()

    # --- 7. Guardar cambios ---
    save_button = driver.find_element(By.CSS_SELECTOR, 'button.btn-success')
    save_button.click()

    try:
        toast = WebDriverWait(driver, 100).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//*[contains(text(), 'The feedback session has been updated')]"
            ))
        )
        assert toast.is_displayed(), "Toast encontrado pero no visible"
        print(" [✓] Éxito CP-05-01-10: Se edito las instrucciones con 2000 carácteres.")
    except TimeoutException:
        raise AssertionError(" [X] CP-05-01-10: No se aplicaron los cambios con éxito.")


# CP-05-01-11
def test_cp_05_01_11_edit_session_grace_period_zero(driver):
    """
    CP-05-01-11: Editar sesión con período de gracia en 0 minutos

    Objetivo:
        Verificar que el sistema acepta período de gracia de 0 minutos como límite mínimo válido

    Técnica utilizada:
        Análisis de valores límite y Tabla de decicsión.

    Datos de prueba:
        - Time Zone: "America/Lima"
        - Session Name: "First team feedback session"
        - Instrucciones: "Actualizadas"
        - Fecha apertura: "2025-08-01"
        - Fecha cierre: "2025-08-01"
        - Período de gracia: 0 minutos
        - Visibilidad sesión: "2025-08-01"
        - Visibilidad respuesta: "2025-08-05"
        - Correos activados: Sin apertura, Sin cierre, Con resultados

    Resultado esperado:
        Edición exitosa: el sistema debe aceptar las instrucciones vacías y guardar correctamente la sesión editada.
    """

    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")
    wait = WebDriverWait(driver, 15)

    # --- 1. Buscar la sesión del curso específico ---
    session_row = wait.until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'example-course-012')]/following-sibling::td[contains(text(), 'First team feedback session')]/.."
    )))

    edit_button = session_row.find_element(By.XPATH, ".//button[contains(text(), 'Edit')]")
    edit_button.click()
    wait.until(EC.url_contains("/web/instructor/sessions/edit"))
    time.sleep(1)
    
    # --- 2. Limpiar instrucciones ---
    driver.switch_to.default_content()
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return typeof tinymce !== 'undefined' && tinymce.activeEditor !== null")
    )
    driver.execute_script("tinymce.activeEditor.setContent('Actualizadas'); tinymce.activeEditor.save();")

    # --- 3. Seleccionar radios para visibilidad personalizada ---
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "btn-change-visibility"))
        ).click()
    except TimeoutException:
        print("Botón 'btn-change-visibility' no apareció, continuando porque ya se tocaron sus atributos en alguna edición previa.")
    time.sleep(1)

    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "session-visibility-custom"))
    ).click()

    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "response-visibility-custom"))
    ).click()

    # --- 3.1. Esperar a que aparezcan los 4 inputs de fecha ---
    WebDriverWait(driver, 10).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, 'input[ngbdatepicker][aria-label="Date"]')) >= 4
    )

    # --- 3.2. Mapear todos los inputs y selects ---
    date_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[ngbdatepicker][readonly][aria-label="Date"]')
    time_selects = driver.find_elements(By.CSS_SELECTOR, 'select[aria-label="Select time"]')

    assert len(date_inputs) >= 4, "Faltan inputs de fecha"
    assert len(time_selects) >= 4, "Faltan selects de hora"

    # --- 4. Insertar fechas y horas ---
    fechas = ["Fri, 29 Aug, 2025", "Fri, 29 Aug, 2025", "Fri, 29 Aug, 2025", "Fri, 29 Aug, 2025"]
    horas = ["02:00", "12:00", "02:00", "12:00"]

    # Insertar fechas
    for input_el, valor in zip(date_inputs, fechas):
        driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """, input_el, valor)

    # Establecer horas
    for select_el, valor in zip(time_selects, horas):
        for option in select_el.find_elements(By.TAG_NAME, 'option'):
            if valor in option.text:
                option.click()
                break

    # --- 5. Ajustar período de gracia ---
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "grace-period"))
    ).click()
        
    grace_period_select = driver.find_element(By.CSS_SELECTOR, 'select#grace-period')
    grace_period_select.click()
    option_grace_period = grace_period_select.find_element(By.XPATH, './/option[@value="0: 0"]')
    option_grace_period.click()

    # --- 6. Ajustar correos ---
    try:
        # Esperar hasta 5 segundos si aparece el botón
        change_email_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "btn-change-email"))
        )
        change_email_button.click()
        
    except TimeoutException:
        print(" Botón de cambio de correo no apareció, continuando porque ya se tocaron sus atributos en alguna edición previa.")

    # Esperar a que los checkboxes sean visibles y clicables
    wait = WebDriverWait(driver, 10)

    # Checkbox: Cierre (desmarcar si está activo)
    checkbox_close = wait.until(EC.element_to_be_clickable((By.ID, "email-closing")))
    if checkbox_close.is_selected():
        checkbox_close.click()

    # Checkbox: Resultados (marcar si no está activo)
    checkbox_result = wait.until(EC.element_to_be_clickable((By.ID, "email-published")))
    if not checkbox_result.is_selected():
        checkbox_result.click()

    # --- 7. Guardar cambios ---
    save_button = driver.find_element(By.CSS_SELECTOR, 'button.btn-success')
    save_button.click()

    try:
        toast = WebDriverWait(driver, 100).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//*[contains(text(), 'The feedback session has been updated')]"
            ))
        )
        assert toast.is_displayed(), "Toast encontrado pero no visible"
        print(" [✓] Éxito CP-05-01-11: Se edito la sesion con instrucciones vacías.")
    except TimeoutException:
        raise AssertionError(" [X] CP-05-01-11: No se aplicaron los cambios con éxito.")


# CP-05-01-12
def test_cp_05_01_12_edit_session_negative_grace_period(driver):
    """
    CP-05-01-12: Editar sesión con período de gracia negativo

    Objetivo:
        Verificar que el sistema rechaza períodos de gracia negativos

    Técnica utilizada:
        Análisis de valores límite

    Datos de prueba:
        - Time Zone: "America/Lima"
        - Session Name: "First team feedback session"
        - Instrucciones: "Actualizadas"
        - Fecha apertura: "2025-08-01"
        - Fecha cierre: "2025-08-01"
        - Período de gracia: -1 min
        - Visibilidad sesión: "2025-08-01"
        - Visibilidad respuesta: "2025-08-05"
        - Correos activados: Sin apertura, Con cierre, Con resultados

    Resultado esperado:
        Error: el sistema debe rechazar el valor por estar fuera del límite permitido para el período de gracia.
    """

    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")
    wait = WebDriverWait(driver, 15)

    # --- 1. Buscar la sesión del curso específico ---
    session_row = wait.until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'example-course-012')]/following-sibling::td[contains(text(), 'First team feedback session')]/.."
    )))

    edit_button = session_row.find_element(By.XPATH, ".//button[contains(text(), 'Edit')]")
    edit_button.click()
    wait.until(EC.url_contains("/web/instructor/sessions/edit"))
    time.sleep(1)
    
    # --- 2. Limpiar instrucciones ---
    driver.switch_to.default_content()
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return typeof tinymce !== 'undefined' && tinymce.activeEditor !== null")
    )
    driver.execute_script("tinymce.activeEditor.setContent('Actualizadas'); tinymce.activeEditor.save();")

    # --- 3. Seleccionar radios para visibilidad personalizada ---
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "btn-change-visibility"))
        ).click()
    except TimeoutException:
        print("Botón 'btn-change-visibility' no apareció, porque ya se tocaron sus atributos en alguna edición previa.")
    time.sleep(1)

    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "session-visibility-custom"))
    ).click()

    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "response-visibility-custom"))
    ).click()

    # --- 3.1. Esperar a que aparezcan los 4 inputs de fecha ---
    WebDriverWait(driver, 10).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, 'input[ngbdatepicker][aria-label="Date"]')) >= 4
    )

    # --- 3.2. Mapear todos los inputs y selects ---
    date_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[ngbdatepicker][readonly][aria-label="Date"]')
    time_selects = driver.find_elements(By.CSS_SELECTOR, 'select[aria-label="Select time"]')

    assert len(date_inputs) >= 4, "Faltan inputs de fecha"
    assert len(time_selects) >= 4, "Faltan selects de hora"

    # --- 4. Insertar fechas y horas ---
    fechas = ["Fri, 29 Aug, 2025", "Fri, 29 Aug, 2025", "Fri, 29 Aug, 2025", "Fri, 29 Aug, 2025"]
    horas = ["02:00", "12:00", "02:00", "12:00"]

    # Insertar fechas
    for input_el, valor in zip(date_inputs, fechas):
        driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """, input_el, valor)

    # Establecer horas
    for select_el, valor in zip(time_selects, horas):
        for option in select_el.find_elements(By.TAG_NAME, 'option'):
            if valor in option.text:
                option.click()
                break

    # --- 5. Ajustar período de gracia ---
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "grace-period"))
    ).click()
        
    grace_period_select = driver.find_element(By.CSS_SELECTOR, 'select#grace-period')
    driver.execute_script("""
    arguments[0].value = '-1';
    arguments[0].dispatchEvent(new Event('change'));
    """, grace_period_select)

    # --- 6. Ajustar correos ---
    try:
        # Esperar hasta 5 segundos si aparece el botón
        change_email_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "btn-change-email"))
        )
        change_email_button.click()
        
    except TimeoutException:
        print("Botón de cambio de correo no apareció, se continúa sin hacer clic, porque ya se tocaron sus atributos en alguna edición previa.")

    # Esperar a que los checkboxes sean visibles y clicables
    wait = WebDriverWait(driver, 10)

    # Checkbox: Cierre (desmarcar si está activo)
    checkbox_close = wait.until(EC.element_to_be_clickable((By.ID, "email-closing")))
    if checkbox_close.is_selected():
        checkbox_close.click()

    # Checkbox: Resultados (marcar si no está activo)
    checkbox_result = wait.until(EC.element_to_be_clickable((By.ID, "email-published")))
    if not checkbox_result.is_selected():
        checkbox_result.click()

    # --- 7. Guardar cambios ---
    save_button = driver.find_element(By.CSS_SELECTOR, 'button.btn-success')
    save_button.click()

    try:
        toast = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//*[contains(@class, 'toast-body') and contains(text(), 'The server encountered an error')]"
            ))
        )
        assert toast.is_displayed(), "Toast encontrado pero no visible"
        print(" [✓] Éxito CP-05-01-12: El sistema rechazó el período de gracia negativo como se esperaba.")
    except TimeoutException:
        raise AssertionError(" [X] CP-05-01-12: No se aplicaron los cambios con éxito.")
    

# CP-05-01-13
def test_cp_05_01_13_edit_session_emails_open_close_enabled(driver):
    """
    CP-05-01-13: Correos solo apertura y cierre activados

    Objetivo:
        Verificar que el sistema configura correctamente el envío de correos cuando solo apertura y cierre están activados

    Técnica utilizada:
        Tabla de decisión (R2)

    Datos de prueba:
        - Time Zone: "America/Lima"
        - Session Name: "First team feedback session"
        - Instrucciones: "Actualizadas"
        - Fecha apertura: "2025-08-01"
        - Fecha cierre: "2025-08-15"
        - Período de gracia: 15 minutos
        - Visibilidad sesión: "2025-07-31"
        - Visibilidad respuesta: "2025-08-05"
        - Correos activados: Con apertura, Con cierre, Sin resultados

    Resultado esperado:
        Edición exitosa: el sistema enviará correos de apertura y cierre solamente.
    """

    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")
    wait = WebDriverWait(driver, 15)

    # --- 1. Buscar la sesión del curso específico ---
    session_row = wait.until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'example-course-012')]/following-sibling::td[contains(text(), 'First team feedback session')]/.."
    )))

    edit_button = session_row.find_element(By.XPATH, ".//button[contains(text(), 'Edit')]")
    edit_button.click()
    wait.until(EC.url_contains("/web/instructor/sessions/edit"))
    time.sleep(1)

    # --- 2. Limpiar instrucciones ---
    driver.switch_to.default_content()
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return typeof tinymce !== 'undefined' && tinymce.activeEditor !== null")
    )
    driver.execute_script("tinymce.activeEditor.setContent('Actualizadas'); tinymce.activeEditor.save();")

    # --- 3. Seleccionar radios para visibilidad personalizada ---
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "btn-change-visibility"))
        ).click()
    except TimeoutException:
        print("Botón 'btn-change-visibility' no apareció, porque ya se tocaron sus atributos en alguna edición previa.")
    time.sleep(1)

    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "session-visibility-custom"))
    ).click()

    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "response-visibility-custom"))
    ).click()

    # --- 3.1. Esperar a que aparezcan los 4 inputs de fecha ---
    WebDriverWait(driver, 10).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, 'input[ngbdatepicker][aria-label="Date"]')) >= 4
    )

    # --- 3.2. Mapear todos los inputs y selects ---
    date_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[ngbdatepicker][readonly][aria-label="Date"]')
    time_selects = driver.find_elements(By.CSS_SELECTOR, 'select[aria-label="Select time"]')

    assert len(date_inputs) >= 4, "Faltan inputs de fecha"
    assert len(time_selects) >= 4, "Faltan selects de hora"

    # --- 4. Insertar fechas y horas ---
    fechas = ["Fri, 29 Aug, 2025", "Fri, 29 Aug, 2025", "Fri, 29 Aug, 2025", "Fri, 29 Aug, 2025"]
    horas = ["02:00", "12:00", "02:00", "12:00"]

    # Insertar fechas
    for input_el, valor in zip(date_inputs, fechas):
        driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """, input_el, valor)

    # Establecer horas
    for select_el, valor in zip(time_selects, horas):
        for option in select_el.find_elements(By.TAG_NAME, 'option'):
            if valor in option.text:
                option.click()
                break
        
    # --- 5. Ajustar período de gracia ---
    # Valores válidos del período de gracia: 0: 0, 1: 5, 2: 10, 3: 15, 4: 20, 5: 25, 6: 30
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "grace-period"))
    ).click()
        
    grace_period_select = driver.find_element(By.CSS_SELECTOR, 'select#grace-period')
    grace_period_select.click()
    option_grace_period = grace_period_select.find_element(By.XPATH, './/option[@value="1: 5"]')
    option_grace_period.click()

    # --- 6. Ajustar correos ---
    try:
        # Esperar hasta 5 segundos si aparece el botón
        change_email_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "btn-change-email"))
        )
        change_email_button.click()
        
    except TimeoutException:
        print("Botón de cambio de correo no apareció, se continúa sin hacer clic, porque ya se tocaron sus atributos en alguna edición previa.")

    # Esperar a que los checkboxes sean visibles y clicables
    wait = WebDriverWait(driver, 10)

    # Checkbox: Cierre (desmarcar si está activo)
    checkbox_close = wait.until(EC.element_to_be_clickable((By.ID, "email-closing")))
    if not checkbox_close.is_selected():
        checkbox_close.click()

    # Checkbox: Resultados (marcar si no está activo)
    checkbox_result = wait.until(EC.element_to_be_clickable((By.ID, "email-published")))
    if checkbox_result.is_selected():
        checkbox_result.click()

    # --- 7. Guardar cambios ---
    save_button = driver.find_element(By.CSS_SELECTOR, 'button.btn-success')
    save_button.click()

    try:
        toast = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//*[contains(@class, 'toast-body') and contains(text(), 'The feedback session has been updated.')]"
            ))
        )
        assert toast.is_displayed(), "Toast encontrado pero no visible"
        print(" [✓] Éxito CP-05-01-13: Se cambio la sesión a correos solo apertura y cierre.")
    except TimeoutException:
        raise AssertionError(" [X] CP-05-01-13: No se aplicaron los cambios con éxito.")


# CP-05-01-14
def test_cp_05_01_14_edit_session_email_open_only_enabled(driver):
    """
    CP-05-01-14: Correos solo apertura activado

    Objetivo:
        Verificar que el sistema configura correctamente el envío de correos cuando solo apertura está activada

    Técnica utilizada:
        Tabla de decisión (R4)

    Datos de prueba:
        - Time Zone: "America/Lima"
        - Session Name: "First team feedback session"
        - Instrucciones: "Actualizadas"
        - Fecha apertura: "2025-08-01"
        - Fecha cierre: "2025-08-15"
        - Período de gracia: 15 minutos
        - Visibilidad sesión: "2025-07-31"
        - Visibilidad respuesta: "2025-08-05"
        - Correos activados: Con apertura, Sin cierre, Sin resultados

    Resultado esperado:
        Edición exitosa: el sistema enviará solo correo de apertura.
    """

    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")
    wait = WebDriverWait(driver, 15)

    # --- 1. Buscar la sesión del curso específico ---
    session_row = wait.until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'example-course-012')]/following-sibling::td[contains(text(), 'First team feedback session')]/.."
    )))

    edit_button = session_row.find_element(By.XPATH, ".//button[contains(text(), 'Edit')]")
    edit_button.click()
    wait.until(EC.url_contains("/web/instructor/sessions/edit"))
    time.sleep(1)
    
    # --- 2. Limpiar instrucciones ---
    driver.switch_to.default_content()
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return typeof tinymce !== 'undefined' && tinymce.activeEditor !== null")
    )
    driver.execute_script("tinymce.activeEditor.setContent('Actualizadas'); tinymce.activeEditor.save();")

    # --- 3. Seleccionar radios para visibilidad personalizada ---
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "btn-change-visibility"))
        ).click()
    except TimeoutException:
        print("Botón 'btn-change-visibility' no apareció, porque ya se tocaron sus atributos en alguna edición previa.")
    time.sleep(1)

    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "session-visibility-custom"))
    ).click()

    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "response-visibility-custom"))
    ).click()

    # --- 3.1. Esperar a que aparezcan los 4 inputs de fecha ---
    WebDriverWait(driver, 10).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, 'input[ngbdatepicker][aria-label="Date"]')) >= 4
    )

    # --- 3.2. Mapear todos los inputs y selects ---
    date_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[ngbdatepicker][readonly][aria-label="Date"]')
    time_selects = driver.find_elements(By.CSS_SELECTOR, 'select[aria-label="Select time"]')

    assert len(date_inputs) >= 4, "Faltan inputs de fecha"
    assert len(time_selects) >= 4, "Faltan selects de hora"

    # --- 4. Insertar fechas y horas ---
    fechas = ["Fri, 29 Aug, 2025", "Fri, 29 Aug, 2025", "Fri, 29 Aug, 2025", "Fri, 29 Aug, 2025"]
    horas = ["02:00", "12:00", "02:00", "12:00"]

    # Insertar fechas
    for input_el, valor in zip(date_inputs, fechas):
        driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """, input_el, valor)

    # Establecer horas
    for select_el, valor in zip(time_selects, horas):
        for option in select_el.find_elements(By.TAG_NAME, 'option'):
            if valor in option.text:
                option.click()
                break
        
    # --- 5. Ajustar período de gracia ---
    # Valores válidos del período de gracia: 0: 0, 1: 5, 2: 10, 3: 15, 4: 20, 5: 25, 6: 30
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "grace-period"))
    ).click()
        
    grace_period_select = driver.find_element(By.CSS_SELECTOR, 'select#grace-period')
    grace_period_select.click()
    option_grace_period = grace_period_select.find_element(By.XPATH, './/option[@value="1: 5"]')
    option_grace_period.click()

    # --- 6. Ajustar correos ---
    try:
        # Esperar hasta 5 segundos si aparece el botón
        change_email_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "btn-change-email"))
        )
        change_email_button.click()
        
    except TimeoutException:
        print("Botón de cambio de correo no apareció, se continúa sin hacer clic, porque ya se tocaron sus atributos en alguna edición previa.")

    # Esperar a que los checkboxes sean visibles y clicables
    wait = WebDriverWait(driver, 10)

    # Checkbox: Cierre (desmarcar si está activo)
    checkbox_close = wait.until(EC.element_to_be_clickable((By.ID, "email-closing")))
    if checkbox_close.is_selected():
        checkbox_close.click()

    # Checkbox: Resultados (marcar si no está activo)
    checkbox_result = wait.until(EC.element_to_be_clickable((By.ID, "email-published")))
    if checkbox_result.is_selected():
        checkbox_result.click()

    # --- 7. Guardar cambios ---
    save_button = driver.find_element(By.CSS_SELECTOR, 'button.btn-success')
    save_button.click()

    try:
        toast = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//*[contains(@class, 'toast-body') and contains(text(), 'The feedback session has been updated.')]"
            ))
        )
        assert toast.is_displayed(), "Toast encontrado pero no visible"
        print(" [✓] Éxito CP-05-01-14: Se cambio la sesión a correos solo apertura.")
    except TimeoutException:
        raise AssertionError(" [X] CP-05-01-14: No se aplicaron los cambios con éxito.")


# CP-05-01-15
def test_cp_05_01_15_edit_session_no_emails_enabled(driver):
    """
    CP-05-01-15: Ningún correo activado

    Objetivo:
        Verificar que el sistema configura correctamente cuando ningún correo automático está activado

    Técnica utilizada:
        Tabla de decisión (R8)

    Datos de prueba:
        - Time Zone: "America/Lima"
        - Session Name: "First team feedback session"
        - Instrucciones: "Actualizadas"
        - Fecha apertura: "2025-08-01"
        - Fecha cierre: "2025-08-15"
        - Período de gracia: 15 minutos
        - Visibilidad sesión: "2025-07-31"
        - Visibilidad respuesta: "2025-08-05"
        - Correos activados: Sin apertura, Sin cierre, Sin resultados

    Resultado esperado:
        Edición exitosa: el sistema no enviará ningún correo automático.
    """

    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")
    wait = WebDriverWait(driver, 15)

    # --- 1. Buscar la sesión del curso específico ---
    session_row = wait.until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'example-course-012')]/following-sibling::td[contains(text(), 'First team feedback session')]/.."
    )))

    edit_button = session_row.find_element(By.XPATH, ".//button[contains(text(), 'Edit')]")
    edit_button.click()
    wait.until(EC.url_contains("/web/instructor/sessions/edit"))
    time.sleep(1)

    # --- 6. Ajustar correos ---
    try:
        # Esperar hasta 5 segundos si aparece el botón
        change_email_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "btn-change-email"))
        )
        change_email_button.click()
        
    except TimeoutException:
        print("Botón de cambio de correo no apareció, se continúa sin hacer clic, porque ya se tocaron sus atributos en alguna edición previa.")

    # Esperar a que los checkboxes sean visibles y clicables
    wait = WebDriverWait(driver, 10)

    # Checkbox: Cierre (desmarcar si está activo)
    checkbox_close = wait.until(EC.element_to_be_clickable((By.ID, "email-closing")))
    if checkbox_close.is_selected():
        checkbox_close.click()

    # Checkbox: Resultados (marcar si no está activo)
    checkbox_result = wait.until(EC.element_to_be_clickable((By.ID, "email-published")))
    if checkbox_result.is_selected():
        checkbox_result.click()

    # --- 7. Guardar cambios ---
    save_button = driver.find_element(By.CSS_SELECTOR, 'button.btn-success')
    save_button.click()

    try:
        toast = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//*[contains(@class, 'toast-body') and contains(text(), 'The feedback session has been updated.')]"
            ))
        )
        assert toast.is_displayed(), "Toast encontrado pero no visible"
        print(" [✓] Éxito CP-05-01-15: Se cambio la sesión a ningún correo activado.")
    except TimeoutException:
        raise AssertionError(" [X] CP-05-01-15: No se aplicaron los cambios con éxito.")
    

# CP-05-02-01
def test_cp_05_02_01_logical_delete_active_feedback_session(driver):
    """
    CP-05-02-01: Eliminar lógicamente una sesión de feedback activa

    Objetivo:
        Verificar cambio de estado de sesión de activa a eliminada

    Técnica utilizada:
        Transición de Estados

    Datos de prueba:
        - Sesión seleccionada: "Sesión Eliminar"
        - Acción: Eliminar (con confirmación en modal)

    Resultado esperado:
        La sesión cambia de estado "activa" a "eliminada", desaparece de la tabla de activas y aparece en la tabla de eliminadas.
    """

    wait = WebDriverWait(driver, 15)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")

    # --- 1. Buscar y eliminar sesión ---
    session_row = wait.until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'example-course-012')]/following-sibling::td[contains(text(), 'Sesión Eliminar')]/.."
    )))
    delete_button = session_row.find_element(By.XPATH, ".//button[contains(text(), 'Delete')]")
    delete_button.click()
    time.sleep(1)

    # --- 2. Confirmar en el modal ---
    confirm_button = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//tm-confirmation-modal//button[text()='Yes']"
    )))
    confirm_button.click()

    expand_button = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//button[@aria-label='Expand panel' and contains(@class, 'btn-course')]"
    )))
    expand_button.click()

    time.sleep(1)

    # --- 3. Verificar que aparece el toast con el mensaje correcto ---
    toast = wait.until(EC.presence_of_element_located((
        By.XPATH, "//div[contains(@class, 'toast-body') and contains(text(), 'The feedback session has been deleted')]"
    )))
    assert toast.is_displayed(), " [X] CP-05-02-01: No apareció el mensaje de confirmación de eliminación"
    print(" [✓] Éxito CP-05-02-01: Se elimino la sesión correctamente.")
    


# CP-05-02-02
def test_cp_05_02_02_cancel_delete_session(driver):
    """
    CP-05-02-02: Cancelar eliminación de sesión

    Objetivo:
        Verificar que se mantiene el estado al cancelar eliminación

    Técnica utilizada:
        Transición de Estados

    Datos de prueba:
        - Sesión seleccionada: "ffre"
        - Acción: Cancelar en modal de confirmación

    Resultado esperado:
        La sesión mantiene el estado "activa", el modal se cierra y no hay cambios en las tablas.
    """

    wait = WebDriverWait(driver, 15)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")

    # --- 1. Buscar y eliminar sesión ---
    session_row = wait.until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'gsotocco.uns-demo')]/following-sibling::td[contains(text(), 'Sesión Eliminar Cancelar')]/.."
    )))
    delete_button = session_row.find_element(By.XPATH, ".//button[contains(text(), 'Delete')]")
    delete_button.click()
    time.sleep(1)

    # --- 2. Cancelar en el modal ---
    cancel_button = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//tm-confirmation-modal//button[contains(text(), 'No, cancel the operation')]"
    )))
    cancel_button.click()

    # --- 3. Validar que la sesión aún esté visible (no fue eliminada) ---
    try:
        wait.until(EC.presence_of_element_located((
            By.XPATH, "//td[contains(text(), 'gsotocco.uns-demo')]/following-sibling::td[contains(text(), 'Sesión Eliminar Cancelar')]"
        )))
        print(" [✓] Éxito CP-05-02-02: La sesión no fue eliminada, permanece en la tabla activa.")
    except:
        assert False, " [X] CP-05-02-02: La sesión no se encontró tras cancelar la operación."
    

# CP-05-03-01
def test_cp_05_03_01_successful_session_copy(driver):
    """
    CP-05-03-01: Copia exitosa de sesión a un curso

    Objetivo:
        Verificar copia exitosa de sesión a un curso destino válido

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - Nombre para sesión copiada: "Copia - ffff"

    Resultado esperado:
        Mensaje: “The feedback session has been copied. Please modify settings/questions as necessary”
    """

    wait = WebDriverWait(driver, 15)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")

    # --- 1. Buscar y eliminar sesión ---
    session_row = wait.until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'gsotocco.uns-demo')]/following-sibling::td[contains(text(), 'Sesión Eliminar Cancelar')]/.."
    )))
    delete_button = session_row.find_element(By.XPATH, ".//button[contains(text(), 'Copy')]")
    delete_button.click()
    time.sleep(1)

    # --- 2. Buscar el input por id y asignar el nuevo nombre ---
    input_nombre_copia = wait.until(EC.presence_of_element_located((
        By.ID, "copy-session-name"
    )))
    input_nombre_copia.clear()
    input_nombre_copia.send_keys("Copia - ffff")

    # --- 3. Click en el checkbox de copia ---
    checkbox = wait.until(EC.presence_of_element_located((
        By.XPATH, "//label[contains(., 'example-course-014')]/input[@type='checkbox']"
    )))
    checkbox.click()

    # --- 4. Confirmar cambio. ---
    btn_confirm_copy = wait.until(EC.presence_of_element_located((
        By.ID, "btn-confirm-copy-course"
    )))
    btn_confirm_copy.click()

    wait.until(EC.url_contains("/web/instructor/sessions/edit?courseid=example-course-014"))
    time.sleep(1)

    # --- 3. Validar que la sesión aún esté visible (no fue eliminada) --- 
    toast = wait.until(EC.presence_of_element_located((
        By.XPATH, "//div[contains(@class, 'toast-body') and contains(text(), 'The feedback session has been copied. Please modify settings/questions as necessary.')]"
    )))
    assert toast.is_displayed(), " [X] CP-05-03-01: No se logro copiar correctamente la sesión."
    print(" [✓] Éxito CP-05-03-01: Se copio la sesión correctamente.")
    

# CP-05-03-02
def test_cp_05_03_02_copy_session_empty_name_validation(driver):
    """
    CP-05-03-02: Copia con nombre vacío

    Objetivo:
        Verificar validación de nombre obligatorio en copia

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - Nombre para sesión copiada: " "

    Resultado esperado:
        Se informa que el campo de nombre para la sesión copia no puede estar vacío.
    """

    wait = WebDriverWait(driver, 15)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")

    # --- 1. Buscar y eliminar sesión ---
    session_row = wait.until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'gsotocco.uns-demo')]/following-sibling::td[contains(text(), 'Sesión Eliminar Cancelar')]/.."
    )))
    delete_button = session_row.find_element(By.XPATH, ".//button[contains(text(), 'Copy')]")
    delete_button.click()
    time.sleep(1)

    # --- 2. Buscar el input por id y asignar el nuevo nombre ---
    input_nombre_copia = wait.until(EC.presence_of_element_located((
        By.ID, "copy-session-name"
    )))
    input_nombre_copia.clear()
    input_nombre_copia.send_keys(" ")   # NOMBRE VACÍO

    # --- 3. Click en el checkbox de copia ---
    checkbox = wait.until(EC.presence_of_element_located((
        By.XPATH, "//label[contains(., 'example-course-014')]/input[@type='checkbox']"
    )))
    checkbox.click()

    # --- 4. Confirmar cambio. ---
    btn_confirm_copy = wait.until(EC.presence_of_element_located((
        By.ID, "btn-confirm-copy-course"
    )))
    btn_confirm_copy.click()
    time.sleep(1)
    
    # --- 3. Validar que la sesión aún esté visible (no fue eliminada) --- 
    error_toast = wait.until(EC.presence_of_element_located((
        By.XPATH, "//div[contains(@class, 'toast-body') and contains(text(), 'Error copying to example-course-014')]"
    )))
    assert error_toast.is_displayed(), " [X] CP-05-03-02: No apareció el mensaje de error esperado al copiar la sesión."
    print(" [✓] Éxito CP-05-03-02: El sistema lanzo el mensaje de error sobre el nombre vacío en la sesión.")


# CP-05-03-03
def test_cp_05_03_03_auto_time_adjustment_on_session_copy(driver):
    """
    CP-05-03-03: Validar ajuste automático de tiempos en copia de sesión

    Objetivo:
        Verificar que el sistema ajusta automáticamente los tiempos de la sesión al copiarla a un curso donde los valores originales no son válidos, y que muestra advertencias al instructor.

    Técnica utilizada:
        Transición de Estados + Tabla de Decisión

    Datos de prueba:
        - Nombre de sesión: "Copia Session with different question types"

    Resultado esperado:
        Se muestra mensaje tipo: “Note On Modified Session Timings”, donde se indican las fechas modificadas (original vs nueva).
    """

    wait = WebDriverWait(driver, 15)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")

    # --- 1. Buscar y eliminar sesión ---
    session_row = wait.until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'gsotocco.uns-demo')]/following-sibling::td[contains(text(), 'Second team feedback session (point-based)')]/.."
    )))
    delete_button = session_row.find_element(By.XPATH, ".//button[contains(text(), 'Copy')]")
    delete_button.click()
    time.sleep(1)

    # --- 2. Buscar el input por id y asignar el nuevo nombre ---
    input_nombre_copia = wait.until(EC.presence_of_element_located((
        By.ID, "copy-session-name"
    )))
    input_nombre_copia.clear()
    input_nombre_copia.send_keys("Copia TIEMPOS VENCIDOS")

    # --- 3. Click en el checkbox de copia ---
    checkbox = wait.until(EC.presence_of_element_located((
        By.XPATH, "//label[contains(., 'example-course-012')]/input[@type='checkbox']"
    )))
    checkbox.click()

    # --- 4. Confirmar cambio. ---
    btn_confirm_copy = wait.until(EC.presence_of_element_located((
        By.ID, "btn-confirm-copy-course"
    )))
    btn_confirm_copy.click()
    time.sleep(1)
    
    # --- 3. Validar que la sesión aún esté visible (no fue eliminada) --- 
    modal = wait.until(EC.presence_of_element_located((
        By.XPATH,
        "//div[contains(@class, 'modal-content')]//span[contains(text(), 'Note On Modified Session Timings')]"
    )))
    assert modal.is_displayed(), " [X] CP-05-03-03: No apareció el modal con la nota sobre modificaciones en los horarios."
    print(" [✓] Éxito CP-05-03-03: Modal con nota sobre modificaciones en los horarios apareció correctamente.")


# CP-05-03-04
def test_cp_05_03_04_copy_session_duplicate_name_rejected(driver):
    """
    CP-05-03-04: Copia con un nombre ya existente

    Objetivo:
        Verificar que el sistema rechaza nombres duplicados en el curso destino

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - Nombre para sesión copia que ya existe y por tanto es duplicado: "Nombre ya tomado"

    Resultado esperado:
        Mensaje o acción que notifique que el nombre de la copia ya existe y por tanto no se puede proseguir con la copia.
    """

    wait = WebDriverWait(driver, 15)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")

    # --- 1. Buscar y eliminar sesión ---
    session_row = wait.until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'gsotocco.uns-demo')]/following-sibling::td[contains(text(), 'Sesión Eliminar Cancelar')]/.."
    )))
    delete_button = session_row.find_element(By.XPATH, ".//button[contains(text(), 'Copy')]")
    delete_button.click()
    time.sleep(1)

    # --- 2. Buscar el input por id y asignar el nuevo nombre ---
    input_nombre_copia = wait.until(EC.presence_of_element_located((
        By.ID, "copy-session-name"
    )))
    input_nombre_copia.clear()
    input_nombre_copia.send_keys("Sesión Eliminar Cancelar")

    # --- 3. Click en el checkbox de copia ---
    checkbox = wait.until(EC.presence_of_element_located((
        By.XPATH, "//label[contains(., 'gsotocco.uns-demo')]/input[@type='checkbox']"
    )))
    checkbox.click()

    # --- 4. Confirmar cambio. ---
    btn_confirm_copy = wait.until(EC.presence_of_element_located((
        By.ID, "btn-confirm-copy-course"
    )))
    btn_confirm_copy.click()
    time.sleep(1)

    # --- 3. Validar que la sesión aún esté visible (no fue eliminada) --- 
    error_toast = wait.until(EC.presence_of_element_located((
        By.XPATH, "//div[contains(@class, 'toast-body') and contains(text(), 'Error copying to gsotocco.uns-demo')]"
    )))
    assert error_toast.is_displayed(), " [X] CP-05-03-04: No apareció el toast con el error de que ya existe el curso con el mismo nombre."
    print(" [✓] Éxito CP-05-03-04: Aparecio el toast sobre el nombre repetido.")
    

# CP-05-03-05
def test_cp_05_03_05_copy_session_no_destination_course_selected(driver):
    """
    CP-05-03-05: No se selecciona ningún curso destino en la copia de sesión

    Objetivo:
        Verificar que el sistema requiere al menos un curso destino seleccionado

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - Nombre de sesión: "Copia sin curso"
        - Cursos seleccionados: ninguno

    Resultado esperado:
        Mensaje de error indicando que se debe seleccionar al menos un curso destino. No se realiza copia.
    """

    wait = WebDriverWait(driver, 15)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")

    # --- 1. Buscar y eliminar sesión ---
    session_row = wait.until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'gsotocco.uns-demo')]/following-sibling::td[contains(text(), 'Sesión Eliminar Cancelar')]/.."
    )))
    delete_button = session_row.find_element(By.XPATH, ".//button[contains(text(), 'Copy')]")
    delete_button.click()
    time.sleep(1)

    # --- 2. Ingresar nombre válido para la copia ---
    input_nombre_copia = wait.until(EC.presence_of_element_located((By.ID, "copy-session-name")))
    input_nombre_copia.clear()
    input_nombre_copia.send_keys("Copia sin curso")

    # --- 3. Verificar que el botón esté deshabilitado (sin cursos seleccionados) ---
    btn_confirm_copy = driver.find_element(By.ID, "btn-confirm-copy-course")
    assert not btn_confirm_copy.is_enabled(), " [X] CP-05-03-05: El botón de copia se habilitó sin seleccionar cursos."
    print(" [✓] Éxito CP-05-03-05: No se admite hacer una copia sin seleccionar cursos.")


# CP-05-03-06
def test_cp_05_03_06_copy_session_multiple_courses(driver):
    """
    CP-05-03-06: Copia exitosa con múltiples cursos seleccionados

    Objetivo:
        Verificar que el sistema permite copiar una sesión a múltiples cursos simultáneamente

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - Nombre de sesión: "Copia válida"
        - Cursos seleccionados: Curso A, Curso B
        - Usuario autenticado: Sí (rol: instructor en ambos cursos)

    Resultado esperado:
        Sesión copiada correctamente en todos los cursos. Aparece en la lista de sesiones activas de cada curso.
    """

    wait = WebDriverWait(driver, 15)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")

    # --- 1. Buscar y eliminar sesión ---
    session_row = wait.until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'gsotocco.uns-demo')]/following-sibling::td[contains(text(), 'Sesión Eliminar Cancelar')]/.."
    )))
    delete_button = session_row.find_element(By.XPATH, ".//button[contains(text(), 'Copy')]")
    delete_button.click()
    time.sleep(1)

    # --- 2. Buscar el input por id y asignar el nuevo nombre ---
    input_nombre_copia = wait.until(EC.presence_of_element_located((
        By.ID, "copy-session-name"
    )))
    input_nombre_copia.clear()
    input_nombre_copia.send_keys("Copia de varios cursos")

    # --- 3. Click en el checkbox de copia ---
    checkbox_1 = wait.until(EC.presence_of_element_located((
        By.XPATH, "//label[contains(., 'example-course-012')]/input[@type='checkbox']"
    )))
    checkbox_1.click()

    checkbox_2 = wait.until(EC.presence_of_element_located((
        By.XPATH, "//label[contains(., 'example-course-014')]/input[@type='checkbox']"
    )))
    checkbox_2.click()

    checkbox_3 = wait.until(EC.presence_of_element_located((
        By.XPATH, "//label[contains(., 'gsotocco.uns-demo')]/input[@type='checkbox']"
    )))
    checkbox_3.click()

    # --- 4. Confirmar cambio. ---
    btn_confirm_copy = wait.until(EC.presence_of_element_located((
        By.ID, "btn-confirm-copy-course"
    )))
    btn_confirm_copy.click()
    time.sleep(2)

    # --- 3. Validar que la sesión aún esté visible (no fue eliminada) --- 
    error_toast = wait.until(EC.presence_of_element_located((
        By.XPATH, "//div[contains(@class, 'toast-body') and contains(text(), 'Feedback session copied successfully to all courses.')]"
    )))
    assert error_toast.is_displayed(), " [X] CP-05-03-06: No se copio el curso de varios cursos seleccionados."
    print(" [✓] Éxito CP-05-03-06: Se copio el curso de varios cursos seleccionados.")


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# CP-05-03-07
def test_cp_05_03_07_copy_session_unauthenticated_user_rejected():
    """
    CP-05-03-07: Error por usuario no autenticado al copiar sesión

    Objetivo:
        Verificar que el sistema rechaza intentos de copia por usuarios no autenticados

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - Nombre de sesión: "Copia sin login"
        - Cursos seleccionados: Curso A
        - Usuario autenticado: No

    Resultado esperado:
        Mensaje de error indicando que el usuario debe iniciar sesión para realizar la acción.
        El modal se cierra o queda bloqueado.
    """

    # --- 1. Crear driver con perfil temporal (sin login) ---
    options = Options()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-infobars')
    options.add_argument('--incognito')  # modo incógnito = sin login
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        # --- 2. Navegar directamente a la URL de sesiones ---
        driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")

        # --- 3. Esperar redirección ---
        WebDriverWait(driver, 10).until(
            EC.url_contains("accounts.google.com")
        )
        assert "accounts.google.com" in driver.current_url, f" [X] CP-05-03-07: No hubo redirección. URL actual: {driver.current_url}"
        print(" [✓] Éxito CP-05-03-07: Redirección exitosa a Google OAuth para la verificación.")

    finally:
        driver.quit()


# CP-05-04-01
def test_cp_05_04_01_view_individual_results_instructor(driver):
    """
    CP-05-04-01: Visualizar resultados individuales del instructor

    Objetivo:
        Verificar acceso a resultados específicos del instructor

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - Sesión seleccionada: "Session with different question types"
        - Acción: View Results (from/to me)

    Resultado esperado:
        Visualización únicamente de resultados dirigidos al instructor o brindados por él.
    """

    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")

    # --- 1. Buscar fila de sesión específica ---
    session_row = WebDriverWait(driver, 10).until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'gsotocco.uns-demo')]/following-sibling::td[contains(text(), 'Session with different question types')]/.."
    )))

    # --- 2. Hacer clic en el botón "Results" ---
    results_button = session_row.find_element(By.XPATH, ".//button[contains(text(), 'Results')]")
    results_button.click()
    time.sleep(2)

    # --- 2. Ver los resultados de la sesión. ---
    dropdown_menu = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".dropdown-menu.show"))
    )

    view_results_link = dropdown_menu.find_element(
        By.XPATH,
        ".//a[contains(text(), 'View Results (from/to me)')]"
    )
    view_results_link.click()

    try:
        time.sleep(3)
        WebDriverWait(driver, 10).until(
            EC.url_contains("/web/instructor/sessions/result")
        )
        print(" [✓] Éxito CP-05-04-01: Se redirigió correctamente a la vista de resultados individuales.")
    except TimeoutException:
        raise AssertionError(" [X] CP-05-04-01: No se redirigió a la vista de resultados dentro del tiempo esperado.")
    

# CP-05-04-02
def test_cp_05_04_02_view_results_unpublished_session(driver):
    """
    CP-05-04-02: Visualizar resultados en sesiones no publicadas

    Objetivo:
        Verificar que no se visualizan resultados si la sesión no fue publicada aún

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - Sesión seleccionada: "Second team feedback session (point-based)"
        - Acción: View Results (from/to me)

    Resultado esperado:
        Mensaje: “The feedback session is not yet published”
    """

    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")

    # --- 1. Buscar fila de sesión específica ---
    session_row = WebDriverWait(driver, 10).until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'gsotocco.uns-demo')]/following-sibling::td[contains(text(), 'Sesión Eliminar Cancelar')]/.."
    )))

    # --- 2. Hacer clic en el botón "Results" ---
    results_button = session_row.find_element(By.XPATH, ".//button[contains(text(), 'Results')]")
    results_button.click()
    time.sleep(2)

    # --- 2.1 Ver los resultados de la sesión. ---
    dropdown_menu = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".dropdown-menu.show"))
    )

    view_results_link = dropdown_menu.find_element(
        By.XPATH,
        ".//a[contains(text(), 'View Results (from/to me)')]"
    )
    view_results_link.click()

    # --- 3. Los resultados se muestran. ---
    time.sleep(3)
    WebDriverWait(driver, 10).until(
        EC.url_contains("/web/instructor/sessions/result")
    )

    try:
        toast = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//div[contains(@class, 'toast-body') and contains(text(), 'This feedback session is not yet published.')]"
            ))
        )
        assert toast.is_displayed(), "Toast encontrado pero no visible"
        print(" [✓] Éxito CP-05-04-02: Apareció el toast indicando que la sesión no está publicada.")
    except TimeoutException:
        raise AssertionError(" [X] CP-05-04-02: No apareció el toast indicando que la sesión no está publicada.")

# CP-05-04-03
def test_cp_05_04_03_publish_session_results(driver):
    """
    CP-05-04-03: Publicar resultados de sesión

    Objetivo:
        Verificar cambio de estado de resultados de no publicados a publicados

    Técnica utilizada:
        Transición de Estados

    Datos de prueba:
        - Sesión seleccionada: "Second team feedback session (point-based)"
        - Acción: Publish Results

    Resultado esperado:
        Mensaje: “The feedback session has been published. Please allow up to 1 hour for all the notification emails to be sent out”
    """
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")

    # --- 1. Buscar fila de sesión específica ---
    session_row = WebDriverWait(driver, 10).until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'gsotocco.uns-demo')]/following-sibling::td[contains(text(), 'Sesión Eliminar Cancelar')]/.."
    )))

    # --- 2. Hacer clic en el botón "Results" ---
    results_button = session_row.find_element(By.XPATH, ".//button[contains(text(), 'Results')]")
    results_button.click()
    time.sleep(2)

    dropdown_menu = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".dropdown-menu.show"))
    )
    time.sleep(1)

    # Ahora buscar dentro del dropdown el botón "Publish Results"
    publish_button = dropdown_menu.find_element(
        By.XPATH, ".//button[contains(text(), 'Publish Results')]"
    )
    publish_button.click()

    yes_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
        By.XPATH,
        "//tm-confirmation-modal//button[contains(@class, 'modal-btn-ok') and text()='Yes']"
    )))
    yes_button.click()
    time.sleep(3)

    try:
        toast = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//div[contains(@class, 'toast-body') and contains(text(), 'The feedback session has been published.')]"
            ))
        )
        assert toast.is_displayed(), "Toast encontrado pero no visible"
        print(" [✓] Éxito CP-05-04-03: Los resultados han sido publicados.")
    except TimeoutException:
        raise AssertionError(" [X] CP-05-04-03: Los resultados NO han sido publicados")

    
# CP-05-04-04
def test_cp_05_04_04_unpublish_session_results(driver):
    """
    CP-05-04-04: Despublicar resultados de sesión

    Objetivo:
        Verificar reversión de publicación de resultados

    Técnica utilizada:
        Transición de Estados

    Datos de prueba:
        - Sesión seleccionada: "Session with different question types"
        - Acción: Unpublish Results

    Resultado esperado:
        Mensaje: “The feedback session has been unpublished.”
    """

    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")

    # --- 1. Buscar fila de sesión específica ---
    session_row = WebDriverWait(driver, 10).until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'gsotocco.uns-demo')]/following-sibling::td[contains(text(), 'Sesión Eliminar Cancelar')]/.."
    )))

    # --- 2. Hacer clic en el botón "Results" ---
    results_button = session_row.find_element(By.XPATH, ".//button[contains(text(), 'Results')]")
    results_button.click()
    time.sleep(2)

    dropdown_menu = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".dropdown-menu.show"))
    )
    time.sleep(0.5)

    # Ahora buscar dentro del dropdown el botón "Publish Results"
    publish_button = dropdown_menu.find_element(
        By.XPATH, ".//button[contains(text(), 'Unpublish Results')]"
    )
    publish_button.click()

    yes_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
        By.XPATH,
        "//tm-confirmation-modal//button[contains(@class, 'modal-btn-ok') and text()='Yes']"
    )))
    yes_button.click()
    time.sleep(3)

    try:
        toast = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//div[contains(@class, 'toast-body') and contains(text(), 'The feedback session has been unpublished.')]"
            ))
        )
        assert toast.is_displayed(), "Toast encontrado pero no visible"
        print(" [✓] Éxito CP-05-04-04: Los resultados han sido des-publicados.")
    except TimeoutException:
        raise AssertionError(" [X] CP-05-04-04: Los resultados NO han sido des-publicados")
    

# CP-05-04-05
def test_cp_05_04_05_download_session_results(driver):
    """
    CP-05-04-05: Descargar resultados de sesión

    Objetivo:
        Verificar descarga correcta de archivo con resultados

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - Sesión seleccionada: "Second team feedback session (point-based)"
        - Acción: Download Results

    Resultado esperado:
        Descarga del archivo en formato Excel.
    """

    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")

    # --- 1. Buscar fila de sesión específica ---
    session_row = WebDriverWait(driver, 10).until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'gsotocco.uns-demo')]/following-sibling::td[contains(text(), 'Session with different question types')]/.."
    )))

    # --- 2. Hacer clic en el botón "Results" ---
    results_button = session_row.find_element(By.XPATH, ".//button[contains(text(), 'Results')]")
    results_button.click()
    time.sleep(2)

    dropdown_menu = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".dropdown-menu.show"))
    )
    time.sleep(0.5)

    # Ahora buscar dentro del dropdown el botón "Publish Results"
    publish_button = dropdown_menu.find_element(
        By.XPATH, ".//button[contains(text(), 'Download Results')]"
    )
    publish_button.click()

    try:
        modal = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.modal-content tm-confirmation-modal"))
        )
        WebDriverWait(driver, 30).until(EC.invisibility_of_element(modal))
        print(" [✓] Éxito CP-05-04-05: Archivo descargado correctamente, sin errores visibles.")
    except TimeoutException:
        raise AssertionError(" [X] CP-05-04-05: El archivo no se pudo descargar correctamente.")
    

# CP-05-04-06
def test_cp_05_04_06_access_results_menu_unauthenticated():
    """
    CP-05-04-06: Intento de acceso al menú "Results" sin estar autenticado

    Objetivo:
        Verificar que el sistema controla el acceso a resultados para usuarios no autenticados

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - Usuario: no autenticado

    Resultado esperado:
        Mensaje de error o redirección a la pantalla de login. No se permite acceso al menú.
    """

    # --- 1. Crear driver con perfil temporal (sin login) ---
    options = Options()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-infobars')
    options.add_argument('--incognito')  # modo incógnito = sin login
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        # --- 2. Navegar directamente a la URL de sesiones ---
        driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions/result")

        # --- 3. Esperar redirección ---
        WebDriverWait(driver, 10).until(
            EC.url_contains("accounts.google.com")
        )
        assert "accounts.google.com" in driver.current_url, f" [X] CP-05-04-06: No hubo redirección. URL actual: {driver.current_url}"
        print(" [✓] Éxito CP-05-04-06: Redirección exitosa a Google OAuth, no se accedio a resultados.")

    finally:
        driver.quit()

# CP-05-04-07
def test_cp_05_04_07_manage_results_without_active_session(driver):
    """
    CP-05-04-07: Intento de gestión de resultados sin seleccionar sesión activa

    Objetivo:
        Verificar que el sistema requiere seleccionar una sesión antes de gestionar resultados

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - Usuario: instructor autenticado
        - Acción: ver resultados individuales
        - Sesión activa: no seleccionada

    Resultado esperado:
        Mensaje de error indicando que se debe seleccionar una sesión activa. 
    """
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions/result")

    try:
        toast = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//*[contains(@class, 'toast-body') and contains(text(), 'The [courseid] HTTP parameter is null.')]"
            ))
        )
        assert toast.is_displayed(), " [X] CP-05-04-07: El mensaje de error está presente pero no es visible."
        print(" [✓] Éxito CP-05-04-07: Se mostró el mensaje de error al intentar gestionar resultados sin sesión activa.")
    except TimeoutException:
        raise AssertionError(" [X] CP-05-04-07: No se mostró el mensaje de error esperado al no seleccionar una sesión activa.")

    
# CP-05-04-08
def test_cp_05_04_08_view_results_when_none_available(driver):
    """
    CP-05-04-08: Visualizar resultados individuales cuando no hay resultados del instructor

    Objetivo:
        Verificar que el sistema informa apropiadamente cuando no existen resultados del instructor

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - Usuario: instructor autenticado
        - Sesión activa: seleccionada
        - Acción: View Results (from/to me)

    Resultado esperado:
        Mensaje indicando que no hay resultados disponibles para visualizar.
    """

    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")

    # --- 1. Buscar fila de sesión específica ---
    session_row = WebDriverWait(driver, 10).until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'gsotocco.uns-demo')]/following-sibling::td[contains(text(), 'Sesión Eliminar Cancelar')]/.."
    )))

    # --- 2. Hacer clic en el botón "Results" ---
    results_button = session_row.find_element(By.XPATH, ".//button[contains(text(), 'Results')]")
    results_button.click()
    time.sleep(2)

    # --- 2. Ver los resultados de la sesión. ---
    dropdown_menu = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".dropdown-menu.show"))
    )

    view_results_link = dropdown_menu.find_element(
        By.XPATH,
        ".//a[contains(text(), 'View Results (from/to me)')]"
    )
    view_results_link.click()


    time.sleep(3)
    WebDriverWait(driver, 10).until(
        EC.url_contains("/web/instructor/sessions/result")
    )
    
    try:
        toast = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//*[contains(@class, 'toast-body') and contains(text(), 'This feedback session is not yet published.')]"
            ))
        )
        assert toast.is_displayed(), " [X] CP-05-04-08: El mensaje de error está presente pero no es visible."
        print(" [✓] Éxito CP-05-04-08: Se mostró el mensaje de error en los resultados de una sesión no publicada.")
    except TimeoutException:
        raise AssertionError(" [X] CP-05-04-08: No se mostró el mensaje de error en los resultados de una sesión no publicada.")


# CP-05-19
def test_cp_05_19_send_reminder_to_all_non_submitters(driver):
    """
    CP-05-19: Envíar recordatorio a todos los estudiantes pendientes

    Objetivo:
        Verificar envío masivo de recordatorios

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - Sesión activa con estudiantes que no han enviado respuestas
        - Sesión seleccionada: "Second team feedback session (point-based)"
        - Acción: Remind all non-submitters

    Resultado esperado:
        Mensaje: “Reminder e-mails have been sent out to those students and instructors.
        Please allow up to 1 hour for all the notification emails to be sent out.”
    """
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")

    # --- 1. Buscar fila de sesión específica ---
    session_row = WebDriverWait(driver, 10).until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'gsotocco.uns-demo')]/following-sibling::td[contains(text(), 'Sesión Eliminar Cancelar')]/.."
    )))

    # --- 2. Hacer clic en el botón "Remind" ---
    results_button = session_row.find_element(
        By.XPATH,
        ".//button[.//span[contains(text(), 'Remind')]]"
    )
    results_button.click()
    time.sleep(2)

    dropdown_menu = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".dropdown-menu.show"))
    )

    remind_button = dropdown_menu.find_element(
        By.XPATH, ".//button[contains(text(), 'Remind all non-submitters')]"
    )
    remind_button.click()
    time.sleep(1)

    modal_remind_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "btn-confirm-send-reminder"))
    )
    modal_remind_button.click()

    try:
        toast = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//*[contains(@class, 'toast-body') and contains(text(), 'Reminder e-mails have been sent out to those students and instructors. Please allow up to 1 hour for all the notification emails to be sent out.')]"
            ))
        )
        assert toast.is_displayed(), " [X] CP-05-19: El mensaje de confirmación está presente pero no es visible."
        print(" [✓] Éxito CP-05-19: El sistema confirmó el envío de recordatorios correctamente.")
    except TimeoutException:
        raise AssertionError(" [X] CP-05-19: No se mostró el mensaje de confirmación tras intentar enviar recordatorios en una sesión no publicada.")


# CP-05-20 List of users to remind cannot be empty

def test_cp_05_20_send_reminder_to_selected_students(driver):
    """
    CP-05-20: Envíar recordatorio a estudiantes seleccionados

    Objetivo:
        Verificar envío selectivo de recordatorios

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - Lista de estudiantes pendientes disponible
        - Sesión seleccionada: "Second team feedback session (point-based)"
        - Acción: Select non-submitters to remind
        - Estudiantes seleccionados: [Hugh Ivanov]

    Resultado esperado:
        Mensaje: “Reminder e-mails have been sent out to those students and instructors.
        Please allow up to 1 hour for all the notification emails to be sent out.”
    """

    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")

    # --- 1. Buscar fila de sesión específica ---
    session_row = WebDriverWait(driver, 10).until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'gsotocco.uns-demo')]/following-sibling::td[contains(text(), 'Sesión Eliminar Cancelar')]/.."
    )))

    # --- 2. Hacer clic en el botón "Remind" ---
    results_button = session_row.find_element(
        By.XPATH,
        ".//button[.//span[contains(text(), 'Remind')]]"
    )
    results_button.click()
    time.sleep(2)

    dropdown_menu = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".dropdown-menu.show"))
    )

    remind_button = dropdown_menu.find_element(
        By.XPATH, ".//button[contains(text(), 'Select non-submitters to remind')]"
    )
    remind_button.click()
    time.sleep(1)

    table = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "student-list-table"))
    )

    first_checkbox = table.find_element(
        By.CSS_SELECTOR,
        "tbody input[type='checkbox']"
    )
    first_checkbox.click()
    time.sleep(0.5)

    modal_remind_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "btn-confirm-send-reminder"))
    )
    modal_remind_button.click()
    
    try:
        toast = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//*[contains(@class, 'toast-body') and contains(text(), 'Reminder e-mails have been sent out to those students and instructors. Please allow up to 1 hour for all the notification emails to be sent out.')]"
            ))
        )
        assert toast.is_displayed(), " [X] CP-05-20: El mensaje de confirmación está presente pero no es visible."
        print(" [✓] Éxito CP-05-20: Se mostró el mensaje de confirmación tras enviar recordatorios a los estudiantes seleccionados.")
    except TimeoutException:
        raise AssertionError(" [X] CP-05-20: No se mostró el mensaje de confirmación tras intentar enviar recordatorios a estudiantes seleccionados.")


# CP-05-05-04
def test_cp_05_05_04_send_reminder_without_selecting_students(driver):
    """
    CP-05-05-04: Envío manual sin seleccionar estudiantes

    Objetivo:
        Verificar que el sistema requiere seleccionar al menos un estudiante para el envío selectivo

    Técnica utilizada:
        Partición de Equivalencia

    Datos de prueba:
        - Sistema disponible
        - Usuario instructor autenticado
        - Sesión activa seleccionada: "Second team feedback session (point-based)"
        - Acción: Select non-submitters to remind
        - Estudiantes seleccionados: []

    Resultado esperado:
        Mensaje de error: "Debe seleccionar al menos un estudiante para enviar el recordatorio."
    """

    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")

    # --- 1. Buscar fila de sesión específica ---
    session_row = WebDriverWait(driver, 10).until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'gsotocco.uns-demo')]/following-sibling::td[contains(text(), 'Sesión Eliminar Cancelar')]/.."
    )))

    # --- 2. Hacer clic en el botón "Remind" ---
    results_button = session_row.find_element(
        By.XPATH,
        ".//button[.//span[contains(text(), 'Remind')]]"
    )
    results_button.click()
    time.sleep(2)

    dropdown_menu = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".dropdown-menu.show"))
    )

    remind_button = dropdown_menu.find_element(
        By.XPATH, ".//button[contains(text(), 'Select non-submitters to remind')]"
    )
    remind_button.click()
    time.sleep(1)

    modal_remind_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "btn-confirm-send-reminder"))
    )
    modal_remind_button.click()
    time.sleep(1)
    
    try:
        toast = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//*[contains(@class, 'toast-body') and contains(text(), 'List of users to remind cannot be empty')]"
            ))
        )
        assert toast.is_displayed(), " [X] CP-05-05-04: El mensaje de error está presente pero no es visible."
        print(" [✓] Éxito CP-05-05-04: El sistema bloqueó el envío y mostró el mensaje de error correctamente.")
    except TimeoutException:
        raise AssertionError(" [X] CP-05-05-04: No se mostró el mensaje de error tras intentar enviar sin seleccionar estudiantes.")


# CP-05-21
def test_cp_05_21_restore_deleted_session(driver):
    """
    CP-05-21: Restaurar sesión eliminada

    Objetivo:
        Verificar cambio de estado de una sesión desde "eliminada" a "activa"

    Técnica utilizada:
        Transición de Estados

    Datos de prueba:
        - Sesión eliminada presente en la tabla de sesiones eliminadas
        - Sesión seleccionada: "Evaluación Parcial 1"
        - Acción: Restaurar

    Resultado esperado:
        La sesión cambia a estado "activa", aparece en la tabla de sesiones activas y desaparece de la tabla de eliminadas
    """

    wait = WebDriverWait(driver, 15)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")

    # --- 1. Desplegar dropdown en la tabla de eliminados ---
    expand_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Expand panel']"))
    )
    expand_button.click()
    time.sleep(1)

    # --- 2. Restaurar curso  ---
    session_row = wait.until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'example-course-012')]/following-sibling::td[contains(text(), 'Sesión Eliminar')]/.."
    )))
    delete_button = session_row.find_element(By.XPATH, ".//button[contains(text(), 'Restore')]")
    delete_button.click()
    time.sleep(3)

    try:
        toast = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//*[contains(@class, 'toast-body') and contains(text(), 'The feedback session has been restored.')]"
            ))
        )
        assert toast.is_displayed(), " [X] CP-05-21: El mensaje de confirmación está presente pero no es visible."
        print(" [✓] Éxito CP-05-21: La sesión eliminada fue restaurada correctamente y el sistema mostró el mensaje de confirmación.")
    except TimeoutException:
        raise AssertionError(" [X] CP-05-21: No se mostró el mensaje de confirmación tras intentar restaurar la sesión eliminada.")


# CP-05-22
def test_cp_05_22_permanent_delete_with_confirmation(driver):
    """
    CP-05-22: Eliminar permanente con confirmación

    Objetivo:
        Verificar la eliminación irreversible de una sesión con confirmación

    Técnica utilizada:
        Transición de Estados

    Datos de prueba:
        - Sesión eliminada visible en la tabla de sesiones eliminadas
        - Modal de advertencia mostrado
        - Sesión seleccionada: "Eliminar Permanentemente"
        - Acción: Eliminar permanentemente (con confirmación)

    Resultado esperado:
        La sesión es eliminada irreversiblemente del sistema y desaparece de la tabla de sesiones eliminadas
    """

    wait = WebDriverWait(driver, 15)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")

    # --- 1. Buscar y eliminar sesión ---
    session_row = wait.until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'example-course-012')]/following-sibling::td[contains(text(), 'Eliminar Permanentemente')]/.."
    )))
    delete_button = session_row.find_element(By.XPATH, ".//button[contains(text(), 'Delete')]")
    delete_button.click()
    time.sleep(1)

    # --- 2. Confirmar en el modal ---
    yes_button = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//tm-confirmation-modal//button[contains(text(), 'Yes')]"
    )))
    yes_button.click()
    time.sleep(2)

    # --- 3. Desplegar dropdown en la tabla de eliminados ---
    expand_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Expand panel']"))
    )
    expand_button.click()
    time.sleep(1)

    # --- 4. Eliminar permanentemente ---
    session_row_1 = wait.until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'example-course-012')]/following-sibling::td[contains(text(), 'Eliminar Permanentemente')]/.."
    )))
    delete_button = session_row_1.find_element(By.XPATH, ".//button[.//span[contains(text(), 'Delete Permanently')]]")
    delete_button.click()
    time.sleep(2)

    # --- 5. Confirmar elimado permanente ---
    yes_button = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//tm-session-permanent-deletion-confirm-modal//button[contains(text(), 'Yes')]"
    )))
    yes_button.click()
    time.sleep(3)

    try:
        toast = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//*[contains(@class, 'toast-body') and contains(text(), 'The feedback session has been permanently deleted.')]"
            ))
        )
        assert toast.is_displayed(), " [X] CP-05-22: El mensaje de confirmación está presente pero no es visible."
        print(" [✓] Éxito CP-05-22: La sesión fue eliminada permanentemente y el sistema mostró el mensaje de confirmación.")
    except TimeoutException:
        raise AssertionError(" [X] CP-05-22: No se mostró el mensaje de confirmación tras eliminar la sesión permanentemente.")
    

# CP-05-23
def test_cp_05_23_cancel_permanent_deletion(driver):
    """
    CP-05-23: Cancelar eliminación permanente

    Objetivo:
        Verificar que se mantiene el estado al cancelar la eliminación permanente

    Técnica utilizada:
        Transición de Estados

    Datos de prueba:
        - Modal de advertencia de eliminación permanente abierto
        - Sesión seleccionada: "ffre"
        - Acción: Cancelar en modal de advertencia

    Resultado esperado:
        La sesión mantiene el estado "eliminada", el modal se cierra y la sesión permanece en la tabla de sesiones eliminadas
    """

    wait = WebDriverWait(driver, 15)
    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/instructor/sessions")

    # --- 3. Desplegar dropdown en la tabla de eliminados ---
    expand_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Expand panel']"))
    )
    expand_button.click()
    time.sleep(1)

    # --- 4. Eliminar permanentemente ---
    session_row_1 = wait.until(EC.presence_of_element_located((
        By.XPATH, "//td[contains(text(), 'example-course-012')]/following-sibling::td[contains(text(), 'Eliminar Permanentemente Cancelar')]/.."
    )))
    delete_button = session_row_1.find_element(By.XPATH, ".//button[.//span[contains(text(), 'Delete Permanently')]]")
    delete_button.click()
    time.sleep(2)

    # --- 5. Confirmar elimado permanente ---
    yes_button = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//tm-session-permanent-deletion-confirm-modal//button[contains(text(), 'No, Cancel the Operation')]"
    )))
    yes_button.click()
    time.sleep(3)

    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//*[contains(@class, 'toast-body') and contains(text(), 'The feedback session has been permanently deleted.')]"
            ))
        )
        raise AssertionError(" [X] CP-05-23: Apareció mensaje de eliminación permanente a pesar de cancelar la operación.")
    except TimeoutException:
        print(" [✓] Éxito CP-05-23: La eliminación permanente fue cancelada correctamente; no se eliminó la sesión.")