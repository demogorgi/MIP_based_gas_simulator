set datafile separator ","
set grid
set title "Quality plot"
set xlabel "Time"
set ylabel "Dispatcher penalty"

if (!exists("filename")) filename='instances/da2/output/information.csv'
f(x) = system(sprintf("wc -l %s | cut -f1 -d' '", x))

r(x) = a * x + b
title_r(a,b) = sprintf('r(x) = %.5fx + %.5f', a, b)

while (1) {
    fit r(x) filename every 8 ::1 using :(abs($19)) via a, b
    plot [0:f(filename)/8] filename every 8 ::1 using :(abs($19)) with steps title "Accumulated C values", r(x) lw 2 t title_r(a,b)
    pause 5
}
