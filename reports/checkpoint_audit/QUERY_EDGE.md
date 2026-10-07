# Query-cell distance to the edge

This complements the existing nearest-chain-edge audit. Rows are correlated stone-trials, not independent observations. Macro accuracy conditions only on true liberty class; chain diameter and generator remain potential confounders.

## Asynchronous / 13×13 / D32 / edge distance 0

Stone accuracy 99.56%; macro 99.82%; overcounts 20; undercounts 473.

```
[[ 7470     0     0     0]
 [  466 74036    18     0]
 [    0     4 14448     2]
 [    0     0     3 14865]]
```

Overcounts only:
```
[[ 0  0  0  0]
 [ 0  0 18  0]
 [ 0  0  0  2]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [466   0   0   0]
 [  0   4   0   0]
 [  0   0   3   0]]
```

## Asynchronous / 13×13 / D32 / edge distance 1

Stone accuracy 62.01%; macro 63.23%; overcounts 103; undercounts 42714.

```
[[13854    69     0     0]
 [14006  8825     2     0]
 [ 5484  7011 10396    32]
 [ 1786  6466  7961 36815]]
```

Overcounts only:
```
[[ 0 69  0  0]
 [ 0  0  2  0]
 [ 0  0  0 32]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [14006     0     0     0]
 [ 5484  7011     0     0]
 [ 1786  6466  7961     0]]
```

## Asynchronous / 13×13 / D32 / edge distance 2

Stone accuracy 80.73%; macro 77.66%; overcounts 214; undercounts 17997.

```
[[24797   160     0     0]
 [10955 10942    18     0]
 [ 1354  1364  7398    36]
 [  494  1717  2113 33161]]
```

Overcounts only:
```
[[  0 160   0   0]
 [  0   0  18   0]
 [  0   0   0  36]
 [  0   0   0   0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [10955     0     0     0]
 [ 1354  1364     0     0]
 [  494  1717  2113     0]]
```

## Asynchronous / 13×13 / D32 / edge distance 3–4

Stone accuracy 72.94%; macro 67.86%; overcounts 111; undercounts 30561.

```
[[24993    54     0     0]
 [11672  7699    15     0]
 [ 3733  4308  9080    42]
 [ 1196  4352  5300 40911]]
```

Overcounts only:
```
[[ 0 54  0  0]
 [ 0  0 15  0]
 [ 0  0  0 42]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [11672     0     0     0]
 [ 3733  4308     0     0]
 [ 1196  4352  5300     0]]
```

## Asynchronous / 13×13 / D32 / edge distance 5–8

Stone accuracy 69.03%; macro 65.17%; overcounts 4; undercounts 7591.

```
[[5040    0    0    0]
 [2611 1547    0    0]
 [1048 1079 2054    4]
 [ 279 1050 1524 8289]]
```

Overcounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 4]
 [0 0 0 0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2611    0    0    0]
 [1048 1079    0    0]
 [ 279 1050 1524    0]]
```

## Asynchronous / 13×13 / D64 / edge distance 0

Stone accuracy 96.55%; macro 98.57%; overcounts 748; undercounts 3088.

```
[[ 7462     8     0     0]
 [ 3022 70780   715     3]
 [    0     1 14431    22]
 [    0     0    65 14803]]
```

Overcounts only:
```
[[  0   8   0   0]
 [  0   0 715   3]
 [  0   0   0  22]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3022    0    0    0]
 [   0    1    0    0]
 [   0    0   65    0]]
```

## Asynchronous / 13×13 / D64 / edge distance 1

Stone accuracy 62.24%; macro 63.08%; overcounts 590; undercounts 41973.

```
[[13584   319    20     0]
 [14530  8160   143     0]
 [ 6379  5234 11202   108]
 [ 1744  6551  7535 37198]]
```

Overcounts only:
```
[[  0 319  20   0]
 [  0   0 143   0]
 [  0   0   0 108]
 [  0   0   0   0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [14530     0     0     0]
 [ 6379  5234     0     0]
 [ 1744  6551  7535     0]]
```

## Asynchronous / 13×13 / D64 / edge distance 2

Stone accuracy 79.08%; macro 76.06%; overcounts 1863; undercounts 17904.

```
[[23457  1424    76     0]
 [11002 10681   232     0]
 [ 1420  1197  7404   131]
 [  443  1709  2133 33200]]
```

Overcounts only:
```
[[   0 1424   76    0]
 [   0    0  232    0]
 [   0    0    0  131]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [11002     0     0     0]
 [ 1420  1197     0     0]
 [  443  1709  2133     0]]
```

## Asynchronous / 13×13 / D64 / edge distance 3–4

Stone accuracy 72.39%; macro 67.16%; overcounts 1231; undercounts 30065.

```
[[24206   666   174     1]
 [11822  7344   217     3]
 [ 4156  3458  9379   170]
 [ 1116  4407  5106 41130]]
```

Overcounts only:
```
[[  0 666 174   1]
 [  0   0 217   3]
 [  0   0   0 170]
 [  0   0   0   0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [11822     0     0     0]
 [ 4156  3458     0     0]
 [ 1116  4407  5106     0]]
```

## Asynchronous / 13×13 / D64 / edge distance 5–8

Stone accuracy 68.58%; macro 64.31%; overcounts 234; undercounts 7472.

```
[[4888  118   34    0]
 [2642 1482   31    3]
 [1151  920 2066   48]
 [ 255 1083 1421 8383]]
```

Overcounts only:
```
[[  0 118  34   0]
 [  0   0  31   3]
 [  0   0   0  48]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2642    0    0    0]
 [1151  920    0    0]
 [ 255 1083 1421    0]]
```

## Asynchronous / 13×13 / D128 / edge distance 0

Stone accuracy 86.94%; macro 93.57%; overcounts 3113; undercounts 11426.

```
[[ 7415    44    11     0]
 [10767 61055  2527   171]
 [    0    15 14079   360]
 [    0     0   644 14224]]
```

Overcounts only:
```
[[   0   44   11    0]
 [   0    0 2527  171]
 [   0    0    0  360]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [10767     0     0     0]
 [    0    15     0     0]
 [    0     0   644     0]]
```

## Asynchronous / 13×13 / D128 / edge distance 1

Stone accuracy 60.98%; macro 61.09%; overcounts 2706; undercounts 41268.

```
[[12555  1206   158     4]
 [13530  8503   764    36]
 [ 5847  5615 10923   538]
 [ 1320  7267  7689 36752]]
```

Overcounts only:
```
[[   0 1206  158    4]
 [   0    0  764   36]
 [   0    0    0  538]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [13530     0     0     0]
 [ 5847  5615     0     0]
 [ 1320  7267  7689     0]]
```

## Asynchronous / 13×13 / D128 / edge distance 2

Stone accuracy 75.90%; macro 72.44%; overcounts 5327; undercounts 17454.

```
[[21319  3207   410    21]
 [10241 10614  1034    26]
 [ 1367  1233  6923   629]
 [  394  1566  2653 32872]]
```

Overcounts only:
```
[[   0 3207  410   21]
 [   0    0 1034   26]
 [   0    0    0  629]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [10241     0     0     0]
 [ 1367  1233     0     0]
 [  394  1566  2653     0]]
```

## Asynchronous / 13×13 / D128 / edge distance 3–4

Stone accuracy 69.52%; macro 63.71%; overcounts 5409; undercounts 29141.

```
[[21871  2683   469    24]
 [10957  7171  1172    86]
 [ 4010  3348  8830   975]
 [  847  4860  5119 40933]]
```

Overcounts only:
```
[[   0 2683  469   24]
 [   0    0 1172   86]
 [   0    0    0  975]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [10957     0     0     0]
 [ 4010  3348     0     0]
 [  847  4860  5119     0]]
```

## Asynchronous / 13×13 / D128 / edge distance 5–8

Stone accuracy 65.41%; macro 60.07%; overcounts 1062; undercounts 7421.

```
[[4503  441   93    3]
 [2622 1284  233   19]
 [1169  865 1878  273]
 [ 161 1254 1350 8377]]
```

Overcounts only:
```
[[  0 441  93   3]
 [  0   0 233  19]
 [  0   0   0 273]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2622    0    0    0]
 [1169  865    0    0]
 [ 161 1254 1350    0]]
```

## Asynchronous / 13×13 / D256 / edge distance 0

Stone accuracy 74.33%; macro 85.32%; overcounts 8342; undercounts 20232.

```
[[ 7022   383    63     2]
 [18500 49136  6220   664]
 [    0    60 13384  1010]
 [    0     0  1672 13196]]
```

Overcounts only:
```
[[   0  383   63    2]
 [   0    0 6220  664]
 [   0    0    0 1010]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [18500     0     0     0]
 [    0    60     0     0]
 [    0     0  1672     0]]
```

## Asynchronous / 13×13 / D256 / edge distance 1

Stone accuracy 58.66%; macro 57.99%; overcounts 5649; undercounts 40939.

```
[[11271  2147   481    24]
 [12233  8716  1763   121]
 [ 5321  6060 10429  1113]
 [ 1215  6601  9509 35703]]
```

Overcounts only:
```
[[   0 2147  481   24]
 [   0    0 1763  121]
 [   0    0    0 1113]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [12233     0     0     0]
 [ 5321  6060     0     0]
 [ 1215  6601  9509     0]]
```

## Asynchronous / 13×13 / D256 / edge distance 2

Stone accuracy 72.82%; macro 69.00%; overcounts 9141; undercounts 16546.

```
[[19499  4418   922   118]
 [ 9013 10594  2123   185]
 [ 1079  1266  6432  1375]
 [  342  1333  3513 32297]]
```

Overcounts only:
```
[[   0 4418  922  118]
 [   0    0 2123  185]
 [   0    0    0 1375]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [9013    0    0    0]
 [1079 1266    0    0]
 [ 342 1333 3513    0]]
```

## Asynchronous / 13×13 / D256 / edge distance 3–4

Stone accuracy 66.45%; macro 60.07%; overcounts 10143; undercounts 27888.

```
[[19476  4536   855   180]
 [ 9360  7400  2338   288]
 [ 3329  3989  7899  1946]
 [  845  4343  6022 40549]]
```

Overcounts only:
```
[[   0 4536  855  180]
 [   0    0 2338  288]
 [   0    0    0 1946]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [9360    0    0    0]
 [3329 3989    0    0]
 [ 845 4343 6022    0]]
```

## Asynchronous / 13×13 / D256 / edge distance 5–8

Stone accuracy 62.87%; macro 57.11%; overcounts 2165; undercounts 6940.

```
[[3981  868  165   26]
 [2063 1504  514   77]
 [ 877 1177 1616  515]
 [ 180 1191 1452 8319]]
```

Overcounts only:
```
[[  0 868 165  26]
 [  0   0 514  77]
 [  0   0   0 515]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2063    0    0    0]
 [ 877 1177    0    0]
 [ 180 1191 1452    0]]
```

## Asynchronous / 19×19 / D32 / edge distance 0

Stone accuracy 96.14%; macro 98.56%; overcounts 22; undercounts 3360.

```
[[ 5292     0     0     0]
 [ 3344 57250    12     0]
 [    0     3 10706    10]
 [    0     0    13 10886]]
```

Overcounts only:
```
[[ 0  0  0  0]
 [ 0  0 12  0]
 [ 0  0  0 10]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3344    0    0    0]
 [   0    3    0    0]
 [   0    0   13    0]]
```

## Asynchronous / 19×19 / D32 / edge distance 1

Stone accuracy 58.48%; macro 57.61%; overcounts 973; undercounts 35829.

```
[[15611   937     3     0]
 [11456  5237    11     0]
 [11253  1868  7908    22]
 [ 6937  3477   838 23074]]
```

Overcounts only:
```
[[  0 937   3   0]
 [  0   0  11   0]
 [  0   0   0  22]
 [  0   0   0   0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [11456     0     0     0]
 [11253  1868     0     0]
 [ 6937  3477   838     0]]
```

## Asynchronous / 19×19 / D32 / edge distance 2

Stone accuracy 76.85%; macro 71.69%; overcounts 1752; undercounts 17086.

```
[[23141  1680    19     0]
 [11280  6424    35     0]
 [ 2372   516  5941    18]
 [ 1635   916   367 27016]]
```

Overcounts only:
```
[[   0 1680   19    0]
 [   0    0   35    0]
 [   0    0    0   18]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [11280     0     0     0]
 [ 2372   516     0     0]
 [ 1635   916   367     0]]
```

## Asynchronous / 19×19 / D32 / edge distance 3–4

Stone accuracy 70.50%; macro 62.82%; overcounts 1275; undercounts 36228.

```
[[35395  1179     2     0]
 [15871  6302    66     0]
 [ 8704  1114  8874    28]
 [ 6734  3039   766 39069]]
```

Overcounts only:
```
[[   0 1179    2    0]
 [   0    0   66    0]
 [   0    0    0   28]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [15871     0     0     0]
 [ 8704  1114     0     0]
 [ 6734  3039   766     0]]
```

## Asynchronous / 19×19 / D32 / edge distance 5–8

Stone accuracy 71.59%; macro 63.16%; overcounts 439; undercounts 31514.

```
[[33233   400     0     0]
 [12198  5131    14     0]
 [ 8785  1006  8454    25]
 [ 6737  2422   366 33693]]
```

Overcounts only:
```
[[  0 400   0   0]
 [  0   0  14   0]
 [  0   0   0  25]
 [  0   0   0   0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [12198     0     0     0]
 [ 8785  1006     0     0]
 [ 6737  2422   366     0]]
```

## Asynchronous / 19×19 / D32 / edge distance 9–16

Stone accuracy 56.00%; macro 55.49%; overcounts 0; undercounts 594.

```
[[216   0   0   0]
 [207  81   0   0]
 [184  14  72   0]
 [136  50   3 387]]
```

Overcounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [207   0   0   0]
 [184  14   0   0]
 [136  50   3   0]]
```

## Asynchronous / 19×19 / D64 / edge distance 0

Stone accuracy 91.96%; macro 96.92%; overcounts 1209; undercounts 5826.

```
[[ 5282     7     3     0]
 [ 5785 53652  1169     0]
 [    0     3 10686    30]
 [    0     0    38 10861]]
```

Overcounts only:
```
[[   0    7    3    0]
 [   0    0 1169    0]
 [   0    0    0   30]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5785    0    0    0]
 [   0    3    0    0]
 [   0    0   38    0]]
```

## Asynchronous / 19×19 / D64 / edge distance 1

Stone accuracy 58.15%; macro 57.14%; overcounts 1414; undercounts 35677.

```
[[15339  1176    36     0]
 [11515  5059   129     1]
 [11660  1224  8095    72]
 [ 7237  2600  1441 23048]]
```

Overcounts only:
```
[[   0 1176   36    0]
 [   0    0  129    1]
 [   0    0    0   72]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [11515     0     0     0]
 [11660  1224     0     0]
 [ 7237  2600  1441     0]]
```

## Asynchronous / 19×19 / D64 / edge distance 2

Stone accuracy 74.81%; macro 69.76%; overcounts 3559; undercounts 16932.

```
[[21925  2787   128     0]
 [11081  6129   528     1]
 [ 2407   475  5850   115]
 [ 1681   759   529 26965]]
```

Overcounts only:
```
[[   0 2787  128    0]
 [   0    0  528    1]
 [   0    0    0  115]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [11081     0     0     0]
 [ 2407   475     0     0]
 [ 1681   759   529     0]]
```

## Asynchronous / 19×19 / D64 / edge distance 3–4

Stone accuracy 69.73%; macro 62.05%; overcounts 2418; undercounts 36066.

```
[[34620  1850   106     0]
 [15812  6144   267    16]
 [ 8776   939  8826   179]
 [ 6932  2503  1104 39069]]
```

Overcounts only:
```
[[   0 1850  106    0]
 [   0    0  267   16]
 [   0    0    0  179]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [15812     0     0     0]
 [ 8776   939     0     0]
 [ 6932  2503  1104     0]]
```

## Asynchronous / 19×19 / D64 / edge distance 5–8

Stone accuracy 71.25%; macro 62.81%; overcounts 951; undercounts 31380.

```
[[32975   629    23     6]
 [12194  5021   125     3]
 [ 8869   767  8469   165]
 [ 6736  2063   751 33668]]
```

Overcounts only:
```
[[  0 629  23   6]
 [  0   0 125   3]
 [  0   0   0 165]
 [  0   0   0   0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [12194     0     0     0]
 [ 8869   767     0     0]
 [ 6736  2063   751     0]]
```

## Asynchronous / 19×19 / D64 / edge distance 9–16

Stone accuracy 56.22%; macro 55.77%; overcounts 0; undercounts 591.

```
[[216   0   0   0]
 [206  82   0   0]
 [180  16  74   0]
 [129  44  16 387]]
```

Overcounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [206   0   0   0]
 [180  16   0   0]
 [129  44  16   0]]
```

## Asynchronous / 19×19 / D128 / edge distance 0

Stone accuracy 82.77%; macro 92.10%; overcounts 2824; undercounts 12257.

```
[[ 5231    46    15     0]
 [11776 46333  2292   205]
 [    0     9 10444   266]
 [    0     0   472 10427]]
```

Overcounts only:
```
[[   0   46   15    0]
 [   0    0 2292  205]
 [   0    0    0  266]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [11776     0     0     0]
 [    0     9     0     0]
 [    0     0   472     0]]
```

## Asynchronous / 19×19 / D128 / edge distance 1

Stone accuracy 56.60%; macro 55.36%; overcounts 3359; undercounts 35107.

```
[[14225  2284    42     0]
 [10733  5421   530    20]
 [10869  2001  7698   483]
 [ 6983  2918  1603 22822]]
```

Overcounts only:
```
[[   0 2284   42    0]
 [   0    0  530   20]
 [   0    0    0  483]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [10733     0     0     0]
 [10869  2001     0     0]
 [ 6983  2918  1603     0]]
```

## Asynchronous / 19×19 / D128 / edge distance 2

Stone accuracy 72.42%; macro 67.22%; overcounts 6187; undercounts 16252.

```
[[20266  4362   200    12]
 [10187  6485  1046    21]
 [ 2319   546  5436   546]
 [ 1633   736   831 26734]]
```

Overcounts only:
```
[[   0 4362  200   12]
 [   0    0 1046   21]
 [   0    0    0  546]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [10187     0     0     0]
 [ 2319   546     0     0]
 [ 1633   736   831     0]]
```

## Asynchronous / 19×19 / D128 / edge distance 3–4

Stone accuracy 67.32%; macro 59.37%; overcounts 5777; undercounts 35774.

```
[[32900  3437   209    30]
 [15340  5709  1088   102]
 [ 8576  1066  8167   911]
 [ 6831  2499  1462 38816]]
```

Overcounts only:
```
[[   0 3437  209   30]
 [   0    0 1088  102]
 [   0    0    0  911]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [15340     0     0     0]
 [ 8576  1066     0     0]
 [ 6831  2499  1462     0]]
```

## Asynchronous / 19×19 / D128 / edge distance 5–8

Stone accuracy 69.21%; macro 60.09%; overcounts 3240; undercounts 31385.

```
[[32413  1113   107     0]
 [12174  4098  1001    70]
 [ 8802   686  7833   949]
 [ 6701  1953  1069 33495]]
```

Overcounts only:
```
[[   0 1113  107    0]
 [   0    0 1001   70]
 [   0    0    0  949]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [12174     0     0     0]
 [ 8802   686     0     0]
 [ 6701  1953  1069     0]]
```

## Asynchronous / 19×19 / D128 / edge distance 9–16

Stone accuracy 54.67%; macro 54.16%; overcounts 21; undercounts 591.

```
[[216   0   0   0]
 [206  67  15   0]
 [182   9  73   6]
 [130  41  23 382]]
```

Overcounts only:
```
[[ 0  0  0  0]
 [ 0  0 15  0]
 [ 0  0  0  6]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [206   0   0   0]
 [182   9   0   0]
 [130  41  23   0]]
```

## Asynchronous / 19×19 / D256 / edge distance 0

Stone accuracy 73.10%; macro 84.76%; overcounts 5965; undercounts 17575.

```
[[ 4970   261    61     0]
 [16201 39571  4216   618]
 [    0    54  9856   809]
 [    0     0  1320  9579]]
```

Overcounts only:
```
[[   0  261   61    0]
 [   0    0 4216  618]
 [   0    0    0  809]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [16201     0     0     0]
 [    0    54     0     0]
 [    0     0  1320     0]]
```

## Asynchronous / 19×19 / D256 / edge distance 1

Stone accuracy 54.19%; macro 52.80%; overcounts 5961; undercounts 34639.

```
[[12805  3504   234     8]
 [ 9728  5786  1110    80]
 [ 9481  3233  7312  1025]
 [ 6350  3685  2162 22129]]
```

Overcounts only:
```
[[   0 3504  234    8]
 [   0    0 1110   80]
 [   0    0    0 1025]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [9728    0    0    0]
 [9481 3233    0    0]
 [6350 3685 2162    0]]
```

## Asynchronous / 19×19 / D256 / edge distance 2

Stone accuracy 68.84%; macro 63.42%; overcounts 9279; undercounts 16069.

```
[[18516  5918   339    67]
 [ 9672  6270  1686   111]
 [ 1894   838  4957  1158]
 [ 1404   875  1386 26269]]
```

Overcounts only:
```
[[   0 5918  339   67]
 [   0    0 1686  111]
 [   0    0    0 1158]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [9672    0    0    0]
 [1894  838    0    0]
 [1404  875 1386    0]]
```

## Asynchronous / 19×19 / D256 / edge distance 3–4

Stone accuracy 63.41%; macro 55.57%; overcounts 12378; undercounts 34141.

```
[[28765  7252   485    74]
 [13515  6172  2248   304]
 [ 7441  2117  7147  2015]
 [ 5882  3203  1983 38540]]
```

Overcounts only:
```
[[   0 7252  485   74]
 [   0    0 2248  304]
 [   0    0    0 2015]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [13515     0     0     0]
 [ 7441  2117     0     0]
 [ 5882  3203  1983     0]]
```

## Asynchronous / 19×19 / D256 / edge distance 5–8

Stone accuracy 65.21%; macro 55.86%; overcounts 8297; undercounts 30831.

```
[[29697  3529   357    50]
 [11378  3738  1963   264]
 [ 8196  1205  6735  2134]
 [ 6156  2412  1484 33166]]
```

Overcounts only:
```
[[   0 3529  357   50]
 [   0    0 1963  264]
 [   0    0    0 2134]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [11378     0     0     0]
 [ 8196  1205     0     0]
 [ 6156  2412  1484     0]]
```

## Asynchronous / 19×19 / D256 / edge distance 9–16

Stone accuracy 51.93%; macro 51.05%; overcounts 52; undercounts 597.

```
[[213   3   0   0]
 [208  50  25   5]
 [177  12  62  19]
 [127  43  30 376]]
```

Overcounts only:
```
[[ 0  3  0  0]
 [ 0  0 25  5]
 [ 0  0  0 19]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [208   0   0   0]
 [177  12   0   0]
 [127  43  30   0]]
```

## Asynchronous / 25×25 / D32 / edge distance 0

Stone accuracy 94.22%; macro 97.80%; overcounts 53; undercounts 3575.

```
[[ 4343     4     0     0]
 [ 3569 38323    48     0]
 [    0     6  7022     1]
 [    0     0     0  9495]]
```

Overcounts only:
```
[[ 0  4  0  0]
 [ 0  0 48  0]
 [ 0  0  0  1]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3569    0    0    0]
 [   0    6    0    0]
 [   0    0    0    0]]
```

## Asynchronous / 25×25 / D32 / edge distance 1

Stone accuracy 61.32%; macro 60.30%; overcounts 1041; undercounts 23471.

```
[[12818   989    17     0]
 [10219  3750    26     0]
 [ 4012   121  5443     9]
 [ 7563  1060   496 16855]]
