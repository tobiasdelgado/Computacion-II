# Trabajo Práctico 2 - Sistema de Scraping Distribuido

Hola profe, quedó listo el TP2. No llegué a hacer los bonus tracks por falta de tiempo pero se implementó de forma correcta el problema principal.

![Pizza Time](assets/pizza-time.webp)

Hice un mini agregado mío personal que creé en `config.py` un bool `USE_PNG` para que al crear las imágenes genere los PNG realmente en la carpeta `images/` y devuelva las URLs para poder visualizarlo en la PC y ver que realmente está bien. Está en `True` pero puede cambiarlo a `False` para que devuelva todo en base64 como pide el enunciado.

Dejé 2 scripts, uno `setup.sh` que instala todo y otro `start.sh` que levanta los dos servidores automáticamente (el B en puerto 9000 y el A en puerto 8000). También dejé un script `kill_servers.sh` por si quedan procesos colgados ocupando los puertos.

Para probar pueden hacer `python client.py https://github.com` o también le dejo la mini colección de Postman en `postman_collection.json` que use para probar.

Saludos!
