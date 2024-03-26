import threading
import json
import os
from selenium_scrapping import scrapping_page
from dotenv import load_dotenv

#Load Variables .env
load_dotenv()

def processing():
    file_path = os.getenv("JSON_SCRAPPING_DATA", "scrapping_data.json")
    # Abre el archivo JSON y lee su contenido
    with open(file_path, 'r') as file:
        content = file.read()
    
    processing_data =  json.loads(content)
    if processing_data['consultas']:
        threads = []
        for consult in processing_data['consultas']:
            type_consult = consult["tipo_actor"]
            identification_number = consult["documento"]
            thread = threading.Thread(target=scrapping_page, args=(type_consult,identification_number))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
            
    # if processing_data['consultas']:
    #     threads = []
    #     # Limitar el número de hilos a 15
    #     for index, consult in enumerate(processing_data['consultas']):
    #         if index >= 15:
    #             break
            
    #         type_consult = consult["tipo_actor"]
    #         identification_number = consult["documento"]
    #         thread = threading.Thread(target=scrapping_page, args=(type_consult, identification_number))
    #         threads.append(thread)
    #         thread.start()
        
    #     for thread in threads:
    #         thread.join()       
            
# Ejecutar el caso de prueba
if __name__ == "__main__":
    processing()
    