```

Overcounts only:
```
[[  0 989  17   0]
 [  0   0  26   0]
 [  0   0   0   9]
 [  0   0   0   0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [10219     0     0     0]
 [ 4012   121     0     0]
 [ 7563  1060   496     0]]
```

## Asynchronous / 25×25 / D32 / edge distance 2

Stone accuracy 76.09%; macro 71.07%; overcounts 2588; undercounts 11626.

```
[[17115  2474    22     0]
 [ 8021  4445    80     0]
 [ 1898    30  4441    12]
 [ 1286   264   127 19230]]
```

Overcounts only:
```
[[   0 2474   22    0]
 [   0    0   80    0]
 [   0    0    0   12]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [8021    0    0    0]
 [1898   30    0    0]
 [1286  264  127    0]]
```

## Asynchronous / 25×25 / D32 / edge distance 3–4

Stone accuracy 72.79%; macro 66.16%; overcounts 1953; undercounts 25509.

```
[[29212  1876     7     0]
 [13362  5472    28     2]
 [ 4254   130  7015    40]
 [ 6756   809   198 31783]]
```

Overcounts only:
```
[[   0 1876    7    0]
 [   0    0   28    2]
 [   0    0    0   40]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [13362     0     0     0]
 [ 4254   130     0     0]
 [ 6756   809   198     0]]
```

## Asynchronous / 25×25 / D32 / edge distance 5–8

Stone accuracy 75.26%; macro 67.31%; overcounts 1570; undercounts 30165.

```
[[41687  1540     0     0]
 [14876  6415    21     0]
 [ 5685    90  9588     9]
 [ 8277  1025   212 38825]]
```

Overcounts only:
```
[[   0 1540    0    0]
 [   0    0   21    0]
 [   0    0    0    9]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [14876     0     0     0]
 [ 5685    90     0     0]
 [ 8277  1025   212     0]]
```

## Asynchronous / 25×25 / D32 / edge distance 9–16

Stone accuracy 74.01%; macro 65.83%; overcounts 161; undercounts 9024.

```
[[11415   159     0     0]
 [ 4081  1758     2     0]
 [ 1910    34  2574     0]
 [ 2422   466   111 10402]]
```

Overcounts only:
```
[[  0 159   0   0]
 [  0   0   2   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4081    0    0    0]
 [1910   34    0    0]
 [2422  466  111    0]]
```

## Asynchronous / 25×25 / D64 / edge distance 0

Stone accuracy 89.39%; macro 95.85%; overcounts 1076; undercounts 5590.

```
[[ 4332    15     0     0]
 [ 5562 35330  1029    19]
 [    0     0  7016    13]
 [    0     0    28  9467]]
```

Overcounts only:
```
[[   0   15    0    0]
 [   0    0 1029   19]
 [   0    0    0   13]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5562    0    0    0]
 [   0    0    0    0]
 [   0    0   28    0]]
```

## Asynchronous / 25×25 / D64 / edge distance 1

Stone accuracy 60.87%; macro 59.73%; overcounts 1340; undercounts 23458.

```
[[12650  1041   133     0]
 [10254  3619   122     0]
 [ 4081    44  5416    44]
 [ 7704   716   659 16895]]
```

Overcounts only:
```
[[   0 1041  133    0]
 [   0    0  122    0]
 [   0    0    0   44]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [10254     0     0     0]
 [ 4081    44     0     0]
 [ 7704   716   659     0]]
```

## Asynchronous / 25×25 / D64 / edge distance 2

Stone accuracy 74.80%; macro 69.74%; overcounts 3561; undercounts 11418.

```
[[16695  2510   406     0]
 [ 7810  4148   588     0]
 [ 1912    23  4389    57]
 [ 1218   236   219 19234]]
```

Overcounts only:
```
[[   0 2510  406    0]
 [   0    0  588    0]
 [   0    0    0   57]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [7810    0    0    0]
 [1912   23    0    0]
 [1218  236  219    0]]
```

## Asynchronous / 25×25 / D64 / edge distance 3–4

Stone accuracy 72.30%; macro 65.51%; overcounts 2536; undercounts 25428.

```
[[28951  1789   355     0]
 [13322  5333   191    18]
 [ 4225   141  6890   183]
 [ 6769   590   381 31806]]
```

Overcounts only:
```
[[   0 1789  355    0]
 [   0    0  191   18]
 [   0    0    0  183]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [13322     0     0     0]
 [ 4225   141     0     0]
 [ 6769   590   381     0]]
```

## Asynchronous / 25×25 / D64 / edge distance 5–8

Stone accuracy 74.92%; macro 66.75%; overcounts 2109; undercounts 30058.

```
[[41543  1276   408     0]
 [14840  6257   214     1]
 [ 5694    77  9391   210]
 [ 8203   802   442 38892]]
```

Overcounts only:
```
[[   0 1276  408    0]
 [   0    0  214    1]
 [   0    0    0  210]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [14840     0     0     0]
 [ 5694    77     0     0]
 [ 8203   802   442     0]]
```

## Asynchronous / 25×25 / D64 / edge distance 9–16

Stone accuracy 73.70%; macro 65.27%; overcounts 315; undercounts 8977.

```
[[11369   157    48     0]
 [ 4081  1716    44     0]
 [ 1921    24  2507    66]
 [ 2412   354   185 10450]]
```

Overcounts only:
```
[[  0 157  48   0]
 [  0   0  44   0]
 [  0   0   0  66]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4081    0    0    0]
 [1921   24    0    0]
 [2412  354  185    0]]
```

## Asynchronous / 25×25 / D128 / edge distance 0

Stone accuracy 80.22%; macro 90.70%; overcounts 2740; undercounts 9687.

```
[[ 4270    55    21     1]
 [ 9291 30216  2159   274]
 [    0     6  6793   230]
 [    0     0   390  9105]]
```

Overcounts only:
```
[[   0   55   21    1]
 [   0    0 2159  274]
 [   0    0    0  230]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [9291    0    0    0]
 [   0    6    0    0]
 [   0    0  390    0]]
```

## Asynchronous / 25×25 / D128 / edge distance 1

Stone accuracy 58.94%; macro 57.41%; overcounts 2969; undercounts 23052.

```
[[11623  2035   166     0]
 [ 9693  3855   435    12]
 [ 3782   348  5134   321]
 [ 7288  1001   940 16745]]
```

Overcounts only:
```
[[   0 2035  166    0]
 [   0    0  435   12]
 [   0    0    0  321]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [9693    0    0    0]
 [3782  348    0    0]
 [7288 1001  940    0]]
```

## Asynchronous / 25×25 / D128 / edge distance 2

Stone accuracy 71.87%; macro 66.55%; overcounts 5577; undercounts 11147.

```
[[15543  3541   522     5]
 [ 7389  4051  1092    14]
 [ 1882    53  4043   403]
 [ 1172   244   407 19084]]
```

Overcounts only:
```
[[   0 3541  522    5]
 [   0    0 1092   14]
 [   0    0    0  403]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [7389    0    0    0]
 [1882   53    0    0]
 [1172  244  407    0]]
```

## Asynchronous / 25×25 / D128 / edge distance 3–4

Stone accuracy 69.92%; macro 62.35%; overcounts 5046; undercounts 25317.

```
[[28072  2514   492    17]
 [13109  4589  1070    96]
 [ 4107   215  6260   857]
 [ 6659   598   629 31660]]
```

Overcounts only:
```
[[   0 2514  492   17]
 [   0    0 1070   96]
 [   0    0    0  857]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [13109     0     0     0]
 [ 4107   215     0     0]
 [ 6659   598   629     0]]
```

## Asynchronous / 25×25 / D128 / edge distance 5–8

Stone accuracy 72.73%; macro 63.40%; overcounts 4630; undercounts 30343.

```
[[41210  1480   534     3]
 [14835  5058  1349    70]
 [ 5668   105  8405  1194]
 [ 8105   769   861 38604]]
```

Overcounts only:
```
[[   0 1480  534    3]
 [   0    0 1349   70]
 [   0    0    0 1194]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [14835     0     0     0]
 [ 5668   105     0     0]
 [ 8105   769   861     0]]
```

## Asynchronous / 25×25 / D128 / edge distance 9–16

Stone accuracy 71.69%; macro 62.23%; overcounts 954; undercounts 9048.

```
[[11294   183    97     0]
 [ 4079  1404   336    22]
 [ 1917    33  2252   316]
 [ 2406   341   272 10382]]
```

Overcounts only:
```
[[  0 183  97   0]
 [  0   0 336  22]
 [  0   0   0 316]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4079    0    0    0]
 [1917   33    0    0]
 [2406  341  272    0]]
```

## Asynchronous / 25×25 / D256 / edge distance 0

Stone accuracy 71.38%; macro 83.90%; overcounts 5028; undercounts 12947.

```
[[ 4043   222    81     1]
 [11933 25866  3578   563]
 [    0    26  6420   583]
 [    0     0   988  8507]]
```

Overcounts only:
```
[[   0  222   81    1]
 [   0    0 3578  563]
 [   0    0    0  583]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [11933     0     0     0]
 [    0    26     0     0]
 [    0     0   988     0]]
```

## Asynchronous / 25×25 / D256 / edge distance 1

Stone accuracy 56.11%; macro 54.25%; overcounts 5324; undercounts 22494.

```
[[10223  3372   224     5]
 [ 8623  4354   965    53]
 [ 3427   719  4734   705]
 [ 6560  1749  1416 16249]]
```

Overcounts only:
```
[[   0 3372  224    5]
 [   0    0  965   53]
 [   0    0    0  705]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [8623    0    0    0]
 [3427  719    0    0]
 [6560 1749 1416    0]]
```

## Asynchronous / 25×25 / D256 / edge distance 2

Stone accuracy 68.19%; macro 62.46%; overcounts 7682; undercounts 11226.

```
[[14559  4362   682     8]
 [ 7186  3591  1668   101]
 [ 1448   406  3666   861]
 [ 1060   364   762 18721]]
```

Overcounts only:
```
[[   0 4362  682    8]
 [   0    0 1668  101]
 [   0    0    0  861]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [7186    0    0    0]
 [1448  406    0    0]
 [1060  364  762    0]]
```

## Asynchronous / 25×25 / D256 / edge distance 3–4

Stone accuracy 65.78%; macro 57.98%; overcounts 10051; undercounts 24487.

```
[[25197  5105   748    45]
 [11878  4503  2173   310]
 [ 3655   607  5507  1670]
 [ 5961  1330  1056 31199]]
```

Overcounts only:
```
[[   0 5105  748   45]
 [   0    0 2173  310]
 [   0    0    0 1670]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [11878     0     0     0]
 [ 3655   607     0     0]
 [ 5961  1330  1056     0]]
```

## Asynchronous / 25×25 / D256 / edge distance 5–8

Stone accuracy 69.10%; macro 58.76%; overcounts 9423; undercounts 30207.

```
[[39305  2995   883    44]
 [14339  3946  2682   345]
 [ 5501   247  7150  2474]
 [ 7922   970  1228 38219]]
```

Overcounts only:
```
[[   0 2995  883   44]
 [   0    0 2682  345]
 [   0    0    0 2474]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [14339     0     0     0]
 [ 5501   247     0     0]
 [ 7922   970  1228     0]]
```

## Asynchronous / 25×25 / D256 / edge distance 9–16

Stone accuracy 68.57%; macro 57.87%; overcounts 2020; undercounts 9087.

```
[[11049   356   165     4]
 [ 4023  1001   702   115]
 [ 1849    82  1909   678]
 [ 2397   356   380 10268]]
```

Overcounts only:
```
[[  0 356 165   4]
 [  0   0 702 115]
 [  0   0   0 678]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4023    0    0    0]
 [1849   82    0    0]
 [2397  356  380    0]]
```

## Asynchronous / 37×37 / D32 / edge distance 0

Stone accuracy 89.51%; macro 96.30%; overcounts 7; undercounts 5097.

```
[[ 2213     1     0     0]
 [ 5097 29724     0     0]
 [    0     0  5322     6]
 [    0     0     0  6300]]
```

Overcounts only:
```
[[0 1 0 0]
 [0 0 0 0]
 [0 0 0 6]
 [0 0 0 0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5097    0    0    0]
 [   0    0    0    0]
 [   0    0    0    0]]
```

## Asynchronous / 37×37 / D32 / edge distance 1

Stone accuracy 48.24%; macro 50.02%; overcounts 1068; undercounts 24817.

```
[[ 6713  1039    15     0]
 [ 6003  2833     2     0]
 [ 8389   207  3686    12]
 [ 9813   389    16 10896]]
```

Overcounts only:
```
[[   0 1039   15    0]
 [   0    0    2    0]
 [   0    0    0   12]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [6003    0    0    0]
 [8389  207    0    0]
 [9813  389   16    0]]
```

## Asynchronous / 37×37 / D32 / edge distance 17+

Stone accuracy 59.66%; macro 53.35%; overcounts 8; undercounts 1357.

```
[[883   8   0   0]
 [306 117   0   0]
 [499  28 175   0]
 [483  32   9 844]]
```

Overcounts only:
```
[[0 8 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [306   0   0   0]
 [499  28   0   0]
 [483  32   9   0]]
```

## Asynchronous / 37×37 / D32 / edge distance 2

Stone accuracy 69.78%; macro 67.62%; overcounts 2611; undercounts 11928.

```
[[14603  2555    32     0]
 [ 8879  3850     6     0]
 [ 1357    73  2944    18]
 [ 1482   109    28 12169]]
```

Overcounts only:
```
[[   0 2555   32    0]
 [   0    0    6    0]
 [   0    0    0   18]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [8879    0    0    0]
 [1357   73    0    0]
 [1482  109   28    0]]
```

## Asynchronous / 37×37 / D32 / edge distance 3–4

Stone accuracy 61.46%; macro 56.00%; overcounts 2234; undercounts 32088.

```
[[22411  2158    19     0]
 [13749  4423    26     0]
 [ 8265   138  5444    31]
 [ 9580   260    96 22446]]
```

Overcounts only:
```
[[   0 2158   19    0]
 [   0    0   26    0]
 [   0    0    0   31]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [13749     0     0     0]
 [ 8265   138     0     0]
 [ 9580   260    96     0]]
```

## Asynchronous / 37×37 / D32 / edge distance 5–8

Stone accuracy 63.69%; macro 57.05%; overcounts 2453; undercounts 49140.

```
[[39668  2237   101    24]
 [20100  6521    10     0]
 [13381   214  9031    81]
 [15228   154    63 35270]]
```

Overcounts only:
```
[[   0 2237  101   24]
 [   0    0   10    0]
 [   0    0    0   81]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [20100     0     0     0]
 [13381   214     0     0]
 [15228   154    63     0]]
```

## Asynchronous / 37×37 / D32 / edge distance 9–16

Stone accuracy 66.14%; macro 57.14%; overcounts 1190; undercounts 43905.

```
[[41547  1125    40     2]
 [15044  4831     6     0]
 [13236   285  8503    17]
 [14641   566   133 33215]]
```

Overcounts only:
```
[[   0 1125   40    2]
 [   0    0    6    0]
 [   0    0    0   17]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [15044     0     0     0]
 [13236   285     0     0]
 [14641   566   133     0]]
```

## Asynchronous / 37×37 / D64 / edge distance 0

Stone accuracy 82.82%; macro 93.75%; overcounts 947; undercounts 7413.

```
[[ 2208     4     2     0]
 [ 7372 26518   931     0]
 [    0     9  5309    10]
 [    0     0    32  6268]]
```

Overcounts only:
```
[[  0   4   2   0]
 [  0   0 931   0]
 [  0   0   0  10]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [7372    0    0    0]
 [   0    9    0    0]
 [   0    0   32    0]]
```

## Asynchronous / 37×37 / D64 / edge distance 1

Stone accuracy 47.44%; macro 48.77%; overcounts 1420; undercounts 24867.

```
[[ 6471  1093   202     1]
 [ 6096  2648    94     0]
 [ 8492    53  3719    30]
 [ 9937   214    75 10888]]
```

Overcounts only:
```
[[   0 1093  202    1]
 [   0    0   94    0]
 [   0    0    0   30]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [6096    0    0    0]
 [8492   53    0    0]
 [9937  214   75    0]]
```

## Asynchronous / 37×37 / D64 / edge distance 17+

Stone accuracy 59.78%; macro 53.48%; overcounts 23; undercounts 1338.

```
[[880   7   4   0]
 [306 115   2   0]
 [497  10 185  10]
 [483   0  42 843]]
```

Overcounts only:
```
[[ 0  7  4  0]
 [ 0  0  2  0]
 [ 0  0  0 10]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [306   0   0   0]
 [497  10   0   0]
 [483   0  42   0]]
```

## Asynchronous / 37×37 / D64 / edge distance 2

Stone accuracy 67.53%; macro 65.67%; overcounts 3561; undercounts 12060.

```
[[14267  2176   744     3]
 [ 8994  3136   605     0]
 [ 1384    30  2945    33]
 [ 1479    75    98 12136]]
```

Overcounts only:
```
[[   0 2176  744    3]
 [   0    0  605    0]
 [   0    0    0   33]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [8994    0    0    0]
 [1384   30    0    0]
 [1479   75   98    0]]
```

## Asynchronous / 37×37 / D64 / edge distance 3–4

Stone accuracy 60.54%; macro 54.99%; overcounts 3127; undercounts 32012.

```
[[22048  1880   651     9]
 [13742  4002   449     5]
 [ 8272    61  5412   133]
 [ 9567   208   162 22445]]
```

Overcounts only:
```
[[   0 1880  651    9]
 [   0    0  449    5]
 [   0    0    0  133]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [13742     0     0     0]
 [ 8272    61     0     0]
 [ 9567   208   162     0]]
```

## Asynchronous / 37×37 / D64 / edge distance 5–8

Stone accuracy 63.23%; macro 56.54%; overcounts 3263; undercounts 48981.

```
[[39405  1454  1043   128]
 [20040  6162   425     4]
 [13362   109  9027   209]
 [15226    85   159 35245]]
```

Overcounts only:
```
[[   0 1454 1043  128]
 [   0    0  425    4]
 [   0    0    0  209]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [20040     0     0     0]
 [13362   109     0     0]
 [15226    85   159     0]]
```

## Asynchronous / 37×37 / D64 / edge distance 9–16

Stone accuracy 65.83%; macro 56.80%; overcounts 1743; undercounts 43768.

```
[[41294   739   640    41]
 [15018  4688   175     0]
 [13181   201  8511   148]
 [14578   260   530 33187]]
```

Overcounts only:
```
[[  0 739 640  41]
 [  0   0 175   0]
 [  0   0   0 148]
 [  0   0   0   0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [15018     0     0     0]
 [13181   201     0     0]
 [14578   260   530     0]]
```

## Asynchronous / 37×37 / D128 / edge distance 0

Stone accuracy 73.82%; macro 89.02%; overcounts 2205; undercounts 10537.

```
[[ 2169    36     6     3]
 [10267 22508  2040     6]
 [    0    37  5177   114]
 [    0     0   233  6067]]
```

Overcounts only:
```
[[   0   36    6    3]
 [   0    0 2040    6]
 [   0    0    0  114]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [10267     0     0     0]
 [    0    37     0     0]
 [    0     0   233     0]]
```

## Asynchronous / 37×37 / D128 / edge distance 1

Stone accuracy 46.58%; macro 47.78%; overcounts 2087; undercounts 24629.

```
[[ 6228  1316   219     4]
 [ 5752  2770   302    14]
 [ 8188   379  3495   232]
 [ 9131  1002   177 10804]]
```

Overcounts only:
```
[[   0 1316  219    4]
 [   0    0  302   14]
 [   0    0    0  232]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5752    0    0    0]
 [8188  379    0    0]
 [9131 1002  177    0]]
```

## Asynchronous / 37×37 / D128 / edge distance 17+

Stone accuracy 58.51%; macro 51.47%; overcounts 65; undercounts 1339.

```
[[874   9   8   0]
 [306  92  25   0]
 [499   8 172  23]
 [483   0  43 842]]
```

Overcounts only:
```
[[ 0  9  8  0]
 [ 0  0 25  0]
 [ 0  0  0 23]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [306   0   0   0]
 [499   8   0   0]
 [483   0  43   0]]
```

## Asynchronous / 37×37 / D128 / edge distance 2

Stone accuracy 64.91%; macro 63.10%; overcounts 5108; undercounts 11773.

```
[[13243  3097   835    15]
 [ 8626  3152   938    19]
 [ 1353    60  2775   204]
 [ 1396   149   189 12054]]
```

Overcounts only:
```
[[   0 3097  835   15]
 [   0    0  938   19]
 [   0    0    0  204]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [8626    0    0    0]
 [1353   60    0    0]
 [1396  149  189    0]]
```

## Asynchronous / 37×37 / D128 / edge distance 3–4

Stone accuracy 58.57%; macro 52.65%; overcounts 4863; undercounts 32028.

```
[[21579  2166   773    70]
 [13612  3365  1139    82]
 [ 8194   121  4930   633]
 [ 9462   296   343 22281]]
```

Overcounts only:
```
[[   0 2166  773   70]
 [   0    0 1139   82]
 [   0    0    0  633]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [13612     0     0     0]
 [ 8194   121     0     0]
 [ 9462   296   343     0]]
```

## Asynchronous / 37×37 / D128 / edge distance 5–8

Stone accuracy 61.67%; macro 54.49%; overcounts 5236; undercounts 49222.

```
[[39287  1436  1144   163]
 [20074  5051  1429    77]
 [13342    83  8295   987]
 [15214    94   415 34992]]
```

Overcounts only:
```
[[   0 1436 1144  163]
 [   0    0 1429   77]
 [   0    0    0  987]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [20074     0     0     0]
 [13342    83     0     0]
 [15214    94   415     0]]
```

## Asynchronous / 37×37 / D128 / edge distance 9–16

Stone accuracy 64.20%; macro 54.52%; overcounts 3705; undercounts 43983.

```
[[41020   852   761    81]
 [15010  3808   991    72]
 [13123   246  7724   948]
 [14568   196   840 32951]]
```

Overcounts only:
```
[[  0 852 761  81]
 [  0   0 991  72]
 [  0   0   0 948]
 [  0   0   0   0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [15010     0     0     0]
 [13123   246     0     0]
 [14568   196   840     0]]
```

## Asynchronous / 37×37 / D256 / edge distance 0

Stone accuracy 67.46%; macro 83.32%; overcounts 3470; undercounts 12364.

```
[[ 2066   119    26     3]
 [11701 20191  2822   107]
 [    4    37  4894   393]
 [    0     0   622  5678]]
```

Overcounts only:
```
[[   0  119   26    3]
 [   0    0 2822  107]
 [   0    0    0  393]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [11701     0     0     0]
 [    4    37     0     0]
 [    0     0   622     0]]
```

## Asynchronous / 37×37 / D256 / edge distance 1

Stone accuracy 44.01%; macro 44.63%; overcounts 3395; undercounts 24607.

```
[[ 5533  1989   226    19]
 [ 5385  2794   627    32]
 [ 7252  1344  3196   502]
 [ 8343  1803   480 10488]]
```

Overcounts only:
```
[[   0 1989  226   19]
 [   0    0  627   32]
 [   0    0    0  502]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5385    0    0    0]
 [7252 1344    0    0]
 [8343 1803  480    0]]
```

## Asynchronous / 37×37 / D256 / edge distance 17+

Stone accuracy 55.32%; macro 47.16%; overcounts 158; undercounts 1354.

```
[[852  25  12   2]
 [309  57  53   4]
 [489  19 132  62]
 [483   0  54 831]]
```

Overcounts only:
```
[[ 0 25 12  2]
 [ 0  0 53  4]
 [ 0  0  0 62]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [309   0   0   0]
 [489  19   0   0]
 [483   0  54   0]]
```

## Asynchronous / 37×37 / D256 / edge distance 2

Stone accuracy 62.29%; macro 59.79%; overcounts 6319; undercounts 11820.

```
[[12729  3480   931    50]
 [ 8405  2969  1292    69]
 [ 1167   258  2470   497]
 [ 1265   291   434 11798]]
```

Overcounts only:
```
[[   0 3480  931   50]
 [   0    0 1292   69]
 [   0    0    0  497]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [8405    0    0    0]
 [1167  258    0    0]
 [1265  291  434    0]]
```

## Asynchronous / 37×37 / D256 / edge distance 3–4

Stone accuracy 55.02%; macro 48.91%; overcounts 8551; undercounts 31498.

```
[[19564  3999   834   191]
 [12779  3217  1926   276]
 [ 7595   726  4232  1325]
 [ 8679   998   721 21984]]
```

Overcounts only:
```
[[   0 3999  834  191]
 [   0    0 1926  276]
 [   0    0    0 1325]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [12779     0     0     0]
 [ 7595   726     0     0]
 [ 8679   998   721     0]]
```

## Asynchronous / 37×37 / D256 / edge distance 5–8

Stone accuracy 58.38%; macro 50.66%; overcounts 9726; undercounts 49409.

```
[[37615  2765  1303   347]
 [19890  3581  2747   413]
 [13217   193  7146  2151]
 [15117   168   824 34606]]
```

Overcounts only:
```
[[   0 2765 1303  347]
 [   0    0 2747  413]
 [   0    0    0 2151]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [19890     0     0     0]
 [13217   193     0     0]
 [15117   168   824     0]]
```

## Asynchronous / 37×37 / D256 / edge distance 9–16

Stone accuracy 61.74%; macro 51.25%; overcounts 6713; undercounts 44241.

```
[[40347  1259   906   202]
 [14960  2662  1976   283]
 [12999   349  6606  2087]
 [14566   138  1229 32622]]
```

Overcounts only:
```
[[   0 1259  906  202]
 [   0    0 1976  283]
 [   0    0    0 2087]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [14960     0     0     0]
 [12999   349     0     0]
 [14566   138  1229     0]]
```

## C128 Synchronous / 13×13 / D32 / edge distance 0

Stone accuracy 100.00%; macro 100.00%; overcounts 0; undercounts 0.

```
[[ 830    0    0    0]
 [   0 8280    0    0]
 [   0    0 1606    0]
 [   0    0    0 1652]]
```

Overcounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

## C128 Synchronous / 13×13 / D32 / edge distance 1

Stone accuracy 64.79%; macro 66.44%; overcounts 69; undercounts 4340.

```
[[1480   67    0    0]
 [1255 1282    0    0]
 [ 413  844 1288    2]
 [  82  668 1078 4064]]
```

Overcounts only:
```
[[ 0 67  0  0]
 [ 0  0  0  0]
 [ 0  0  0  2]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1255    0    0    0]
 [ 413  844    0    0]
 [  82  668 1078    0]]
