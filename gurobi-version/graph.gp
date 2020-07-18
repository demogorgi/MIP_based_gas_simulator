set datafile separator ","
if (!exists("filename")) filename='instances/da2/output/information.csv'
while (1) {
    plot filename every ::1 using 6:7, filename every ::1 using 8:9, x
    pause 1
}
