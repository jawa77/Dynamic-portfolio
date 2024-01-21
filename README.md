# change these in that app

### src/__init__.py

config_file = "/home/Jawahar.s/website_flask/config.json"

### templates/cctv.html

var defaultBaseUrl = 'https://jawa.selfmade.technology/hls/';

### in app.py change the folder path

import sys
sys.path.append('/home/Jawahar.s/website_flask')

### create config.json inside the project folder

{
    "mangodb_conection_string":"Conection string",
    "mongodb_database":"jawahar_iot_cloud",
    "secret_key": "Vr4d5lvRh5j6FJ5Cmbzm",
    "secretPass":"Secret room pass",
    "mailPass":"get app pasword from gmail account",
    "mailforotp":"your mail"

}