```

## C128 Synchronous / 13×13 / D32 / edge distance 2

Stone accuracy 85.67%; macro 83.33%; overcounts 152; undercounts 1353.

```
[[2626  147    0    0]
 [ 621 1814    0    0]
 [ 100  176  847    5]
 [  13  152  291 3709]]
```

Overcounts only:
```
[[  0 147   0   0]
 [  0   0   0   0]
 [  0   0   0   5]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [621   0   0   0]
 [100 176   0   0]
 [ 13 152 291   0]]
```

## C128 Synchronous / 13×13 / D32 / edge distance 3–4

Stone accuracy 76.01%; macro 72.53%; overcounts 46; undercounts 2975.

```
[[2742   41    0    0]
 [ 936 1216    0    2]
 [ 245  589 1070    3]
 [  47  434  724 4546]]
```

Overcounts only:
```
[[ 0 41  0  0]
 [ 0  0  0  2]
 [ 0  0  0  3]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [936   0   0   0]
 [245 589   0   0]
 [ 47 434 724   0]]
```

## C128 Synchronous / 13×13 / D32 / edge distance 5–8

Stone accuracy 71.41%; macro 68.45%; overcounts 1; undercounts 778.

```
[[559   1   0   0]
 [240 222   0   0]
 [ 68 160 237   0]
 [  9 102 199 928]]
```

Overcounts only:
```
[[0 1 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [240   0   0   0]
 [ 68 160   0   0]
 [  9 102 199   0]]
```

## C128 Synchronous / 13×13 / D64 / edge distance 0

Stone accuracy 99.89%; macro 99.70%; overcounts 6; undercounts 8.

```
[[ 824    6    0    0]
 [   0 8280    0    0]
 [   0    3 1603    0]
 [   0    2    3 1647]]
```

Overcounts only:
```
[[0 6 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 3 0 0]
 [0 2 3 0]]
```

## C128 Synchronous / 13×13 / D64 / edge distance 1

Stone accuracy 64.11%; macro 65.73%; overcounts 47; undercounts 4448.

```
[[1501   46    0    0]
 [1348 1189    0    0]
 [ 458  812 1276    1]
 [  94  697 1039 4062]]
```

Overcounts only:
```
[[ 0 46  0  0]
 [ 0  0  0  0]
 [ 0  0  0  1]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1348    0    0    0]
 [ 458  812    0    0]
 [  94  697 1039    0]]
```

## C128 Synchronous / 13×13 / D64 / edge distance 2

Stone accuracy 85.33%; macro 82.89%; overcounts 149; undercounts 1392.

```
[[2630  143    0    0]
 [ 650 1785    0    0]
 [  75  207  840    6]
 [   9  219  232 3705]]
```

Overcounts only:
```
[[  0 143   0   0]
 [  0   0   0   0]
 [  0   0   0   6]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [650   0   0   0]
 [ 75 207   0   0]
 [  9 219 232   0]]
```

## C128 Synchronous / 13×13 / D64 / edge distance 3–4

Stone accuracy 75.33%; macro 71.43%; overcounts 73; undercounts 3034.

```
[[2716   67    0    0]
 [ 980 1171    1    2]
 [ 265  601 1038    3]
 [  51  517  620 4563]]
```

Overcounts only:
```
[[ 0 67  0  0]
 [ 0  0  1  2]
 [ 0  0  0  3]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [980   0   0   0]
 [265 601   0   0]
 [ 51 517 620   0]]
```

## C128 Synchronous / 13×13 / D64 / edge distance 5–8

Stone accuracy 70.75%; macro 67.57%; overcounts 7; undercounts 790.

```
[[553   7   0   0]
 [249 213   0   0]
 [ 71 159 235   0]
 [  8 123 180 927]]
```

Overcounts only:
```
[[0 7 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [249   0   0   0]
 [ 71 159   0   0]
 [  8 123 180   0]]
```

## C128 Synchronous / 13×13 / D128 / edge distance 0

Stone accuracy 99.63%; macro 99.38%; overcounts 11; undercounts 35.

```
[[ 820   10    0    0]
 [  18 8261    0    1]
 [   0    4 1602    0]
 [   0    8    5 1639]]
```

Overcounts only:
```
[[ 0 10  0  0]
 [ 0  0  0  1]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [18  0  0  0]
 [ 0  4  0  0]
 [ 0  8  5  0]]
```

## C128 Synchronous / 13×13 / D128 / edge distance 1

Stone accuracy 62.95%; macro 63.99%; overcounts 111; undercounts 4529.

```
[[1456   66    0   25]
 [1413 1113    9    2]
 [ 514  777 1247    9]
 [ 110  753  962 4067]]
```

Overcounts only:
```
[[ 0 66  0 25]
 [ 0  0  9  2]
 [ 0  0  0  9]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1413    0    0    0]
 [ 514  777    0    0]
 [ 110  753  962    0]]
```

## C128 Synchronous / 13×13 / D128 / edge distance 2

Stone accuracy 84.24%; macro 81.25%; overcounts 194; undercounts 1461.

```
[[2635  134    0    4]
 [ 743 1681    6    5]
 [  79  197  807   45]
 [  11  199  232 3723]]
```

Overcounts only:
```
[[  0 134   0   4]
 [  0   0   6   5]
 [  0   0   0  45]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [743   0   0   0]
 [ 79 197   0   0]
 [ 11 199 232   0]]
```

## C128 Synchronous / 13×13 / D128 / edge distance 3–4

Stone accuracy 74.18%; macro 69.56%; overcounts 198; undercounts 3054.

```
[[2654  103    0   26]
 [1028 1105    6   15]
 [ 293  582  984   48]
 [  60  575  516 4600]]
```

Overcounts only:
```
[[  0 103   0  26]
 [  0   0   6  15]
 [  0   0   0  48]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1028    0    0    0]
 [ 293  582    0    0]
 [  60  575  516    0]]
```

## C128 Synchronous / 13×13 / D128 / edge distance 5–8

Stone accuracy 69.39%; macro 65.40%; overcounts 50; undercounts 784.

```
[[539  14   0   7]
 [252 194   0  16]
 [ 81 149 222  13]
 [  9 147 146 936]]
```

Overcounts only:
```
[[ 0 14  0  7]
 [ 0  0  0 16]
 [ 0  0  0 13]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [252   0   0   0]
 [ 81 149   0   0]
 [  9 147 146   0]]
```

## C128 Synchronous / 13×13 / D256 / edge distance 0

Stone accuracy 98.13%; macro 98.01%; overcounts 31; undercounts 200.

```
[[ 805   25    0    0]
 [ 153 8124    0    3]
 [   0   28 1575    3]
 [   0   10    9 1633]]
```

Overcounts only:
```
[[ 0 25  0  0]
 [ 0  0  0  3]
 [ 0  0  0  3]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [153   0   0   0]
 [  0  28   0   0]
 [  0  10   9   0]]
```

## C128 Synchronous / 13×13 / D256 / edge distance 1

Stone accuracy 60.98%; macro 61.08%; overcounts 308; undercounts 4578.

```
[[1377   86    4   80]
 [1469 1001   22   45]
 [ 608  674 1194   71]
 [ 136  796  895 4065]]
```

Overcounts only:
```
[[ 0 86  4 80]
 [ 0  0 22 45]
 [ 0  0  0 71]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1469    0    0    0]
 [ 608  674    0    0]
 [ 136  796  895    0]]
```

## C128 Synchronous / 13×13 / D256 / edge distance 2

Stone accuracy 81.83%; macro 78.25%; overcounts 399; undercounts 1509.

```
[[2572  128   17   56]
 [ 832 1482   42   79]
 [  96  175  780   77]
 [  15  179  212 3759]]
```

Overcounts only:
```
[[  0 128  17  56]
 [  0   0  42  79]
 [  0   0   0  77]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [832   0   0   0]
 [ 96 175   0   0]
 [ 15 179 212   0]]
```

## C128 Synchronous / 13×13 / D256 / edge distance 3–4

Stone accuracy 72.28%; macro 67.06%; overcounts 396; undercounts 3095.

```
[[2570  140    1   72]
 [1044 1008   37   65]
 [ 350  534  942   81]
 [  70  648  449 4584]]
```

Overcounts only:
```
[[  0 140   1  72]
 [  0   0  37  65]
 [  0   0   0  81]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1044    0    0    0]
 [ 350  534    0    0]
 [  70  648  449    0]]
```

## C128 Synchronous / 13×13 / D256 / edge distance 5–8

Stone accuracy 66.94%; macro 61.94%; overcounts 100; undercounts 801.

```
[[518  24   0  18]
 [258 170   2  32]
 [ 95 147 199  24]
 [  9 178 114 937]]
```

Overcounts only:
```
[[ 0 24  0 18]
 [ 0  0  2 32]
 [ 0  0  0 24]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [258   0   0   0]
 [ 95 147   0   0]
 [  9 178 114   0]]
```

## C128 Synchronous / 19×19 / D32 / edge distance 0

Stone accuracy 99.97%; macro 99.95%; overcounts 2; undercounts 1.

```
[[ 588    0    0    0]
 [   1 6733    0    0]
 [   0    0 1189    2]
 [   0    0    0 1211]]
```

Overcounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 2]
 [0 0 0 0]]
```

Undercounts only:
```
[[0 0 0 0]
 [1 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

## C128 Synchronous / 19×19 / D32 / edge distance 1

Stone accuracy 58.26%; macro 57.22%; overcounts 263; undercounts 3848.

```
[[1577  262    0    0]
 [1167  689    0    0]
 [1049  382  907    1]
 [ 694  453  103 2564]]
```

Overcounts only:
```
[[  0 262   0   0]
 [  0   0   0   0]
 [  0   0   0   1]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1167    0    0    0]
 [1049  382    0    0]
 [ 694  453  103    0]]
```

## C128 Synchronous / 19×19 / D32 / edge distance 2

Stone accuracy 77.73%; macro 73.73%; overcounts 452; undercounts 1561.

```
[[2314  446    0    0]
 [ 924 1043    4    0]
 [ 241   73  667    2]
 [ 177   99   47 3003]]
```

Overcounts only:
```
[[  0 446   0   0]
 [  0   0   4   0]
 [  0   0   0   2]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [924   0   0   0]
 [241  73   0   0]
 [177  99  47   0]]
```

## C128 Synchronous / 19×19 / D32 / edge distance 3–4

Stone accuracy 71.00%; macro 64.08%; overcounts 277; undercounts 3820.

```
[[3800  264    0    0]
 [1571  890   10    0]
 [ 849  228 1000    3]
 [ 646  436   90 4340]]
```

Overcounts only:
```
[[  0 264   0   0]
 [  0   0  10   0]
 [  0   0   0   3]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1571    0    0    0]
 [ 849  228    0    0]
 [ 646  436   90    0]]
```

## C128 Synchronous / 19×19 / D32 / edge distance 5–8

Stone accuracy 72.36%; macro 64.46%; overcounts 52; undercounts 3402.

```
[[3685   52    0    0]
 [1268  659    0    0]
 [ 905  169  956    0]
 [ 628  385   47 3742]]
```

Overcounts only:
```
[[ 0 52  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1268    0    0    0]
 [ 905  169    0    0]
 [ 628  385   47    0]]
```

## C128 Synchronous / 19×19 / D32 / edge distance 9–16

Stone accuracy 56.00%; macro 55.49%; overcounts 0; undercounts 66.

```
[[24  0  0  0]
 [23  9  0  0]
 [19  3  8  0]
 [10 11  0 43]]
```

Overcounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [23  0  0  0]
 [19  3  0  0]
 [10 11  0  0]]
```

## C128 Synchronous / 19×19 / D64 / edge distance 0

Stone accuracy 99.87%; macro 99.72%; overcounts 3; undercounts 10.

```
[[ 587    1    0    0]
 [   1 6733    0    0]
 [   0    5 1184    2]
 [   0    0    4 1207]]
```

Overcounts only:
```
[[0 1 0 0]
 [0 0 0 0]
 [0 0 0 2]
 [0 0 0 0]]
```

Undercounts only:
```
[[0 0 0 0]
 [1 0 0 0]
 [0 5 0 0]
 [0 0 4 0]]
```

## C128 Synchronous / 19×19 / D64 / edge distance 1

Stone accuracy 59.55%; macro 58.97%; overcounts 50; undercounts 3934.

```
[[1791   48    0    0]
 [1249  606    1    0]
 [1098  337  903    1]
 [ 737  415   98 2564]]
```

Overcounts only:
```
[[ 0 48  0  0]
 [ 0  0  1  0]
 [ 0  0  0  1]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1249    0    0    0]
 [1098  337    0    0]
 [ 737  415   98    0]]
```

## C128 Synchronous / 19×19 / D64 / edge distance 2

Stone accuracy 78.35%; macro 73.72%; overcounts 257; undercounts 1700.

```
[[2513  246    1    0]
 [1059  904    8    0]
 [ 223   92  666    2]
 [ 177  117   32 3000]]
```

Overcounts only:
```
[[  0 246   1   0]
 [  0   0   8   0]
 [  0   0   0   2]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1059    0    0    0]
 [ 223   92    0    0]
 [ 177  117   32    0]]
```

## C128 Synchronous / 19×19 / D64 / edge distance 3–4

Stone accuracy 71.37%; macro 64.19%; overcounts 179; undercounts 3866.

```
[[3904  160    0    0]
 [1609  848   14    0]
 [ 859  224  992    5]
 [ 669  427   78 4338]]
```

Overcounts only:
```
[[  0 160   0   0]
 [  0   0  14   0]
 [  0   0   0   5]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1609    0    0    0]
 [ 859  224    0    0]
 [ 669  427   78    0]]
```

## C128 Synchronous / 19×19 / D64 / edge distance 5–8

Stone accuracy 72.03%; macro 63.91%; overcounts 49; undercounts 3446.

```
[[3692   45    0    0]
 [1295  632    0    0]
 [ 918  171  937    4]
 [ 654  368   40 3740]]
```

Overcounts only:
```
[[ 0 45  0  0]
 [ 0  0  0  0]
 [ 0  0  0  4]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1295    0    0    0]
 [ 918  171    0    0]
 [ 654  368   40    0]]
```

## C128 Synchronous / 19×19 / D64 / edge distance 9–16

Stone accuracy 56.00%; macro 55.49%; overcounts 0; undercounts 66.

```
[[24  0  0  0]
 [23  9  0  0]
 [19  3  8  0]
 [11 10  0 43]]
```

Overcounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [23  0  0  0]
 [19  3  0  0]
 [11 10  0  0]]
```

## C128 Synchronous / 19×19 / D128 / edge distance 0

Stone accuracy 99.44%; macro 98.35%; overcounts 29; undercounts 25.

```
[[ 563   25    0    0]
 [   1 6733    0    0]
 [   0   12 1175    4]
 [   0    5    7 1199]]
```

Overcounts only:
```
[[ 0 25  0  0]
 [ 0  0  0  0]
 [ 0  0  0  4]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [ 1  0  0  0]
 [ 0 12  0  0]
 [ 0  5  7  0]]
```

## C128 Synchronous / 19×19 / D128 / edge distance 1

Stone accuracy 59.15%; macro 58.54%; overcounts 50; undercounts 3973.

```
[[1802   35    1    1]
 [1271  579    5    1]
 [1152  292  888    7]
 [ 778  386   94 2556]]
```

Overcounts only:
```
[[ 0 35  1  1]
 [ 0  0  5  1]
 [ 0  0  0  7]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1271    0    0    0]
 [1152  292    0    0]
 [ 778  386   94    0]]
```

## C128 Synchronous / 19×19 / D128 / edge distance 2

Stone accuracy 78.33%; macro 73.22%; overcounts 172; undercounts 1787.

```
[[2609  149    2    0]
 [1145  816    8    2]
 [ 220   96  656   11]
 [ 177  121   28 3000]]
```

Overcounts only:
```
[[  0 149   2   0]
 [  0   0   8   2]
 [  0   0   0  11]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1145    0    0    0]
 [ 220   96    0    0]
 [ 177  121   28    0]]
```

## C128 Synchronous / 19×19 / D128 / edge distance 3–4

Stone accuracy 71.11%; macro 63.65%; overcounts 236; undercounts 3845.

```
[[3895  123    0   46]
 [1637  812   10   12]
 [ 878  187  970   45]
 [ 710  376   57 4369]]
```

Overcounts only:
```
[[  0 123   0  46]
 [  0   0  10  12]
 [  0   0   0  45]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1637    0    0    0]
 [ 878  187    0    0]
 [ 710  376   57    0]]
```

## C128 Synchronous / 19×19 / D128 / edge distance 5–8

Stone accuracy 71.69%; macro 63.25%; overcounts 133; undercounts 3405.

```
[[3669   49    0   19]
 [1300  607    2   18]
 [ 931  146  908   45]
 [ 685  307   36 3774]]
```

Overcounts only:
```
[[ 0 49  0 19]
 [ 0  0  2 18]
 [ 0  0  0 45]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1300    0    0    0]
 [ 931  146    0    0]
 [ 685  307   36    0]]
```

## C128 Synchronous / 19×19 / D128 / edge distance 9–16

Stone accuracy 56.00%; macro 55.49%; overcounts 0; undercounts 66.

```
[[24  0  0  0]
 [23  9  0  0]
 [20  2  8  0]
 [14  7  0 43]]
```

Overcounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [23  0  0  0]
 [20  2  0  0]
 [14  7  0  0]]
```

## C128 Synchronous / 19×19 / D256 / edge distance 0

Stone accuracy 97.23%; macro 95.85%; overcounts 60; undercounts 209.

```
[[ 539   48    0    1]
 [ 140 6587    1    6]
 [   0   36 1151    4]
 [   0    8   25 1178]]
```

Overcounts only:
```
[[ 0 48  0  1]
 [ 0  0  1  6]
 [ 0  0  0  4]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [140   0   0   0]
 [  0  36   0   0]
 [  0   8  25   0]]
```

## C128 Synchronous / 19×19 / D256 / edge distance 1

Stone accuracy 57.84%; macro 56.87%; overcounts 197; undercounts 3955.

```
[[1743   27    4   65]
 [1284  536   19   17]
 [1187  226  861   65]
 [ 840  311  107 2556]]
```

Overcounts only:
```
[[ 0 27  4 65]
 [ 0  0 19 17]
 [ 0  0  0 65]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1284    0    0    0]
 [1187  226    0    0]
 [ 840  311  107    0]]
```

## C128 Synchronous / 19×19 / D256 / edge distance 2

Stone accuracy 77.43%; macro 71.63%; overcounts 239; undercounts 1801.

```
[[2625  108    4   23]
 [1221  719   12   19]
 [ 231   51  628   73]
 [ 176   85   37 3028]]
```

Overcounts only:
```
[[  0 108   4  23]
 [  0   0  12  19]
 [  0   0   0  73]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1221    0    0    0]
 [ 231   51    0    0]
 [ 176   85   37    0]]
```

## C128 Synchronous / 19×19 / D256 / edge distance 3–4

Stone accuracy 69.89%; macro 62.08%; overcounts 463; undercounts 3791.

```
[[3839  107    1  117]
 [1609  737   18  107]
 [ 891  143  933  113]
 [ 754  311   83 4364]]
```

Overcounts only:
```
[[  0 107   1 117]
 [  0   0  18 107]
 [  0   0   0 113]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1609    0    0    0]
 [ 891  143    0    0]
 [ 754  311   83    0]]
```

## C128 Synchronous / 19×19 / D256 / edge distance 5–8

Stone accuracy 70.93%; macro 62.08%; overcounts 354; undercounts 3278.

```
[[3615   51    1   70]
 [1284  561    6   76]
 [ 925   81  874  150]
 [ 703  247   38 3814]]
```

Overcounts only:
```
[[  0  51   1  70]
 [  0   0   6  76]
 [  0   0   0 150]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1284    0    0    0]
 [ 925   81    0    0]
 [ 703  247   38    0]]
```

## C128 Synchronous / 19×19 / D256 / edge distance 9–16

Stone accuracy 54.67%; macro 53.67%; overcounts 4; undercounts 64.

```
[[23  0  0  1]
 [22  8  0  2]
 [21  0  8  1]
 [15  6  0 43]]
```

Overcounts only:
```
[[0 0 0 1]
 [0 0 0 2]
 [0 0 0 1]
 [0 0 0 0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [22  0  0  0]
 [21  0  0  0]
 [15  6  0  0]]
```

## C128 Synchronous / 25×25 / D32 / edge distance 0

Stone accuracy 100.00%; macro 100.00%; overcounts 0; undercounts 0.

```
[[ 483    0    0    0]
 [   0 4660    0    0]
 [   0    0  781    0]
 [   0    0    0 1055]]
```

Overcounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

## C128 Synchronous / 25×25 / D32 / edge distance 1

Stone accuracy 61.02%; macro 59.99%; overcounts 178; undercounts 2567.

```
[[1359  166   10    1]
 [1091  464    0    0]
 [ 439   19  606    1]
 [ 800  148   70 1868]]
```

Overcounts only:
```
[[  0 166  10   1]
 [  0   0   0   0]
 [  0   0   0   1]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1091    0    0    0]
 [ 439   19    0    0]
 [ 800  148   70    0]]
```

## C128 Synchronous / 25×25 / D32 / edge distance 2

Stone accuracy 75.75%; macro 71.35%; overcounts 382; undercounts 1220.

