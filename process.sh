#!/bin/bash

awk -F, '{sum+=$47*0.0929}END{print "Средняя площадь наземной территории:", sum/(NR-1), "м2"}' $1
echo 
echo "Количество домов с определенным типом гаража:"
awk -F, 'NR>1{type_count[$59]++}END{for (type in type_count) if(type != "NA") print type, type_count[type]}' $1
echo
echo "Средний рейтинг условий проживания для годов продажи:"
awk -F, 'NR>1{rate[$78]+=$19;count[$78]++}END{for (year in rate) print year, rate[year] / count[year]}' $1

echo
echo
gnuplot -persist <<-EOFMarker
    set terminal png size 300,400
    set output 'q_vs_s.png'
    set datafile separator comma
    plot "$1" using 18:81 title 'Qual vs Price' with points
    f(x) = a*x+b
    fit f(x) "$1" using 18:81 via a,b
    set output 'q_vs_s_fit.png'
    plot "$1" using 18:81 title 'Qual vs Price' with points, f(x) title 'fit'
    save fit 'fit.dat'
EOFMarker
echo
echo "Коэффициенты для линейной регрессии стоимости продажи от общего качества строения (f(x) = ax+b):"
echo
cat fit.dat


