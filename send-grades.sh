#!/usr/bin/zsh

python3 get-submissions.py "${1}g"
python3 format_grades.py gradebook-$1.csv

# To actually send grades, go into directory with generated student folders and
#
#   for d in *(/); do msmtp -t < $d/*.txt; done
