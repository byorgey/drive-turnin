#!/usr/bin/python3

import re
import sys
from pathlib import Path
import subprocess
import time

import chevron

if len(sys.argv) < 4:
    print("Usage: email-files.py <subject> <email body> <file>*")
    sys.exit(0)

subject = sys.argv[1]
template = sys.argv[2]
files = sys.argv[3:]

if not template.endswith('txt') and not template.endswith('mustache'):
    print(f"Supposed email template file {template} doesn't have .txt or .mustache extension, aborting!")
    sys.exit(1)

alias_dict = {}
with Path("~/.aliases/stu.aliases").expanduser().open() as aliases:
    for alias in aliases:
        m = re.search(r"\"(.*) <(.*)>", alias)
        if m:
            alias_dict[m.group(1).lower()] = m.group(2)

for f in files:
    name = ' '.join(re.split(' |/', f.replace(',',''))[:2])
    if name.lower() in alias_dict:
        email = alias_dict[name.lower()]
        print(f'Sending {f} to {name} ({email})...')
        with open(template, 'r') as template_file:
            if template.endswith('txt'):
                template_txt = template_file.read()
            else:
                template_txt = chevron.render(template_file, {'fname': name.split(' ')[0]})

        mutt_process = subprocess.Popen(['mutt', '-a', f, '-s', subject, '--', email], stdin=subprocess.PIPE)
        mutt_process.stdin.write(bytes(template_txt, 'utf-8'))
        mutt_process.stdin.close()

        time.sleep(0.5)

    else:
        print(f'WARNING: no email found for {name}!')

