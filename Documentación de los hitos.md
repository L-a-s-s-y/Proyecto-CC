## Hito 2
### Gestor de tareas
Como gestor de tareas se ha elegido *GNU Make* pues es potente, polivalente y se tiene experiencia en su uso. La *Makefile* inicial para el proyecto es la siguiente (es bastante básico y seguramente se amplíe y mejore conforme el proyecto avance):
~~~
# define the name of the virtual environment directory
VENV := venv

# default target, when make executed without arguments
all: venv

$(VENV)/bin/activate: requirements.txt
	python -m venv $(VENV)
	./$(VENV)/bin/pip install -r requirements.txt

# venv is a shortcut target
venv: $(VENV)/bin/activate

run: venv
	./$(VENV)/bin/python main.py

test: pytest

clean:
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete

.PHONY: all venv run clean
~~~
### Biblioteca de tests/aserciones
Se ha elegido *Pytest* ya que es el que se recomienda en la documentación proporcionada en el hito y además tiene una documentación bastante detallada. Además, parece más sencillo de usar que *unittest*, que es el módulo por defecto en Python. Un ejemplo de un test sería el siguiente:
~~~
import pytest
from main import funcTestFunc

def test_sample():
    assert funcTestFunc("tests/Three Samples_ASCII.cue") == dict
~~~
### Integración continua
Para la integración continua se ha elegido Github Actions. Es uno de los sistemas más usado, tiene un *free tier* bastante holgado antes de tener que pagar.

La configuración es bastante sencilla. Hay que crear en el proyecto un archivo `.yml`en el siguiente directorio:
> .github/workflows/[nombre_al_gusto].yml

Tras esto hay que configurar el trabajo que se quiere hacer. Para el caso de este proyecto se usa la siguiente configuración (seguramente se amplíe conforme avance el proyecto):
~~~
name: Integración continua v.0.1

on:
    push:
        branches: [master, main]
    pull_request:
        branches: [master, main]

jobs:
    build:
        runs-on: ubuntu-latest

        steps:
            - name: Install ffmpeg
              run: sudo apt install -y ffmpeg

            - name: Checkout code
              uses: actions/checkout@v2
            
            - name: Set up Python
              uses: actions/setup-python@v2
              with:
                python-version: '3.12.7'

            - name: Install dependencies
              run: |
                python -m pip install --upgrade pip
                pip install -r requirements.txt

            - name: Run tests
              run: |
                pytest test_basics.py
~~~
## Hito 3

### Framework

Para la elección del microservicio se ha optado por el módulo Flask de Python. Se ha optado por ese *framework* por ser minimalista, fácil de usar y ligero. Su documentación es también bastante abundante y, al estar su uso bastante extendido, hay cantidad de soluciones a problemas vía online. Por último, y como ventaja decisiva frente a otros framworks como Django, permitía solucionar el problema central de este proyecto, es decir, la subida y bajada de archivos a través de la API, de una forma sencilla.

### Diseño de la API

- **Método POST en /cue:** para subir un archivo `.cue`. Como respuesta se tendrá el nombre adaptado del archivo `.cue` o un mensaje de error.
- **Método POST en /audio:** para subir un archivo de audio. Los tipos permitidos son: `.flac .wave .mp3 .ape`. Como respuesta se tendrá el nombre adaptado del archivo de audio o un mensaje de error.
- **Método GET en /info/<nombre_cue>:** devuelve información del álbum a trocear y qué pistas se han encontrado o un mensaje de error.
- **Método GET en /download/<nombre_cue>:** realiza el troceado del álbum y envía el resultado en un `.zip` o un mensaje de error.

### Logs
Como herramienta de logs se ha optado por la que ofrece el propio módulo de flask. Proporciona registros de la IP que realizó la petición, hora, protocolo, ruta y resultado.

Como herramienta para el análisis de logs se podría usar la suite de elastic. No se ha optado por realizar una demostración (todavía) puesto que el periodo de prueba es solo de 15 días.

También se ha habilitado una base de datos que registrará la música que se ha subido al servidor de la API.

## Hito 4

### Estructura del clúster de contenedores

Los tres contenedores que conformarán el clúster serán:
- **Frontend**: un contenedor que servirá como frontend para la API en caso de que se quiera usar a través del navegador.
- **API**: la API en sí. Este contenedor también tendrá disponible un puerto para utilizar la API sin necesidad de utilizar el frontend.
- **Database**: un contenedor que implementará una base de datos Postgresql para registrar qué música se ha subido al contenedor de la API.

### Documentación de los contenedores.

- **Database**: este contenedor es el más sencillo en términos de configuración. Utiliza la imagen más reciente de Postgresql. Se configura para el usuario por defecto una contraseña y se crea una base de datos. El nombre del contenedor es importante para que la API puede conectarse a él y escribir en la base de datos. Tendrá abierto el puerto 5432 para comunicarse con la API y con el exterior. Este contenedor no requiere de un Dockerfile para construir su imagen.
>sudo docker run --network nat --name my-postgres-database -e POSTGRES_PASSWORD=1234 -e POSTGRES_DB=music_chops -d -p 5432:5432 postgres

