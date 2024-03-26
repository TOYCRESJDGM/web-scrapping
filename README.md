## Description

Code to extract information from the web page  <a href="https://procesosjudiciales.funcionjudicial.gob.ec/busqueda-filtros" target="blank"> "Consultation of Judicial Processes" </a> using Web Scraping techniques. 

## Description & Using API & Code
The selenium_scrapping.py file is in charge of web scraping the page and extracting the information of each one of the judicial processes, for each one of the cases Actor/Ofendido or Demandado/Procesado, Additionally it saves the information in a .json file whose name is specified in the input variables.

![image](https://github.com/TOYCRESJDGM/web-scrapping/assets/69774985/3fcb3a17-7801-4051-82cb-2e0194c99b30)

Specify the type and document 
```run selenium_scrapping.py
$ python selenium_scrapping.py
```

The processing.py file is in charge of concurrently processing each of the desired records stored in a json file, limiting the number of threads to 15.
Specify records in json file

```run processing.py
$ python processing.py
```

Finally an api made with FastApi is included to show these web scraping results, using a basic authentication, with the user and password, whose values are specified in the environment variables. This authentication is necessary to be able to access each of the resources. 

```Run Api
$ uvicorn main:app --reload
```

![image](https://github.com/TOYCRESJDGM/web-scrapping/assets/69774985/482fb9a5-6437-42da-8f83-d333300c0ae0)

