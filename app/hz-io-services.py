from flask import Flask, request, jsonify, redirect
import logging, json, requests
from requests.auth import HTTPBasicAuth
import os, sys

app = Flask(__name__)
app.debug=True

form = 'horizon-developer-preview'
key = 'WUFOO_KEY'
if key not in os.environ:
    print("Wufoo key not set (%s)" % key)
    sys.exit(1)


def wufoo(form, data):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    auth = HTTPBasicAuth(os.environ[key], 'wufoo')
    req = requests.post('https://rethinkdb.wufoo.com/api/v3/forms/%s/entries.json' % form, data=data, auth=auth)
    if req.status_code is 201:
        return {
            'status': 'success',
            'errors': [],
        }
    if req.status_code is 200:
        response = json.loads(req.text)
        if response['Success'] is 0:
            if len(response['FieldErrors']) > 0:
                return {
                    'status': 'error',
                    'errors': response['FieldErrors']
                }
            app.logger.error("Data: %s\nResponse: %s" %(data,response))
            return {
                'status': 'error',
                'errors': []
            }
    app.logger.error("Data: %s\nResponse: %s" %(data,req.text))
    return {
        'status': 'error',
        'errors': []
    }

@app.before_first_request
def setup_logging():
    if not app.debug:
         # In production mode, log errors to sys.stderr
        app.logger.addHandler(logging.StreamHandler(stream=sys.stdout))
        app.logger.setLevel(logging.INFO)

@app.route("/cloud-beta", methods=['POST'])
def horizon_cloud():
    data = {
        'Field1': request.form['firstName'],
        'Field2': request.form['lastName'],
        'Field3': request.form['github'],
        'Field4': request.form['email']
    }
    return wufoo('horizon-cloud-beta', data)

@app.route("/mailing", methods=['POST'])
def mailing_list():
    data = {
        'Field1': request.form['email']
    }
    return wufoo('horizon-cloud-beta', data)

if __name__ == '__main__':
    app.run()
