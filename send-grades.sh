#!/usr/bin/zsh

./get-submissions.py "${1}g"
./format_grades.py gradebook-$1.csv ../encrypt/students/
cd ../encrypt && ./publish.py keys.txt students students-enc && rsync -r students-enc/* ozark:ozark/encrypted/
