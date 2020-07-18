set datafile separator ","
set grid
set title "Quality plot"
set xlabel "Nomination in 1000 m³/h"
set ylabel "Flow in 1000 m³/h"
if (!exists("filename")) filename='instances/da2/output/information.csv'
while (5) {
    plot [-500:2500][-500:2500] filename every ::1 using 6:7 title "nom(EN) vs. flow(EN)", filename every ::1 using 8:9 title "nom(EH) vs. flow(EH)", x title "perfect match"
    #plot [0:1100][0:1100] filename every ::1 using 6:7 title "nom(EN) vs. flow(EN)", filename every ::1 using 8:9 title "nom(EH) vs. flow(EH)", x title "perfect match"
    pause 1
}