```
[[1799  380    0    0]
 [ 815  579    0    0]
 [ 209    5  493    2]
 [ 148   32   11 2132]]
```

Overcounts only:
```
[[  0 380   0   0]
 [  0   0   0   0]
 [  0   0   0   2]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [815   0   0   0]
 [209   5   0   0]
 [148  32  11   0]]
```

## C128 Synchronous / 25×25 / D32 / edge distance 3–4

Stone accuracy 73.70%; macro 67.46%; overcounts 207; undercounts 2743.

```
[[3248  207    0    0]
 [1390  706    0    0]
 [ 449   35  787    0]
 [ 713  128   28 3525]]
```

Overcounts only:
```
[[  0 207   0   0]
 [  0   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1390    0    0    0]
 [ 449   35    0    0]
 [ 713  128   28    0]]
```

## C128 Synchronous / 25×25 / D32 / edge distance 5–8

Stone accuracy 75.95%; macro 68.27%; overcounts 149; undercounts 3278.

```
[[4658  145    0    0]
 [1572  792    4    0]
 [ 604   37 1067    0]
 [ 829  207   29 4306]]
```

Overcounts only:
```
[[  0 145   0   0]
 [  0   0   4   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1572    0    0    0]
 [ 604   37    0    0]
 [ 829  207   29    0]]
```

## C128 Synchronous / 25×25 / D32 / edge distance 9–16

Stone accuracy 74.48%; macro 66.66%; overcounts 25; undercounts 977.

```
[[1261   25    0    0]
 [ 429  220    0    0]
 [ 181   35  286    0]
 [ 234   87   11 1157]]
```

Overcounts only:
```
[[ 0 25  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [429   0   0   0]
 [181  35   0   0]
 [234  87  11   0]]
```

## C128 Synchronous / 25×25 / D64 / edge distance 0

Stone accuracy 99.81%; macro 99.41%; overcounts 9; undercounts 4.

```
[[ 474    9    0    0]
 [   0 4660    0    0]
 [   0    4  777    0]
 [   0    0    0 1055]]
```

Overcounts only:
```
[[0 9 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 4 0 0]
 [0 0 0 0]]
```

## C128 Synchronous / 25×25 / D64 / edge distance 1

Stone accuracy 62.23%; macro 61.39%; overcounts 49; undercounts 2611.

```
[[1489   43    4    0]
 [1134  420    1    0]
 [ 441   17  606    1]
 [ 810  145   64 1867]]
```

Overcounts only:
```
[[ 0 43  4  0]
 [ 0  0  1  0]
 [ 0  0  0  1]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1134    0    0    0]
 [ 441   17    0    0]
 [ 810  145   64    0]]
```

## C128 Synchronous / 25×25 / D64 / edge distance 2

Stone accuracy 76.64%; macro 71.50%; overcounts 243; undercounts 1300.

```
[[1939  240    0    0]
 [ 893  501    0    0]
 [ 209    5  492    3]
 [ 148   35   10 2130]]
```

Overcounts only:
```
[[  0 240   0   0]
 [  0   0   0   0]
 [  0   0   0   3]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [893   0   0   0]
 [209   5   0   0]
 [148  35  10   0]]
```

## C128 Synchronous / 25×25 / D64 / edge distance 3–4

Stone accuracy 74.04%; macro 67.49%; overcounts 132; undercounts 2780.

```
[[3325  130    0    0]
 [1415  680    1    0]
 [ 457   36  777    1]
 [ 713  136   23 3522]]
```

Overcounts only:
```
[[  0 130   0   0]
 [  0   0   1   0]
 [  0   0   0   1]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1415    0    0    0]
 [ 457   36    0    0]
 [ 713  136   23    0]]
```

## C128 Synchronous / 25×25 / D64 / edge distance 5–8

Stone accuracy 76.06%; macro 68.14%; overcounts 93; undercounts 3318.

```
[[4717   86    0    0]
 [1608  754    6    0]
 [ 614   27 1066    1]
 [ 862  179   28 4302]]
```

Overcounts only:
```
[[ 0 86  0  0]
 [ 0  0  6  0]
 [ 0  0  0  1]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1608    0    0    0]
 [ 614   27    0    0]
 [ 862  179   28    0]]
```

## C128 Synchronous / 25×25 / D64 / edge distance 9–16

Stone accuracy 74.55%; macro 66.52%; overcounts 12; undercounts 987.

```
[[1275   11    0    0]
 [ 438  211    0    0]
 [ 197   19  285    1]
 [ 255   69    9 1156]]
```

Overcounts only:
```
[[ 0 11  0  0]
 [ 0  0  0  0]
 [ 0  0  0  1]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [438   0   0   0]
 [197  19   0   0]
 [255  69   9   0]]
```

## C128 Synchronous / 25×25 / D128 / edge distance 0

Stone accuracy 99.37%; macro 98.30%; overcounts 25; undercounts 19.

```
[[ 458   25    0    0]
 [   6 4654    0    0]
 [   0    8  773    0]
 [   0    0    5 1050]]
```

Overcounts only:
```
[[ 0 25  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [6 0 0 0]
 [0 8 0 0]
 [0 0 5 0]]
```

## C128 Synchronous / 25×25 / D128 / edge distance 1

Stone accuracy 61.62%; macro 60.84%; overcounts 58; undercounts 2645.

```
[[1485   50    1    0]
 [1144  409    0    2]
 [ 446   12  602    5]
 [ 823  143   77 1843]]
```

Overcounts only:
```
[[ 0 50  1  0]
 [ 0  0  0  2]
 [ 0  0  0  5]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1144    0    0    0]
 [ 446   12    0    0]
 [ 823  143   77    0]]
```

## C128 Synchronous / 25×25 / D128 / edge distance 2

Stone accuracy 77.18%; macro 71.45%; overcounts 158; undercounts 1349.

```
[[2033  146    0    0]
 [ 940  451    2    1]
 [ 204   10  486    9]
 [ 149   33   13 2128]]
```

Overcounts only:
```
[[  0 146   0   0]
 [  0   0   2   1]
 [  0   0   0   9]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [940   0   0   0]
 [204  10   0   0]
 [149  33  13   0]]
```

## C128 Synchronous / 25×25 / D128 / edge distance 3–4

Stone accuracy 74.03%; macro 67.13%; overcounts 113; undercounts 2800.

```
[[3382   67    0    6]
 [1430  645    1   20]
 [ 458   33  761   19]
 [ 720  106   53 3515]]
```

Overcounts only:
```
[[ 0 67  0  6]
 [ 0  0  1 20]
 [ 0  0  0 19]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1430    0    0    0]
 [ 458   33    0    0]
 [ 720  106   53    0]]
```

## C128 Synchronous / 25×25 / D128 / edge distance 5–8

Stone accuracy 75.47%; macro 67.05%; overcounts 191; undercounts 3304.

```
[[4719   72    1   11]
 [1603  700   12   53]
 [ 620   18 1028   42]
 [ 894  147   22 4308]]
```

Overcounts only:
```
[[ 0 72  1 11]
 [ 0  0 12 53]
 [ 0  0  0 42]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1603    0    0    0]
 [ 620   18    0    0]
 [ 894  147   22    0]]
```

## C128 Synchronous / 25×25 / D128 / edge distance 9–16

Stone accuracy 74.07%; macro 65.64%; overcounts 33; undercounts 985.

```
[[1277    8    0    1]
 [ 436  202    0   11]
 [ 201   14  274   13]
 [ 264   62    8 1155]]
```

Overcounts only:
```
[[ 0  8  0  1]
 [ 0  0  0 11]
 [ 0  0  0 13]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [436   0   0   0]
 [201  14   0   0]
 [264  62   8   0]]
```

## C128 Synchronous / 25×25 / D256 / edge distance 0

Stone accuracy 97.66%; macro 96.69%; overcounts 42; undercounts 121.

```
[[ 456   26    0    1]
 [  84 4571    0    5]
 [   0   29  742   10]
 [   0    5    3 1047]]
```

Overcounts only:
```
[[ 0 26  0  1]
 [ 0  0  0  5]
 [ 0  0  0 10]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [84  0  0  0]
 [ 0 29  0  0]
 [ 0  5  3  0]]
```

## C128 Synchronous / 25×25 / D256 / edge distance 1

Stone accuracy 61.33%; macro 60.12%; overcounts 105; undercounts 2618.

```
[[1475   20   22   19]
 [1156  383    4   12]
 [ 444   10  583   28]
 [ 835   90   83 1878]]
```

Overcounts only:
```
[[ 0 20 22 19]
 [ 0  0  4 12]
 [ 0  0  0 28]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1156    0    0    0]
 [ 444   10    0    0]
 [ 835   90   83    0]]
```

## C128 Synchronous / 25×25 / D256 / edge distance 2

Stone accuracy 76.53%; macro 70.19%; overcounts 145; undercounts 1405.

```
[[2073   68   17   21]
 [ 991  390    1   12]
 [ 202   11  470   26]
 [ 149   29   23 2122]]
```

Overcounts only:
```
[[ 0 68 17 21]
 [ 0  0  1 12]
 [ 0  0  0 26]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [991   0   0   0]
 [202  11   0   0]
 [149  29  23   0]]
```

## C128 Synchronous / 25×25 / D256 / edge distance 3–4

Stone accuracy 73.22%; macro 65.74%; overcounts 234; undercounts 2770.

```
[[3395   40    0   20]
 [1427  605    3   61]
 [ 437    9  715  110]
 [ 721   98   78 3497]]
```

Overcounts only:
```
[[  0  40   0  20]
 [  0   0   3  61]
 [  0   0   0 110]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1427    0    0    0]
 [ 437    9    0    0]
 [ 721   98   78    0]]
```

## C128 Synchronous / 25×25 / D256 / edge distance 5–8

Stone accuracy 74.26%; macro 65.30%; overcounts 417; undercounts 3251.

```
[[4675   53    0   75]
 [1559  629    2  178]
 [ 616    5  978  109]
 [ 932  105   34 4300]]
```

Overcounts only:
```
[[  0  53   0  75]
 [  0   0   2 178]
 [  0   0   0 109]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1559    0    0    0]
 [ 616    5    0    0]
 [ 932  105   34    0]]
```

## C128 Synchronous / 25×25 / D256 / edge distance 9–16

Stone accuracy 73.33%; macro 64.35%; overcounts 89; undercounts 958.

```
[[1275    6    0    5]
 [ 430  188    1   30]
 [ 196    0  259   47]
 [ 287   31   14 1157]]
```

Overcounts only:
```
[[ 0  6  0  5]
 [ 0  0  1 30]
 [ 0  0  0 47]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [430   0   0   0]
 [196   0   0   0]
 [287  31  14   0]]
```

## C128 Synchronous / 37×37 / D32 / edge distance 0

Stone accuracy 100.00%; macro 100.00%; overcounts 0; undercounts 0.

```
[[ 246    0    0    0]
 [   0 3869    0    0]
 [   0    0  592    0]
 [   0    0    0  700]]
```

Overcounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

## C128 Synchronous / 37×37 / D32 / edge distance 1

Stone accuracy 46.43%; macro 47.13%; overcounts 211; undercounts 2766.

```
[[ 653  210    0    0]
 [ 674  308    0    0]
 [ 948    9  408    1]
 [1089   46    0 1211]]
```

Overcounts only:
```
[[  0 210   0   0]
 [  0   0   0   0]
 [  0   0   0   1]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [ 674    0    0    0]
 [ 948    9    0    0]
 [1089   46    0    0]]
```

## C128 Synchronous / 37×37 / D32 / edge distance 17+

Stone accuracy 59.57%; macro 53.21%; overcounts 1; undercounts 151.

```
[[98  1  0  0]
 [34 13  0  0]
 [50  9 19  0]
 [55  3  0 94]]
```

Overcounts only:
```
[[0 1 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [34  0  0  0]
 [50  9  0  0]
 [55  3  0  0]]
```

## C128 Synchronous / 37×37 / D32 / edge distance 2

Stone accuracy 69.22%; macro 66.87%; overcounts 240; undercounts 1405.

```
[[1672  238    0    0]
 [1065  350    0    0]
 [ 156    3  327    2]
 [ 168   10    3 1351]]
```

Overcounts only:
```
[[  0 238   0   0]
 [  0   0   0   0]
 [  0   0   0   2]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1065    0    0    0]
 [ 156    3    0    0]
 [ 168   10    3    0]]
```

## C128 Synchronous / 37×37 / D32 / edge distance 3–4

Stone accuracy 61.71%; macro 56.18%; overcounts 198; undercounts 3590.

```
[[2539  193    0    0]
 [1547  475    0    0]
 [ 923   11  603    5]
 [1049   50   10 2489]]
```

Overcounts only:
```
[[  0 193   0   0]
 [  0   0   0   0]
 [  0   0   0   5]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1547    0    0    0]
 [ 923   11    0    0]
 [1049   50   10    0]]
```

## C128 Synchronous / 37×37 / D32 / edge distance 5–8

Stone accuracy 64.47%; macro 57.80%; overcounts 162; undercounts 5447.

```
[[4514  156    0    0]
 [2218  741    0    0]
 [1411   95 1011    6]
 [1642   70   11 3912]]
```

Overcounts only:
```
[[  0 156   0   0]
 [  0   0   0   0]
 [  0   0   0   6]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2218    0    0    0]
 [1411   95    0    0]
 [1642   70   11    0]]
```

## C128 Synchronous / 37×37 / D32 / edge distance 9–16

Stone accuracy 66.65%; macro 57.78%; overcounts 85; undercounts 4851.

```
[[4661   85    0    0]
 [1632  577    0    0]
 [1409   96  944    0]
 [1573  125   16 3681]]
```

Overcounts only:
```
[[ 0 85  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1632    0    0    0]
 [1409   96    0    0]
 [1573  125   16    0]]
```

## C128 Synchronous / 37×37 / D64 / edge distance 0

Stone accuracy 99.96%; macro 99.93%; overcounts 0; undercounts 2.

```
[[ 246    0    0    0]
 [   0 3869    0    0]
 [   0    0  592    0]
 [   0    1    1  698]]
```

Overcounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 1 1 0]]
```

## C128 Synchronous / 37×37 / D64 / edge distance 1

Stone accuracy 49.54%; macro 52.26%; overcounts 5; undercounts 2799.

```
[[ 859    4    0    0]
 [ 707  275    0    0]
 [ 956    1  408    1]
 [1101   34    0 1211]]
```

Overcounts only:
```
[[0 4 0 0]
 [0 0 0 0]
 [0 0 0 1]
 [0 0 0 0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [ 707    0    0    0]
 [ 956    1    0    0]
 [1101   34    0    0]]
```

## C128 Synchronous / 37×37 / D64 / edge distance 17+

Stone accuracy 59.84%; macro 53.47%; overcounts 0; undercounts 151.

```
[[99  0  0  0]
 [34 13  0  0]
 [52  7 19  0]
 [58  0  0 94]]
```

Overcounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [34  0  0  0]
 [52  7  0  0]
 [58  0  0  0]]
```

## C128 Synchronous / 37×37 / D64 / edge distance 2

Stone accuracy 70.36%; macro 67.39%; overcounts 118; undercounts 1466.

```
[[1794  116    0    0]
 [1125  290    0    0]
 [ 158    1  327    2]
 [ 169   10    3 1350]]
```

Overcounts only:
```
[[  0 116   0   0]
 [  0   0   0   0]
 [  0   0   0   2]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1125    0    0    0]
 [ 158    1    0    0]
 [ 169   10    3    0]]
```

## C128 Synchronous / 37×37 / D64 / edge distance 3–4

Stone accuracy 62.48%; macro 56.83%; overcounts 110; undercounts 3602.

```
[[2628  104    0    0]
 [1558  464    0    0]
 [ 926    8  602    6]
 [1059   41   10 2488]]
```

Overcounts only:
```
[[  0 104   0   0]
 [  0   0   0   0]
 [  0   0   0   6]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1558    0    0    0]
 [ 926    8    0    0]
 [1059   41   10    0]]
```

## C128 Synchronous / 37×37 / D64 / edge distance 5–8

Stone accuracy 64.91%; macro 58.10%; overcounts 82; undercounts 5457.

```
[[4600   70    0    0]
 [2230  728    0    1]
 [1443   65 1004   11]
 [1675   37    7 3916]]
```

Overcounts only:
```
[[ 0 70  0  0]
 [ 0  0  0  1]
 [ 0  0  0 11]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2230    0    0    0]
 [1443   65    0    0]
 [1675   37    7    0]]
```

## C128 Synchronous / 37×37 / D64 / edge distance 9–16

Stone accuracy 66.65%; macro 57.69%; overcounts 71; undercounts 4864.

```
[[4676   70    0    0]
 [1645  564    0    0]
 [1437   69  942    1]
 [1614   87   12 3682]]
```

Overcounts only:
```
[[ 0 70  0  0]
 [ 0  0  0  0]
 [ 0  0  0  1]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1645    0    0    0]
 [1437   69    0    0]
 [1614   87   12    0]]
```

## C128 Synchronous / 37×37 / D128 / edge distance 0

Stone accuracy 99.83%; macro 99.56%; overcounts 3; undercounts 6.

```
[[ 244    2    0    0]
 [   1 3868    0    0]
 [   0    1  590    1]
 [   0    3    1  696]]
```

Overcounts only:
```
[[0 2 0 0]
 [0 0 0 0]
 [0 0 0 1]
 [0 0 0 0]]
```

Undercounts only:
```
[[0 0 0 0]
 [1 0 0 0]
 [0 1 0 0]
 [0 3 1 0]]
```

## C128 Synchronous / 37×37 / D128 / edge distance 1

Stone accuracy 49.51%; macro 52.23%; overcounts 4; undercounts 2802.

```
[[ 862    1    0    0]
 [ 710  272    0    0]
 [ 957    0  406    3]
 [1107   28    0 1211]]
```

Overcounts only:
```
[[0 1 0 0]
 [0 0 0 0]
 [0 0 0 3]
 [0 0 0 0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [ 710    0    0    0]
 [ 957    0    0    0]
 [1107   28    0    0]]
```

## C128 Synchronous / 37×37 / D128 / edge distance 17+

Stone accuracy 59.84%; macro 53.47%; overcounts 0; undercounts 151.

```
[[99  0  0  0]
 [34 13  0  0]
 [54  5 19  0]
 [58  0  0 94]]
```

Overcounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [34  0  0  0]
 [54  5  0  0]
 [58  0  0  0]]
```

## C128 Synchronous / 37×37 / D128 / edge distance 2

Stone accuracy 71.11%; macro 67.71%; overcounts 50; undercounts 1494.

```
[[1864   46    0    0]
 [1152  263    0    0]
 [ 158    1  325    4]
 [ 170   10    3 1349]]
```

Overcounts only:
```
[[ 0 46  0  0]
 [ 0  0  0  0]
 [ 0  0  0  4]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1152    0    0    0]
 [ 158    1    0    0]
 [ 170   10    3    0]]
```

## C128 Synchronous / 37×37 / D128 / edge distance 3–4

Stone accuracy 62.84%; macro 56.95%; overcounts 95; undercounts 3582.

```
[[2707   25    0    0]
 [1541  427    0   54]
 [ 929    6  591   16]
 [1074   26    6 2492]]
```

Overcounts only:
```
[[ 0 25  0  0]
 [ 0  0  0 54]
 [ 0  0  0 16]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1541    0    0    0]
 [ 929    6    0    0]
 [1074   26    6    0]]
```

## C128 Synchronous / 37×37 / D128 / edge distance 5–8

Stone accuracy 64.65%; macro 57.71%; overcounts 131; undercounts 5450.

```
[[4595   22    1   52]
 [2226  706    5   22]
 [1482   27  985   29]
 [1699   13    3 3920]]
```

Overcounts only:
```
[[ 0 22  1 52]
 [ 0  0  5 22]
 [ 0  0  0 29]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2226    0    0    0]
 [1482   27    0    0]
 [1699   13    3    0]]
```

## C128 Synchronous / 37×37 / D128 / edge distance 9–16

Stone accuracy 66.69%; macro 57.60%; overcounts 61; undercounts 4869.

```
[[4697   40    0    9]
 [1655  550    4    0]
 [1462   44  935    8]
 [1678   23    7 3687]]
```

Overcounts only:
```
[[ 0 40  0  9]
 [ 0  0  4  0]
 [ 0  0  0  8]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1655    0    0    0]
 [1462   44    0    0]
 [1678   23    7    0]]
```

## C128 Synchronous / 37×37 / D256 / edge distance 0

Stone accuracy 98.56%; macro 97.43%; overcounts 8; undercounts 70.

```
[[ 242    4    0    0]
 [  22 3846    0    1]
 [   0   26  563    3]
 [   0    9   13  678]]
```

Overcounts only:
```
[[0 4 0 0]
 [0 0 0 1]
 [0 0 0 3]
 [0 0 0 0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [22  0  0  0]
 [ 0 26  0  0]
 [ 0  9 13  0]]
```

## C128 Synchronous / 37×37 / D256 / edge distance 1

Stone accuracy 49.00%; macro 51.57%; overcounts 36; undercounts 2798.

```
[[ 857    2    1    3]
 [ 709  258    7    8]
 [ 953    0  398   15]
 [1118   17    1 1210]]
```

Overcounts only:
```
[[ 0  2  1  3]
 [ 0  0  7  8]
 [ 0  0  0 15]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [ 709    0    0    0]
 [ 953    0    0    0]
 [1118   17    1    0]]
```

## C128 Synchronous / 37×37 / D256 / edge distance 17+

Stone accuracy 58.51%; macro 51.86%; overcounts 13; undercounts 143.

```
[[99  0  0  0]
 [34 13  0  0]
 [51  0 14 13]
 [58  0  0 94]]
```

Overcounts only:
```
[[ 0  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0 13]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [34  0  0  0]
 [51  0  0  0]
 [58  0  0  0]]
```

## C128 Synchronous / 37×37 / D256 / edge distance 2

Stone accuracy 70.74%; macro 66.86%; overcounts 54; undercounts 1510.

```
[[1885   23    0    2]
 [1167  238    6    4]
 [ 155    1  313   19]
 [ 171    9    7 1345]]
```

Overcounts only:
```
[[ 0 23  0  2]
 [ 0  0  6  4]
 [ 0  0  0 19]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1167    0    0    0]
 [ 155    1    0    0]
 [ 171    9    7    0]]
```

## C128 Synchronous / 37×37 / D256 / edge distance 3–4

Stone accuracy 62.39%; macro 56.33%; overcounts 128; undercounts 3593.

```
[[2709   20    0    3]
 [1552  408    4   58]
 [ 930    1  568   43]
 [1080   19   11 2488]]
```

Overcounts only:
```
[[ 0 20  0  3]
 [ 0  0  4 58]
 [ 0  0  0 43]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1552    0    0    0]
 [ 930    1    0    0]
 [1080   19   11    0]]
```

## C128 Synchronous / 37×37 / D256 / edge distance 5–8

Stone accuracy 64.10%; macro 56.97%; overcounts 219; undercounts 5449.

```
[[4592   17    1   60]
 [2220  665    6   68]
 [1488   18  950   67]
 [1709    3   11 3912]]
```

Overcounts only:
```
[[ 0 17  1 60]
 [ 0  0  6 68]
 [ 0  0  0 67]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2220    0    0    0]
 [1488   18    0    0]
 [1709    3   11    0]]
```

## C128 Synchronous / 37×37 / D256 / edge distance 9–16

Stone accuracy 66.06%; macro 56.72%; overcounts 188; undercounts 4835.

```
[[4677   19    0   50]
 [1660  521    6   22]
 [1453   12  893   91]
 [1690   10   10 3685]]
```

Overcounts only:
```
[[ 0 19  0 50]
 [ 0  0  6 22]
 [ 0  0  0 91]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1660    0    0    0]
 [1453   12    0    0]
 [1690   10   10    0]]
```

## Synchronous / 13×13 / D32 / edge distance 0

Stone accuracy 97.93%; macro 99.17%; overcounts 6; undercounts 762.

```
[[ 2488     2     0     0]
 [  752 24084     4     0]
 [    0     1  4817     0]
 [    0     1     8  4947]]
