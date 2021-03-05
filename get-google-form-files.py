#!/usr/bin/python3

from __future__ import print_function
import httplib2
import os
import io
import sys

import re

import os.path
from os import path

from apiclient import discovery
from apiclient.http import MediaIoBaseDownload

from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import csv

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

def main():
    if len(sys.argv) < 3:
        print('Usage: get-google-form-files.py <sheetID> <name_col>')
        sys.exit(0)

    sheet_id = sys.argv[1]
    name_col_str = sys.argv[2]

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    sheet_name = service.files().get(fileId=sheet_id).execute()['name'] + '.csv'
    csv_request = service.files().export_media(fileId=sheet_id, mimeType='text/csv')
    download(csv_request, sheet_name)

    with open(sheet_name, 'r') as csvfile:
        submissions = csv.reader(csvfile, delimiter=',', quotechar='"')
        name_col = 0

        first_line = True

        for s in submissions:
            if first_line:
                first_line = False
                name_col = s.index(name_col_str)

            elif (s[name_col] != ''):
                student_name = s[name_col].replace('/','').replace('\'','')

                print(f'---------- {student_name} ----------')
                try:
                    os.mkdir(student_name)
                except OSError:
                    pass
                with open(student_name + '/submission.txt', 'w') as submissionfile:
                    for line in s:
                        submissionfile.write(line + '\n')
                for cell in s:
                    if cell.startswith('https://drive.google.com'):
                        for f in cell.split(', '):
                            file_id = f.split('=')[-1]
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
                                    print(f'Downloading {filename} failed.')

def download(request, filename):
    print(f'Downloading {filename}...')
    if path.exists(filename):
        base,ext = path.splitext(filename)
        c = 1
        while path.exists(base + '(' + str(c) + ')' + ext):
            c += 1
        filename = base + str(c) + ext
        print(f'  (File exists, downloading as {filename}...)')
    fh = io.FileIO(filename, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))

if __name__ == '__main__':
    main()
