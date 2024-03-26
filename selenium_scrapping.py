import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv
from selenium.webdriver.common.by import By

#Load Variables .env
load_dotenv()

def write_json(data):
    file_path = os.getenv("JSON_COLLECTED", "data_collected.json")
    try:
        with open(file_path, "r", encoding="utf-8") as archivo_json:
            content_exist = archivo_json.read()
            data_exist = json.loads(content_exist)
    except json.JSONDecodeError:
        data_exist = []

    data_exist.extend(data)
    
    # Escribir la estructura de datos actualizada de vuelta al archivo JSON
    with open(file_path, "w", encoding="utf-8") as archivo_json:
        # Escribir la estructura de datos actualizada en el archivo JSON
        json.dump(data_exist, archivo_json, indent=4)
        print("Data correctly collected")


def scrapping_page(type, identification_number):

    # Configura el servicio de ChromeDriver
    
    chrome_driver_path = os.getenv("CHROME_DRIVER_PATH")

    # Crea un objeto Service y arranca el servicio
    service = Service(r"{}".format(chrome_driver_path))
    service.start()

    dowload_directory = os.getenv("DOWNLOAD_DIRECTORY")

    # Configura las opciones del navegador
    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')  # Ejecución en modo headless (sin interfaz gráfica)
    options.add_argument('--no-sandbox')  # Evita problemas de sandbox
    options.add_experimental_option("prefs", {
        "download.default_directory": r"{}".format(dowload_directory),
        "download.prompt_for_download": False,  # Desactiva el diálogo de confirmación de descarga
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    # Inicializa el navegador
    driver = webdriver.Chrome(service=service, options=options)

    # URL Inicial
    url = os.getenv("INITIAL_URL")

    # Carga la página
    driver.get(url)

    # Espera a que el contenido dinámico se cargue completamente
    driver.implicitly_wait(10)

    if type == 'Demandado/Procesado':
        element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@formcontrolname='cedulaDemandado']")))
    else:
        element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@formcontrolname='cedulaActor']")))

    element.clear()
    
    element.send_keys(identification_number)

    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
    driver.implicitly_wait(2)
    time.sleep(2)

    parent_window_id = driver.current_window_handle
    print(driver.current_url)

    #scrapping
    court_proceedings = []


    process = driver.find_elements(By.CSS_SELECTOR, '.causa-individual.ng-star-inserted')
    for p in process:
        
        p_id_element = WebDriverWait(p, 15).until(EC.visibility_of_element_located((By.CLASS_NAME, 'id')))
        process_id = p_id_element.text.strip()

        print('ID:', process_id)
        
        # Hacer clic en el botón de detalle para abrir una nueva pestaña
        p_detail_button = WebDriverWait(p, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.detalle a')))
        ActionChains(driver).key_down(Keys.CONTROL).click(p_detail_button).key_up(Keys.CONTROL).perform()

        # Cambiar el foco a la nueva pestaña abierta
        new_window = [window for window in driver.window_handles if window != parent_window_id][0]
        driver.switch_to.window(new_window)

        driver.implicitly_wait(2)

        p_detail = driver.find_element(By.CLASS_NAME, 'movimiento-individual')

        if p_detail:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.actuaciones-judiciales a'))).click()

            time.sleep(2)

            strong_elements = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'section.filtros-busqueda strong')))
            span_elements = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'section.filtros-busqueda span')))

            correlaciones = {}

            # Itera sobre los elementos <strong> y <span> y los agrega al diccionario
            for strong, span in zip(strong_elements, span_elements):
                texto_strong = strong.text
                texto_span = span.text
                correlaciones[texto_strong] = texto_span

            correlaciones = {clave[:-1] if clave.endswith(':') else clave: valor for clave, valor in correlaciones.items()}

            panels = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, '//mat-accordion[@id="actuaciones-judiciales"]//mat-expansion-panel')))
            driver.implicitly_wait(2)
            activities = []
            for panel in panels:
                # Obtén la fecha del panel
                date_activitie = panel.find_element(By.XPATH,'.//div[contains(@class, "cabecera-tabla")]/span[1]').text
                
                # Obtén el título del panel
                title_activitie = panel.find_element(By.XPATH,'.//div[contains(@class, "cabecera-tabla")]/span[2]').text
                activitie = {
                    'date_activitie': date_activitie,
                    'title_activitie': title_activitie 
                }

                
                #Dowloads files
                folder_icon = WebDriverWait(panel, 10).until(EC.element_to_be_clickable((By.XPATH, './/div[@mattooltip="Ver archivos"]'))).click()
                time.sleep(2)

                try:
                    dowload_file_name = driver.find_element(By.CSS_SELECTOR, "table.document-table tbody tr td:nth-child(2) span")
                    # Obtener el nombre del archivo
                    name_file = dowload_file_name.text
                except NoSuchElementException:
                    print("El elemento no se encontró en la página.")
                    name_file = "Nombre de archivo no disponible"
                
                #download_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@mattooltip="Descargar"]'))).click()
                time.sleep(1)
                button_close = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='mdc-button mdc-button--unelevated mat-mdc-unelevated-button mat-primary mat-mdc-button-base']/span[contains(text(),'Cerrar')]")))
                button_close.click()
                driver.implicitly_wait(2)

                activitie['name_file'] = name_file

                activities.append(activitie)

            process_make = {
                'id': process_id,
                **correlaciones,
                'activities': activities
            }

            court_proceedings.append(process_make)

            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Botón regresar"]'))).click()
            driver.implicitly_wait(2)

            # Cierra la pestaña secundaria y vuelve a la pestaña principal
            driver.close()
            driver.switch_to.window(parent_window_id)

            
    write_json(court_proceedings)

    # Cerrar el navegador
    driver.quit()