- **Frontend**: este contenedor ejecutará una simple web echa en VUE que permite hacer peticiones a la API. La web se sirve mediante un servidor NGINX que tendrá disponible el puerto 80. Para lanzar el contenedor se hace de la siguiente forma:
>sudo docker run -dit --network nat -p 8080:80 --name frontend proyecto-cc/frontend-test
- **API**: este contenedor ejecutará la API construida en el Hito 3. Se comunicará con el frontend y el exterior mediante el puerto 5000, y con la base de datos mediante el puerto 5432.
>sudo docker run --name backend -p 5000:5000 --network nat -dit proyecto-cc/backend-test

Por último, nótese que todos los contenedores deben engancharse a la misma red para que sean funcionales.

### Documentación de los dockerfiles

**Frontend**: Se parte de una imagen de node.js para compilar la web creada en Vue. Tras esto se utiliza una imagen de nginx para servirla a través de él.
~~~
FROM node:lts-alpine AS build-stage
WORKDIR /app
COPY package*.json ./
#COPY *js ./
RUN npm install
COPY . .
RUN npm run build
FROM nginx:stable-alpine AS production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY default.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
~~~
Adicionalmente, se tiene un .dockerignore para descartar ciertos archivos y directorios que no deben añadirse a la imagen:
~~~
node_modules
docker-notas
~~~
Y un archivo `default.conf` personalizado para NGINX de forma que la web en VUE funcione correctamente:
~~~
server {
    listen       80;
    listen  [::]:80;
    server_name  localhost;

    #access_log  /var/log/nginx/host.access.log  main;

    location / {
    	try_files $uri $uri/ /index.html;
        root   /usr/share/nginx/html;
        index  index.html index.htm;
    }

    #error_page  404              /404.html;

    # redirect server error pages to the static page /50x.html
    #
    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/share/nginx/html;
    }

    # proxy the PHP scripts to Apache listening on 127.0.0.1:80
    #
    #location ~ \.php$ {
    #    proxy_pass   http://127.0.0.1;
    #}

    # pass the PHP scripts to FastCGI server listening on 127.0.0.1:9000
    #
    #location ~ \.php$ {
    #    root           html;
    #    fastcgi_pass   127.0.0.1:9000;
    #    fastcgi_index  index.php;
    #    fastcgi_param  SCRIPT_FILENAME  /scripts$fastcgi_script_name;
    #    include        fastcgi_params;
    #}

    # deny access to .htaccess files, if Apache's document root
    # concurs with nginx's one
    #
    #location ~ /\.ht {
    #    deny  all;
    #}
}
~~~

**API**: Se parte de una imagen de Alpine Linux, que será la base sobre la que se ejecutará la API. Esto es así porque la API requiere del uso de `ffmpeg` y era la solución más directa para poder usarla (crear una imagen con python y ffmpeg no es trivial). Se ha optado por Alpine Linux por ser ligera y ampliamente usada en contenedores. En esta imagen de Alpine Linux se instalarán ffmpeg y python. Tras esto se le proporcionarán los archivos para instalar la API y sus dependencias y se lanzará el servidor. Para esto se ha optado por `gunicorn`.
~~~
FROM alpine:3.20
RUN apk add --no-cache python3 py3-pip
RUN apk add ffmpeg
WORKDIR /home/api
COPY ./api.py .
COPY ./requirements.txt .
COPY ./setup.py .
COPY ./splitter.py .
COPY ./README.md .
RUN python3 -m venv venv
RUN source venv/bin/activate
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn
RUN venv/bin/pip install build
RUN venv/bin/pip install .
EXPOSE 5000
ENTRYPOINT ["venv/bin/gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "300", "api:app"]
~~~

### Documentación del Docker Compose.

El `docker-compose.yml` para este clúster de contenedores lanzará cada uno de los contenedores tal y como se ha descrito en secciones anteriores. También creará una red de docker propia de tipo puente y enganchará a los contenedores a esta.

~~~
version: '3.8'

services:
  backend:
    image: proyecto-cc/backend-v1
    container_name: backend
    ports:
      - "5000:5000"
    networks:
      - app_nat
    restart: always

  frontend:
    image: proyecto-cc/frontend-v1
    container_name: frontend
    ports:
      - "8080:80"
    networks:
      - app_nat
    restart: always

  database:
    image: postgres
    container_name: my-postgres-database
    environment:
      POSTGRES_PASSWORD: 1234
      POSTGRES_DB: music_chops
    ports:
      - "5432:5432"
    networks:
      - app_nat
    restart: always

networks:
  app_nat:
    driver: bridge
~~~
