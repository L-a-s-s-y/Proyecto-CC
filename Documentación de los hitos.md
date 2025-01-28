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

## Hito 5

### Cambios en el clúster de contenedores
Para un correcto despliegue de la aplicación se han tenido que realizar algunas modificaciones al clúster de contenedores:
#### Reverse proxy y CORS
Se ha implementado un contenedor adicional para que actúe como reverse proxy para el backend. Esto es necesario para poder utilizar este backend desde el frontend desde otras ubicaciones. Si no se usa este resverse proxy, se viola la política CORS, aun teniéndola habilitada en la aplicación de flask que se ejecuta en el backend.

Este nuevo contenedor es muy sencillo. Parte de una imagen de nginx a la que hay que modificar para que actúe como este reverse proxy. Para ello se utiliza este default.conf modificado:
~~~
server {
    listen       80;
    server_name  localhost;

    client_max_body_size 5000M; # Aumentar el límite del tamaño de la solicitud
    # Agregar tiempos de espera personalizados
    proxy_read_timeout 300s;
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;

    add_header 'Access-Control-Allow-Origin' '*' always;
    add_header 'Access-Control-Allow-Credentials' 'true' always;
    add_header 'Access-Control-Allow-Headers' 'Authorization,Accept,Origin,DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Content-Range,Range' always;
    add_header 'Access-Control-Allow-Methods' 'GET,POST,OPTIONS,PUT,DELETE,PATCH' always;

    location / {
        proxy_pass http://backend:5000;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Prefix /;

    	# Mantener el resto de los encabezados tal como los envía el backend
    	proxy_pass_header Content-Disposition;
    	# Asegúrate de que los encabezados como Content-Disposition se transmitan
    	proxy_hide_header Content-Disposition;
    	
    	
        # Manejar solicitudes OPTIONS
        if ($request_method = OPTIONS) {
            add_header 'Access-Control-Allow-Origin' '*' always;
            add_header 'Access-Control-Allow-Credentials' 'true' always;
            add_header 'Access-Control-Allow-Headers' 'Authorization,Accept,Origin,DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Content-Range,Range' always;
            add_header 'Access-Control-Allow-Methods' 'GET,POST,OPTIONS,PUT,DELETE,PATCH' always;
            return 204; # Sin contenido
        }
    }

    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}

~~~

El Dockerfile asociado es muy sencillo:
~~~
FROM nginx:stable-alpine
COPY default.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
ENTRYPOINT ["nginx", "-g", "daemon off;"]
~~~

Ahora, al archivo Docker Compose, se le añade este nuevo contenedor:
~~~
version: '3.8'

services:
  proxy:
    image: proyecto-cc/proxy
    container_name: proxy
    ports:
      - "80:80"
    networks:
      - app_nat
    restart: always
    
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
    environment:
      - VUE_APP_API_MACHINE=http://192.168.178.29:80
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
Destacar que ahora, a la dirección IP del backend se accede mediante el puerto 80.

#### Asignación de la IP del backend de forma dinámica en el frontend
El otro problema a resolver es dotar al frontend de la IP de la máquina donde se aloja el backend. No solo basta con la IP dentro de la red docker sino que debe usarse la IP de la máquina donde se aloja. Esto es debido a que el frontend no es más que un programa en javascript que se ejecutará en el navegador del usuario. Por tanto debe tener acceso a la IP pública donde se ejecute el backend.

Para ello se ha creado un archivo `.env` en el proyecto de Vue que permite definir variables de entorno. Se debe crear una variable de entorno dentro de la siguiente forma:
~~~
VUE_APP_API_MACHINE=VUE_APP_API_MACHINE
~~~
El nombre debe empezar por VUE_APP aunque el resto es al gusto del creador.

Lo siguiente es crear un archivo `app.config.js` con el siguiente código:
~~~
export const backend = process.env.VUE_APP_API_MACHINE

export default {
    backend,
}
~~~
La variable ***backend*** será la que almacene la dirección IP.

El último archivo será un script de shell (`.sh`) para sustituir el valor de la variable de entorno VUE_APP por el valor de la variable de entorno que se le proporcionará al contenedor:
~~~
#!/bin/sh

ROOT_DIR=/usr/share/nginx/html

# Replace env vars in JavaScript files
echo "Replacing env constants in JS"
for file in $ROOT_DIR/js/app.*.js* $ROOT_DIR/index.html $ROOT_DIR/precache-manifest*.js;
do
  echo "Processing $file ...";

  sed -i 's|VUE_APP_API_MACHINE|'${VUE_APP_API_MACHINE}'|g' $file 

done

echo "Starting Nginx"
nginx -g 'daemon off;'
~~~
Para proporcionar la IP deseada cuando se despliegue la aplicación, bastará con especificar la IP adecuada en el archivo Docker Compose:
~~~
frontend:
    image: proyecto-cc/frontend-v1
    container_name: frontend
    ports:
      - "8080:80"
    networks:
      - app_nat
    environment:
      - VUE_APP_API_MACHINE=http://192.168.178.29:80
    restart: always
~~~
Se ha modificado el Dockerfile del contenedor del frontend para que se ejecute el script:
~~~
FROM node:lts-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
FROM nginx:stable-alpine AS production-stage
COPY default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
COPY entrypoint.sh /usr/share/nginx/html/entrypoint.sh
RUN chmod +x /usr/share/nginx/html/entrypoint.sh
EXPOSE 80
WORKDIR /usr/share/nginx/html
ENTRYPOINT ["./entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
~~~

### Despliegue en AWS
Como plataforma Cloud se ha elegido AWS. Es una de las plataformas más utilizadas, lo cual nos garantiza bastante documentación y ayuda en caso de necesitarla. Además, el tier gratuito es bastante variado y, entre lo ofertado, están distintas máquinas virtuales de Linux, que serán la base para desplegar los contenedores.

#### Detalles del despligue

Se ha utilizado una instancia de EC2 con SO Amazon Linux. La configuración es bastante estándar salvo porque hay que añadir los permisos para todos los orígenes para ssh, http, https (posteriormente se verá que hay que añadir más).

Una vez creada hay que añadir dos reglas ACL para los puertos 8080 (puerto para acceder al frontend) y para el puerto 5432 (puerto para acceder a la base de datos de Postgresql). Esto se puede hacer antes o después del siguiente paso.

Una vez conectados a la instancia EC2 hay que ejecutar las siguientes órdenes para poner a punto la máquina
- **Actualizar el sistema**
>sudo yum update -y
- **Instalar docker**
>sudo yum install docker
- **Iniciar docker**
>sudo service docker start
- **Instalar git**
>sudo yum install git
- **Clonar el repositorio**
>git clone https://github.com/L-a-s-s-y/Proyecto-CC.git
- **Construir cada uno de los contenedores a partir de su dockerfile**
- **Modificar Docker Compose para añadir la IP pública de la máquina a la variable de entorno del frontend**
- **Instalar docker compose**
>	sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
>	sudo chmod +x /usr/local/bin/docker-compose
>	docker-compose --version
- **Desplegar la aplicación con docker-compose**
>sudo docker-compose up -d
