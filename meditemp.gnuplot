set datafile separator ";"

set style fill transparent
set xdata time
set yrange [0:*]
set ylabel 'internal temperature [°C]' tc ls 1
set timefmt "%m/%d/%Y, %H:%M"
set term canvas standalone mousing
set output "med_temp.html"


set style line 1 \
    linecolor rgb '#0060ad' \
    linetype 1 linewidth 2 \
    pointtype 7 pointsize 0.4

set style line 2 \
    linecolor rgb '#0060ad' \
    linetype 1 linewidth 1 \
    pointtype 7 pointsize 0.4

set style line 3 \
    linecolor rgb '#964B00' \
    linetype 1 linewidth 2 \
    pointtype 7 pointsize 0.4

set style line 4 \
    linecolor rgb '#964B00' \
    linetype 1 linewidth 1 \
    pointtype 7 pointsize 0.4

set ytics nomirror tc ls 1
set y2tics nomirror tc ls 3
set y2range [0:1]
set y2label 'internal humidity [%]' tc ls 3

plot 'med_temp.csv' using 1:2 title "internal temperature [°C]" with linespoints linestyle 1, \
     25 notitle with lines linestyle 2, 15 notitle with lines linestyle 2, \
     'med_temp.csv' using 1:3 title "internal humidity [%]" with linespoints linestyle 3 axes x1y2, \
     0.6 notitle with lines linestyle 4 axes x1y2
