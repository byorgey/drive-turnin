#!/usr/bin/python3

import re
import os
import sys
import csv

if len(sys.argv) < 3:
    print("Usage: format_grades.py <gradebook> <output dir>")
    sys.exit(0)

gradebook_file = sys.argv[1]
outdir         = sys.argv[2]

classNum = re.match(r".*-(\d+)\.csv", gradebook_file).group(1)

with open(gradebook_file, 'r') as gradebook:
    lineCount = 0
    entries = csv.reader(gradebook, delimiter=',', quotechar='"')
    for entry in entries:
        lineCount += 1
        if lineCount == 1:
            header = entry
            emailColumn: int = entry.index('E-mail')
        else:
            email = entry[emailColumn]
            if email != '':
                print("Formatting grades for " + email + "...")
                d = outdir + "/" + email
                try:
                    os.makedirs(d)
                except OSError:  # dir already exists
                    pass

                with open("%s/%s-grades.txt" % (d, classNum), 'w') as student_file:
                    for i in range(len(header)):
                        student_file.write('%-25s: %s\n' % (header[i], entry[i]))
