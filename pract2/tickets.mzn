include "globals.mzn";
array[1..6] of var 0..9: d;
constraint all_different(d);
constraint d[1] + d[2] + d[3] = d[4] + d[5] + d[6];
var int: s = d[1] + d[2] + d[3];
solve minimize s;
output ["Билет: \(d), сумма трёх цифр = \(s)\n"];
