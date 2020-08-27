set datafile separator ","
set grid
set title "Quality plot"
set xlabel "Time"
set ylabel "Accumulated C values"

if (!exists("filename")) filename='instances/da2/output/information.csv'
f(x) = system(sprintf("wc -l %s | cut -f1 -d' '", x))

while (1) {
    plot [0:f(filename)/8] filename every 8 ::1 using :(abs($19)) with steps title "Accumulated C values"
    pause 5
}
