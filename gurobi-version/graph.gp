set datafile separator ","
set grid
if (!exists("filename")) filename='instances/da2/output/information.csv'
while (1) {
    plot filename every ::1 using 6:7 title "flow(EN) vs. nom(EN)", filename every ::1 using 8:9 title "flow(EH) vs. nom(EH)", x title "perfect match"
    pause 1
}
