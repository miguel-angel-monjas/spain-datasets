# Datasets sobre procesos electorales en España

Este repo contiene datasets y código usado para construir visualizaciones sobre procesos electorales en España. Hay un foco especial también en Madrid.

## Secciones censales

El principal dataset proporcionado es el de secciones censales (2019), en formato GeoJSON, extraído a partir de la web del [INE](https://www.ine.es/ss/Satellite?L=es_ES&c=Page&cid=1259952026632&p=1259952026632&pagename=ProductosYServicios%2FPYSLayout). Los ficheros se encontraban originalmente en formato shape y coordenadas con proyección UTM en huso 30 (28 para Canarias). 

This repo contains miscellaneous data and tools used to carry out visualizations based on census sections in Spain. The main focus is Madrid.

The census sections can be extracted from the [INE website](https://www.ine.es/ss/Satellite?L=es_ES&c=Page&cid=1259952026632&p=1259952026632&pagename=ProductosYServicios%2FPYSLayout), in shape format. Trasnformation from shape to geoJSON format has been carried out with [MapShaper](https://mapshaper.org/). You can find them in the `data/` folder (split by autonomous community, with the [ISO_3166-2 codes](https://en.wikipedia.org/wiki/ISO_3166-2:ES) to identify each community) in geoJSON format (thanks to [@Saigesp](https://github.com/Saigesp)).
