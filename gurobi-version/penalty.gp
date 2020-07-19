set datafile separator ","
set grid
set title "Quality plot"
set xlabel "Time"
set ylabel "Dispatcher penalty"
if (!exists("filename")) filename='instances/da2/output/information.csv'
f(x) = system(sprintf("wc -l %s | cut -f1 -d' '", x))
while (1) {
    plot [0:f(filename)] filename every ::1 using :17 with lines title "Dispatcher penalty"
    pause 5
}
