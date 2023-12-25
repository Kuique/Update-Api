from flask import Flask, jsonify, request
from flask_cors import CORS
from pocketbase import PocketBase
import requests
import platform
import json
import time 

system = platform.system()
app = Flask(__name__)
CORS(app)
pb = PocketBase('http://54.37.245.123:8090')
class Data:
    actual_time = 0
    last_time_get_relaease = 0
    
    github_latest_release_url_myapp = 'https://api.github.com/repos/Youssef6022/My-app/releases/latest'
    myapp_headers = None
    
    release = None

data = Data()
@app.route('/get_latest_release/<target>/<arch>/<current_version>')
def api(target, arch, current_version):
    try:
        data.actual_time = time.time()
        if data.actual_time > data.last_time_get_relaease + 300:
            data.release = requests.get(data.github_latest_release_url_myapp).json()
            data.last_time_get_relaease = data.actual_time
            print('Release updated')
            
        release_response = {
            'version': data.release['tag_name'],
            'notes': data.release['body'].removesuffix('See the assets to download this version and install.').rstrip('\r\n '),
            'pub_date': data.release['published_at'],
            'platforms': {
                f"{target}-{arch}": {
                    "url": data.release['assets'][1]['browser_download_url'],
                    "signature": requests.get(data.release['assets'][1]['browser_download_url'] + '.sig').text
                }
            }
        }
        return release_response
    except requests.RequestException:
        return {}
    
@app.route('/login', methods=['POST'])
def login():
    userkey = request.json.get('userkey')
    hwid = request.json.get('hwid')

    list_result = pb.collection('NoxuUsers').get_list()
    records = list_result.items
    record = next((record for record in records if record.user_key == userkey), None)
    if not record:
        return jsonify({"error": "Invalid userkey"}), 401

    if not record.hwid: 
        pb.collection('NoxuUsers').update(record.id, {'hwid': hwid})
        return jsonify({"message": "HWID updated and login successful"})

    if record.hwid != hwid:
        return jsonify({"error": "Key already used on another device"}), 401

    return jsonify({"message": "Login successful"})

if __name__ == '__main__':
    if system == 'Windows':
        app.run(debug=True)
    if system == 'Linux':
        app.run(host='0.0.0.0', port=9566)