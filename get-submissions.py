#!/usr/bin/python3

# Based on https://developers.google.com/workspace/drive/api/quickstart/python

from __future__ import print_function
import httplib2
import os
import io
import sys

import re

# See https://stackoverflow.com/questions/34550023/imported-python-module-overrides-option-parser
args = sys.argv
sys.argv = [sys.argv[0]]

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

import csv

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)

    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    creds = None
    if os.path.exists(credential_path):
        creds = Credentials.from_authorized_user_file(credential_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(os.path.join(credential_dir, CLIENT_SECRET_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        print('Storing credentials to ' + credential_path)
        with open(credential_path, "w") as token:
            token.write(creds.to_json())

    return creds

# def main():
#     """Shows basic usage of the Google Drive API.

#     Creates a Google Drive API service object and outputs the names and IDs
#     for up to 10 files.
#     """
#     credentials = get_credentials()
#     http = credentials.authorize(httplib2.Http())
#     service = discovery.build('drive', 'v3', http=http)

#     results = service.files().list(
#         pageSize=10,fields="nextPageToken, files(id, name)").execute()
#     items = results.get('files', [])
#     if not items:
#         print('No files found.')
#     else:
#         print('Files:')
#         for item in items:
#             print('{0} ({1})'.format(item['name'], item['id']))

classes = \
    { '382': '1YRDpOcrAdyqjeL4pmMkbRuOFjWwlNoAz9pWpP2wntTA'
    , '382g': '1Ff881qxs3_IRj7T1BNbI4LGSxIJ7G2dk7yOiCKvLVw8'
    }

def main():
    key = args[1]
    if key in classes:
        file_id = classes[key]
    else:
        file_id = key

    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)

    if (key[-1] == 'g'):
        filename = 'gradebook-%s.csv' % key[:-1]
    else:
        filename = 'turnin-%s.csv' % key

    csv_request = service.files().export_media(fileId=file_id, mimeType='text/csv')
    download(csv_request, filename)

    if len(args) > 2:

        with open(filename, 'r') as csvfile:
            submissions = csv.reader(csvfile, delimiter=',', quotechar='"')
            assignment = args[2]

            first_line = True

            for s in submissions:
                if first_line:
                    first_line = False
                    assignment_col = 2
                    try:
                        assignment_col = s.index('Assignment')
                    except ValueError:
                        assignment_col = s.index('Project')

                    dl_col = -1
                    if 'DL' in s:
                        dl_col = s.index('DL')

                elif (assignment.lower() in s[assignment_col].lower() and (dl_col == -1 or s[dl_col] != 'Y')):
                    student_name = s[1].replace('/','')

                    print("---------- %s ----------" % student_name)
                    try:
                        os.mkdir(student_name)
                    except OSError:
                        pass
                    with open(student_name + '/submission.txt', 'w') as submissionfile:
                        for line in s:
                            submissionfile.write(line + '\n')
                    for f in s[assignment_col + 1].split(', '):
                        file_id = f.split('=')[-1]
                        if file_id == '':
                            print('Submission with no files attached, skipping...')
                            continue
                        filename = service.files().get(fileId=file_id).execute()['name']
                        filename = re.sub(r" - [^.]*", '', filename)
                        try:
                            file_request = service.files().get_media(fileId=file_id)
                            download(file_request, student_name + '/' + filename)
                        except:
                            try:
                                file_request = service.files().export_media(fileId=file_id, mimeType='application/pdf')
                                download(file_request, student_name + '/' + filename)
                            except:
                                print("Downloading %s failed." % filename)

def download(request, filename):
    print("Downloading %s..." % filename)
    fh = io.FileIO(filename, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))

if __name__ == '__main__':
    main()