```

Overcounts only:
```
[[0 2 0 0]
 [0 0 4 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [752   0   0   0]
 [  0   1   0   0]
 [  0   1   8   0]]
```

## Synchronous / 13×13 / D32 / edge distance 1

Stone accuracy 60.69%; macro 61.79%; overcounts 108; undercounts 14662.

```
[[ 4543    98     0     0]
 [ 4761  2846     4     0]
 [ 2802  1507  3326     6]
 [ 1756  2164  1672 12084]]
```

Overcounts only:
```
[[ 0 98  0  0]
 [ 0  0  4  0]
 [ 0  0  0  6]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4761    0    0    0]
 [2802 1507    0    0]
 [1756 2164 1672    0]]
```

## Synchronous / 13×13 / D32 / edge distance 2

Stone accuracy 80.94%; macro 77.92%; overcounts 191; undercounts 5815.

```
[[ 8144   174     1     0]
 [ 3373  3929     3     0]
 [  581   350  2440    13]
 [  375   581   555 10984]]
```

Overcounts only:
```
[[  0 174   1   0]
 [  0   0   3   0]
 [  0   0   0  13]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3373    0    0    0]
 [ 581  350    0    0]
 [ 375  581  555    0]]
```

## Synchronous / 13×13 / D32 / edge distance 3–4

Stone accuracy 72.20%; macro 67.16%; overcounts 65; undercounts 10441.

```
[[ 8312    33     4     0]
 [ 3889  2569     4     0]
 [ 1848   916  2933    24]
 [ 1280  1357  1151 13465]]
```

Overcounts only:
```
[[ 0 33  4  0]
 [ 0  0  4  0]
 [ 0  0  0 24]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3889    0    0    0]
 [1848  916    0    0]
 [1280 1357 1151    0]]
```

## Synchronous / 13×13 / D32 / edge distance 5–8

Stone accuracy 67.34%; macro 63.42%; overcounts 18; undercounts 2652.

```
[[1670    8    2    0]
 [ 897  489    0    0]
 [ 509  232  646    8]
 [ 329  341  344 2700]]
```

Overcounts only:
```
[[0 8 2 0]
 [0 0 0 0]
 [0 0 0 8]
 [0 0 0 0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [897   0   0   0]
 [509 232   0   0]
 [329 341 344   0]]
```

## Synchronous / 13×13 / D64 / edge distance 0

Stone accuracy 94.78%; macro 97.55%; overcounts 175; undercounts 1762.

```
[[ 2446    44     0     0]
 [ 1751 22971   118     0]
 [    0     2  4803    13]
 [    0     0     9  4947]]
```

Overcounts only:
```
[[  0  44   0   0]
 [  0   0 118   0]
 [  0   0   0  13]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1751    0    0    0]
 [   0    2    0    0]
 [   0    0    9    0]]
```

## Synchronous / 13×13 / D64 / edge distance 1

Stone accuracy 60.26%; macro 60.98%; overcounts 306; undercounts 14624.

```
[[ 4431   205     5     0]
 [ 4794  2737    80     0]
 [ 2984  1280  3361    16]
 [ 1792  2036  1738 12110]]
```

Overcounts only:
```
[[  0 205   5   0]
 [  0   0  80   0]
 [  0   0   0  16]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4794    0    0    0]
 [2984 1280    0    0]
 [1792 2036 1738    0]]
```

## Synchronous / 13×13 / D64 / edge distance 2

Stone accuracy 78.82%; macro 75.83%; overcounts 419; undercounts 6254.

```
[[ 7978   305    35     1]
 [ 3780  3464    61     0]
 [  640   275  2452    17]
 [  422   481   656 10936]]
```

Overcounts only:
```
[[  0 305  35   1]
 [  0   0  61   0]
 [  0   0   0  17]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3780    0    0    0]
 [ 640  275    0    0]
 [ 422  481  656    0]]
```

## Synchronous / 13×13 / D64 / edge distance 3–4

Stone accuracy 71.20%; macro 65.90%; overcounts 313; undercounts 10568.

```
[[ 8132   176    41     0]
 [ 4030  2371    61     0]
 [ 1990   747  2949    35]
 [ 1373  1157  1271 13452]]
```

Overcounts only:
```
[[  0 176  41   0]
 [  0   0  61   0]
 [  0   0   0  35]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4030    0    0    0]
 [1990  747    0    0]
 [1373 1157 1271    0]]
```

## Synchronous / 13×13 / D64 / edge distance 5–8

Stone accuracy 66.92%; macro 62.84%; overcounts 57; undercounts 2647.

```
[[1641   29   10    0]
 [ 906  474    5    1]
 [ 548  184  651   12]
 [ 380  272  357 2705]]
```

Overcounts only:
```
[[ 0 29 10  0]
 [ 0  0  5  1]
 [ 0  0  0 12]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [906   0   0   0]
 [548 184   0   0]
 [380 272 357   0]]
```

## Synchronous / 13×13 / D128 / edge distance 0

Stone accuracy 87.66%; macro 89.59%; overcounts 1538; undercounts 3040.

```
[[ 2054   425    11     0]
 [ 2657 21156  1017    10]
 [    0    16  4727    75]
 [    0     0   367  4589]]
```

Overcounts only:
```
[[   0  425   11    0]
 [   0    0 1017   10]
 [   0    0    0   75]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2657    0    0    0]
 [   0   16    0    0]
 [   0    0  367    0]]
```

## Synchronous / 13×13 / D128 / edge distance 1

Stone accuracy 56.25%; macro 56.57%; overcounts 1225; undercounts 15211.

```
[[ 3907   630   104     0]
 [ 4599  2577   435     0]
 [ 2944  1226  3415    56]
 [ 1783  2087  2572 11234]]
```

Overcounts only:
```
[[  0 630 104   0]
 [  0   0 435   0]
 [  0   0   0  56]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4599    0    0    0]
 [2944 1226    0    0]
 [1783 2087 2572    0]]
```

## Synchronous / 13×13 / D128 / edge distance 2

Stone accuracy 72.82%; macro 70.96%; overcounts 1488; undercounts 7076.

```
[[ 7315   805   199     0]
 [ 3724  3136   445     0]
 [  630   253  2462    39]
 [  397   408  1664 10026]]
```

Overcounts only:
```
[[  0 805 199   0]
 [  0   0 445   0]
 [  0   0   0  39]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3724    0    0    0]
 [ 630  253    0    0]
 [ 397  408 1664    0]]
```

## Synchronous / 13×13 / D128 / edge distance 3–4

Stone accuracy 66.59%; macro 61.95%; overcounts 1326; undercounts 11298.

```
[[ 7568   579   202     0]
 [ 3892  2104   465     1]
 [ 2054   608  2980    79]
 [ 1328  1164  2252 12509]]
```

Overcounts only:
```
[[  0 579 202   0]
 [  0   0 465   1]
 [  0   0   0  79]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3892    0    0    0]
 [2054  608    0    0]
 [1328 1164 2252    0]]
```

## Synchronous / 13×13 / D128 / edge distance 5–8

Stone accuracy 63.23%; macro 58.90%; overcounts 290; undercounts 2716.

```
[[1514  119   47    0]
 [ 897  390   98    1]
 [ 568  144  658   25]
 [ 370  275  462 2607]]
```

Overcounts only:
```
[[  0 119  47   0]
 [  0   0  98   1]
 [  0   0   0  25]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [897   0   0   0]
 [568 144   0   0]
 [370 275 462   0]]
```

## Synchronous / 13×13 / D256 / edge distance 0

Stone accuracy 78.32%; macro 77.31%; overcounts 3385; undercounts 4659.

```
[[ 1564   815   109     2]
 [ 3320 19257  2228    35]
 [    0    29  4593   196]
 [    0     2  1308  3646]]
```

Overcounts only:
```
[[   0  815  109    2]
 [   0    0 2228   35]
 [   0    0    0  196]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3320    0    0    0]
 [   0   29    0    0]
 [   0    2 1308    0]]
```

## Synchronous / 13×13 / D256 / edge distance 1

Stone accuracy 50.78%; macro 51.52%; overcounts 2538; undercounts 15955.

```
[[3238 1031  371    1]
 [3823 2759 1023    6]
 [2407 1619 3509  106]
 [1703 2080 4323 9570]]
```

Overcounts only:
```
[[   0 1031  371    1]
 [   0    0 1023    6]
 [   0    0    0  106]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3823    0    0    0]
 [2407 1619    0    0]
 [1703 2080 4323    0]]
```

## Synchronous / 13×13 / D256 / edge distance 2

Stone accuracy 64.64%; macro 64.86%; overcounts 2873; undercounts 8266.

```
[[6709  887  720    3]
 [3384 2763 1139   19]
 [ 539  243 2497  105]
 [ 342  407 3351 8395]]
```

Overcounts only:
```
[[   0  887  720    3]
 [   0    0 1139   19]
 [   0    0    0  105]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3384    0    0    0]
 [ 539  243    0    0]
 [ 342  407 3351    0]]
```

## Synchronous / 13×13 / D256 / edge distance 3–4

Stone accuracy 58.70%; macro 55.33%; overcounts 2773; undercounts 12831.

```
[[ 6934   766   642     7]
 [ 3729  1528  1183    22]
 [ 1833   731  3004   153]
 [ 1308  1189  4041 10715]]
```

Overcounts only:
```
[[   0  766  642    7]
 [   0    0 1183   22]
 [   0    0    0  153]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3729    0    0    0]
 [1833  731    0    0]
 [1308 1189 4041    0]]
```

## Synchronous / 13×13 / D256 / edge distance 5–8

Stone accuracy 56.01%; macro 52.85%; overcounts 558; undercounts 3038.

```
[[1400  153  124    3]
 [ 871  277  231    7]
 [ 542  144  669   40]
 [ 372  259  850 2233]]
```

Overcounts only:
```
[[  0 153 124   3]
 [  0   0 231   7]
 [  0   0   0  40]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [871   0   0   0]
 [542 144   0   0]
 [372 259 850   0]]
```

## Synchronous / 19×19 / D32 / edge distance 0

Stone accuracy 88.42%; macro 95.75%; overcounts 11; undercounts 3367.

```
[[ 1762     2     0     0]
 [ 3367 16833     2     0]
 [    0     0  3566     7]
 [    0     0     0  3633]]
```

Overcounts only:
```
[[0 2 0 0]
 [0 0 2 0]
 [0 0 0 7]
 [0 0 0 0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3367    0    0    0]
 [   0    0    0    0]
 [   0    0    0    0]]
```

## Synchronous / 19×19 / D32 / edge distance 1

Stone accuracy 57.95%; macro 56.93%; overcounts 405; undercounts 12019.

```
[[5127  388    2    0]
 [3879 1685    4    0]
 [3952  438 2616   11]
 [3133  546   71 7692]]
```

Overcounts only:
```
[[  0 388   2   0]
 [  0   0   4   0]
 [  0   0   0  11]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3879    0    0    0]
 [3952  438    0    0]
 [3133  546   71    0]]
```

## Synchronous / 19×19 / D32 / edge distance 2

Stone accuracy 77.31%; macro 72.77%; overcounts 1090; undercounts 5063.

```
[[7209 1065    6    0]
 [3143 2761    9    0]
 [ 849  118 1972   10]
 [ 708  186   59 9025]]
```

Overcounts only:
```
[[   0 1065    6    0]
 [   0    0    9    0]
 [   0    0    0   10]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3143    0    0    0]
 [ 849  118    0    0]
 [ 708  186   59    0]]
```

## Synchronous / 19×19 / D32 / edge distance 3–4

Stone accuracy 70.46%; macro 62.92%; overcounts 579; undercounts 11940.

```
[[11642   520    30     0]
 [ 5165  2226    22     0]
 [ 3071   211  2951     7]
 [ 2965   434    94 13043]]
```

Overcounts only:
```
[[  0 520  30   0]
 [  0   0  22   0]
 [  0   0   0   7]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5165    0    0    0]
 [3071  211    0    0]
 [2965  434   94    0]]
```

## Synchronous / 19×19 / D32 / edge distance 5–8

Stone accuracy 71.16%; macro 62.85%; overcounts 306; undercounts 10507.

```
[[10907   270    34     0]
 [ 4036  1743     2     0]
 [ 3068   214  2808     0]
 [ 2981   162    46 11217]]
```

Overcounts only:
```
[[  0 270  34   0]
 [  0   0   2   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4036    0    0    0]
 [3068  214    0    0]
 [2981  162   46    0]]
```

## Synchronous / 19×19 / D32 / edge distance 9–16

Stone accuracy 56.00%; macro 55.49%; overcounts 0; undercounts 198.

```
[[ 72   0   0   0]
 [ 69  27   0   0]
 [ 64   2  24   0]
 [ 62   1   0 129]]
```

Overcounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [69  0  0  0]
 [64  2  0  0]
 [62  1  0  0]]
```

## Synchronous / 19×19 / D64 / edge distance 0

Stone accuracy 84.49%; macro 93.78%; overcounts 179; undercounts 4345.

```
[[ 1724    39     1     0]
 [ 4338 15736   128     0]
 [    0     0  3562    11]
 [    0     0     7  3626]]
```

Overcounts only:
```
[[  0  39   1   0]
 [  0   0 128   0]
 [  0   0   0  11]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4338    0    0    0]
 [   0    0    0    0]
 [   0    0    7    0]]
```

## Synchronous / 19×19 / D64 / edge distance 1

Stone accuracy 57.67%; macro 56.57%; overcounts 459; undercounts 12047.

```
[[5111  362   41    3]
 [3914 1614   40    0]
 [3944  428 2632   13]
 [3310  375   76 7681]]
```

Overcounts only:
```
[[  0 362  41   3]
 [  0   0  40   0]
 [  0   0   0  13]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3914    0    0    0]
 [3944  428    0    0]
 [3310  375   76    0]]
```

## Synchronous / 19×19 / D64 / edge distance 2

Stone accuracy 76.20%; macro 71.39%; overcounts 1093; undercounts 5361.

```
[[7348  856   70    6]
 [3407 2358  146    2]
 [ 874   90 1972   13]
 [ 747  137  106 8988]]
```

Overcounts only:
```
[[  0 856  70   6]
 [  0   0 146   2]
 [  0   0   0  13]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3407    0    0    0]
 [ 874   90    0    0]
 [ 747  137  106    0]]
```

## Synchronous / 19×19 / D64 / edge distance 3–4

Stone accuracy 69.75%; macro 62.03%; overcounts 783; undercounts 12037.

```
[[11557   455   158    22]
 [ 5252  2029   130     2]
 [ 3068   213  2943    16]
 [ 3073   334    97 13032]]
```

Overcounts only:
```
[[  0 455 158  22]
 [  0   0 130   2]
 [  0   0   0  16]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5252    0    0    0]
 [3068  213    0    0]
 [3073  334   97    0]]
```

## Synchronous / 19×19 / D64 / edge distance 5–8

Stone accuracy 70.47%; macro 62.15%; overcounts 571; undercounts 10501.

```
[[10720   308   130    53]
 [ 4027  1680    66     8]
 [ 3089   185  2810     6]
 [ 2972   171    57 11206]]
```

Overcounts only:
```
[[  0 308 130  53]
 [  0   0  66   8]
 [  0   0   0   6]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4027    0    0    0]
 [3089  185    0    0]
 [2972  171   57    0]]
```

## Synchronous / 19×19 / D64 / edge distance 9–16

Stone accuracy 56.00%; macro 55.49%; overcounts 0; undercounts 198.

```
[[ 72   0   0   0]
 [ 69  27   0   0]
 [ 64   2  24   0]
 [ 62   1   0 129]]
```

Overcounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [69  0  0  0]
 [64  2  0  0]
 [62  1  0  0]]
```

## Synchronous / 19×19 / D128 / edge distance 0

Stone accuracy 76.62%; macro 85.09%; overcounts 1100; undercounts 5721.

```
[[ 1393   357    14     0]
 [ 5484 14046   660    12]
 [    0     5  3511    57]
 [    0     0   232  3401]]
```

Overcounts only:
```
[[  0 357  14   0]
 [  0   0 660  12]
 [  0   0   0  57]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5484    0    0    0]
 [   0    5    0    0]
 [   0    0  232    0]]
```

## Synchronous / 19×19 / D128 / edge distance 1

Stone accuracy 55.40%; macro 54.33%; overcounts 955; undercounts 12222.

```
[[4835  552  120   10]
 [3803 1526  238    1]
 [3803  490 2690   34]
 [3326  340  460 7316]]
```

Overcounts only:
```
[[  0 552 120  10]
 [  0   0 238   1]
 [  0   0   0  34]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3803    0    0    0]
 [3803  490    0    0]
 [3326  340  460    0]]
```

## Synchronous / 19×19 / D128 / edge distance 2

Stone accuracy 71.52%; macro 67.26%; overcounts 1461; undercounts 6262.

```
[[7240  757  268   15]
 [3635 1886  390    2]
 [ 854  109 1957   29]
 [ 748  129  787 8314]]
```

Overcounts only:
```
[[  0 757 268  15]
 [  0   0 390   2]
 [  0   0   0  29]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3635    0    0    0]
 [ 854  109    0    0]
 [ 748  129  787    0]]
```

## Synchronous / 19×19 / D128 / edge distance 3–4

Stone accuracy 65.96%; macro 58.71%; overcounts 1805; undercounts 12620.

```
[[10934   739   454    65]
 [ 5182  1729   500     2]
 [ 3007   248  2940    45]
 [ 3007   381   795 12353]]
```

Overcounts only:
```
[[  0 739 454  65]
 [  0   0 500   2]
 [  0   0   0  45]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5182    0    0    0]
 [3007  248    0    0]
 [3007  381  795    0]]
```

## Synchronous / 19×19 / D128 / edge distance 5–8

Stone accuracy 66.94%; macro 58.69%; overcounts 1449; undercounts 10944.

```
[[10294   415   412    90]
 [ 3972  1324   477     8]
 [ 3083   164  2796    47]
 [ 2855   282   588 10681]]
```

Overcounts only:
```
[[  0 415 412  90]
 [  0   0 477   8]
 [  0   0   0  47]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3972    0    0    0]
 [3083  164    0    0]
 [2855  282  588    0]]
```

## Synchronous / 19×19 / D128 / edge distance 9–16

Stone accuracy 53.78%; macro 53.28%; overcounts 7; undercounts 201.

```
[[ 69   2   1   0]
 [ 67  25   4   0]
 [ 64   2  24   0]
 [ 60   4   4 124]]
```

Overcounts only:
```
[[0 2 1 0]
 [0 0 4 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [67  0  0  0]
 [64  2  0  0]
 [60  4  4  0]]
```

## Synchronous / 19×19 / D256 / edge distance 0

Stone accuracy 68.22%; macro 73.31%; overcounts 2105; undercounts 7165.

```
[[ 1073   582   108     1]
 [ 6211 12733  1178    80]
 [    0    16  3401   156]
 [    0     1   937  2695]]
```

Overcounts only:
```
[[   0  582  108    1]
 [   0    0 1178   80]
 [   0    0    0  156]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [6211    0    0    0]
 [   0   16    0    0]
 [   0    1  937    0]]
```

## Synchronous / 19×19 / D256 / edge distance 1

Stone accuracy 49.83%; macro 49.58%; overcounts 1723; undercounts 13099.

```
[[4466  792  216   43]
 [3631 1333  592   12]
 [3434  714 2801   68]
 [3127  434 1759 6122]]
```

Overcounts only:
```
[[  0 792 216  43]
 [  0   0 592  12]
 [  0   0   0  68]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3631    0    0    0]
 [3434  714    0    0]
 [3127  434 1759    0]]
```

## Synchronous / 19×19 / D256 / edge distance 2

Stone accuracy 64.31%; macro 61.89%; overcounts 2115; undercounts 7564.

```
[[6921  854  385  120]
 [3655 1576  653   29]
 [ 778  101 1996   74]
 [ 727  100 2203 6948]]
```

Overcounts only:
```
[[  0 854 385 120]
 [  0   0 653  29]
 [  0   0   0  74]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3655    0    0    0]
 [ 778  101    0    0]
 [ 727  100 2203    0]]
```

## Synchronous / 19×19 / D256 / edge distance 3–4

Stone accuracy 59.17%; macro 53.29%; overcounts 2933; undercounts 14371.

```
[[10483   766   680   263]
 [ 5035  1254  1085    39]
 [ 2947   228  2965   100]
 [ 2964   245  2952 10375]]
```

Overcounts only:
```
[[   0  766  680  263]
 [   0    0 1085   39]
 [   0    0    0  100]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5035    0    0    0]
 [2947  228    0    0]
 [2964  245 2952    0]]
```

## Synchronous / 19×19 / D256 / edge distance 5–8

Stone accuracy 60.62%; macro 53.34%; overcounts 2326; undercounts 12438.

```
[[9975  432  457  347]
 [3916  897  892   76]
 [2983  179 2806  122]
 [2813  153 2394 9046]]
```

Overcounts only:
```
[[  0 432 457 347]
 [  0   0 892  76]
 [  0   0   0 122]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3916    0    0    0]
 [2983  179    0    0]
 [2813  153 2394    0]]
```

## Synchronous / 19×19 / D256 / edge distance 9–16

Stone accuracy 45.11%; macro 45.84%; overcounts 23; undercounts 224.

```
[[ 66   3   3   0]
 [ 67  13  16   0]
 [ 63   3  23   1]
 [ 60   2  29 101]]
```

Overcounts only:
```
[[ 0  3  3  0]
 [ 0  0 16  0]
 [ 0  0  0  1]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [67  0  0  0]
 [63  3  0  0]
 [60  2 29  0]]
```

## Synchronous / 25×25 / D32 / edge distance 0

Stone accuracy 87.24%; macro 95.19%; overcounts 7; undercounts 2665.

```
[[ 1449     0     0     0]
 [ 2661 11312     6     1]
 [    0     4  2339     0]
 [    0     0     0  3165]]
```

Overcounts only:
```
[[0 0 0 0]
 [0 0 6 1]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2661    0    0    0]
 [   0    4    0    0]
 [   0    0    0    0]]
```

## Synchronous / 25×25 / D32 / edge distance 1

Stone accuracy 61.78%; macro 60.86%; overcounts 282; undercounts 7793.

```
[[4329  271    8    0]
 [3362 1301    2    0]
 [1322   54 1818    1]
 [2708  287   60 5603]]
```

Overcounts only:
```
[[  0 271   8   0]
 [  0   0   2   0]
 [  0   0   0   1]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3362    0    0    0]
 [1322   54    0    0]
 [2708  287   60    0]]
```

## Synchronous / 25×25 / D32 / edge distance 2

Stone accuracy 77.27%; macro 72.95%; overcounts 1036; undercounts 3467.

```
[[5505 1015   17    0]
 [2257 1921    4    0]
 [ 630   12 1485    0]
 [ 479   58   31 6401]]
```

Overcounts only:
```
[[   0 1015   17    0]
 [   0    0    4    0]
 [   0    0    0    0]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2257    0    0    0]
 [ 630   12    0    0]
 [ 479   58   31    0]]
```

## Synchronous / 25×25 / D32 / edge distance 3–4

Stone accuracy 73.52%; macro 67.03%; overcounts 583; undercounts 8327.

```
[[ 9801   550    14     0]
 [ 4254  2028     6     0]
 [ 1408    65  2327    13]
 [ 2402   179    19 10582]]
```

Overcounts only:
```
[[  0 550  14   0]
 [  0   0   6   0]
 [  0   0   0  13]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4254    0    0    0]
 [1408   65    0    0]
 [2402  179   19    0]]
```

## Synchronous / 25×25 / D32 / edge distance 5–8

Stone accuracy 75.39%; macro 67.44%; overcounts 457; undercounts 10065.

```
[[13960   436    13     0]
 [ 4942  2159     3     0]
 [ 1890    36  3193     5]
 [ 3039   136    22 12916]]
