#!/usr/bin/python3

import re
import os
import sys
import csv

CURSEMESTER = '20G'

if len(sys.argv) < 2:
    print("Usage: format_grades.py <gradebook> [<output dir>]")
    sys.exit(0)

gradebook_file = sys.argv[1]

classNum = re.match(r".*-(M?\d+)\.csv", gradebook_file).group(1)


if len(sys.argv) < 3:
    outdir = f'/home/brent/teaching/{classNum}/{CURSEMESTER}/grades/'
    print(f'Defaulting to output dir {outdir}...')
else:
    outdir         = sys.argv[2]

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
                    student_file.write(f'Here are your most recent grades for {className}.  I do sometimes make mistakes or miss things, so please let me know if you have any questions or notice any discrepancies.\n\n')
                    for i in range(len(header)):
                        if ('(!)' not in header[i]):
                            student_file.write('%-25s: %s\n' % (header[i], entry[i]))
