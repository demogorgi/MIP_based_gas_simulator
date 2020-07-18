set datafile separator ","
set grid
if (!exists("filename")) filename='instances/da2/output/information.csv'
while (1) {
    plot filename every ::1 using 6:7 title "nom(EN) vs. flow(EN)", filename every ::1 using 8:9 title "nom(EH) vs. flow(EH)", x title "perfect match"
    pause 1
}