```

Overcounts only:
```
[[  0 436  13   0]
 [  0   0   3   0]
 [  0   0   0   5]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4942    0    0    0]
 [1890   36    0    0]
 [3039  136   22    0]]
```

## Synchronous / 25×25 / D32 / edge distance 9–16

Stone accuracy 73.76%; macro 65.74%; overcounts 92; undercounts 2998.

```
[[3767   91    0    0]
 [1346  600    1    0]
 [ 635   13  858    0]
 [ 955   42    7 3463]]
```

Overcounts only:
```
[[ 0 91  0  0]
 [ 0  0  1  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1346    0    0    0]
 [ 635   13    0    0]
 [ 955   42    7    0]]
```

## Synchronous / 25×25 / D64 / edge distance 0

Stone accuracy 83.84%; macro 93.61%; overcounts 149; undercounts 3234.

```
[[ 1429    19     1     0]
 [ 3232 10621   127     0]
 [    0     0  2341     2]
 [    0     0     2  3163]]
```

Overcounts only:
```
[[  0  19   1   0]
 [  0   0 127   0]
 [  0   0   0   2]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3232    0    0    0]
 [   0    0    0    0]
 [   0    0    2    0]]
```

## Synchronous / 25×25 / D64 / edge distance 1

Stone accuracy 61.46%; macro 60.53%; overcounts 324; undercounts 7817.

```
[[4323  259   26    0]
 [3376 1258   31    0]
 [1316   58 1813    8]
 [2760  232   75 5591]]
```

Overcounts only:
```
[[  0 259  26   0]
 [  0   0  31   0]
 [  0   0   0   8]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3376    0    0    0]
 [1316   58    0    0]
 [2760  232   75    0]]
```

## Synchronous / 25×25 / D64 / edge distance 2

Stone accuracy 76.66%; macro 71.96%; overcounts 949; undercounts 3676.

```
[[5671  776   90    0]
 [2419 1683   80    0]
 [ 633    9 1482    3]
 [ 474   58   83 6354]]
```

Overcounts only:
```
[[  0 776  90   0]
 [  0   0  80   0]
 [  0   0   0   3]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2419    0    0    0]
 [ 633    9    0    0]
 [ 474   58   83    0]]
```

## Synchronous / 25×25 / D64 / edge distance 3–4

Stone accuracy 72.75%; macro 66.09%; overcounts 701; undercounts 8468.

```
[[ 9781   483   101     0]
 [ 4370  1823    95     0]
 [ 1405    61  2325    22]
 [ 2416   171    45 10550]]
```

Overcounts only:
```
[[  0 483 101   0]
 [  0   0  95   0]
 [  0   0   0  22]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4370    0    0    0]
 [1405   61    0    0]
 [2416  171   45    0]]
```

## Synchronous / 25×25 / D64 / edge distance 5–8

Stone accuracy 75.02%; macro 66.99%; overcounts 578; undercounts 10099.

```
[[13912   323   173     1]
 [ 4959  2089    56     0]
 [ 1882    43  3174    25]
 [ 3100    82    33 12898]]
```

Overcounts only:
```
[[  0 323 173   1]
 [  0   0  56   0]
 [  0   0   0  25]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4959    0    0    0]
 [1882   43    0    0]
 [3100   82   33    0]]
```

## Synchronous / 25×25 / D64 / edge distance 9–16

Stone accuracy 73.23%; macro 65.14%; overcounts 145; undercounts 3008.

```
[[3738   69   51    0]
 [1351  574   22    0]
 [ 634   14  855    3]
 [ 980   17   12 3458]]
```

Overcounts only:
```
[[ 0 69 51  0]
 [ 0  0 22  0]
 [ 0  0  0  3]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1351    0    0    0]
 [ 634   14    0    0]
 [ 980   17   12    0]]
```

## Synchronous / 25×25 / D128 / edge distance 0

Stone accuracy 74.28%; macro 84.16%; overcounts 810; undercounts 4575.

```
[[1156  287    6    0]
 [4340 9148  488    4]
 [   0    9 2309   25]
 [   0    0  226 2939]]
```

Overcounts only:
```
[[  0 287   6   0]
 [  0   0 488   4]
 [  0   0   0  25]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4340    0    0    0]
 [   0    9    0    0]
 [   0    0  226    0]]
```

## Synchronous / 25×25 / D128 / edge distance 1

Stone accuracy 58.14%; macro 57.50%; overcounts 804; undercounts 8039.

```
[[4031  542   33    2]
 [3297 1162  206    0]
 [1283   82 1809   21]
 [2681  295  401 5281]]
```

Overcounts only:
```
[[  0 542  33   2]
 [  0   0 206   0]
 [  0   0   0  21]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3297    0    0    0]
 [1283   82    0    0]
 [2681  295  401    0]]
```

## Synchronous / 25×25 / D128 / edge distance 2

Stone accuracy 71.81%; macro 67.16%; overcounts 1270; undercounts 4315.

```
[[5669  764   99    5]
 [2590 1219  373    0]
 [ 628   18 1452   29]
 [ 469   46  564 5890]]
```

Overcounts only:
```
[[  0 764  99   5]
 [  0   0 373   0]
 [  0   0   0  29]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2590    0    0    0]
 [ 628   18    0    0]
 [ 469   46  564    0]]
```

## Synchronous / 25×25 / D128 / edge distance 3–4

Stone accuracy 69.19%; macro 62.71%; overcounts 1414; undercounts 8952.

```
[[ 9552   555   237    21]
 [ 4324  1438   523     3]
 [ 1351   103  2284    75]
 [ 2377   197   600 10008]]
```

Overcounts only:
```
[[  0 555 237  21]
 [  0   0 523   3]
 [  0   0   0  75]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4324    0    0    0]
 [1351  103    0    0]
 [2377  197  600    0]]
```

## Synchronous / 25×25 / D128 / edge distance 5–8

Stone accuracy 71.43%; macro 63.51%; overcounts 1704; undercounts 10509.

```
[[13360   549   436    64]
 [ 4862  1686   549     7]
 [ 1864    48  3113    99]
 [ 3116    66   553 12378]]
```

Overcounts only:
```
[[  0 549 436  64]
 [  0   0 549   7]
 [  0   0   0  99]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4862    0    0    0]
 [1864   48    0    0]
 [3116   66  553    0]]
```

## Synchronous / 25×25 / D128 / edge distance 9–16

Stone accuracy 69.82%; macro 61.99%; overcounts 399; undercounts 3156.

```
[[3614  125   98   21]
 [1330  469  148    0]
 [ 631   16  852    7]
 [ 987   11  181 3288]]
```

Overcounts only:
```
[[  0 125  98  21]
 [  0   0 148   0]
 [  0   0   0   7]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1330    0    0    0]
 [ 631   16    0    0]
 [ 987   11  181    0]]
```

## Synchronous / 25×25 / D256 / edge distance 0

Stone accuracy 65.87%; macro 72.09%; overcounts 1550; undercounts 5595.

```
[[ 843  516   88    2]
 [4769 8339  832   40]
 [   0   25 2246   72]
 [   0    0  801 2364]]
```

Overcounts only:
```
[[  0 516  88   2]
 [  0   0 832  40]
 [  0   0   0  72]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4769    0    0    0]
 [   0   25    0    0]
 [   0    0  801    0]]
```

## Synchronous / 25×25 / D256 / edge distance 1

Stone accuracy 51.45%; macro 52.19%; overcounts 1419; undercounts 8838.

```
[[3735  688  176    9]
 [3149 1008  506    2]
 [1226  142 1789   38]
 [2558  358 1405 4337]]
```

Overcounts only:
```
[[  0 688 176   9]
 [  0   0 506   2]
 [  0   0   0  38]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3149    0    0    0]
 [1226  142    0    0]
 [2558  358 1405    0]]
```

## Synchronous / 25×25 / D256 / edge distance 2

Stone accuracy 63.68%; macro 60.60%; overcounts 1746; undercounts 5451.

```
[[5474  767  279   17]
 [2660  890  593   39]
 [ 546   71 1459   51]
 [ 467   48 1659 4795]]
```

Overcounts only:
```
[[  0 767 279  17]
 [  0   0 593  39]
 [  0   0   0  51]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2660    0    0    0]
 [ 546   71    0    0]
 [ 467   48 1659    0]]
```

## Synchronous / 25×25 / D256 / edge distance 3–4

Stone accuracy 61.92%; macro 56.83%; overcounts 2364; undercounts 10448.

```
[[9242  610  453   60]
 [4197  995 1035   61]
 [1310  109 2249  145]
 [2388  133 2311 8350]]
```

Overcounts only:
```
[[   0  610  453   60]
 [   0    0 1035   61]
 [   0    0    0  145]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4197    0    0    0]
 [1310  109    0    0]
 [2388  133 2311    0]]
```

## Synchronous / 25×25 / D256 / edge distance 5–8

Stone accuracy 64.36%; macro 57.36%; overcounts 2984; undercounts 12251.

```
[[12832   596   844   137]
 [ 4740  1158  1172    34]
 [ 1838    70  3015   201]
 [ 3161    57  2385 10510]]
```

Overcounts only:
```
[[   0  596  844  137]
 [   0    0 1172   34]
 [   0    0    0  201]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4740    0    0    0]
 [1838   70    0    0]
 [3161   57 2385    0]]
```

## Synchronous / 25×25 / D256 / edge distance 9–16

Stone accuracy 62.15%; macro 55.26%; overcounts 768; undercounts 3690.

```
[[3472  120  206   60]
 [1317  295  330    5]
 [ 606   27  826   47]
 [1000   11  729 2727]]
```

Overcounts only:
```
[[  0 120 206  60]
 [  0   0 330   5]
 [  0   0   0  47]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1317    0    0    0]
 [ 606   27    0    0]
 [1000   11  729    0]]
```

## Synchronous / 37×37 / D32 / edge distance 0

Stone accuracy 83.27%; macro 94.09%; overcounts 5; undercounts 2709.

```
[[ 738    0    0    0]
 [2706 8899    2    0]
 [   0    0 1773    3]
 [   1    0    2 2097]]
```

Overcounts only:
```
[[0 0 0 0]
 [0 0 2 0]
 [0 0 0 3]
 [0 0 0 0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2706    0    0    0]
 [   0    0    0    0]
 [   1    0    2    0]]
```

## Synchronous / 37×37 / D32 / edge distance 1

Stone accuracy 48.38%; macro 50.28%; overcounts 303; undercounts 8303.

```
[[2292  296    1    0]
 [2025  918    3    0]
 [2827   45 1223    3]
 [3230  175    1 3632]]
```

Overcounts only:
```
[[  0 296   1   0]
 [  0   0   3   0]
 [  0   0   0   3]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2025    0    0    0]
 [2827   45    0    0]
 [3230  175    1    0]]
```

## Synchronous / 37×37 / D32 / edge distance 17+

Stone accuracy 59.22%; macro 52.97%; overcounts 8; undercounts 452.

```
[[289   8   0   0]
 [101  40   0   0]
 [152  25  57   0]
 [152  22   0 282]]
```

Overcounts only:
```
[[0 8 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [101   0   0   0]
 [152  25   0   0]
 [152  22   0   0]]
```

## Synchronous / 37×37 / D32 / edge distance 2

Stone accuracy 71.54%; macro 69.54%; overcounts 1049; undercounts 3515.

```
[[4689 1036    5    0]
 [2495 1747    3    0]
 [ 471    8  980    5]
 [ 513   18   10 4055]]
```

Overcounts only:
```
[[   0 1036    5    0]
 [   0    0    3    0]
 [   0    0    0    5]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2495    0    0    0]
 [ 471    8    0    0]
 [ 513   18   10    0]]
```

## Synchronous / 37×37 / D32 / edge distance 3–4

Stone accuracy 62.55%; macro 57.38%; overcounts 766; undercounts 10349.

```
[[7451  745    0    0]
 [4225 1828   13    0]
 [2763   41 1814    8]
 [3111  188   21 7474]]
```

Overcounts only:
```
[[  0 745   0   0]
 [  0   0  13   0]
 [  0   0   0   8]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4225    0    0    0]
 [2763   41    0    0]
 [3111  188   21    0]]
```

## Synchronous / 37×37 / D32 / edge distance 5–8

Stone accuracy 64.17%; macro 57.84%; overcounts 955; undercounts 16016.

```
[[13073   937     0     0]
 [ 6351  2522     4     0]
 [ 4441    80  3034    14]
 [ 4808   328     8 11761]]
```

Overcounts only:
```
[[  0 937   0   0]
 [  0   0   4   0]
 [  0   0   0  14]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [6351    0    0    0]
 [4441   80    0    0]
 [4808  328    8    0]]
```

## Synchronous / 37×37 / D32 / edge distance 9–16

Stone accuracy 66.23%; macro 57.67%; overcounts 585; undercounts 14410.

```
[[13658   574     6     0]
 [ 4777  1845     5     0]
 [ 4244   271  2832     0]
 [ 4638   448    32 11067]]
```

Overcounts only:
```
[[  0 574   6   0]
 [  0   0   5   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4777    0    0    0]
 [4244  271    0    0]
 [4638  448   32    0]]
```

## Synchronous / 37×37 / D64 / edge distance 0

Stone accuracy 78.12%; macro 91.63%; overcounts 108; undercounts 3441.

```
[[ 720   18    0    0]
 [3433 8090   81    3]
 [   0    2 1768    6]
 [   1    0    5 2094]]
```

Overcounts only:
```
[[ 0 18  0  0]
 [ 0  0 81  3]
 [ 0  0  0  6]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3433    0    0    0]
 [   0    2    0    0]
 [   1    0    5    0]]
```

## Synchronous / 37×37 / D64 / edge distance 1

Stone accuracy 48.11%; macro 49.97%; overcounts 323; undercounts 8327.

```
[[2294  255   40    0]
 [2039  885   22    0]
 [2821   52 1219    6]
 [3260  145   10 3623]]
```

Overcounts only:
```
[[  0 255  40   0]
 [  0   0  22   0]
 [  0   0   0   6]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2039    0    0    0]
 [2821   52    0    0]
 [3260  145   10    0]]
```

## Synchronous / 37×37 / D64 / edge distance 17+

Stone accuracy 59.31%; macro 52.96%; overcounts 6; undercounts 453.

```
[[291   6   0   0]
 [102  39   0   0]
 [164  13  57   0]
 [164  10   0 282]]
```

Overcounts only:
```
[[0 6 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [102   0   0   0]
 [164  13   0   0]
 [164  10   0   0]]
```

## Synchronous / 37×37 / D64 / edge distance 2

Stone accuracy 70.89%; macro 68.65%; overcounts 936; undercounts 3732.

```
[[4868  779   83    0]
 [2687 1491   67    0]
 [ 471    7  979    7]
 [ 512   17   38 4029]]
```

Overcounts only:
```
[[  0 779  83   0]
 [  0   0  67   0]
 [  0   0   0   7]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2687    0    0    0]
 [ 471    7    0    0]
 [ 512   17   38    0]]
```

## Synchronous / 37×37 / D64 / edge distance 3–4

Stone accuracy 61.82%; macro 56.40%; overcounts 732; undercounts 10601.

```
[[7553  520  123    0]
 [4451 1545   70    0]
 [2754   50 1803   19]
 [3079  212   55 7448]]
```

Overcounts only:
```
[[  0 520 123   0]
 [  0   0  70   0]
 [  0   0   0  19]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4451    0    0    0]
 [2754   50    0    0]
 [3079  212   55    0]]
```

## Synchronous / 37×37 / D64 / edge distance 5–8

Stone accuracy 63.73%; macro 57.10%; overcounts 857; undercounts 16321.

```
[[13245   555   205     5]
 [ 6632  2185    60     0]
 [ 4501    24  3012    32]
 [ 4983   149    32 11741]]
```

Overcounts only:
```
[[  0 555 205   5]
 [  0   0  60   0]
 [  0   0   0  32]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [6632    0    0    0]
 [4501   24    0    0]
 [4983  149   32    0]]
```

## Synchronous / 37×37 / D64 / edge distance 9–16

Stone accuracy 66.40%; macro 57.48%; overcounts 348; undercounts 14571.

```
[[13931   196    94    17]
 [ 4907  1684    36     0]
 [ 4408   108  2826     5]
 [ 4897   190    61 11037]]
```

Overcounts only:
```
[[  0 196  94  17]
 [  0   0  36   0]
 [  0   0   0   5]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4907    0    0    0]
 [4408  108    0    0]
 [4897  190   61    0]]
```

## Synchronous / 37×37 / D128 / edge distance 0

Stone accuracy 69.96%; macro 82.93%; overcounts 420; undercounts 4452.

```
[[ 590  146    2    0]
 [4309 7066  215   17]
 [   0    7 1729   40]
 [   1    0  135 1964]]
```

Overcounts only:
```
[[  0 146   2   0]
 [  0   0 215  17]
 [  0   0   0  40]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4309    0    0    0]
 [   0    7    0    0]
 [   1    0  135    0]]
```

## Synchronous / 37×37 / D128 / edge distance 1

Stone accuracy 46.12%; macro 47.85%; overcounts 535; undercounts 8447.

```
[[2207  304   60   18]
 [2000  813  132    1]
 [2781  100 1197   20]
 [3187  212  167 3472]]
```

Overcounts only:
```
[[  0 304  60  18]
 [  0   0 132   1]
 [  0   0   0  20]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2000    0    0    0]
 [2781  100    0    0]
 [3187  212  167    0]]
```

## Synchronous / 37×37 / D128 / edge distance 17+

Stone accuracy 57.18%; macro 50.85%; overcounts 22; undercounts 461.

```
[[279  16   2   0]
 [102  35   4   0]
 [156  20  58   0]
 [167   4  12 273]]
```

Overcounts only:
```
[[ 0 16  2  0]
 [ 0  0  4  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [102   0   0   0]
 [156  20   0   0]
 [167   4  12   0]]
```

## Synchronous / 37×37 / D128 / edge distance 2

Stone accuracy 67.07%; macro 64.86%; overcounts 1059; undercounts 4222.

```
[[4961  578  164   27]
 [2914 1057  266    8]
 [ 467   16  965   16]
 [ 505   18  302 3771]]
```

Overcounts only:
```
[[  0 578 164  27]
 [  0   0 266   8]
 [  0   0   0  16]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2914    0    0    0]
 [ 467   16    0    0]
 [ 505   18  302    0]]
```

## Synchronous / 37×37 / D128 / edge distance 3–4

Stone accuracy 58.70%; macro 53.39%; overcounts 1280; undercounts 10980.

```
[[7389  515  237   55]
 [4453 1185  428    0]
 [2718   89 1774   45]
 [3021  267  432 7074]]
```

Overcounts only:
```
[[  0 515 237  55]
 [  0   0 428   0]
 [  0   0   0  45]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4453    0    0    0]
 [2718   89    0    0]
 [3021  267  432    0]]
```

## Synchronous / 37×37 / D128 / edge distance 5–8

Stone accuracy 60.85%; macro 54.25%; overcounts 1716; undercounts 16825.

```
[[12958   552   380   120]
 [ 6613  1670   593     1]
 [ 4485    36  2978    70]
 [ 5004   118   569 11214]]
```

Overcounts only:
```
[[  0 552 380 120]
 [  0   0 593   1]
 [  0   0   0  70]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [6613    0    0    0]
 [4485   36    0    0]
 [5004  118  569    0]]
```

## Synchronous / 37×37 / D128 / edge distance 9–16

Stone accuracy 63.64%; macro 54.71%; overcounts 1100; undercounts 15042.

```
[[13533   394   251    60]
 [ 4924  1357   346     0]
 [ 4322   186  2790    49]
 [ 4911   114   585 10575]]
```

Overcounts only:
```
[[  0 394 251  60]
 [  0   0 346   0]
 [  0   0   0  49]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4924    0    0    0]
 [4322  186    0    0]
 [4911  114  585    0]]
```

## Synchronous / 37×37 / D256 / edge distance 0

Stone accuracy 61.96%; macro 70.93%; overcounts 831; undercounts 5339.

```
[[ 437  249   52    0]
 [4791 6359  402   55]
 [   0    9 1694   73]
 [   1    0  538 1561]]
```

Overcounts only:
```
[[  0 249  52   0]
 [  0   0 402  55]
 [  0   0   0  73]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4791    0    0    0]
 [   0    9    0    0]
 [   1    0  538    0]]
```

## Synchronous / 37×37 / D256 / edge distance 1

Stone accuracy 41.07%; macro 43.38%; overcounts 892; undercounts 8932.

```
[[2065  391  101   32]
 [1923  707  313    3]
 [2680  201 1165   52]
 [3079  314  735 2910]]
```

Overcounts only:
```
[[  0 391 101  32]
 [  0   0 313   3]
 [  0   0   0  52]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1923    0    0    0]
 [2680  201    0    0]
 [3079  314  735    0]]
```

## Synchronous / 37×37 / D256 / edge distance 17+

Stone accuracy 51.51%; macro 46.34%; overcounts 48; undercounts 499.

```
[[264  11  14   8]
 [102  27  11   1]
 [148  17  66   3]
 [168   4  60 224]]
```

Overcounts only:
```
[[ 0 11 14  8]
 [ 0  0 11  1]
 [ 0  0  0  3]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [102   0   0   0]
 [148  17   0   0]
 [168   4  60   0]]
```

## Synchronous / 37×37 / D256 / edge distance 2

Stone accuracy 60.42%; macro 58.79%; overcounts 1367; undercounts 4980.

```
[[4855  595  212   68]
 [2997  798  428   22]
 [ 466   14  942   42]
 [ 500   26  977 3093]]
```

Overcounts only:
```
[[  0 595 212  68]
 [  0   0 428  22]
 [  0   0   0  42]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2997    0    0    0]
 [ 466   14    0    0]
 [ 500   26  977    0]]
```

## Synchronous / 37×37 / D256 / edge distance 3–4

Stone accuracy 52.07%; macro 47.90%; overcounts 1961; undercounts 12265.

```
[[7149  510  356  181]
 [4410  831  810   15]
 [2702  102 1733   89]
 [3040  279 1732 5743]]
```

Overcounts only:
```
[[  0 510 356 181]
 [  0   0 810  15]
 [  0   0   0  89]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4410    0    0    0]
 [2702  102    0    0]
 [3040  279 1732    0]]
```

## Synchronous / 37×37 / D256 / edge distance 5–8

Stone accuracy 54.48%; macro 48.68%; overcounts 2980; undercounts 18579.

```
[[12493   511   586   420]
 [ 6499  1052  1297    29]
 [ 4464    61  2907   137]
 [ 5047   103  2405  9350]]
```

Overcounts only:
```
[[   0  511  586  420]
 [   0    0 1297   29]
 [   0    0    0  137]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [6499    0    0    0]
 [4464   61    0    0]
 [5047  103 2405    0]]
```

## Synchronous / 37×37 / D256 / edge distance 9–16

Stone accuracy 57.15%; macro 49.05%; overcounts 2329; undercounts 16694.

```
[[12858   389   583   408]
 [ 4904   909   779    35]
 [ 4289   168  2755   135]
 [ 4956   101  2276  8852]]
```

Overcounts only:
```
[[  0 389 583 408]
 [  0   0 779  35]
 [  0   0   0 135]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4904    0    0    0]
 [4289  168    0    0]
 [4956  101 2276    0]]
```

## Synchronous + algorithm hints / 13×13 / D32 / edge distance 0

Stone accuracy 99.44%; macro 99.76%; overcounts 9; undercounts 60.

```
[[ 830    0    0    0]
 [  57 8214    9    0]
 [   0    0 1606    0]
 [   0    0    3 1649]]
