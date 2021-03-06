#!/usr/bin/python3

import re
import os
import sys
import csv

CURSEMESTER = '21G'

if len(sys.argv) < 2:
    print("Usage: format_grades.py <gradebook> [<message file>] [<output dir>]")
    sys.exit(0)

gradebook_file = sys.argv[1]

classNum = re.match(r".*-(M?\d+)\.csv", gradebook_file).group(1)


if len(sys.argv) < 4:
    outdir = f'/home/brent/teaching/{classNum}/{CURSEMESTER}/grades/'
    print(f'Defaulting to output dir {outdir}...')
else:
    print(f'Using custom output dir {sys.argv[3]}...')
    outdir = sys.argv[3]

classNames =\
    { '365': 'Functional Programming',
      'M240': 'Discrete Math',
      '410': 'Senior Seminar',
      '150': 'CSCI 150',
      '151': 'Data Structures',
      '360': 'Programming Languages',
      '382': 'Algorithms'
    }

className: str = classNames[classNum]

if len(sys.argv) < 3:
    print('Using default message...')
    message = f'Here are your most recent grades for {className}.  I do sometimes make mistakes or miss things, so please let me know if you have any questions or notice any discrepancies.\n\n'
else:
    print(f'Loading message from {sys.argv[2]}...')
    with open(sys.argv[2], 'r') as msgfile:
        message = msgfile.read()

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
            emailColumn: int = entry.index('Email')
            nameColumn: int = entry.index('Preferred')

            try:
                droppedColumn: int = entry.index('Dropped (!)')
            except ValueError:
                droppedColumn = -1
        else:
            email = entry[emailColumn]
            name  = entry[nameColumn]
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

                    student_file.write(f'Subject: Current {className} grades\n')
                    student_file.write(f'To: {email}\n')
                    student_file.write(f'From: Brent Yorgey <yorgey@hendrix.edu>\n\n')

                    student_file.write(f'Dear {name},\n\n')
                    student_file.write(message)
                    for i in range(len(header)):
                        if ('(!)' not in header[i] and header[i] != ''):
                            field = header[i]
                            if (field[0] == '-'):
                                field = '  ' + field[1:]
                            if (totals[i] == '' or totals[i] == 'Total'):
                                student_file.write('%-25s: %s\n' % (field, entry[i]))
                            else:
                                student_file.write('%-25s: %5s / %3s\n' % (field, entry[i], totals[i]))
