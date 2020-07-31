set datafile separator ","
set grid
if (!exists("filename")) filename='instances/da2/output/information.csv'
f(x) = system(sprintf("wc -l %s | cut -f1 -d' '", x))
while (1) {
    r = f(filename)
    set multiplot #layout 3, 1 title "Quality plot"
    #
    set key inside right top
    set xlabel "Time"
    set ylabel "Dispatcher penalty"
    set origin 0, 0.8
    set size 1, 0.2
    plot [0:r] filename every ::1 using :17 with lines title "Dispatcher penalty"
    #
    set key inside right top
    set xlabel "Time"
    set ylabel "Accumulated penalty"
    set origin 0, 0.6
    set size 1, 0.2
    plot [0:r] filename every ::1 using :19 with lines title "Accumulated penalty"
    #
    set key inside right top
    set xlabel "Time"
    set ylabel "Nominations and flows\nin 1000 m³/h"
    set origin 0, 0.4
    set size 1, 0.2
    plot [0:r] filename every ::1 using :6 with steps lt 1 lw 2 title "nom(EN)", filename every ::1 using :7 with steps lt 1 dt 2 title "flow(EN)", filename every ::1 using :8 with steps lt 2 lw 2 title "nom(EH)", filename every ::1 using :9 with steps lt 2 dt 2 title "flow(EH)" 
    #
    set key inside left top
    set xlabel "Nomination in 1000 m³/h"
    set ylabel "Flow in 1000 m³/h"
    set origin 0, 0
    set size 0.4, 0.4
    plot [-500:1200][-500:1200] filename every ::1 using 6:7 title "nom(EN) vs. flow(EN)", filename every ::1 using 8:9 title "nom(EH) vs. flow(EH)", x title "perfect match"
    #
    unset multiplot
    pause 1
}