```

Overcounts only:
```
[[0 0 0 0]
 [0 0 9 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [57  0  0  0]
 [ 0  0  0  0]
 [ 0  0  3  0]]
```

## Synchronous + algorithm hints / 13×13 / D32 / edge distance 1

Stone accuracy 83.85%; macro 83.11%; overcounts 337; undercounts 1685.

```
[[1503   44    0    0]
 [ 595 1886   55    1]
 [  44  461 1805  237]
 [   4   56  525 5307]]
```

Overcounts only:
```
[[  0  44   0   0]
 [  0   0  55   1]
 [  0   0   0 237]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [595   0   0   0]
 [ 44 461   0   0]
 [  4  56 525   0]]
```

## Synchronous + algorithm hints / 13×13 / D32 / edge distance 2

Stone accuracy 87.27%; macro 85.14%; overcounts 242; undercounts 1095.

```
[[2668  105    0    0]
 [ 703 1646   86    0]
 [  58   86  933   51]
 [  11   79  158 3917]]
```

Overcounts only:
```
[[  0 105   0   0]
 [  0   0  86   0]
 [  0   0   0  51]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [703   0   0   0]
 [ 58  86   0   0]
 [ 11  79 158   0]]
```

## Synchronous + algorithm hints / 13×13 / D32 / edge distance 3–4

Stone accuracy 85.38%; macro 80.84%; overcounts 272; undercounts 1570.

```
[[2711   70    2    0]
 [ 755 1365   34    0]
 [  40  375 1326  166]
 [  15   54  331 5351]]
```

Overcounts only:
```
[[  0  70   2   0]
 [  0   0  34   0]
 [  0   0   0 166]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [755   0   0   0]
 [ 40 375   0   0]
 [ 15  54 331   0]]
```

## Synchronous + algorithm hints / 13×13 / D32 / edge distance 5–8

Stone accuracy 83.05%; macro 78.38%; overcounts 71; undercounts 391.

```
[[ 546   13    0    1]
 [ 179  274    9    0]
 [  18  100  299   48]
 [   4   10   80 1144]]
```

Overcounts only:
```
[[ 0 13  0  1]
 [ 0  0  9  0]
 [ 0  0  0 48]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [179   0   0   0]
 [ 18 100   0   0]
 [  4  10  80   0]]
```

## Synchronous + algorithm hints / 13×13 / D64 / edge distance 0

Stone accuracy 99.18%; macro 99.64%; overcounts 11; undercounts 91.

```
[[ 830    0    0    0]
 [  87 8182   11    0]
 [   0    1 1605    0]
 [   0    0    3 1649]]
```

Overcounts only:
```
[[ 0  0  0  0]
 [ 0  0 11  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [87  0  0  0]
 [ 0  1  0  0]
 [ 0  0  3  0]]
```

## Synchronous + algorithm hints / 13×13 / D64 / edge distance 1

Stone accuracy 80.24%; macro 77.02%; overcounts 464; undercounts 2010.

```
[[1517   28    2    0]
 [1017 1459   61    0]
 [  33  685 1456  373]
 [   3   61  211 5617]]
```

Overcounts only:
```
[[  0  28   2   0]
 [  0   0  61   0]
 [  0   0   0 373]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1017    0    0    0]
 [  33  685    0    0]
 [   3   61  211    0]]
```

## Synchronous + algorithm hints / 13×13 / D64 / edge distance 2

Stone accuracy 85.92%; macro 82.97%; overcounts 204; undercounts 1275.

```
[[2693   62    9    9]
 [ 884 1508   43    0]
 [  61  103  883   81]
 [   6   77  144 3938]]
```

Overcounts only:
```
[[ 0 62  9  9]
 [ 0  0 43  0]
 [ 0  0  0 81]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [884   0   0   0]
 [ 61 103   0   0]
 [  6  77 144   0]]
```

## Synchronous + algorithm hints / 13×13 / D64 / edge distance 3–4

Stone accuracy 83.48%; macro 76.76%; overcounts 357; undercounts 1724.

```
[[2715   67    0    1]
 [ 990 1124   40    0]
 [  40  441 1177  249]
 [  11   50  192 5498]]
```

Overcounts only:
```
[[  0  67   0   1]
 [  0   0  40   0]
 [  0   0   0 249]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [990   0   0   0]
 [ 40 441   0   0]
 [ 11  50 192   0]]
```

## Synchronous + algorithm hints / 13×13 / D64 / edge distance 5–8

Stone accuracy 82.28%; macro 75.38%; overcounts 87; undercounts 396.

```
[[ 546   12    2    0]
 [ 233  220    9    0]
 [  14  110  277   64]
 [   0    0   39 1199]]
```

Overcounts only:
```
[[ 0 12  2  0]
 [ 0  0  9  0]
 [ 0  0  0 64]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [233   0   0   0]
 [ 14 110   0   0]
 [  0   0  39   0]]
```

## Synchronous + algorithm hints / 13×13 / D128 / edge distance 0

Stone accuracy 95.85%; macro 98.03%; overcounts 103; undercounts 410.

```
[[ 819   11    0    0]
 [ 400 7788   92    0]
 [   0    6 1600    0]
 [   0    0    4 1648]]
```

Overcounts only:
```
[[ 0 11  0  0]
 [ 0  0 92  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [400   0   0   0]
 [  0   6   0   0]
 [  0   0   4   0]]
```

## Synchronous + algorithm hints / 13×13 / D128 / edge distance 1

Stone accuracy 78.54%; macro 74.83%; overcounts 483; undercounts 2204.

```
[[1504   41    1    1]
 [1141 1334   62    0]
 [  66  723 1380  378]
 [   4   73  197 5618]]
```

Overcounts only:
```
[[  0  41   1   1]
 [  0   0  62   0]
 [  0   0   0 378]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1141    0    0    0]
 [  66  723    0    0]
 [   4   73  197    0]]
```

## Synchronous + algorithm hints / 13×13 / D128 / edge distance 2

Stone accuracy 84.85%; macro 81.72%; overcounts 227; undercounts 1364.

```
[[2667   88    8   10]
 [ 948 1449   38    0]
 [  64  113  868   83]
 [   6   70  163 3926]]
```

Overcounts only:
```
[[ 0 88  8 10]
 [ 0  0 38  0]
 [ 0  0  0 83]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [948   0   0   0]
 [ 64 113   0   0]
 [  6  70 163   0]]
```

## Synchronous + algorithm hints / 13×13 / D128 / edge distance 3–4

Stone accuracy 82.29%; macro 75.00%; overcounts 396; undercounts 1835.

```
[[2700   67   14    2]
 [1061 1047   46    0]
 [  93  425 1122  267]
 [   4   55  197 5495]]
```

Overcounts only:
```
[[  0  67  14   2]
 [  0   0  46   0]
 [  0   0   0 267]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1061    0    0    0]
 [  93  425    0    0]
 [   4   55  197    0]]
```

## Synchronous + algorithm hints / 13×13 / D128 / edge distance 5–8

Stone accuracy 80.07%; macro 72.41%; overcounts 110; undercounts 433.

```
[[ 532   26    2    0]
 [ 254  195   13    0]
 [  64   72  260   69]
 [   0    2   41 1195]]
```

Overcounts only:
```
[[ 0 26  2  0]
 [ 0  0 13  0]
 [ 0  0  0 69]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [254   0   0   0]
 [ 64  72   0   0]
 [  0   2  41   0]]
```

## Synchronous + algorithm hints / 13×13 / D256 / edge distance 0

Stone accuracy 89.48%; macro 93.92%; overcounts 258; undercounts 1043.

```
[[ 773   57    0    0]
 [ 994 7085  201    0]
 [   0   25 1581    0]
 [   0    0   24 1628]]
```

Overcounts only:
```
[[  0  57   0   0]
 [  0   0 201   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [994   0   0   0]
 [  0  25   0   0]
 [  0   0  24   0]]
```

## Synchronous + algorithm hints / 13×13 / D256 / edge distance 1

Stone accuracy 76.93%; macro 72.73%; overcounts 522; undercounts 2367.

```
[[1456   89    1    1]
 [1209 1261   67    0]
 [  87  764 1332  364]
 [   7  112  188 5585]]
```

Overcounts only:
```
[[  0  89   1   1]
 [  0   0  67   0]
 [  0   0   0 364]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1209    0    0    0]
 [  87  764    0    0]
 [   7  112  188    0]]
```

## Synchronous + algorithm hints / 13×13 / D256 / edge distance 2

Stone accuracy 82.82%; macro 79.53%; overcounts 297; undercounts 1507.

```
[[2602  152    9   10]
 [1021 1370   44    0]
 [  58  144  844   82]
 [  12   67  205 3881]]
```

Overcounts only:
```
[[  0 152   9  10]
 [  0   0  44   0]
 [  0   0   0  82]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1021    0    0    0]
 [  58  144    0    0]
 [  12   67  205    0]]
```

## Synchronous + algorithm hints / 13×13 / D256 / edge distance 3–4

Stone accuracy 79.98%; macro 72.06%; overcounts 498; undercounts 2024.

```
[[2607  155   21    0]
 [1156  944   54    0]
 [ 156  418 1065  268]
 [   0   73  221 5457]]
```

Overcounts only:
```
[[  0 155  21   0]
 [  0   0  54   0]
 [  0   0   0 268]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1156    0    0    0]
 [ 156  418    0    0]
 [   0   73  221    0]]
```

## Synchronous + algorithm hints / 13×13 / D256 / edge distance 5–8

Stone accuracy 77.76%; macro 69.93%; overcounts 133; undercounts 473.

```
[[ 513   40    6    1]
 [ 263  182   17    0]
 [  80   65  251   69]
 [   0    7   58 1173]]
```

Overcounts only:
```
[[ 0 40  6  1]
 [ 0  0 17  0]
 [ 0  0  0 69]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [263   0   0   0]
 [ 80  65   0   0]
 [  0   7  58   0]]
```

## Synchronous + algorithm hints / 19×19 / D32 / edge distance 0

Stone accuracy 93.05%; macro 97.44%; overcounts 288; undercounts 388.

```
[[ 588    0    0    0]
 [ 387 6061  253   33]
 [   0    0 1189    2]
 [   0    0    1 1210]]
```

Overcounts only:
```
[[  0   0   0   0]
 [  0   0 253  33]
 [  0   0   0   2]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [387   0   0   0]
 [  0   0   0   0]
 [  0   0   1   0]]
```

## Synchronous + algorithm hints / 19×19 / D32 / edge distance 1

Stone accuracy 67.24%; macro 64.87%; overcounts 809; undercounts 2417.

```
[[1337  424   58   20]
 [ 614 1052  119   71]
 [ 464  601 1157  117]
 [ 100  205  433 3076]]
```

Overcounts only:
```
[[  0 424  58  20]
 [  0   0 119  71]
 [  0   0   0 117]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [614   0   0   0]
 [464 601   0   0]
 [100 205 433   0]]
```

## Synchronous + algorithm hints / 19×19 / D32 / edge distance 2

Stone accuracy 76.92%; macro 73.52%; overcounts 975; undercounts 1111.

```
[[2109  563   78   10]
 [ 703  974  234   60]
 [ 126  103  724   30]
 [  39   59   81 3147]]
```

Overcounts only:
```
[[  0 563  78  10]
 [  0   0 234  60]
 [  0   0   0  30]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [703   0   0   0]
 [126 103   0   0]
 [ 39  59  81   0]]
```

## Synchronous + algorithm hints / 19×19 / D32 / edge distance 3–4

Stone accuracy 73.56%; macro 67.97%; overcounts 1186; undercounts 2549.

```
[[3209  718  128    9]
 [1025 1201  172   73]
 [ 331  467 1196   86]
 [ 117  249  360 4786]]
```

Overcounts only:
```
[[  0 718 128   9]
 [  0   0 172  73]
 [  0   0   0  86]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1025    0    0    0]
 [ 331  467    0    0]
 [ 117  249  360    0]]
```

## Synchronous + algorithm hints / 19×19 / D32 / edge distance 5–8

Stone accuracy 73.78%; macro 67.60%; overcounts 1013; undercounts 2264.

```
[[2972  603  157    5]
 [ 794  963  125   45]
 [ 476  391 1085   78]
 [ 111  257  235 4199]]
```

Overcounts only:
```
[[  0 603 157   5]
 [  0   0 125  45]
 [  0   0   0  78]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [794   0   0   0]
 [476 391   0   0]
 [111 257 235   0]]
```

## Synchronous + algorithm hints / 19×19 / D32 / edge distance 9–16

Stone accuracy 66.67%; macro 63.15%; overcounts 8; undercounts 42.

```
[[20  4  0  0]
 [13 17  1  1]
 [10  8 10  2]
 [ 3  1  7 53]]
```

Overcounts only:
```
[[0 4 0 0]
 [0 0 1 1]
 [0 0 0 2]
 [0 0 0 0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [13  0  0  0]
 [10  8  0  0]
 [ 3  1  7  0]]
```

## Synchronous + algorithm hints / 19×19 / D64 / edge distance 0

Stone accuracy 90.80%; macro 96.53%; overcounts 283; undercounts 612.

```
[[ 586    1    1    0]
 [ 610 5845  233   46]
 [   0    0 1189    2]
 [   0    0    2 1209]]
```

Overcounts only:
```
[[  0   1   1   0]
 [  0   0 233  46]
 [  0   0   0   2]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [610   0   0   0]
 [  0   0   0   0]
 [  0   0   2   0]]
```

## Synchronous + algorithm hints / 19×19 / D64 / edge distance 1

Stone accuracy 70.87%; macro 67.29%; overcounts 766; undercounts 2103.

```
[[1539  244   50    6]
 [ 726  917  119   94]
 [ 503  526 1057  253]
 [  43  105  200 3466]]
```

Overcounts only:
```
[[  0 244  50   6]
 [  0   0 119  94]
 [  0   0   0 253]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [726   0   0   0]
 [503 526   0   0]
 [ 43 105 200   0]]
```

## Synchronous + algorithm hints / 19×19 / D64 / edge distance 2

Stone accuracy 77.96%; macro 73.54%; overcounts 818; undercounts 1174.

```
[[2244  414   95    7]
 [ 800  929  162   80]
 [ 113  123  687   60]
 [  31   47   60 3188]]
```

Overcounts only:
```
[[  0 414  95   7]
 [  0   0 162  80]
 [  0   0   0  60]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [800   0   0   0]
 [113 123   0   0]
 [ 31  47  60   0]]
```

## Synchronous + algorithm hints / 19×19 / D64 / edge distance 3–4

Stone accuracy 74.51%; macro 66.74%; overcounts 1135; undercounts 2466.

```
[[3428  469  145   22]
 [1245  938  189   99]
 [ 431  339 1099  211]
 [  90  149  212 5061]]
```

Overcounts only:
```
[[  0 469 145  22]
 [  0   0 189  99]
 [  0   0   0 211]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1245    0    0    0]
 [ 431  339    0    0]
 [  90  149  212    0]]
```

## Synchronous + algorithm hints / 19×19 / D64 / edge distance 5–8

Stone accuracy 75.59%; macro 67.58%; overcounts 993; undercounts 2057.

```
[[3143  395  178   21]
 [ 907  845  101   74]
 [ 489  308 1009  224]
 [  49  124  180 4449]]
```

Overcounts only:
```
[[  0 395 178  21]
 [  0   0 101  74]
 [  0   0   0 224]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [907   0   0   0]
 [489 308   0   0]
 [ 49 124 180   0]]
```

## Synchronous + algorithm hints / 19×19 / D64 / edge distance 9–16

Stone accuracy 67.33%; macro 63.05%; overcounts 9; undercounts 40.

```
[[23  1  0  0]
 [17 13  0  2]
 [10  6  8  6]
 [ 0  2  5 57]]
```

Overcounts only:
```
[[0 1 0 0]
 [0 0 0 2]
 [0 0 0 6]
 [0 0 0 0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [17  0  0  0]
 [10  6  0  0]
 [ 0  2  5  0]]
```

## Synchronous + algorithm hints / 19×19 / D128 / edge distance 0

Stone accuracy 84.33%; macro 93.87%; overcounts 294; undercounts 1230.

```
[[ 579    6    2    1]
 [1225 5226  209   74]
 [   0    2 1187    2]
 [   0    0    3 1208]]
```

Overcounts only:
```
[[  0   6   2   1]
 [  0   0 209  74]
 [  0   0   0   2]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1225    0    0    0]
 [   0    2    0    0]
 [   0    0    3    0]]
```

## Synchronous + algorithm hints / 19×19 / D128 / edge distance 1

Stone accuracy 70.55%; macro 66.66%; overcounts 753; undercounts 2147.

```
[[1568  227   39    5]
 [ 794  850   94  118]
 [ 582  470 1017  270]
 [  48  121  132 3513]]
```

Overcounts only:
```
[[  0 227  39   5]
 [  0   0  94 118]
 [  0   0   0 270]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [794   0   0   0]
 [582 470   0   0]
 [ 48 121 132   0]]
```

## Synchronous + algorithm hints / 19×19 / D128 / edge distance 2

Stone accuracy 78.30%; macro 73.55%; overcounts 707; undercounts 1255.

```
[[2324  360   68    8]
 [ 877  887  127   80]
 [ 127  112  680   64]
 [  33   48   58 3187]]
```

Overcounts only:
```
[[  0 360  68   8]
 [  0   0 127  80]
 [  0   0   0  64]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [877   0   0   0]
 [127 112   0   0]
 [ 33  48  58   0]]
```

## Synchronous + algorithm hints / 19×19 / D128 / edge distance 3–4

Stone accuracy 74.39%; macro 65.74%; overcounts 1095; undercounts 2523.

```
[[3512  414  118   20]
 [1346  836  155  134]
 [ 510  283 1033  254]
 [  91  161  132 5128]]
```

Overcounts only:
```
[[  0 414 118  20]
 [  0   0 155 134]
 [  0   0   0 254]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1346    0    0    0]
 [ 510  283    0    0]
 [  91  161  132    0]]
```

## Synchronous + algorithm hints / 19×19 / D128 / edge distance 5–8

Stone accuracy 75.46%; macro 66.72%; overcounts 962; undercounts 2105.

```
[[3200  376  139   22]
 [ 989  752   90   96]
 [ 582  218  991  239]
 [  54  150  112 4486]]
```

Overcounts only:
```
[[  0 376 139  22]
 [  0   0  90  96]
 [  0   0   0 239]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [989   0   0   0]
 [582 218   0   0]
 [ 54 150 112   0]]
```

## Synchronous + algorithm hints / 19×19 / D128 / edge distance 9–16

Stone accuracy 66.00%; macro 61.93%; overcounts 9; undercounts 42.

```
[[23  1  0  0]
 [18 11  1  2]
 [12  4  9  5]
 [ 0  2  6 56]]
```

Overcounts only:
```
[[0 1 0 0]
 [0 0 1 2]
 [0 0 0 5]
 [0 0 0 0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [18  0  0  0]
 [12  4  0  0]
 [ 0  2  6  0]]
```

## Synchronous + algorithm hints / 19×19 / D256 / edge distance 0

Stone accuracy 78.32%; macro 89.96%; overcounts 336; undercounts 1772.

```
[[ 550   36    2    0]
 [1731 4707  219   77]
 [   0   25 1164    2]
 [   0    0   16 1195]]
```

Overcounts only:
```
[[  0  36   2   0]
 [  0   0 219  77]
 [  0   0   0   2]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1731    0    0    0]
 [   0   25    0    0]
 [   0    0   16    0]]
```

## Synchronous + algorithm hints / 19×19 / D256 / edge distance 1

Stone accuracy 69.36%; macro 65.29%; overcounts 747; undercounts 2270.

```
[[1577  230   29    3]
 [ 870  766  109  111]
 [ 619  460  995  265]
 [  48  131  142 3493]]
```

Overcounts only:
```
[[  0 230  29   3]
 [  0   0 109 111]
 [  0   0   0 265]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [870   0   0   0]
 [619 460   0   0]
 [ 48 131 142   0]]
```

## Synchronous + algorithm hints / 19×19 / D256 / edge distance 2

Stone accuracy 77.22%; macro 72.32%; overcounts 710; undercounts 1349.

```
[[2316  369   69    6]
 [ 917  848  131   75]
 [ 136  123  664   60]
 [  31   54   88 3153]]
```

Overcounts only:
```
[[  0 369  69   6]
 [  0   0 131  75]
 [  0   0   0  60]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [917   0   0   0]
 [136 123   0   0]
 [ 31  54  88   0]]
```

## Synchronous + algorithm hints / 19×19 / D256 / edge distance 3–4

Stone accuracy 73.41%; macro 64.66%; overcounts 1148; undercounts 2608.

```
[[3460  478  108   18]
 [1374  801  163  133]
 [ 555  267 1010  248]
 [  85  170  157 5100]]
```

Overcounts only:
```
[[  0 478 108  18]
 [  0   0 163 133]
 [  0   0   0 248]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1374    0    0    0]
 [ 555  267    0    0]
 [  85  170  157    0]]
```

## Synchronous + algorithm hints / 19×19 / D256 / edge distance 5–8

Stone accuracy 74.06%; macro 65.22%; overcounts 1041; undercounts 2201.

```
[[3138  428  150   21]
 [1006  713   92  116]
 [ 619  214  963  234]
 [  58  153  151 4440]]
```

Overcounts only:
```
[[  0 428 150  21]
 [  0   0  92 116]
 [  0   0   0 234]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1006    0    0    0]
 [ 619  214    0    0]
 [  58  153  151    0]]
```

## Synchronous + algorithm hints / 19×19 / D256 / edge distance 9–16

Stone accuracy 62.67%; macro 58.54%; overcounts 10; undercounts 46.

```
[[22  2  0  0]
 [20  9  1  2]
 [12  4  9  5]
 [ 0  3  7 54]]
```

Overcounts only:
```
[[0 2 0 0]
 [0 0 1 2]
 [0 0 0 5]
 [0 0 0 0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [20  0  0  0]
 [12  4  0  0]
 [ 0  3  7  0]]
```

## Synchronous + algorithm hints / 25×25 / D32 / edge distance 0

Stone accuracy 73.66%; macro 90.14%; overcounts 282; undercounts 1556.

```
[[ 483    0    0    0]
 [1556 2822  239   43]
 [   0    0  781    0]
 [   0    0    0 1055]]
```

Overcounts only:
```
[[  0   0   0   0]
 [  0   0 239  43]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1556    0    0    0]
 [   0    0    0    0]
 [   0    0    0    0]]
```

## Synchronous + algorithm hints / 25×25 / D32 / edge distance 1

Stone accuracy 66.09%; macro 64.90%; overcounts 718; undercounts 1670.

```
[[1106  320   98   12]
 [ 586  770  136   63]
 [ 155  115  706   89]
 [ 344  249  221 2072]]
```

Overcounts only:
```
[[  0 320  98  12]
 [  0   0 136  63]
 [  0   0   0  89]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [586   0   0   0]
 [155 115   0   0]
 [344 249 221   0]]
```

## Synchronous + algorithm hints / 25×25 / D32 / edge distance 2

Stone accuracy 72.29%; macro 69.53%; overcounts 988; undercounts 842.

```
[[1471  380  287   41]
 [ 568  583  174   69]
 [ 123   22  527   37]
 [  47   29   53 2194]]
```

Overcounts only:
```
[[  0 380 287  41]
 [  0   0 174  69]
 [  0   0   0  37]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [568   0   0   0]
 [123  22   0   0]
 [ 47  29  53   0]]
```

## Synchronous + algorithm hints / 25×25 / D32 / edge distance 3–4

Stone accuracy 70.51%; macro 67.32%; overcounts 1368; undercounts 1940.

```
[[2358  650  364   83]
 [ 933  955  153   55]
 [ 196  102  910   63]
 [ 306  201  202 3685]]
```

Overcounts only:
```
[[  0 650 364  83]
 [  0   0 153  55]
 [  0   0   0  63]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [933   0   0   0]
 [196 102   0   0]
 [306 201 202   0]]
```

## Synchronous + algorithm hints / 25×25 / D32 / edge distance 5–8

Stone accuracy 71.15%; macro 67.11%; overcounts 1701; undercounts 2410.

```
[[3398  815  507   83]
 [1118 1044  124   82]
 [ 295  133 1190   90]
 [ 367  322  175 4507]]
