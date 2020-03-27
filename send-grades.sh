#!/usr/bin/zsh

./get-submissions.py "${1}g"
./format_grades.py gradebook-$1.csv $2
