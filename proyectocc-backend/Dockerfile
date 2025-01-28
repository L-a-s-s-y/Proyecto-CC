FROM alpine:3.20
RUN apk add --no-cache python3 py3-pip
RUN apk add ffmpeg
#RUN apk add nginx
#RUN mkdir -p /run/nginx
#COPY nginx.conf /etc/nginx/nginx.conf
#RUN openrc
#RUN touch /run/openrc/softlevel
#RUN rc-service nginx start
#RUN rc-service nginx start
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
#EXPOSE 80
#RUN nginx
ENTRYPOINT ["venv/bin/gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "300", "api:app"]
