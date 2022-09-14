#!/usr/bin/python3

import re
import os
import sys
import csv
from pathlib import Path

CURSEMESTER = '22L'

if len(sys.argv) < 2:
    print("Usage: format_grades.py <gradebook> [<message file>] [<subject>] [<output dir>]")
    sys.exit(0)

gradebook_file = sys.argv[1]

classNumMatch = re.match(r".*-(M?\d+)\.csv", gradebook_file)
if classNumMatch is not None:
    classNum = classNumMatch.group(1)
else:
    classNum = 'unknown'

if len(sys.argv) < 5:
    outdir = f'/home/brent/teaching/{classNum}/{CURSEMESTER}/grades/'
    print(f'Defaulting to output dir {outdir}...')
else:
    print(f'Using custom output dir {sys.argv[4]}...')
    outdir = sys.argv[4]

classNames =\
    { '365': 'Functional Programming',
      'M240': 'Discrete Math',
      '410': 'Senior Seminar',
      '150': 'CSCI 150',
      '151': 'Data Structures',
      '360': 'Programming Languages',
      '382': 'Algorithms',
      '322': 'CSO',
      'unknown': 'Unknown'
    }

className: str = classNames[classNum]

if len(sys.argv) < 3:
    custom_msg = outdir + '/grades_msg.txt'
    if os.path.exists(custom_msg):
        print(f'Loading message from {custom_msg}...')
        with open(custom_msg, 'r') as msgfile:
            message = msgfile.read()
    else:
        print('Using default message...')
        message = f'Here are your most recent grades for {className}.  I do sometimes make mistakes or miss things, so please let me know if you have any questions or notice any discrepancies.\n\n'
else:
    print(f'Loading message from {sys.argv[2]}...')
    with open(sys.argv[2], 'r') as msgfile:
        message = msgfile.read()

if len(sys.argv) < 4:
    print('Using default subject...')
    subject = ''
else:
    subject = sys.argv[3]
    print(f'Using custom subject: {subject}')

alias_dict = {}
with Path("~/.aliases/stu.aliases").expanduser().open() as aliases:
    for alias in aliases:
        m = re.search(r"\"(.*) <(.*)>", alias)
        if m:
            alias_dict[m.group(1).lower()] = m.group(2)

with open(gradebook_file, 'r') as gradebook:
    lineCount = 0
    entries = csv.reader(gradebook, delimiter=',', quotechar='"')
    totals = []
    for entry in entries:
        lineCount += 1
        if lineCount > 1 and 'Total' in entry:
            totals = entry
            break

with open(gradebook_file, 'r') as gradebook:
    lineCount = 0
    entries = csv.reader(gradebook, delimiter=',', quotechar='"')
    for entry in entries:
        lineCount += 1
        if lineCount == 1:
            header = entry
            if 'Email' in entry:
                emailColumn: int = entry.index('Email')
            else:
                emailColumn = None

            if 'Preferred' in entry:
                nameColumn: int = entry.index('Preferred')
            elif 'Name' in entry:
                nameColumn: int = entry.index('Name')
            else:
                nameColumn = None

            try:
                droppedColumn: int = entry.index('Dropped (!)')
            except ValueError:
                droppedColumn = -1
        else:
            if emailColumn is not None:
                email = entry[emailColumn]

            if nameColumn is not None:
                name = entry[nameColumn].strip()

            if emailColumn is None and nameColumn is not None:
                if name.lower() in alias_dict:
                    email = alias_dict[name.lower()]
                else:
                    print(f'Warning, {name} not found in alias dict.')
                    email = ''

            if droppedColumn != -1:
                dropped = entry[droppedColumn]

            if email != '' and (droppedColumn == -1 or dropped != '1'):
                print("Formatting grades for " + email + "...")
                d = outdir + "/" + email
                try:
                    os.makedirs(d)
                except OSError:  # dir already exists
                    pass

                with open("%s/%s-grades.txt" % (d, classNum), 'w') as student_file:

                    if subject == '':
                        student_file.write(f'Subject: Current {className} grades\n')
                    else:
                        student_file.write(f'Subject: {subject}\n')
                    student_file.write(f'To: {email}\n')
                    student_file.write(f'From: Brent Yorgey <yorgey@hendrix.edu>\n\n')

                    student_file.write(f'Dear {name.split()[0]},\n\n')
                    student_file.write(message)
                    for i in range(len(header)):
                        if ('(!)' not in header[i] and header[i] != ''):
                            field = header[i]
                            if (field[0] == '-'):
                                field = '  ' + field[1:]
                            if (totals == [] or totals[i] == '' or totals[i] == 'Total'):
                                student_file.write('%-25s: %s\n' % (field, entry[i]))
                            else:
                                student_file.write('%-25s: %5s / %3s\n' % (field, entry[i], totals[i]))
