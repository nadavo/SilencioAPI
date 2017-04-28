import webbrowser

import httplib2
from click._compat import raw_input
from auth import authorized
from flask import Flask, jsonify, request
from flask import request
from googleapiclient import discovery
from oauth2client import client
from oauth2client import crypt
from oauth2client.client import AccessTokenCredentials

CLIENT_ID = '1035698262681-trd8sf2imu42st43sfr5iik21l8nov5o.apps.googleusercontent.com'
app = Flask(__name__)

# @app.route('/', methods=['POST'])
# def main():
#     flow = client.flow_from_clientsecrets(
#         'client_secret.json',
#         scope='https://www.googleapis.com/auth/drive.metadata.readonly',
#         redirect_uri='urn:ietf:wg:oauth:2.0:oob')
#
#     # auth_uri = flow.step1_get_authorize_url()
#     # webbrowser.open(auth_uri)
#     #
#     # auth_code = raw_input('Enter the auth code: ')
#     # r = request.json()
#     token = request.form['token']
#     try:
#         idinfo = client.verify_id_token(token, CLIENT_ID)
#
#         # Or, if multiple clients access the backend server:
#         # idinfo = client.verify_id_token(token, None)
#         # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
#         #    raise crypt.AppIdentityError("Unrecognized client.")
#
#         if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
#             raise crypt.AppIdentityError("Wrong issuer.")
#     except crypt.AppIdentityError:
#         return "check"
#
#     userid = idinfo['sub']
#     return userid
#     credentials  = AccessTokenCredentials(token, 'my-user-agent/1.0')
#     # credentials = flow.step2_exchange(token)
#     http_auth = credentials.authorize(httplib2.Http())
#
#     drive_service = discovery.build('drive', 'v2', http_auth)
#     files = drive_service.files().list().execute()
#     for f in files['items']:
#         return f['title']


@app.route('/return')
def page():
    return "check"


@app.route('/', methods=['POST'])
def main():
    json = request.get_json(force=True, silent=True)
    auth_code = json["auth_code"]
    #
    # try:
    #     idinfo = client.verify_id_token(token, CLIENT_ID)
    #
    #     # Or, if multiple clients access the backend server:
    #     # idinfo = client.verify_id_token(token, None)
    #     # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
    #     #    raise crypt.AppIdentityError("Unrecognized client.")
    #
    #     if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
    #         raise crypt.AppIdentityError("Wrong issuer.")
    #
    #         # If auth request is from a G Suite domain:
    #         # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
    #         #    raise crypt.AppIdentityError("Wrong hosted domain.")
    # except crypt.AppIdentityError:
    #     return "Error"
    # # Invalid token
    # userid = idinfo['sub']
    # print(userid)


    CLIENT_SECRET_FILE = '/home/ofeder/Desktop/silencio/client_secret.json'

    # Exchange auth code for access token, refresh token, and ID token
    credentials = client.credentials_from_clientsecrets_and_code(
        CLIENT_SECRET_FILE,
        ['https://www.googleapis.com/auth/gmail.labels', 'profile', 'email'],
        auth_code)

    http_auth = credentials.authorize(httplib2.Http())

    # Call Google API
    # http_auth = credentials.authorize(httplib2.Http())
    # drive_service = discovery.build('drive', 'v3', http=http_auth)
    # appfolder = drive_service.files().get(fileId='appfolder').execute()

    # Get profile info from ID token
    userid = credentials.id_token['sub']
    email = credentials.id_token['email']
    return email

if __name__ == "__main__":
    # app.run(host="0.0.0.0")
    app.run()
