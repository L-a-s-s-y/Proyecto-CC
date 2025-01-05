import pytest
import requests
from splitter import album_info

#TODO: por ahora los test deben de realizarse en el orden establecido. En un futuro se prevee que el backend sea más tolerante a errores.

CUE_URL="http://localhost:5000/cue"
AUDIO_URL="http://localhost:5000/audio"
INFO_URL="http://localhost:5000/info/Three_Samples_ASCII.cue"
DOWNLOAD_URL="http://localhost:5000/download/Three_Samples_ASCII.cue"

def test_info_return_type():
    assert type(album_info("tests/Three Samples_ASCII.cue")) == dict

def test_info_return_not_empty():
    assert bool(album_info("tests/Three Samples_ASCII.cue"))

#def test_cue_get():
#    peticion = requests.get(CUE_URL)
#    assert peticion.status_code == 200

#def test_audio_get():
#    peticion = requests.get(AUDIO_URL)
#    assert peticion.status_code == 200

def test_cue_post():
    files = {'file': open('tests/Three Samples_ASCII.cue', 'rb')}
    peticion = requests.post(CUE_URL, files=files)
    assert peticion.status_code == 200

def test_audio_post():
    files = {'file': open('tests/Three Samples.flac', 'rb')}
    #peticion = requests.post(AUDIO_URL+"?name=Three_Samples_ASCII.cue", files=files)
    peticion = requests.post(AUDIO_URL+"?name=Three_Samples_ASCII.cue", files=files)
    assert peticion.status_code == 200

def test_info_code():
    peticion = requests.get(INFO_URL)
    assert peticion.status_code == 200

def test_info_json():
    peticion = requests.get(INFO_URL)
    assert type(peticion.json()) == dict and bool(peticion.json())

def test_download():
    peticion = requests.get(DOWNLOAD_URL)
    assert type(peticion.content) == bytes