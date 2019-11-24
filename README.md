<<<<<<< HEAD
# Datasets sobre procesos electorales en España

Este repo contiene datasets y código usado para construir visualizaciones sobre procesos electorales en España. Hay un foco especial también en Madrid.

## Secciones censales

El principal dataset proporcionado es el de secciones censales (2019), en formato GeoJSON, extraído a partir de la web del [INE](https://www.ine.es/ss/Satellite?L=es_ES&c=Page&cid=1259952026632&p=1259952026632&pagename=ProductosYServicios%2FPYSLayout) y fragmentado por comunidad autónoma. Los ficheros se encontraban originalmente en formato shape y coordenadas con proyección UTM en huso 30 (28 para Canarias). A partir de código disponible en diversas fuentes ([respuesta de Alexis de Varennes en Stackoverflow sobre la conversión de shapefiles en ficheros GeoJSON](https://stackoverflow.com/questions/43119040/shapefile-into-geojson-conversion-python-3) y [un script de Tom Payne para hacer conversiones entre proyecciones UTM y WSG84](https://gist.github.com/twpayne/4409500)), se ha conseguido hacer la conversión a GeoJSON con coordenadas WSG84, de forma que los ficheros pueden cargarse en CartoDB, Flourish o Google Maps.
=======
# Miscellaneous repo for visualizations based on census sections in Spain
>>>>>>> parent of a14b2fd... Starting

Los ficheros con las secciones censales se encuentran en la carpeta `data/census` (por comunidad autónoma, con los [códigos ISO_3166-2](https://en.wikipedia.org/wiki/ISO_3166-2:ES) para identificar la comunidad autónoma).

### Ejecución
La forma más sencilla de conseguir los ficheros GeoJSON es simplemente clonando este repo:
```bash
git clone https://github.com/miguel-angel-monjas/spain-datasets.git
```

No obstante, se proporciona también el código utilizado que puede ser reutilizado por cualquiera. Se trata de Python 3.7. Si quieres ejecutar los scripts, simplemente, clona el repo y accede a la carpeta `src/`:
```bash
git clone https://github.com/miguel-angel-monjas/spain-datasets.git
cd spain-datasets/src
```
A continuación, instala los módulos necesarios:
```bash
pip install -r requirements.txt
```

Finally, run the script:
```bash
python shape_extractor.py
```

El proceso involucra la descarga y descompresión de los shape files en una carpeta llamada `src/seccionado2019`. La carpeta y sus contenidos no pueden ser borrados, ya que los ficheros están todavía en uso, por lo que el borrado tendrá que hacerse, manualmente, tras la ejecución del script.

### Agradecimientos
Además de las fuentes citadas, la pista inicial me la propocionó [Santiago Espinosa (@Saigesp)](https://github.com/Saigesp).

## Renta media

La renta media por sección censal se encuentra en `data/Renta media en España.csv`. El fichero ha sido extraído del [Atlas de distribución de renta de los hogares](https://www.ine.es/experimental/atlas/exp_atlas_tab.htm) del Instituto Nacional de Estadística. Se ha realizado un procesado manual del fichero [XLSX](https://www.ine.es/jaxiT3/files/t/es/xlsx/30824.xlsx?nocab=1) generándose un fichero CSV separado por comas con el siguiente diccionario de datos:
- Código de territorio: identifica unívocamente el territorio. En el caso de las secciones censales, coincide con el código de los datasets de secciones censales (en concreto con la propiedad `CUSEC`). Este código consta de 9 dígitos: los dos primeros son el código de provincia; los dos siguientes los de municipio; los cinco siguientes los de sección censal (en el caso de municipio con distritos y barrios, los dos primeros dígitos identifican el distrito).
- Comunidad autónoma: nombre de la comunidad autónoma.
- Provincia: nombre de la provincia.
- Código de provincia: código de provincia (dos dígitos; propiedad `CPRO` en el dataset de secciones censales)
- Municipio: nombre del municipio.
- Código de municipio: código del municipio (cuatro dígitos; propiedad `CUMUN`)
- Tipo de elemento: municipio, distrito o sección (censal)
- Renta media por persona
- Renta media por hogar

## Resultados electorales