```

Overcounts only:
```
[[  0 815 507  83]
 [  0   0 124  82]
 [  0   0   0  90]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1118    0    0    0]
 [ 295  133    0    0]
 [ 367  322  175    0]]
```

## Synchronous + algorithm hints / 25×25 / D32 / edge distance 9–16

Stone accuracy 71.40%; macro 66.47%; overcounts 369; undercounts 754.

```
[[ 999  121  157    9]
 [ 326  255   42   26]
 [ 121   27  340   14]
 [ 193   54   33 1209]]
```

Overcounts only:
```
[[  0 121 157   9]
 [  0   0  42  26]
 [  0   0   0  14]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [326   0   0   0]
 [121  27   0   0]
 [193  54  33   0]]
```

## Synchronous + algorithm hints / 25×25 / D64 / edge distance 0

Stone accuracy 68.75%; macro 88.30%; overcounts 324; undercounts 1857.

```
[[ 483    0    0    0]
 [1857 2479  269   55]
 [   0    0  781    0]
 [   0    0    0 1055]]
```

Overcounts only:
```
[[  0   0   0   0]
 [  0   0 269  55]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1857    0    0    0]
 [   0    0    0    0]
 [   0    0    0    0]]
```

## Synchronous + algorithm hints / 25×25 / D64 / edge distance 1

Stone accuracy 69.13%; macro 66.59%; overcounts 777; undercounts 1397.

```
[[1246  193   81   16]
 [ 581  720   79  175]
 [ 134   50  648  233]
 [ 321  199  112 2254]]
```

Overcounts only:
```
[[  0 193  81  16]
 [  0   0  79 175]
 [  0   0   0 233]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [581   0   0   0]
 [134  50   0   0]
 [321 199 112   0]]
```

## Synchronous + algorithm hints / 25×25 / D64 / edge distance 2

Stone accuracy 72.54%; macro 69.14%; overcounts 1023; undercounts 791.

```
[[1475  281  299  124]
 [ 572  569  140  113]
 [ 120   15  508   66]
 [  34   22   28 2239]]
```

Overcounts only:
```
[[  0 281 299 124]
 [  0   0 140 113]
 [  0   0   0  66]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [572   0   0   0]
 [120  15   0   0]
 [ 34  22  28   0]]
```

## Synchronous + algorithm hints / 25×25 / D64 / edge distance 3–4

Stone accuracy 71.73%; macro 66.79%; overcounts 1464; undercounts 1707.

```
[[2477  449  324  205]
 [ 938  868  135  155]
 [ 182   51  842  196]
 [ 289  156   91 3858]]
```

Overcounts only:
```
[[  0 449 324 205]
 [  0   0 135 155]
 [  0   0   0 196]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [938   0   0   0]
 [182  51   0   0]
 [289 156  91   0]]
```

## Synchronous + algorithm hints / 25×25 / D64 / edge distance 5–8

Stone accuracy 71.19%; macro 65.09%; overcounts 1942; undercounts 2164.

```
[[3433  556  523  291]
 [1183  870  135  180]
 [ 267   97 1087  257]
 [ 308  205  104 4754]]
```

Overcounts only:
```
[[  0 556 523 291]
 [  0   0 135 180]
 [  0   0   0 257]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1183    0    0    0]
 [ 267   97    0    0]
 [ 308  205  104    0]]
```

## Synchronous + algorithm hints / 25×25 / D64 / edge distance 9–16

Stone accuracy 71.42%; macro 64.73%; overcounts 456; undercounts 666.

```
[[ 990   85  112   99]
 [ 318  251    9   71]
 [ 112   20  290   80]
 [ 142   12   62 1273]]
```

Overcounts only:
```
[[  0  85 112  99]
 [  0   0   9  71]
 [  0   0   0  80]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [318   0   0   0]
 [112  20   0   0]
 [142  12  62   0]]
```

## Synchronous + algorithm hints / 25×25 / D128 / edge distance 0

Stone accuracy 67.12%; macro 87.38%; overcounts 356; undercounts 1939.

```
[[ 478    5    0    0]
 [1936 2373  289   62]
 [   0    2  779    0]
 [   0    0    1 1054]]
```

Overcounts only:
```
[[  0   5   0   0]
 [  0   0 289  62]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1936    0    0    0]
 [   0    2    0    0]
 [   0    0    1    0]]
```

## Synchronous + algorithm hints / 25×25 / D128 / edge distance 1

Stone accuracy 68.87%; macro 66.21%; overcounts 695; undercounts 1497.

```
[[1320  127   85    4]
 [ 674  636   69  176]
 [ 143   51  637  234]
 [ 373  181   75 2257]]
```

Overcounts only:
```
[[  0 127  85   4]
 [  0   0  69 176]
 [  0   0   0 234]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [674   0   0   0]
 [143  51   0   0]
 [373 181  75   0]]
```

## Synchronous + algorithm hints / 25×25 / D128 / edge distance 2

Stone accuracy 72.70%; macro 68.88%; overcounts 955; undercounts 848.

```
[[1522  278  255  124]
 [ 625  540  120  109]
 [ 119   21  500   69]
 [  34   24   25 2240]]
```

Overcounts only:
```
[[  0 278 255 124]
 [  0   0 120 109]
 [  0   0   0  69]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [625   0   0   0]
 [119  21   0   0]
 [ 34  24  25   0]]
```

## Synchronous + algorithm hints / 25×25 / D128 / edge distance 3–4

Stone accuracy 71.90%; macro 66.37%; overcounts 1339; undercounts 1813.

```
[[2598  375  279  203]
 [1040  771  126  159]
 [ 180   60  834  197]
 [ 305  145   83 3861]]
```

Overcounts only:
```
[[  0 375 279 203]
 [  0   0 126 159]
 [  0   0   0 197]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1040    0    0    0]
 [ 180   60    0    0]
 [ 305  145   83    0]]
```

## Synchronous + algorithm hints / 25×25 / D128 / edge distance 5–8

Stone accuracy 71.97%; macro 65.33%; overcounts 1784; undercounts 2210.

```
[[3599  515  396  293]
 [1243  806  133  186]
 [ 262   98 1087  261]
 [ 312  205   90 4764]]
```

Overcounts only:
```
[[  0 515 396 293]
 [  0   0 133 186]
 [  0   0   0 261]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1243    0    0    0]
 [ 262   98    0    0]
 [ 312  205   90    0]]
```

## Synchronous + algorithm hints / 25×25 / D128 / edge distance 9–16

Stone accuracy 72.47%; macro 65.24%; overcounts 422; undercounts 659.

```
[[1025   70   96   95]
 [ 321  249    8   71]
 [ 111   26  283   82]
 [ 140   12   49 1288]]
```

Overcounts only:
```
[[ 0 70 96 95]
 [ 0  0  8 71]
 [ 0  0  0 82]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [321   0   0   0]
 [111  26   0   0]
 [140  12  49   0]]
```

## Synchronous + algorithm hints / 25×25 / D256 / edge distance 0

Stone accuracy 65.45%; macro 85.82%; overcounts 387; undercounts 2024.

```
[[ 466   17    0    0]
 [2006 2284  306   64]
 [   0   15  766    0]
 [   0    0    3 1052]]
```

Overcounts only:
```
[[  0  17   0   0]
 [  0   0 306  64]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2006    0    0    0]
 [   0   15    0    0]
 [   0    0    3    0]]
```

## Synchronous + algorithm hints / 25×25 / D256 / edge distance 1

Stone accuracy 67.85%; macro 65.05%; overcounts 700; undercounts 1564.

```
[[1310  159   65    2]
 [ 704  607   70  174]
 [ 147   68  620  230]
 [ 379  192   74 2241]]
```

Overcounts only:
```
[[  0 159  65   2]
 [  0   0  70 174]
 [  0   0   0 230]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [704   0   0   0]
 [147  68   0   0]
 [379 192  74   0]]
```

## Synchronous + algorithm hints / 25×25 / D256 / edge distance 2

Stone accuracy 71.92%; macro 67.72%; overcounts 954; undercounts 901.

```
[[1529  304  231  115]
 [ 643  513  135  103]
 [ 117   43  483   66]
 [  33   31   34 2225]]
```

Overcounts only:
```
[[  0 304 231 115]
 [  0   0 135 103]
 [  0   0   0  66]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [643   0   0   0]
 [117  43   0   0]
 [ 33  31  34   0]]
```

## Synchronous + algorithm hints / 25×25 / D256 / edge distance 3–4

Stone accuracy 71.26%; macro 65.49%; overcounts 1321; undercounts 1902.

```
[[2603  419  243  190]
 [1072  750  118  156]
 [ 178   89  809  195]
 [ 307  149  107 3831]]
```

Overcounts only:
```
[[  0 419 243 190]
 [  0   0 118 156]
 [  0   0   0 195]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1072    0    0    0]
 [ 178   89    0    0]
 [ 307  149  107    0]]
```

## Synchronous + algorithm hints / 25×25 / D256 / edge distance 5–8

Stone accuracy 71.47%; macro 64.71%; overcounts 1788; undercounts 2277.

```
[[3600  553  360  290]
 [1256  789  138  185]
 [ 253  125 1068  262]
 [ 309  198  136 4728]]
```

Overcounts only:
```
[[  0 553 360 290]
 [  0   0 138 185]
 [  0   0   0 262]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1256    0    0    0]
 [ 253  125    0    0]
 [ 309  198  136    0]]
```

## Synchronous + algorithm hints / 25×25 / D256 / edge distance 9–16

Stone accuracy 71.22%; macro 63.50%; overcounts 444; undercounts 686.

```
[[1012   97   88   89]
 [ 327  236   14   72]
 [ 107   46  265   84]
 [ 126   26   54 1283]]
```

Overcounts only:
```
[[ 0 97 88 89]
 [ 0  0 14 72]
 [ 0  0  0 84]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [327   0   0   0]
 [107  46   0   0]
 [126  26  54   0]]
```

## Synchronous + algorithm hints / 37×37 / D32 / edge distance 0

Stone accuracy 63.08%; macro 86.89%; overcounts 117; undercounts 1879.

```
[[ 246    0    0    0]
 [1874 1879   81   35]
 [   0    5  586    1]
 [   0    0    0  700]]
```

Overcounts only:
```
[[ 0  0  0  0]
 [ 0  0 81 35]
 [ 0  0  0  1]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1874    0    0    0]
 [   0    5    0    0]
 [   0    0    0    0]]
```

## Synchronous + algorithm hints / 37×37 / D32 / edge distance 1

Stone accuracy 54.76%; macro 55.13%; overcounts 473; undercounts 2041.

```
[[ 616  149   54   44]
 [ 346  488  113   35]
 [ 483  256  549   78]
 [ 564  202  190 1390]]
```

Overcounts only:
```
[[  0 149  54  44]
 [  0   0 113  35]
 [  0   0   0  78]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [346   0   0   0]
 [483 256   0   0]
 [564 202 190   0]]
```

## Synchronous + algorithm hints / 37×37 / D32 / edge distance 17+

Stone accuracy 55.59%; macro 52.01%; overcounts 49; undercounts 118.

```
[[ 60  14  18   7]
 [ 17  23   4   3]
 [ 47   3  25   3]
 [ 28  14   9 101]]
```

Overcounts only:
```
[[ 0 14 18  7]
 [ 0  0  4  3]
 [ 0  0  0  3]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [17  0  0  0]
 [47  3  0  0]
 [28 14  9  0]]
```

## Synchronous + algorithm hints / 37×37 / D32 / edge distance 2

Stone accuracy 63.99%; macro 64.66%; overcounts 910; undercounts 1015.

```
[[1202  405  201  102]
 [ 785  462  115   53]
 [  56   51  347   34]
 [  71   27   25 1409]]
```

Overcounts only:
```
[[  0 405 201 102]
 [  0   0 115  53]
 [  0   0   0  34]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [785   0   0   0]
 [ 56  51   0   0]
 [ 71  27  25   0]]
```

## Synchronous + algorithm hints / 37×37 / D32 / edge distance 3–4

Stone accuracy 61.00%; macro 57.22%; overcounts 1287; undercounts 2572.

```
[[1823  454  306  149]
 [ 953  797  186   86]
 [ 430  255  751  106]
 [ 468  281  185 2664]]
```

Overcounts only:
```
[[  0 454 306 149]
 [  0   0 186  86]
 [  0   0   0 106]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [953   0   0   0]
 [430 255   0   0]
 [468 281 185   0]]
```

## Synchronous + algorithm hints / 37×37 / D32 / edge distance 5–8

Stone accuracy 58.78%; macro 55.52%; overcounts 2757; undercounts 3751.

```
[[2585 1109  716  260]
 [1263 1259  328  109]
 [ 704  318 1266  235]
 [ 701  454  311 4169]]
```

Overcounts only:
```
[[   0 1109  716  260]
 [   0    0  328  109]
 [   0    0    0  235]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1263    0    0    0]
 [ 704  318    0    0]
 [ 701  454  311    0]]
```

## Synchronous + algorithm hints / 37×37 / D32 / edge distance 9–16

Stone accuracy 58.39%; macro 53.82%; overcounts 2684; undercounts 3474.

```
[[2629  843  849  425]
 [ 998  878  254   79]
 [ 873  222 1120  234]
 [ 626  499  256 4014]]
```

Overcounts only:
```
[[  0 843 849 425]
 [  0   0 254  79]
 [  0   0   0 234]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [998   0   0   0]
 [873 222   0   0]
 [626 499 256   0]]
```

## Synchronous + algorithm hints / 37×37 / D64 / edge distance 0

Stone accuracy 58.09%; macro 85.14%; overcounts 268; undercounts 1998.

```
[[ 246    0    0    0]
 [1993 1609  164  103]
 [   0    5  586    1]
 [   0    0    0  700]]
```

Overcounts only:
```
[[  0   0   0   0]
 [  0   0 164 103]
 [  0   0   0   1]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1993    0    0    0]
 [   0    5    0    0]
 [   0    0    0    0]]
```

## Synchronous + algorithm hints / 37×37 / D64 / edge distance 1

Stone accuracy 54.44%; macro 51.41%; overcounts 886; undercounts 1646.

```
[[ 523  158   60  122]
 [ 302  408   99  173]
 [ 398  228  466  274]
 [ 363  196  159 1628]]
```

Overcounts only:
```
[[  0 158  60 122]
 [  0   0  99 173]
 [  0   0   0 274]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [302   0   0   0]
 [398 228   0   0]
 [363 196 159   0]]
```

## Synchronous + algorithm hints / 37×37 / D64 / edge distance 17+

Stone accuracy 53.46%; macro 46.08%; overcounts 69; undercounts 106.

```
[[ 60   7  12  20]
 [ 19  13   3  12]
 [ 37   7  19  15]
 [ 20   6  17 109]]
```

Overcounts only:
```
[[ 0  7 12 20]
 [ 0  0  3 12]
 [ 0  0  0 15]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [19  0  0  0]
 [37  7  0  0]
 [20  6 17  0]]
```

## Synchronous + algorithm hints / 37×37 / D64 / edge distance 2

Stone accuracy 60.11%; macro 61.13%; overcounts 1272; undercounts 860.

```
[[1038  272  305  295]
 [ 698  394  144  179]
 [  52   29  330   77]
 [  51   17   13 1451]]
```

Overcounts only:
```
[[  0 272 305 295]
 [  0   0 144 179]
 [  0   0   0  77]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [698   0   0   0]
 [ 52  29   0   0]
 [ 51  17  13   0]]
```

## Synchronous + algorithm hints / 37×37 / D64 / edge distance 3–4

Stone accuracy 58.22%; macro 53.09%; overcounts 1852; undercounts 2282.

```
[[1578  318  357  479]
 [ 983  612  138  289]
 [ 424  169  678  271]
 [ 403  147  156 2892]]
```

Overcounts only:
```
[[  0 318 357 479]
 [  0   0 138 289]
 [  0   0   0 271]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [983   0   0   0]
 [424 169   0   0]
 [403 147 156   0]]
```

## Synchronous + algorithm hints / 37×37 / D64 / edge distance 5–8

Stone accuracy 58.47%; macro 53.30%; overcounts 3131; undercounts 3425.

```
[[2607  509  645  909]
 [1400  960  222  377]
 [ 664  274 1116  469]
 [ 611  235  241 4548]]
```

Overcounts only:
```
[[  0 509 645 909]
 [  0   0 222 377]
 [  0   0   0 469]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1400    0    0    0]
 [ 664  274    0    0]
 [ 611  235  241    0]]
```

## Synchronous + algorithm hints / 37×37 / D64 / edge distance 9–16

Stone accuracy 58.82%; macro 53.00%; overcounts 3060; undercounts 3034.

```
[[2566  481  722  977]
 [1021  742  159  287]
 [ 711  214 1090  434]
 [ 505  278  305 4307]]
```

Overcounts only:
```
[[  0 481 722 977]
 [  0   0 159 287]
 [  0   0   0 434]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1021    0    0    0]
 [ 711  214    0    0]
 [ 505  278  305    0]]
```

## Synchronous + algorithm hints / 37×37 / D128 / edge distance 0

Stone accuracy 56.93%; macro 84.45%; overcounts 358; undercounts 1971.

```
[[ 244    2    0    0]
 [1963 1551  202  153]
 [   0    7  584    1]
 [   0    0    1  699]]
```

Overcounts only:
```
[[  0   2   0   0]
 [  0   0 202 153]
 [  0   0   0   1]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1963    0    0    0]
 [   0    7    0    0]
 [   0    0    1    0]]
```

## Synchronous + algorithm hints / 37×37 / D128 / edge distance 1

Stone accuracy 55.21%; macro 52.52%; overcounts 820; undercounts 1669.

```
[[ 580  106   58  119]
 [ 328  391   60  203]
 [ 475  170  447  274]
 [ 409  149  138 1650]]
```

Overcounts only:
```
[[  0 106  58 119]
 [  0   0  60 203]
 [  0   0   0 274]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [328   0   0   0]
 [475 170   0   0]
 [409 149 138   0]]
```

## Synchronous + algorithm hints / 37×37 / D128 / edge distance 17+

Stone accuracy 53.72%; macro 46.07%; overcounts 71; undercounts 103.

```
[[ 58   6  15  20]
 [ 19  13   0  15]
 [ 39   5  19  15]
 [ 19  11  10 112]]
```

Overcounts only:
```
[[ 0  6 15 20]
 [ 0  0  0 15]
 [ 0  0  0 15]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [19  0  0  0]
 [39  5  0  0]
 [19 11 10  0]]
```

## Synchronous + algorithm hints / 37×37 / D128 / edge distance 2

Stone accuracy 59.76%; macro 60.57%; overcounts 1276; undercounts 875.

```
[[1052  271  260  327]
 [ 706  367  146  196]
 [  62   25  325   76]
 [  53   14   15 1450]]
```

Overcounts only:
```
[[  0 271 260 327]
 [  0   0 146 196]
 [  0   0   0  76]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [706   0   0   0]
 [ 62  25   0   0]
 [ 53  14  15   0]]
```

## Synchronous + algorithm hints / 37×37 / D128 / edge distance 3–4

Stone accuracy 58.48%; macro 53.12%; overcounts 1791; undercounts 2317.

```
[[1659  230  327  516]
 [ 993  580  119  330]
 [ 469  143  661  269]
 [ 428  116  168 2886]]
```

Overcounts only:
```
[[  0 230 327 516]
 [  0   0 119 330]
 [  0   0   0 269]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [993   0   0   0]
 [469 143   0   0]
 [428 116 168   0]]
```

## Synchronous + algorithm hints / 37×37 / D128 / edge distance 5–8

Stone accuracy 58.12%; macro 52.68%; overcounts 3147; undercounts 3465.

```
[[2628  503  539 1000]
 [1442  872  182  463]
 [ 721  234 1108  460]
 [ 682  168  218 4567]]
```

Overcounts only:
```
[[   0  503  539 1000]
 [   0    0  182  463]
 [   0    0    0  460]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1442    0    0    0]
 [ 721  234    0    0]
 [ 682  168  218    0]]
```

## Synchronous + algorithm hints / 37×37 / D128 / edge distance 9–16

Stone accuracy 58.80%; macro 52.59%; overcounts 3055; undercounts 3042.

```
[[2594  508  648  996]
 [1041  687   71  410]
 [ 756  190 1081  422]
 [ 529  266  260 4340]]
```

Overcounts only:
```
[[  0 508 648 996]
 [  0   0  71 410]
 [  0   0   0 422]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1041    0    0    0]
 [ 756  190    0    0]
 [ 529  266  260    0]]
```

## Synchronous + algorithm hints / 37×37 / D256 / edge distance 0

Stone accuracy 55.24%; macro 82.15%; overcounts 435; undercounts 1985.

```
[[ 229   16    1    0]
 [1967 1484  251  167]
 [   0   10  582    0]
 [   0    0    8  692]]
```

Overcounts only:
```
[[  0  16   1   0]
 [  0   0 251 167]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1967    0    0    0]
 [   0   10    0    0]
 [   0    0    8    0]]
```

## Synchronous + algorithm hints / 37×37 / D256 / edge distance 1

Stone accuracy 54.89%; macro 52.17%; overcounts 835; undercounts 1672.

```
[[ 591   99   62  111]
 [ 320  369   91  202]
 [ 494  159  443  270]
 [ 443  123  133 1647]]
```

Overcounts only:
```
[[  0  99  62 111]
 [  0   0  91 202]
 [  0   0   0 270]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [320   0   0   0]
 [494 159   0   0]
 [443 123 133   0]]
```

## Synchronous + algorithm hints / 37×37 / D256 / edge distance 17+

Stone accuracy 53.72%; macro 46.16%; overcounts 70; undercounts 104.

```
[[ 59   8  12  20]
 [ 19  13   0  15]
 [ 44   0  19  15]
 [ 18   9  14 111]]
```

Overcounts only:
```
[[ 0  8 12 20]
 [ 0  0  0 15]
 [ 0  0  0 15]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [19  0  0  0]
 [44  0  0  0]
 [18  9 14  0]]
```

## Synchronous + algorithm hints / 37×37 / D256 / edge distance 2

Stone accuracy 58.90%; macro 59.74%; overcounts 1312; undercounts 885.

```
[[1021  326  236  327]
 [ 701  366  157  191]
 [  65   28  320   75]
 [  52   14   25 1441]]
```

Overcounts only:
```
[[  0 326 236 327]
 [  0   0 157 191]
 [  0   0   0  75]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [701   0   0   0]
 [ 65  28   0   0]
 [ 52  14  25   0]]
```

## Synchronous + algorithm hints / 37×37 / D256 / edge distance 3–4

Stone accuracy 57.76%; macro 52.32%; overcounts 1829; undercounts 2350.

```
[[1653  257  309  513]
 [ 989  551  133  349]
 [ 466  162  646  268]
 [ 428  103  202 2865]]
```

Overcounts only:
```
[[  0 257 309 513]
 [  0   0 133 349]
 [  0   0   0 268]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [989   0   0   0]
 [466 162   0   0]
 [428 103 202   0]]
```

## Synchronous + algorithm hints / 37×37 / D256 / edge distance 5–8

Stone accuracy 57.26%; macro 51.70%; overcounts 3194; undercounts 3553.

```
[[2596  578  501  995]
 [1444  851  169  495]
 [ 732  275 1060  456]
 [ 686  168  248 4533]]
```

Overcounts only:
```
[[  0 578 501 995]
 [  0   0 169 495]
 [  0   0   0 456]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1444    0    0    0]
 [ 732  275    0    0]
 [ 686  168  248    0]]
```

## Synchronous + algorithm hints / 37×37 / D256 / edge distance 9–16

Stone accuracy 57.57%; macro 51.19%; overcounts 3119; undercounts 3160.

```
[[2516  613  628  989]
 [1093  639   67  410]
 [ 762  226 1049  412]
 [ 541  268  270 4316]]
```

Overcounts only:
```
[[  0 613 628 989]
 [  0   0  67 410]
 [  0   0   0 412]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1093    0    0    0]
 [ 762  226    0    0]
 [ 541  268  270    0]]
```
