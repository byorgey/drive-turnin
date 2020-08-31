#!/usr/bin/python

from __future__ import print_function
import httplib2
import os
import io
import sys

import re

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

classes = \
    { '382': '1Tfx4UdF7n5YssUHqsX-H3aAS4ERCUTiU0D7JrhEmzd8',
      '410': '1vn2YagETsFJReoN4Jd7SstBS2t3RqT3uoCDnnJ24zAs',
      '410g': '11BbjzykVg27BJBJXejG5DVrKajhTctpSMoVcq7XSCn4'
    }

def main():
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

    if len(sys.argv) > 2:

        with open(filename, 'rb') as csvfile:
            submissions = csv.reader(csvfile, delimiter=',', quotechar='"')
            assignment = sys.argv[2]

            first_line = True

            for s in submissions:
                if first_line:
                    first_line = False
                    assignment_col = s.index('Assignment')

                elif (assignment in s[assignment_col]):
                    student_name = s[1]

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
