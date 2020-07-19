set datafile separator ","
set grid
if (!exists("filename")) filename='instances/da2/output/information.csv'
f(x) = system(sprintf("wc -l %s | cut -f1 -d' '", x))
while (1) {
    set multiplot layout 2, 1 title "Quality plot"
    #
    set key inside right top
    set xlabel "Time"
    set ylabel "Dispatcher penalty"
    plot [0:f(filename)] filename every ::1 using :17 with lines title "Dispatcher penalty"
    #
    set key outside right top
    set xlabel "Nomination in 1000 m³/h"
    set ylabel "Flow in 1000 m³/h"
    plot [-500:1200][-500:1200] filename every ::1 using 6:7 title "nom(EN) vs. flow(EN)", filename every ::1 using 8:9 title "nom(EH) vs. flow(EH)", x title "perfect match"
    #
    unset multiplot
    pause 5
}
