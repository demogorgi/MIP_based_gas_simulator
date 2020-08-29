set datafile separator ","
set grid

if (!exists("filename")) filename='instances/da2/output/information.csv'
f(x) = system(sprintf("wc -l %s | cut -f1 -d' '", x))

r(x) = a * x + b
title_r(a,b) = sprintf('regression line r(x) = %.5fx + %.5f', a, b)

m(x) = mean_y
title_m(mean_y) = sprintf('mean value m(x) = %.5f', mean_y)

#set fit logfile "fit.log"
set print "slope_evolution.csv"

print "gnuplot loops,slope of regression line,y-axis interception of regression line,average value"

i = 1
while (1) {
    fit r(x) filename every 8::8 using :(abs($19)) via a, b
    fit m(x) filename every 8::8 using :(abs($19)) via mean_y
    print i, ",", a, ",", b, ",", mean_y
    i = i + 1
    set size 1,1
    set origin 0,0
    set multiplot layout 1,2
    set title "Quality plot"
    set xlabel "Time"
    set ylabel "Dispatcher penalty"
    plot [0:f(filename)/8] filename every 8::8 using :(abs($19)) with points lt 22 ps 1 title "Accumulated C values", r(x) lt 7 lw 4 t title_r(a,b), m(x) lt 8 lw 3 t title_m(mean_y) #, "slope_evolution.csv" every ::1 using :2 with lines lt 4 lw 1.5 t "Fitting parameter a evolution", "slope_evolution.csv" every ::1 using :3 with lines lt 5 lw 1 t "Mean value evolution"
    #
    set y2tics
    set ytics nomirror
    set title "Quality plot"
    set xlabel "Number of gnuplot iterations"
    set ylabel "Regression line slope"
    set y2label "Mean value"
    plot "slope_evolution.csv" every ::1 using :2 with linespoints axes x1y1 t "Fitting parameter 'a' evolution", "slope_evolution.csv" every ::1 using :4 with linespoints axes x1y2 t "Mean value evolution"
    unset y2tics
    pause 5
}
