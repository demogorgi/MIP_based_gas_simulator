set datafile separator ","
set grid
set title "Quality plot"
set xlabel "Time"
set ylabel "Dispatcher penalty"
if (!exists("filename")) filename='instances/da2/output/information.csv'
while (1) {
    plot filename every ::1 using :17 with lines title "Dispatcher penalty"
    pause 1
}
