print "#########################################"
print "Invocation example:"
print ">gnuplot -e \"threshold=666;start=10;end=20;filename='example.csv'\" multi.gp"
print "- if filename is not set 'instances/da2/output/information.csv' will be used"
print "- start: first line in information.csv that will be used for plotting"
print "- end: last line in information.csv that will be used for plotting"
print "- threshold: if threshold is set, a straight line at threshold is drawn in second plot"
print "#########################################"
set terminal qt 0 font "Sans,12"
set datafile separator ","
set grid
if (!exists("threshold")) threshold=-1
if (!exists("start")) start=0
if (!exists("end")) {
   x=1
} else {
   x=0
}
if (!exists("filename")) filename='instances/da2/output/information.csv'
f(x) = system(sprintf("wc -l %s | cut -f1 -d' '", x))
if (threshold) > 0 {
    title_t(threshold) = sprintf('threshold %.1f', threshold)
} else {
    title_t(threshold) = ""
}
while (1) {
    if (x) {end=f(filename)}
    if (end <= 280) {
       set xtics 0, 8
    }
    set lmargin 12
    set rmargin 12
    set multiplot #layout 3, 1 title "Quality plot"
    #
    set key inside top outside center horizontal
    set xlabel "Time"
    set ylabel "gas"
    set ytics nomirror
    set y2range [0:1300]
    set y2tics
    set y2label "zeta"
    set origin 0, 0.8
    set size 1, 0.2
    plot [start:end][-0.05:1.05] filename every ::1 using :10 with steps title "va18" axis x1y1, filename every ::1 using :11 with steps title "va17" axis x1y1, filename every ::1 using :12 with steps lw 2 title "zeta" axis x1y2, filename every ::1 using :13 with steps lw 2 title "gas" axis x1y1, filename every ::1 using :14 with steps lw 2 title "compressor" axis x1y1
    unset y2label
    unset y2tics
    #
    set key inside left top
    set xlabel "Time"
    set ylabel "Accumulated c values"
    set origin 0, 0.6
    set size 1, 0.2
    plot [start:end][0:*] filename every ::1 using :19 with steps title "Accumulated c values", threshold t title_t(threshold)
    #
    set key inside center bottom
    set xlabel "Time"
    set ylabel "Nominations and flows\nin 1000 m³/h"
    set origin 0, 0.4
    set size 1, 0.2
    plot [start:end] filename every ::1 using :6 with steps lt 1 lw 2 title "nom(EN)", filename every ::1 using :7 with steps lt 1 dt 2 title "flow(EN)", filename every ::1 using :8 with steps lt 2 lw 2 title "nom(EH)", filename every ::1 using :9 with steps lt 2 dt 2 title "flow(EH)"
    #
    set xtics autofreq
    set key inside left top vertical
    set xlabel "Nomination in 1000 m³/h"
    set ylabel "Flow in 1000 m³/h"
    set origin 0, 0
    set size 0.4, 0.4
    plot [-500:1200][-500:1200] filename every ::start+1::end using 6:7 title "nom(EN) vs. flow(EN)", filename every ::start+1::end using 8:9 title "nom(EH) vs. flow(EH)", x title "perfect match"
    #
    unset multiplot
    pause 5
}
