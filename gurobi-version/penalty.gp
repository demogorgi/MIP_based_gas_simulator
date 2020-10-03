print "#########################################"
print "Invocation example:"
print ">gnuplot -e \"nomination_freq=8;append='true';filename='example.csv';i=42;threshold=666\" penalty.gp"
print "- nomination_freq is mandatory"
print "- if append is not set 'slope_evolution.csv' will be overwritten"
print "  (This file is used for the right plot)"
print "- if filename is not set 'instances/da2/output/information.csv' will be used"
print "  (This file is used for the left plot)"
print "- if i is set it will be used for the iteration number in the frist column of slope_evolution.csv"
print "- if i threshold is set, a straight line at threshold is drawn in left plot"
print "#########################################"
set datafile separator ","
set grid
set title "Quality plot"
set xlabel "Time"
set ylabel "Accumulated C"

if (!exists("filename")) filename='instances/da2/output/information.csv'
f(x) = system(sprintf("wc -l %s | cut -f1 -d' '", x))

r(x) = a * x + b
title_r(a,b) = sprintf('regression line r(x) = %.5fx + %.5f', a, b)

m(x) = mean_y
title_m(mean_y) = sprintf('mean value m(x) = %.5f', mean_y)

title_t(threshold) = sprintf('threshold %.1f', threshold)

set fit logfile "fit.log"
if (!exists("append")) append='false'
if (append eq 'true') {
    set print "slope_evolution.csv" append
} else {
    set print "slope_evolution.csv"
    print "gnuplot loops,slope of regression line,y-axis interception of regression line,average value"
    #print "1,7.123,19.123,31.123"
}


if (!exists("i")) i=1
k = f(filename)
while (1) {
    if (k + nomination_freq <= f(filename) && f(filename) >= 2 * nomination_freq) {
       fit r(x) filename every nomination_freq::nomination_freq using :(abs($19)) via a, b
       fit m(x) filename every nomination_freq::nomination_freq using :(abs($19)) via mean_y
       print i, ",", a, ",", b, ",", mean_y
       i = i + 1
       set size 1,1
       set origin 0,0
       set multiplot layout 1,2
       set title "Quality plot"
       set xlabel "Time"
       set ylabel "Accumulated C"
       set xrange [0:f(filename)/nomination_freq]
       set yrange [0:*]
       if (!exists("threshold")) {
	       plot filename every nomination_freq::nomination_freq using :(abs($19)) with points lt 22 ps 1 title "Accumulated C values", r(x) lt 7 lw 4 t title_r(a,b), m(x) lt 8 lw 3 t title_m(mean_y)
       } else {
	       plot filename every nomination_freq::nomination_freq using :(abs($19)) with points lt 22 ps 1 title "Accumulated C values", r(x) lt 7 lw 4 t title_r(a,b), m(x) lt 8 lw 3 t title_m(mean_y), threshold t title_t(threshold)
       }
       #
       set y2tics
       set ytics nomirror
       set title "Quality plot"
       set ylabel "Mean value"
       set y2label "Regression line slope"
       set y2range [-10:10]
       plot "slope_evolution.csv" every ::1 using :2 with linespoints axes x1y2 t "Fitting parameter 'a' evolution", "slope_evolution.csv" every ::1 using :4 with linespoints axes x1y1 t "Mean value evolution"
       unset y2tics
       unset y2label
       k = f(filename)
    } else {
       pause 1
    }
}
