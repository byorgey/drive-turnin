#!/usr/bin/zsh

./get-submissions.py "${1}g"
./format_grades.py gradebook-$1.csv ../encrypt/students/
cd ../encrypt && ./publish.py keys.txt students students-enc && aws s3 sync students-enc/ s3://ozark.hendrix.edu/~yorgey/encrypted/
