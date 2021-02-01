#!/usr/bin/python3

from __future__ import print_function
import httplib2
import os
import io
import sys
import subprocess

import re

from apiclient import discovery
from apiclient.http import MediaIoBaseDownload

from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import csv

import chevron

# try:
#     import argparse
#     flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
# except ImportError:
#     flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive.readonly'
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

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        # if flags:
        #     credentials = tools.run_flow(flow, store, flags)
        # else: # Needed only for compatibility with Python 2.6
        credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

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
    { 'M240': '1KVbd5FM4yZELhKEtEZC9VWadx2qBvuMCy-6adZqA78U',
      '150': '1-l0ldBmgnj81CA4hvwa9RmkgSOhBS-MfA3d7e5EUkMo'
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: get-ungraded.py <class>")
        sys.exit(0)

    key = sys.argv[1]
    if key in classes:
        file_id = classes[key]
    else:
        file_id = key

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    if (key[-1] == 'g'):
        filename = 'gradebook-%s.csv' % key[:-1]
    else:
        filename = 'turnin-%s.csv' % key

    csv_request = service.files().export_media(fileId=file_id, mimeType='text/csv')
    download(csv_request, filename)

    with open(filename, 'r') as csvfile:
        submissions = csv.reader(csvfile, delimiter=',', quotechar='"')

        first_line = True

        for s in submissions:
            if first_line:
                first_line = False
                assignment_col = s.index('Assignment')
                downloaded_col = s.index('DL')

            elif (s[downloaded_col] != 'Y'):
                timestamp = s[0].replace('/', '-')
                student_name = s[1].strip()
                assignment = s[2].strip()
                assignment_stripped = assignment.replace('#','')
                assignment_escaped  = escape(assignment)

                print("---------- %s ----------" % student_name)

                filecounter = 0
                for f in s[assignment_col + 1].split(', '):
                    file_id = f.split('=')[-1]
                    if filecounter > 0:
                        fileLetter = chr(ord('A') + filecounter)
                    else:
                        fileLetter = ''
                    filename = f'{student_name} {timestamp} {assignment_stripped}{fileLetter}'
                    pdf = filename + '.submit.pdf'
                    try:
                        file_request = service.files().get_media(fileId=file_id)
                        download(file_request, pdf)
                    except:
                        try:
                            file_request = service.files().export_media(fileId=file_id, mimeType='application/pdf')
                            download(file_request, pdf)
                        except:
                            print("Downloading %s failed." % pdf)

                    d = { 'name': student_name,
                          'timestamp': timestamp,
                          'problems': assignment_escaped,
                          'problemlist': [{'problem': p} for p in assignment_escaped.split(', ')],
                          'estimate': escape(s[4]),
                          'comments': escape(s[5]),
                        }

                    with open('../cover-sheet.tex.mustache', 'r') as tpl, open(filename + '.cover.tex', 'w') as cover_sheet:
                        cover_sheet.write(chevron.render(tpl, d))

                    subprocess.run(['pdflatex', filename + '.cover.tex'])
                    subprocess.run(['pdftk', filename + '.cover.pdf', filename + '.submit.pdf',
                                    'output', filename + '.pdf'])
                    os.system('rm *.aux *.log *.tex *.submit.pdf *.cover.pdf')

                    filecounter += 1

def download(request, filename):
    print("Downloading %s..." % filename)
    fh = io.FileIO(filename, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))

def escape(s):
    return s.replace('#', '\\#').replace('&', '\\&')

if __name__ == '__main__':
    main()
