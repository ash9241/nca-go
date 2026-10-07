# Existing-checkpoint audit

Descriptive analysis of already opened data; no training or checkpoint selection.
Graph diameter + 1 is a chain-propagation proxy, not the grid NCA's exact receptive field. A chain outside this proxy can still be locally classifiable, especially in the 4+ class.

Confusion rows are exact classes, columns predicted classes. Above diagonal = overcount; below diagonal = undercount. Values are capped liberty classes, not uncapped numerical errors.

Explicit split matrices: each complete matrix is followed by its overcount-only and undercount-only triangles. Correct predictions are omitted from both error matrices.

## Interpretation

A strict radius32 light cone cannot explain the 13x13, 19x19 or 25x25 errors: every board cell is within Chebyshev distance32 of every stone. At37x37, most errors still have every liberty within that radius. Chain graph distance strongly predicts failures, but this is descriptive correlation: it does not establish that a learned grid model routes only along chains.
Raw cycle accuracies are confounded by liberty-class and chain-size distributions. Cycles are not the worst raw subgroup; the new sum/max and minimally perturbed pair experiments are needed to test double-counting. Longer rollout degradation is independently visible in the existing depth tables and saved trajectories.

- 13x13: 0/99788 errors (0.00%) have at least one liberty outside the strict grid radius32.
- 19x19: 0/129072 errors (0.00%) have at least one liberty outside the strict grid radius32.
- 25x25: 0/110736 errors (0.00%) have at least one liberty outside the strict grid radius32.
- 37x37: 15200/177903 errors (8.54%) have at least one liberty outside the strict grid radius32.

## Cycle comparison on common support

Conditioning on generator, diameter bin, chain-size bin, edge-distance bin and exact capped liberty class, the cyclic-minus-acyclic accuracy differences at D32 are -0.14, -0.59, -0.10 and +0.24 percentage points for sizes13,19,25 and37. Only6--9% of stone-trials have common support under this reweighting. This subset does not show a consistent cycle penalty and cannot explain the unmatched long-chain errors. These are descriptive comparisons, not causal estimates or independent stone-level trials. See `cycle_common_support.json` for all support counts.

## Final-test confusion matrices for all recipes and depths

Asynchronous size=9 depth=32: over=537 under=449
```
[[ 98652     42      0      0]
 [   139 301960    121      0]
 [     0     97 174327    374]
 [     0      0    213 290730]]
```

Overcounts only:
```
[[  0  42   0   0]
 [  0   0 121   0]
 [  0   0   0 374]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [139   0   0   0]
 [  0  97   0   0]
 [  0   0 213   0]]
```

Asynchronous size=9 depth=64: over=7852 under=3793
```
[[ 95842   2289    562      1]
 [  2046 296833   3323     18]
 [     0    622 172517   1659]
 [     0      0   1125 289818]]
```

Overcounts only:
```
[[   0 2289  562    1]
 [   0    0 3323   18]
 [   0    0    0 1659]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2046    0    0    0]
 [   0  622    0    0]
 [   0    0 1125    0]]
```

Asynchronous size=9 depth=128: over=37356 under=33978
```
[[ 84677   7695   6285     37]
 [ 20042 265168  16789    221]
 [     1   7079 161389   6329]
 [     0      1   6855 284087]]
```

Overcounts only:
```
[[    0  7695  6285    37]
 [    0     0 16789   221]
 [    0     0     0  6329]
 [    0     0     0     0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [20042     0     0     0]
 [    1  7079     0     0]
 [    0     1  6855     0]]
```

Asynchronous size=9 depth=256: over=83745 under=71289
```
[[ 75176  12930  10468    120]
 [ 39159 215390  46519   1152]
 [   363  12759 149120  12556]
 [     0      2  19006 271935]]
```

Overcounts only:
```
[[    0 12930 10468   120]
 [    0     0 46519  1152]
 [    0     0     0 12556]
 [    0     0     0     0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [39159     0     0     0]
 [  363 12759     0     0]
 [    0     2 19006     0]]
```

Asynchronous size=13 depth=32: over=452 under=99336
```
[[ 76154    283      0      0]
 [ 39710 103049     53      0]
 [ 11619  13766  43376    116]
 [  3755  13585  16901 134041]]
```

Overcounts only:
```
[[  0 283   0   0]
 [  0   0  53   0]
 [  0   0   0 116]
 [  0   0   0   0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [39710     0     0     0]
 [11619 13766     0     0]
 [ 3755 13585 16901     0]]
```

Asynchronous size=13 depth=64: over=4666 under=100502
```
[[ 73597   2535    304      1]
 [ 43018  98447   1338      9]
 [ 13106  10810  44482    479]
 [  3558  13750  16260 134714]]
```

Overcounts only:
```
[[   0 2535  304    1]
 [   0    0 1338    9]
 [   0    0    0  479]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [43018     0     0     0]
 [13106 10810     0     0]
 [ 3558 13750 16260     0]]
```

Asynchronous size=13 depth=128: over=17617 under=106710
```
[[ 67663   7581   1141     52]
 [ 48117  88627   5730    338]
 [ 12393  11076  42633   2775]
 [  2722  14947  17455 133158]]
```

Overcounts only:
```
[[   0 7581 1141   52]
 [   0    0 5730  338]
 [   0    0    0 2775]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [48117     0     0     0]
 [12393 11076     0     0]
 [ 2722 14947 17455     0]]
```

Asynchronous size=13 depth=256: over=35440 under=112545
```
[[ 61249  12352   2486    350]
 [ 51169  77350  12958   1335]
 [ 10606  12552  39760   5959]
 [  2582  13468  22168 130064]]
```

Overcounts only:
```
[[    0 12352  2486   350]
 [    0     0 12958  1335]
 [    0     0     0  5959]
 [    0     0     0     0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [51169     0     0     0]
 [10606 12552     0     0]
 [ 2582 13468 22168     0]]
```

Asynchronous size=19 depth=32: over=4461 under=124611
```
[[112888   4196     24      0]
 [ 54356  80425    138      0]
 [ 31298   4521  41955    103]
 [ 22179   9904   2353 134125]]
```

Overcounts only:
```
[[   0 4196   24    0]
 [   0    0  138    0]
 [   0    0    0  103]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [54356     0     0     0]
 [31298  4521     0     0]
 [22179  9904  2353     0]]
```

Asynchronous size=19 depth=64: over=9551 under=126472
```
[[110357   6449    296      6]
 [ 56593  76087   2218     21]
 [ 31892   3424  42000    561]
 [ 22715   7969   3879 133998]]
```

Overcounts only:
```
[[   0 6449  296    6]
 [   0    0 2218   21]
 [   0    0    0  561]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [56593     0     0     0]
 [31892  3424     0     0]
 [22715  7969  3879     0]]
```

Asynchronous size=19 depth=128: over=21408 under=131366
```
[[105251  11242    573     42]
 [ 60416  68113   5972    418]
 [ 30748   4317  39651   3161]
 [ 22278   8147   5460 132676]]
```

Overcounts only:
```
[[    0 11242   573    42]
 [    0     0  5972   418]
 [    0     0     0  3161]
 [    0     0     0     0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [60416     0     0     0]
 [30748  4317     0     0]
 [22278  8147  5460     0]]
```

Asynchronous size=19 depth=256: over=41932 under=133852
```
[[ 94966  20467   1476    199]
 [ 60702  61587  11248   1382]
 [ 27189   7459  36069   7160]
 [ 19919  10218   8365 130059]]
```

Overcounts only:
```
[[    0 20467  1476   199]
 [    0     0 11248  1382]
 [    0     0     0  7160]
 [    0     0     0     0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [60702     0     0     0]
 [27189  7459     0     0]
 [19919 10218  8365     0]]
```

Asynchronous size=25 depth=32: over=7366 under=103370
```
[[116590   7042     46      0]
 [ 54128  60163    205      2]
 [ 17759    411  36083     71]
 [ 26304   3624   1144 126590]]
```

Overcounts only:
```
[[   0 7042   46    0]
 [   0    0  205    2]
 [   0    0    0   71]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [54128     0     0     0]
 [17759   411     0     0]
 [26304  3624  1144     0]]
```

Asynchronous size=25 depth=64: over=10937 under=104929
```
[[115540   6788   1350      0]
 [ 55869  56403   2188     38]
 [ 17833    309  35609    573]
 [ 26306   2698   1914 126744]]
```

Overcounts only:
```
[[   0 6788 1350    0]
 [   0    0 2188   38]
 [   0    0    0  573]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [55869     0     0     0]
 [17833   309     0     0]
 [26306  2698  1914     0]]
```

Asynchronous size=25 depth=128: over=21916 under=108594
```
[[112012   9808   1832     26]
 [ 58396  49173   6441    488]
 [ 17356    760  32887   3321]
 [ 25630   2953   3499 125580]]
```

Overcounts only:
```
[[   0 9808 1832   26]
 [   0    0 6441  488]
 [   0    0    0 3321]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [58396     0     0     0]
 [17356   760     0     0]
 [25630  2953  3499     0]]
```

Asynchronous size=25 depth=256: over=39528 under=110448
```
[[104376  16412   2783    107]
 [ 57982  43261  11768   1487]
 [ 15880   2087  29386   6971]
 [ 23900   4769   5830 123163]]
```

Overcounts only:
```
[[    0 16412  2783   107]
 [    0     0 11768  1487]
 [    0     0     0  6971]
 [    0     0     0     0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [57982     0     0     0]
 [15880  2087     0     0]
 [23900  4769  5830     0]]
```

Asynchronous size=37 depth=32: over=9571 under=168332
```
[[128038   9123    207     26]
 [ 69178  52299     50      0]
 [ 45127    945  35105    165]
 [ 51227   1510    345 121140]]
```

Overcounts only:
```
[[   0 9123  207   26]
 [   0    0   50    0]
 [   0    0    0  165]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [69178     0     0     0]
 [45127   945     0     0]
 [51227  1510   345     0]]
```

Asynchronous size=37 depth=64: over=14084 under=170439
```
[[126573   7353   3286    182]
 [ 71568  47269   2681      9]
 [ 45188    473  35108    573]
 [ 51270    842   1098 121012]]
```

Overcounts only:
```
[[   0 7353 3286  182]
 [   0    0 2681    9]
 [   0    0    0  573]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [71568     0     0     0]
 [45188   473     0     0]
 [51270   842  1098     0]]
```

Asynchronous size=37 depth=128: over=23269 under=173511
```
[[124400   8912   3746    336]
 [ 73647  40746   6864    270]
 [ 44699    934  32568   3141]
 [ 50254   1737   2240 119991]]
```

Overcounts only:
```
[[   0 8912 3746  336]
 [   0    0 6864  270]
 [   0    0    0 3141]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [73647     0     0     0]
 [44699   934     0     0]
 [50254  1737  2240     0]]
```

Asynchronous size=37 depth=256: over=38332 under=175293
```
[[118706  13636   4238    814]
 [ 73429  35471  11443   1184]
 [ 42723   2926  28676   7017]
 [ 48453   3398   4364 118007]]
```

Overcounts only:
```
[[    0 13636  4238   814]
 [    0     0 11443  1184]
 [    0     0     0  7017]
 [    0     0     0     0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [73429     0     0     0]
 [42723  2926     0     0]
 [48453  3398  4364     0]]
```

C128 Synchronous size=9 depth=32: over=7 under=34
```
[[10965     1     0     0]
 [    0 33580     0     0]
 [    0     1 19415     6]
 [    0     0    33 32294]]
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
[[ 0  0  0  0]
 [ 0  0  0  0]
 [ 0  1  0  0]
 [ 0  0 33  0]]
```

C128 Synchronous size=9 depth=64: over=37 under=94
```
[[10948    18     0     0]
 [    3 33575     2     0]
 [    2    26 19377    17]
 [    0     2    61 32264]]
```

Overcounts only:
```
[[ 0 18  0  0]
 [ 0  0  2  0]
 [ 0  0  0 17]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [ 3  0  0  0]
 [ 2 26  0  0]
 [ 0  2 61  0]]
```

C128 Synchronous size=9 depth=128: over=553 under=291
```
[[10866    95     1     4]
 [   13 33441    86    40]
 [    5   112 18978   327]
 [    0     9   152 32166]]
```

Overcounts only:
```
[[  0  95   1   4]
 [  0   0  86  40]
 [  0   0   0 327]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [ 13   0   0   0]
 [  5 112   0   0]
 [  0   9 152   0]]
```

C128 Synchronous size=9 depth=256: over=1734 under=606
```
[[10611   263    31    61]
 [   85 32973   337   185]
 [    4   222 18339   857]
 [    0    16   279 32032]]
```

Overcounts only:
```
[[  0 263  31  61]
 [  0   0 337 185]
 [  0   0   0 857]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [ 85   0   0   0]
 [  4 222   0   0]
 [  0  16 279   0]]
```

C128 Synchronous size=13 depth=32: over=268 under=9446
```
[[ 8237   256     0     0]
 [ 3052 12814     0     2]
 [  826  1769  5048    10]
 [  151  1356  2292 14899]]
```

Overcounts only:
```
[[  0 256   0   0]
 [  0   0   0   2]
 [  0   0   0  10]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3052    0    0    0]
 [ 826 1769    0    0]
 [ 151 1356 2292    0]]
```

C128 Synchronous size=13 depth=64: over=282 under=9672
```
[[ 8224   269     0     0]
 [ 3227 12638     1     2]
 [  869  1782  4992    10]
 [  162  1558  2074 14904]]
```

Overcounts only:
```
[[  0 269   0   0]
 [  0   0   1   2]
 [  0   0   0  10]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3227    0    0    0]
 [ 869 1782    0    0]
 [ 162 1558 2074    0]]
```

C128 Synchronous size=13 depth=128: over=564 under=9863
```
[[ 8104   327     0    62]
 [ 3454 12354    21    39]
 [  967  1709  4862   115]
 [  190  1682  1861 14965]]
```

Overcounts only:
```
[[  0 327   0  62]
 [  0   0  21  39]
 [  0   0   0 115]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3454    0    0    0]
 [ 967 1709    0    0]
 [ 190 1682 1861    0]]
```

C128 Synchronous size=13 depth=256: over=1234 under=10183
```
[[ 7842   403    22   226]
 [ 3756 11785   103   224]
 [ 1149  1558  4690   256]
 [  230  1811  1679 14978]]
```

Overcounts only:
```
[[  0 403  22 226]
 [  0   0 103 224]
 [  0   0   0 256]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3756    0    0    0]
 [1149 1558    0    0]
 [ 230 1811 1679    0]]
```

C128 Synchronous size=19 depth=32: over=1046 under=12698
```
[[11988  1024     0     0]
 [ 4954 10023    14     0]
 [ 3063   855  4727     8]
 [ 2155  1384   287 14903]]
```

Overcounts only:
```
[[   0 1024    0    0]
 [   0    0   14    0]
 [   0    0    0    8]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4954    0    0    0]
 [3063  855    0    0]
 [2155 1384  287    0]]
```

C128 Synchronous size=19 depth=64: over=538 under=13022
```
[[12511   500     1     0]
 [ 5236  9732    23     0]
 [ 3117   832  4690    14]
 [ 2248  1337   252 14892]]
```

Overcounts only:
```
[[  0 500   1   0]
 [  0   0  23   0]
 [  0   0   0  14]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5236    0    0    0]
 [3117  832    0    0]
 [2248 1337  252    0]]
```

C128 Synchronous size=19 depth=128: over=620 under=13101
```
[[12562   381     3    66]
 [ 5377  9556    25    33]
 [ 3201   735  4605   112]
 [ 2364  1202   222 14941]]
```

Overcounts only:
```
[[  0 381   3  66]
 [  0   0  25  33]
 [  0   0   0 112]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5377    0    0    0]
 [3201  735    0    0]
 [2364 1202  222    0]]
```

C128 Synchronous size=19 depth=256: over=1317 under=13098
```
[[12384   341    10   277]
 [ 5560  9148    56   227]
 [ 3255   537  4455   406]
 [ 2488   968   290 14983]]
```

Overcounts only:
```
[[  0 341  10 277]
 [  0   0  56 227]
 [  0   0   0 406]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5560    0    0    0]
 [3255  537    0    0]
 [2488  968  290    0]]
```

C128 Synchronous size=25 depth=32: over=941 under=10785
```
[[12808   923    10     1]
 [ 5297  7421     4     0]
 [ 1882   131  4020     3]
 [ 2724   602   149 14043]]
```

Overcounts only:
```
[[  0 923  10   1]
 [  0   0   4   0]
 [  0   0   0   3]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5297    0    0    0]
 [1882  131    0    0]
 [2724  602  149    0]]
```

C128 Synchronous size=25 depth=64: over=538 under=11000
```
[[13219   519     4     0]
 [ 5488  7226     8     0]
 [ 1918   108  4003     7]
 [ 2788   564   134 14032]]
```

Overcounts only:
```
[[  0 519   4   0]
 [  0   0   8   0]
 [  0   0   0   7]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5488    0    0    0]
 [1918  108    0    0]
 [2788  564  134    0]]
```

C128 Synchronous size=25 depth=128: over=578 under=11102
```
[[13354   368     2    18]
 [ 5559  7061    15    87]
 [ 1929    95  3924    88]
 [ 2850   491   178 13999]]
```

Overcounts only:
```
[[  0 368   2  18]
 [  0   0  15  87]
 [  0   0   0  88]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5559    0    0    0]
 [1929   95    0    0]
 [2850  491  178    0]]
```

C128 Synchronous size=25 depth=256: over=1032 under=11123
```
[[13349   213    39   141]
 [ 5647  6766    11   298]
 [ 1895    64  3747   330]
 [ 2924   358   235 14001]]
```

Overcounts only:
```
[[  0 213  39 141]
 [  0   0  11 298]
 [  0   0   0 330]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5647    0    0    0]
 [1895   64    0    0]
 [2924  358  235    0]]
```

C128 Synchronous size=37 depth=32: over=897 under=18210
```
[[14383   883     0     0]
 [ 7170  6333     0     0]
 [ 4897   223  3904    14]
 [ 5576   304    40 13438]]
```

Overcounts only:
```
[[  0 883   0   0]
 [  0   0   0   0]
 [  0   0   0  14]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [7170    0    0    0]
 [4897  223    0    0]
 [5576  304   40    0]]
```

C128 Synchronous size=37 depth=64: over=386 under=18341
```
[[14902   364     0     0]
 [ 7299  6203     0     1]
 [ 4972   151  3894    21]
 [ 5676   210    33 13439]]
```

Overcounts only:
```
[[  0 364   0   0]
 [  0   0   0   1]
 [  0   0   0  21]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [7299    0    0    0]
 [4972  151    0    0]
 [5676  210   33    0]]
```

C128 Synchronous size=37 depth=128: over=344 under=18354
```
[[15068   136     1    61]
 [ 7319  6099     9    76]
 [ 5042    84  3851    61]
 [ 5786   103    20 13449]]
```

Overcounts only:
```
[[  0 136   1  61]
 [  0   0   9  76]
 [  0   0   0  61]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [7319    0    0    0]
 [5042   84    0    0]
 [5786  103   20    0]]
```

C128 Synchronous size=37 depth=256: over=646 under=18398
```
[[15061    85     2   118]
 [ 7364  5949    29   161]
 [ 5030    58  3699   251]
 [ 5826    67    53 13412]]
```

Overcounts only:
```
[[  0  85   2 118]
 [  0   0  29 161]
 [  0   0   0 251]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [7364    0    0    0]
 [5030   58    0    0]
 [5826   67   53    0]]
```

Synchronous size=9 depth=32: over=154 under=309
```
[[ 32888     10      0      0]
 [    52 100627     61      0]
 [     0     74  58109     83]
 [     0      0    183  96798]]
```

Overcounts only:
```
[[ 0 10  0  0]
 [ 0  0 61  0]
 [ 0  0  0 83]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [ 52   0   0   0]
 [  0  74   0   0]
 [  0   0 183   0]]
```

Synchronous size=9 depth=64: over=2910 under=1612
```
[[32123   743    32     0]
 [  418 98705  1617     0]
 [    6   272 57470   518]
 [    0     0   916 96065]]
```

Overcounts only:
```
[[   0  743   32    0]
 [   0    0 1617    0]
 [   0    0    0  518]
 [   0    0    0    0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [418   0   0   0]
 [  6 272   0   0]
 [  0   0 916   0]]
```

Synchronous size=9 depth=128: over=17250 under=15466
```
[[25420  6622   851     5]
 [ 2075 90029  8593    43]
 [    3  3316 53811  1136]
 [    5     2 10065 86909]]
```

Overcounts only:
```
[[   0 6622  851    5]
 [   0    0 8593   43]
 [   0    0    0 1136]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [ 2075     0     0     0]
 [    3  3316     0     0]
 [    5     2 10065     0]]
```

Synchronous size=9 depth=256: over=37964 under=37041
```
[[17956 11090  3820    32]
 [ 4402 75187 21040   111]
 [ 1072  4325 50998  1871]
 [   34   128 27080 69739]]
```

Overcounts only:
```
[[    0 11090  3820    32]
 [    0     0 21040   111]
 [    0     0     0  1871]
 [    0     0     0     0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [ 4402     0     0     0]
 [ 1072  4325     0     0]
 [   34   128 27080     0]]
```

Synchronous size=13 depth=32: over=388 under=34332
```
[[25157   315     7     0]
 [13672 33917    15     0]
 [ 5740  3006 14162    51]
 [ 3740  4444  3730 44180]]
```

Overcounts only:
```
[[  0 315   7   0]
 [  0   0  15   0]
 [  0   0   0  51]
 [  0   0   0   0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [13672     0     0     0]
 [ 5740  3006     0     0]
 [ 3740  4444  3730     0]]
```

Synchronous size=13 depth=64: over=1270 under=35855
```
[[24628   759    91     1]
 [15261 32017   325     1]
 [ 6162  2488 14216    93]
 [ 3967  3946  4031 44150]]
```

Overcounts only:
```
[[  0 759  91   1]
 [  0   0 325   1]
 [  0   0   0  93]
 [  0   0   0   0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [15261     0     0     0]
 [ 6162  2488     0     0]
 [ 3967  3946  4031     0]]
```

Synchronous size=13 depth=128: over=5867 under=39341
```
[[22358  2558   563     0]
 [15769 29363  2460    12]
 [ 6196  2247 14242   274]
 [ 3878  3934  7317 40965]]
```

Overcounts only:
```
[[   0 2558  563    0]
 [   0    0 2460   12]
 [   0    0    0  274]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [15769     0     0     0]
 [ 6196  2247     0     0]
 [ 3878  3934  7317     0]]
```

Synchronous size=13 depth=256: over=12127 under=44749
```
[[19845  3652  1966    16]
 [15127 26584  5804    89]
 [ 5321  2766 14272   600]
 [ 3725  3937 13873 34559]]
```

Overcounts only:
```
[[   0 3652 1966   16]
 [   0    0 5804   89]
 [   0    0    0  600]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [15127     0     0     0]
 [ 5321  2766     0     0]
 [ 3725  3937 13873     0]]
```

Synchronous size=19 depth=32: over=2391 under=43094
```
[[36719  2245    72     0]
 [19659 25275    39     0]
 [11004   983 13937    35]
 [ 9849  1329   270 44739]]
```

Overcounts only:
```
[[   0 2245   72    0]
 [   0    0   39    0]
 [   0    0    0   35]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [19659     0     0     0]
 [11004   983     0     0]
 [ 9849  1329   270     0]]
```

Synchronous size=19 depth=64: over=3085 under=44489
```
[[36532  2020   400    84]
 [21007 23444   510    12]
 [11039   918 13943    59]
 [10164  1018   343 44662]]
```

Overcounts only:
```
[[   0 2020  400   84]
 [   0    0  510   12]
 [   0    0    0   59]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [21007     0     0     0]
 [11039   918     0     0]
 [10164  1018   343     0]]
```

Synchronous size=19 depth=128: over=6777 under=47970
```
[[34765  2822  1269   180]
 [22143 20536  2269    25]
 [10811  1018 13918   212]
 [ 9996  1136  2866 42189]]
```

Overcounts only:
```
[[   0 2822 1269  180]
 [   0    0 2269   25]
 [   0    0    0  212]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [22143     0     0     0]
 [10811  1018     0     0]
 [ 9996  1136  2866     0]]
```

Synchronous size=19 depth=256: over=11225 under=54861
```
[[32984  3429  1849   774]
 [22515 17806  4416   236]
 [10205  1241 13992   521]
 [ 9691   935 10274 35287]]
```

Overcounts only:
```
[[   0 3429 1849  774]
 [   0    0 4416  236]
 [   0    0    0  521]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [22515     0     0     0]
 [10205  1241     0     0]
 [ 9691   935 10274     0]]
```

Synchronous size=25 depth=32: over=2457 under=35315
```
[[38811  2363    52     0]
 [18822 19321    22     1]
 [ 5885   184 12020    19]
 [ 9583   702   139 42130]]
```

Overcounts only:
```
[[   0 2363   52    0]
 [   0    0   22    1]
 [   0    0    0   19]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [18822     0     0     0]
 [ 5885   184     0     0]
 [ 9583   702   139     0]]
```

Synchronous size=25 depth=64: over=2846 under=36302
```
[[38854  1929   442     1]
 [19707 18048   411     0]
 [ 5870   185 11990    63]
 [ 9730   560   250 42014]]
```

Overcounts only:
```
[[   0 1929  442    1]
 [   0    0  411    0]
 [   0    0    0   63]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [19707     0     0     0]
 [ 5870   185     0     0]
 [ 9730   560   250     0]]
```

Synchronous size=25 depth=128: over=6401 under=39546
```
[[37382  2822   909   113]
 [20743 15122  2287    14]
 [ 5757   276 11819   256]
 [ 9630   615  2525 39784]]
```

Overcounts only:
```
[[   0 2822  909  113]
 [   0    0 2287   14]
 [   0    0    0  256]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [20743     0     0     0]
 [ 5757   276     0     0]
 [ 9630   615  2525     0]]
```

Synchronous size=25 depth=256: over=10831 under=46273
```
[[35598  3297  2046   285]
 [20832 12685  4468   181]
 [ 5526   444 11584   554]
 [ 9574   607  9290 33083]]
```

Overcounts only:
```
[[   0 3297 2046  285]
 [   0    0 4468  181]
 [   0    0    0  554]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [20832     0     0     0]
 [ 5526   444     0     0]
 [ 9574   607  9290     0]]
```

Synchronous size=37 depth=32: over=3671 under=55754
```
[[42190  3596    12     0]
 [22680 17799    30     0]
 [14898   470 11713    33]
 [16453  1179    74 40368]]
```

Overcounts only:
```
[[   0 3596   12    0]
 [   0    0   30    0]
 [   0    0    0   33]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [22680     0     0     0]
 [14898   470     0     0]
 [16453  1179    74     0]]
```

Synchronous size=37 depth=64: over=3310 under=57446
```
[[42902  2329   545    22]
 [24251 15919   336     3]
 [15119   256 11664    75]
 [16896   723   201 40254]]
```

Overcounts only:
```
[[   0 2329  545   22]
 [   0    0  336    3]
 [   0    0    0   75]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [24251     0     0     0]
 [15119   256     0     0]
 [16896   723   201     0]]
```

Synchronous size=37 depth=128: over=6132 under=60429
```
[[41917  2505  1096   280]
 [25315 13183  1984    27]
 [14929   454 11491   240]
 [16796   733  2202 38343]]
```

Overcounts only:
```
[[   0 2505 1096  280]
 [   0    0 1984   27]
 [   0    0    0  240]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [25315     0     0     0]
 [14929   454     0     0]
 [16796   733  2202     0]]
```

Synchronous size=37 depth=256: over=10408 under=67288
```
[[40121  2656  1904  1117]
 [25626 10683  4040   160]
 [14749   572 11262   531]
 [16791   827  8723 31733]]
```

Overcounts only:
```
[[   0 2656 1904 1117]
 [   0    0 4040  160]
 [   0    0    0  531]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [25626     0     0     0]
 [14749   572     0     0]
 [16791   827  8723     0]]
```

Synchronous + algorithm hints size=9 depth=32: over=179 under=137
```
[[10958     8     0     0]
 [   12 33536    32     0]
 [    0    45 19238   139]
 [    0     0    80 32247]]
```

Overcounts only:
```
[[  0   8   0   0]
 [  0   0  32   0]
 [  0   0   0 139]
 [  0   0   0   0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [12  0  0  0]
 [ 0 45  0  0]
 [ 0  0 80  0]]
```

Synchronous + algorithm hints size=9 depth=64: over=329 under=368
```
[[10891    64     6     5]
 [  240 33320    20     0]
 [    0    65 19123   234]
 [    0     0    63 32264]]
```

Overcounts only:
```
[[  0  64   6   5]
 [  0   0  20   0]
 [  0   0   0 234]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [240   0   0   0]
 [  0  65   0   0]
 [  0   0  63   0]]
```

Synchronous + algorithm hints size=9 depth=128: over=734 under=1095
```
[[10531   425     3     7]
 [  787 32745    48     0]
 [    0   176 18995   251]
 [    0     0   132 32195]]
```

Overcounts only:
```
[[  0 425   3   7]
 [  0   0  48   0]
 [  0   0   0 251]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [787   0   0   0]
 [  0 176   0   0]
 [  0   0 132   0]]
```

Synchronous + algorithm hints size=9 depth=256: over=1679 under=2998
```
[[ 9774  1162    24     6]
 [ 1181 32139   260     0]
 [    0  1380 17815   227]
 [    0     1   436 31890]]
```

Overcounts only:
```
[[   0 1162   24    6]
 [   0    0  260    0]
 [   0    0    0  227]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1181    0    0    0]
 [   0 1380    0    0]
 [   0    1  436    0]]
```

Synchronous + algorithm hints size=13 depth=32: over=931 under=4801
```
[[ 8258   232     2     1]
 [ 2289 13385   193     1]
 [  160  1022  5969   502]
 [   34   199  1097 17368]]
```

Overcounts only:
```
[[  0 232   2   1]
 [  0   0 193   1]
 [  0   0   0 502]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2289    0    0    0]
 [ 160 1022    0    0]
 [  34  199 1097    0]]
```

Synchronous + algorithm hints size=13 depth=64: over=1123 under=5496
```
[[ 8301   169    13    10]
 [ 3211 12493   164     0]
 [  148  1340  5398   767]
 [   20   188   589 17901]]
```

Overcounts only:
```
[[  0 169  13  10]
 [  0   0 164   0]
 [  0   0   0 767]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3211    0    0    0]
 [ 148 1340    0    0]
 [  20  188  589    0]]
```

Synchronous + algorithm hints size=13 depth=128: over=1319 under=6246
```
[[ 8222   233    25    13]
 [ 3804 11813   251     0]
 [  287  1339  5230   797]
 [   14   200   602 17882]]
```

Overcounts only:
```
[[  0 233  25  13]
 [  0   0 251   0]
 [  0   0   0 797]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3804    0    0    0]
 [ 287 1339    0    0]
 [  14  200  602    0]]
```

Synchronous + algorithm hints size=13 depth=256: over=1708 under=7414
```
[[ 7951   493    37    12]
 [ 4643 10842   383     0]
 [  381  1416  5073   783]
 [   19   259   696 17724]]
```

Overcounts only:
```
[[  0 493  37  12]
 [  0   0 383   0]
 [  0   0   0 783]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4643    0    0    0]
 [ 381 1416    0    0]
 [  19  259  696    0]]
```

Synchronous + algorithm hints size=19 depth=32: over=4279 under=8771
```
[[10235  2312   421    44]
 [ 3536 10268   904   283]
 [ 1407  1570  5361   315]
 [  370   771  1117 16471]]
```

Overcounts only:
```
[[   0 2312  421   44]
 [   0    0  904  283]
 [   0    0    0  315]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3536    0    0    0]
 [1407 1570    0    0]
 [ 370  771 1117    0]]
```

Synchronous + algorithm hints size=19 depth=64: over=4004 under=8452
```
[[10963  1524   469    56]
 [ 4305  9487   804   395]
 [ 1546  1302  5049   756]
 [  213   427   659 17430]]
```

Overcounts only:
```
[[   0 1524  469   56]
 [   0    0  804  395]
 [   0    0    0  756]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4305    0    0    0]
 [1546 1302    0    0]
 [ 213  427  659    0]]
```

Synchronous + algorithm hints size=19 depth=128: over=3820 under=9302
```
[[11206  1384   366    56]
 [ 5249  8562   676   504]
 [ 1813  1089  4917   834]
 [  226   482   443 17578]]
```

Overcounts only:
```
[[   0 1384  366   56]
 [   0    0  676  504]
 [   0    0    0  834]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5249    0    0    0]
 [1813 1089    0    0]
 [ 226  482  443    0]]
```

Synchronous + algorithm hints size=19 depth=256: over=3992 under=10246
```
[[11063  1543   358    48]
 [ 5918  7844   715   514]
 [ 1941  1093  4805   814]
 [  222   511   561 17435]]
```

Overcounts only:
```
[[   0 1543  358   48]
 [   0    0  715  514]
 [   0    0    0  814]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5918    0    0    0]
 [1941 1093    0    0]
 [ 222  511  561    0]]
```

Synchronous + algorithm hints size=25 depth=32: over=5426 under=9172
```
[[ 9815  2286  1413   228]
 [ 5087  6429   868   338]
 [  890   399  4454   293]
 [ 1257   855   684 14722]]
```

Overcounts only:
```
[[   0 2286 1413  228]
 [   0    0  868  338]
 [   0    0    0  293]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5087    0    0    0]
 [ 890  399    0    0]
 [1257  855  684    0]]
```

Synchronous + algorithm hints size=25 depth=64: over=5986 under=8582
```
[[10104  1564  1339   735]
 [ 5449  5757   767   749]
 [  815   233  4156   832]
 [ 1094   594   397 15433]]
```

Overcounts only:
```
[[   0 1564 1339  735]
 [   0    0  767  749]
 [   0    0    0  832]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5449    0    0    0]
 [ 815  233    0    0]
 [1094  594  397    0]]
```

Synchronous + algorithm hints size=25 depth=128: over=5551 under=8966
```
[[10542  1370  1111   719]
 [ 5839  5375   745   763]
 [  815   258  4120   843]
 [ 1164   567   323 15464]]
```

Overcounts only:
```
[[   0 1370 1111  719]
 [   0    0  745  763]
 [   0    0    0  843]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5839    0    0    0]
 [ 815  258    0    0]
 [1164  567  323    0]]
```

Synchronous + algorithm hints size=25 depth=256: over=5594 under=9354
```
[[10520  1549   987   686]
 [ 6008  5179   781   754]
 [  802   386  4011   837]
 [ 1154   596   408 15360]]
```

Overcounts only:
```
[[   0 1549  987  686]
 [   0    0  781  754]
 [   0    0    0  837]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [6008    0    0    0]
 [ 802  386    0    0]
 [1154  596  408    0]]
```

Synchronous + algorithm hints size=37 depth=32: over=8277 under=14850
```
[[ 9161  2974  2144   987]
 [ 6236  5786  1081   400]
 [ 2593  1110  4644   691]
 [ 2458  1477   976 14447]]
```

Overcounts only:
```
[[   0 2974 2144  987]
 [   0    0 1081  400]
 [   0    0    0  691]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [6236    0    0    0]
 [2593 1110    0    0]
 [2458 1477  976    0]]
```

Synchronous + algorithm hints size=37 depth=64: over=10538 under=13351
```
[[ 8618  1745  2101  2802]
 [ 6416  4738   929  1420]
 [ 2286   926  4285  1541]
 [ 1953   879   891 15635]]
```

Overcounts only:
```
[[   0 1745 2101 2802]
 [   0    0  929 1420]
 [   0    0    0 1541]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [6416    0    0    0]
 [2286  926    0    0]
 [1953  879  891    0]]
```

Synchronous + algorithm hints size=37 depth=128: over=10518 under=13442
```
[[ 8815  1626  1847  2978]
 [ 6492  4461   780  1770]
 [ 2522   774  4225  1517]
 [ 2120   724   810 15704]]
```

Overcounts only:
```
[[   0 1626 1847 2978]
 [   0    0  780 1770]
 [   0    0    0 1517]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [6492    0    0    0]
 [2522  774    0    0]
 [2120  724  810    0]]
```

Synchronous + algorithm hints size=37 depth=256: over=10794 under=13709
```
[[ 8665  1897  1749  2955]
 [ 6533  4273   868  1829]
 [ 2563   860  4119  1496]
 [ 2168   685   900 15605]]
```

Overcounts only:
```
[[   0 1897 1749 2955]
 [   0    0  868 1829]
 [   0    0    0 1496]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [6533    0    0    0]
 [2563  860    0    0]
 [2168  685  900    0]]
```

## Main asynchronous model: 13×13, all=all
Stone accuracy 78.14%; macro 78.60%; overcounts 452; undercounts 99336
```
[[ 76154    283      0      0]
 [ 39710 103049     53      0]
 [ 11619  13766  43376    116]
 [  3755  13585  16901 134041]]
```

Overcounts only:
```
[[  0 283   0   0]
 [  0   0  53   0]
 [  0   0   0 116]
 [  0   0   0   0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [39710     0     0     0]
 [11619 13766     0     0]
 [ 3755 13585 16901     0]]
```

## Main asynchronous model: 13×13, diameter=0–4
Stone accuracy 99.87%; macro 99.88%; overcounts 88; undercounts 140
```
[[16421     4     0     0]
 [  109 48866    12     0]
 [    0     3 39786    72]
 [    0     0    28 76301]]
```

Overcounts only:
```
[[ 0  4  0  0]
 [ 0  0 12  0]
 [ 0  0  0 72]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [109   0   0   0]
 [  0   3   0   0]
 [  0   0  28   0]]
```

## Main asynchronous model: 13×13, diameter=17–31
Stone accuracy 29.01%; macro 37.88%; overcounts 2; undercounts 37446
```
[[ 6452     1     0     0]
 [13251  2300     1     0]
 [ 3883  5658   962     0]
 [ 1741  5939  6974  5587]]
```

Overcounts only:
```
[[0 1 0 0]
 [0 0 1 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [13251     0     0     0]
 [ 3883  5658     0     0]
 [ 1741  5939  6974     0]]
```

## Main asynchronous model: 13×13, diameter=32–63
Stone accuracy 59.79%; macro 46.27%; overcounts 49; undercounts 11221
```
[[13217    49     0     0]
 [ 8592  2010     0     0]
 [    0   629   235     0]
 [    4   220  1776  1294]]
```

Overcounts only:
```
[[ 0 49  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [8592    0    0    0]
 [   0  629    0    0]
 [   4  220 1776    0]]
```

## Main asynchronous model: 13×13, diameter=5–8
Stone accuracy 97.72%; macro 96.52%; overcounts 45; undercounts 1270
```
[[ 4787     1     0     0]
 [ 1095 15590    28     0]
 [    0   105  1616    16]
 [    0     0    70 34409]]
```

Overcounts only:
```
[[ 0  1  0  0]
 [ 0  0 28  0]
 [ 0  0  0 16]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1095    0    0    0]
 [   0  105    0    0]
 [   0    0   70    0]]
```

## Main asynchronous model: 13×13, diameter=64–127
Stone accuracy 13.61%; macro 25.78%; overcounts 0; undercounts 39165
```
[[ 5751     0     0     0]
 [12721    59     0     0]
 [ 6863  6515    23     0]
 [ 1613  5779  5674   335]]
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
[[    0     0     0     0]
 [12721     0     0     0]
 [ 6863  6515     0     0]
 [ 1613  5779  5674     0]]
```

## Main asynchronous model: 13×13, diameter=9–16
Stone accuracy 88.61%; macro 74.34%; overcounts 268; undercounts 10094
```
[[29526   228     0     0]
 [ 3942 34224    12     0]
 [  873   856   754    28]
 [  397  1647  2379 16115]]
```

Overcounts only:
```
[[  0 228   0   0]
 [  0   0  12   0]
 [  0   0   0  28]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3942    0    0    0]
 [ 873  856    0    0]
 [ 397 1647 2379    0]]
```

## Main asynchronous model: 13×13, chain_distance_vs_depth=inside
Stone accuracy 87.12%; macro 87.61%; overcounts 403; undercounts 48950
```
[[ 57186    234      0      0]
 [ 18397 100980     53      0]
 [  4756   6622  43118    116]
 [  2138   7586   9451 132412]]
```

Overcounts only:
```
[[  0 234   0   0]
 [  0   0  53   0]
 [  0   0   0 116]
 [  0   0   0   0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [18397     0     0     0]
 [ 4756  6622     0     0]
 [ 2138  7586  9451     0]]
```

## Main asynchronous model: 13×13, chain_distance_vs_depth=outside
Stone accuracy 31.25%; macro 30.04%; overcounts 49; undercounts 50386
```
[[18968    49     0     0]
 [21313  2069     0     0]
 [ 6863  7144   258     0]
 [ 1617  5999  7450  1629]]
```

Overcounts only:
```
[[ 0 49  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [21313     0     0     0]
 [ 6863  7144     0     0]
 [ 1617  5999  7450     0]]
```

## Main asynchronous model: 13×13, liberties_vs_grid_light_cone=inside
Stone accuracy 78.14%; macro 78.60%; overcounts 452; undercounts 99336
```
[[ 76154    283      0      0]
 [ 39710 103049     53      0]
 [ 11619  13766  43376    116]
 [  3755  13585  16901 134041]]
```

Overcounts only:
```
[[  0 283   0   0]
 [  0   0  53   0]
 [  0   0   0 116]
 [  0   0   0   0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [39710     0     0     0]
 [11619 13766     0     0]
 [ 3755 13585 16901     0]]
```

## Main asynchronous model: 13×13, cycle=acyclic
Stone accuracy 78.25%; macro 78.87%; overcounts 383; undercounts 89269
```
[[ 71564    283      0      0]
 [ 36489 101311     35      0]
 [ 10659  12855  41302     65]
 [  3222  11367  14677 108308]]
```

Overcounts only:
```
[[  0 283   0   0]
 [  0   0  35   0]
 [  0   0   0  65]
 [  0   0   0   0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [36489     0     0     0]
 [10659 12855     0     0]
 [ 3222 11367 14677     0]]
```

## Main asynchronous model: 13×13, cycle=cyclic
Stone accuracy 77.10%; macro 67.66%; overcounts 69; undercounts 10067
```
[[ 4590     0     0     0]
 [ 3221  1738    18     0]
 [  960   911  2074    51]
 [  533  2218  2224 25733]]
```

Overcounts only:
```
[[ 0  0  0  0]
 [ 0  0 18  0]
 [ 0  0  0 51]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3221    0    0    0]
 [ 960  911    0    0]
 [ 533 2218 2224    0]]
```

## Main asynchronous model: 13×13, chain_size=0–1
Stone accuracy 100.00%; macro 100.00%; overcounts 0; undercounts 0
```
[[ 9648     0     0     0]
 [    0 24678     0     0]
 [    0     0 22014     0]
 [    0     0     0 10818]]
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

## Main asynchronous model: 13×13, chain_size=17–32
Stone accuracy 60.41%; macro 53.76%; overcounts 2; undercounts 12325
```
[[ 5624     1     0     0]
 [ 6072  2297     1     0]
 [  796   938   372     0]
 [  397  1648  2474 10520]]
```

Overcounts only:
```
[[0 1 0 0]
 [0 0 1 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [6072    0    0    0]
 [ 796  938    0    0]
 [ 397 1648 2474    0]]
```

## Main asynchronous model: 13×13, chain_size=2–4
Stone accuracy 99.89%; macro 99.89%; overcounts 7; undercounts 88
```
[[ 5272     2     0     0]
 [   57 20255     1     0]
 [    0     3 15536     4]
 [    0     0    28 47141]]
```

Overcounts only:
```
[[0 2 0 0]
 [0 0 1 0]
 [0 0 0 4]
 [0 0 0 0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [57  0  0  0]
 [ 0  3  0  0]
 [ 0  0 28  0]]
```

## Main asynchronous model: 13×13, chain_size=33–64
Stone accuracy 58.02%; macro 43.62%; overcounts 49; undercounts 13386
```
[[14513    49     0     0]
 [ 9542  2104     0     0]
 [  164   825   235     0]
 [  140   792  1923  1717]]
```

Overcounts only:
```
[[ 0 49  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [9542    0    0    0]
 [ 164  825    0    0]
 [ 140  792 1923    0]]
```

## Main asynchronous model: 13×13, chain_size=5–8
Stone accuracy 98.81%; macro 98.28%; overcounts 71; undercounts 608
```
[[ 4723     2     0     0]
 [  551 12531    13     0]
 [    0    23  3170    56]
 [    0     0    34 36056]]
```

Overcounts only:
```
[[ 0  2  0  0]
 [ 0  0 13  0]
 [ 0  0  0 56]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [551   0   0   0]
 [  0  23   0   0]
 [  0   0  34   0]]
```

## Main asynchronous model: 13×13, chain_size=65–128
Stone accuracy 12.78%; macro 27.72%; overcounts 0; undercounts 70189
```
[[ 7668     0     0     0]
 [21372   993     0     0]
 [10582 11686   718     0]
 [ 3218 11144 12187   910]]
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
[[    0     0     0     0]
 [21372     0     0     0]
 [10582 11686     0     0]
 [ 3218 11144 12187     0]]
```

## Main asynchronous model: 13×13, chain_size=9–16
Stone accuracy 96.94%; macro 92.25%; overcounts 323; undercounts 2740
```
[[28706   229     0     0]
 [ 2116 40191    38     0]
 [   77   291  1331    56]
 [    0     1   255 26879]]
```

Overcounts only:
```
[[  0 229   0   0]
 [  0   0  38   0]
 [  0   0   0  56]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2116    0    0    0]
 [  77  291    0    0]
 [   0    1  255    0]]
```

## Main asynchronous model: 13×13, edge_distance=0–0
Stone accuracy 99.64%; macro 99.82%; overcounts 23; undercounts 495
```
[[ 8136     0     0     0]
 [  469 76361    21     0]
 [    0     6 17749     2]
 [    0     0    20 39319]]
```

Overcounts only:
```
[[ 0  0  0  0]
 [ 0  0 21  0]
 [ 0  0  0  2]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [469   0   0   0]
 [  0   6   0   0]
 [  0   0  20   0]]
```

## Main asynchronous model: 13×13, edge_distance=1–1
Stone accuracy 55.64%; macro 53.39%; overcounts 367; undercounts 89411
```
[[48674   268     0     0]
 [33803 14525    20     0]
 [10823 13013  9475    79]
 [ 3493 12509 15770 39949]]
```

Overcounts only:
```
[[  0 268   0   0]
 [  0   0  20   0]
 [  0   0   0  79]
 [  0   0   0   0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [33803     0     0     0]
 [10823 13013     0     0]
 [ 3493 12509 15770     0]]
```

## Main asynchronous model: 13×13, edge_distance=2–2
Stone accuracy 86.52%; macro 82.76%; overcounts 10; undercounts 8781
```
[[14923     8     0     0]
 [ 5288  6087     1     0]
 [  737   540  7155     1]
 [  262   950  1004 28240]]
```

Overcounts only:
```
[[0 8 0 0]
 [0 0 1 0]
 [0 0 0 1]
 [0 0 0 0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5288    0    0    0]
 [ 737  540    0    0]
 [ 262  950 1004    0]]
```

## Main asynchronous model: 13×13, edge_distance=3–4
Stone accuracy 98.31%; macro 97.98%; overcounts 52; undercounts 649
```
[[ 3971     7     0     0]
 [  150  5032    11     0]
 [   59   207  7449    34]
 [    0   126   107 24337]]
```

Overcounts only:
```
[[ 0  7  0  0]
 [ 0  0 11  0]
 [ 0  0  0 34]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [150   0   0   0]
 [ 59 207   0   0]
 [  0 126 107   0]]
```

## Main asynchronous model: 13×13, edge_distance=5–8
Stone accuracy 100.00%; macro 100.00%; overcounts 0; undercounts 0
```
[[ 450    0    0    0]
 [   0 1044    0    0]
 [   0    0 1548    0]
 [   0    0    0 2196]]
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

## Main asynchronous model: 19×19, all=all
Stone accuracy 74.11%; macro 72.36%; overcounts 4461; undercounts 124611
```
[[112888   4196     24      0]
 [ 54356  80425    138      0]
 [ 31298   4521  41955    103]
 [ 22179   9904   2353 134125]]
```

Overcounts only:
```
[[   0 4196   24    0]
 [   0    0  138    0]
 [   0    0    0  103]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [54356     0     0     0]
 [31298  4521     0     0]
 [22179  9904  2353     0]]
```

## Main asynchronous model: 19×19, diameter=0–4
Stone accuracy 99.82%; macro 99.80%; overcounts 153; undercounts 148
```
[[12982     5     0     0]
 [  119 37505   122     0]
 [    0     4 40551    26]
 [    0     0    25 79976]]
```

Overcounts only:
```
[[  0   5   0   0]
 [  0   0 122   0]
 [  0   0   0  26]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [119   0   0   0]
 [  0   4   0   0]
 [  0   0  25   0]]
```

## Main asynchronous model: 19×19, diameter=128+
Stone accuracy 23.38%; macro 25.04%; overcounts 0; undercounts 47075
```
[[14346     0     0     0]
 [14259    15     0     0]
 [18246  1842     0     0]
 [ 9913  2381   434     7]]
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
[[    0     0     0     0]
 [14259     0     0     0]
 [18246  1842     0     0]
 [ 9913  2381   434     0]]
```

## Main asynchronous model: 19×19, diameter=17–31
Stone accuracy 53.33%; macro 43.60%; overcounts 3; undercounts 7381
```
[[3903    3    0    0]
 [3009  186    0    0]
 [1901  420   19    0]
 [1217  661  173 4330]]
```

Overcounts only:
```
[[0 3 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3009    0    0    0]
 [1901  420    0    0]
 [1217  661  173    0]]
```

## Main asynchronous model: 19×19, diameter=32–63
Stone accuracy 31.09%; macro 31.36%; overcounts 96; undercounts 48811
```
[[16464    96     0     0]
 [19812  1284     0     0]
 [ 9756  1462    77     0]
 [10623  6047  1111  4242]]
```

Overcounts only:
```
[[ 0 96  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [19812     0     0     0]
 [ 9756  1462     0     0]
 [10623  6047  1111     0]]
```

## Main asynchronous model: 19×19, diameter=5–8
Stone accuracy 96.94%; macro 93.17%; overcounts 49; undercounts 1017
```
[[ 1835     1     0     0]
 [  981  3831     3     0]
 [    2    26   998    45]
 [    0     0     8 27154]]
```

Overcounts only:
```
[[ 0  1  0  0]
 [ 0  0  3  0]
 [ 0  0  0 45]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [981   0   0   0]
 [  2  26   0   0]
 [  0   0   8   0]]
```

## Main asynchronous model: 19×19, diameter=64–127
Stone accuracy 54.31%; macro 26.91%; overcounts 119; undercounts 10864
```
[[12148    99    20     0]
 [ 9622   908     0     0]
 [  560    70     0     0]
 [   53   207   352     0]]
```

Overcounts only:
```
[[ 0 99 20  0]
 [ 0  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [9622    0    0    0]
 [ 560   70    0    0]
 [  53  207  352    0]]
```

## Main asynchronous model: 19×19, diameter=9–16
Stone accuracy 88.87%; macro 71.97%; overcounts 4041; undercounts 9315
```
[[51210  3992     4     0]
 [ 6554 36696    13     0]
 [  833   697   310    32]
 [  373   608   250 18416]]
```

Overcounts only:
```
[[   0 3992    4    0]
 [   0    0   13    0]
 [   0    0    0   32]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [6554    0    0    0]
 [ 833  697    0    0]
 [ 373  608  250    0]]
```

## Main asynchronous model: 19×19, chain_distance_vs_depth=inside
Stone accuracy 93.54%; macro 92.82%; overcounts 4246; undercounts 17861
```
[[ 69930   4001      4      0]
 [ 10663  78218    138      0]
 [  2736   1147  41878    103]
 [  1590   1269    456 129876]]
```

Overcounts only:
```
[[   0 4001    4    0]
 [   0    0  138    0]
 [   0    0    0  103]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [10663     0     0     0]
 [ 2736  1147     0     0]
 [ 1590  1269   456     0]]
```

## Main asynchronous model: 19×19, chain_distance_vs_depth=outside
Stone accuracy 31.63%; macro 29.14%; overcounts 215; undercounts 106750
```
[[42958   195    20     0]
 [43693  2207     0     0]
 [28562  3374    77     0]
 [20589  8635  1897  4249]]
```

Overcounts only:
```
[[  0 195  20   0]
 [  0   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [43693     0     0     0]
 [28562  3374     0     0]
 [20589  8635  1897     0]]
```

## Main asynchronous model: 19×19, liberties_vs_grid_light_cone=inside
Stone accuracy 74.11%; macro 72.36%; overcounts 4461; undercounts 124611
```
[[112888   4196     24      0]
 [ 54356  80425    138      0]
 [ 31298   4521  41955    103]
 [ 22179   9904   2353 134125]]
```

Overcounts only:
```
[[   0 4196   24    0]
 [   0    0  138    0]
 [   0    0    0  103]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [54356     0     0     0]
 [31298  4521     0     0]
 [22179  9904  2353     0]]
```

## Main asynchronous model: 19×19, cycle=acyclic
Stone accuracy 73.76%; macro 72.52%; overcounts 4362; undercounts 115516
```
[[109154   4195     24      0]
 [ 52759  79732     70      0]
 [ 27745   3474  40330     73]
 [ 20702   8706   2130 107737]]
```

Overcounts only:
```
[[   0 4195   24    0]
 [   0    0   70    0]
 [   0    0    0   73]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [52759     0     0     0]
 [27745  3474     0     0]
 [20702  8706  2130     0]]
```

## Main asynchronous model: 19×19, cycle=cyclic
Stone accuracy 77.92%; macro 61.36%; overcounts 99; undercounts 9095
```
[[ 3734     1     0     0]
 [ 1597   693    68     0]
 [ 3553  1047  1625    30]
 [ 1477  1198   223 26388]]
```

Overcounts only:
```
[[ 0  1  0  0]
 [ 0  0 68  0]
 [ 0  0  0 30]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1597    0    0    0]
 [3553 1047    0    0]
 [1477 1198  223    0]]
```

## Main asynchronous model: 19×19, chain_size=0–1
Stone accuracy 100.00%; macro 99.99%; overcounts 3; undercounts 0
```
[[ 8495     1     0     0]
 [    0 22318     2     0]
 [    0     0 24228     0]
 [    0     0     0 13752]]
```

Overcounts only:
```
[[0 1 0 0]
 [0 0 2 0]
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

## Main asynchronous model: 19×19, chain_size=129+
Stone accuracy 24.95%; macro 25.52%; overcounts 86; undercounts 88433
```
[[28750    86     0     0]
 [28165   599     0     0]
 [26975  3179    77     0]
 [20536  8313  1265     9]]
```

Overcounts only:
```
[[ 0 86  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [28165     0     0     0]
 [26975  3179     0     0]
 [20536  8313  1265     0]]
```

## Main asynchronous model: 19×19, chain_size=17–32
Stone accuracy 83.83%; macro 71.50%; overcounts 39; undercounts 6858
```
[[ 1257     3     0     0]
 [ 4348 26415     8     0]
 [  756   655   208    28]
 [  368   584   147  7883]]
```

Overcounts only:
```
[[ 0  3  0  0]
 [ 0  0  8  0]
 [ 0  0  0 28]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4348    0    0    0]
 [ 756  655    0    0]
 [ 368  584  147    0]]
```

## Main asynchronous model: 19×19, chain_size=2–4
Stone accuracy 99.86%; macro 99.82%; overcounts 27; undercounts 81
```
[[ 3831     3     0     0]
 [   60 13867    23     0]
 [    0     2 13974     1]
 [    0     0    19 47969]]
```

Overcounts only:
```
[[ 0  3  0  0]
 [ 0  0 23  0]
 [ 0  0  0  1]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [60  0  0  0]
 [ 0  2  0  0]
 [ 0  0 19  0]]
```

## Main asynchronous model: 19×19, chain_size=33–64
Stone accuracy 47.72%; macro 45.18%; overcounts 10; undercounts 13236
```
[[5264   10    0    0]
 [7317  729    0    0]
 [2928  545   19    0]
 [1217  776  453 6077]]
```

Overcounts only:
```
[[ 0 10  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [7317    0    0    0]
 [2928  545    0    0]
 [1217  776  453    0]]
```

## Main asynchronous model: 19×19, chain_size=5–8
Stone accuracy 97.94%; macro 95.33%; overcounts 144; undercounts 710
```
[[ 1844     1     0     0]
 [  693  3851   100     0]
 [    0     6  3146    43]
 [    0     0    11 31669]]
```

Overcounts only:
```
[[  0   1   0   0]
 [  0   0 100   0]
 [  0   0   0  43]
 [  0   0   0   0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [693   0   0   0]
 [  0   6   0   0]
 [  0   0  11   0]]
```

## Main asynchronous model: 19×19, chain_size=65–128
Stone accuracy 54.31%; macro 26.91%; overcounts 119; undercounts 10864
```
[[12148    99    20     0]
 [ 9622   908     0     0]
 [  560    70     0     0]
 [   53   207   352     0]]
```

Overcounts only:
```
[[ 0 99 20  0]
 [ 0  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [9622    0    0    0]
 [ 560   70    0    0]
 [  53  207  352    0]]
```

## Main asynchronous model: 19×19, chain_size=9–16
Stone accuracy 91.42%; macro 82.41%; overcounts 4033; undercounts 4429
```
[[51299  3993     4     0]
 [ 4151 11738     5     0]
 [   79    64   303    31]
 [    5    24   106 26766]]
```

Overcounts only:
```
[[   0 3993    4    0]
 [   0    0    5    0]
 [   0    0    0   31]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4151    0    0    0]
 [  79   64    0    0]
 [   5   24  106    0]]
```

## Main asynchronous model: 19×19, edge_distance=0–0
Stone accuracy 96.90%; macro 98.53%; overcounts 73; undercounts 3391
```
[[ 5930     1     0     0]
 [ 3366 58713    30     0]
 [    0     5 13651    42]
 [    0     0    20 30049]]
```

Overcounts only:
```
[[ 0  1  0  0]
 [ 0  0 30  0]
 [ 0  0  0 42]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3366    0    0    0]
 [   0    5    0    0]
 [   0    0   20    0]]
```

## Main asynchronous model: 19×19, edge_distance=1–1
Stone accuracy 52.83%; macro 43.19%; overcounts 4155; undercounts 106763
```
[[83821  4094    24     0]
 [41001  8382     9     0]
 [30007  3852  6442    28]
 [20826  8974  2103 25571]]
```

Overcounts only:
```
[[   0 4094   24    0]
 [   0    0    9    0]
 [   0    0    0   28]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [41001     0     0     0]
 [30007  3852     0     0]
 [20826  8974  2103     0]]
```

## Main asynchronous model: 19×19, edge_distance=2–2
Stone accuracy 85.22%; macro 79.79%; overcounts 186; undercounts 8262
```
[[13489    83     0     0]
 [ 6372  3581    82     0]
 [  474   249  5664    21]
 [  730   327   110 25986]]
```

Overcounts only:
```
[[ 0 83  0  0]
 [ 0  0 82  0]
 [ 0  0  0 21]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [6372    0    0    0]
 [ 474  249    0    0]
 [ 730  327  110    0]]
```

## Main asynchronous model: 19×19, edge_distance=3–4
Stone accuracy 90.11%; macro 86.29%; overcounts 16; undercounts 5796
```
[[ 6621    12     0     0]
 [ 3593  5062     3     0]
 [  630   235  8575     1]
 [  623   603   112 32673]]
```

Overcounts only:
```
[[ 0 12  0  0]
 [ 0  0  3  0]
 [ 0  0  0  1]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3593    0    0    0]
 [ 630  235    0    0]
 [ 623  603  112    0]]
```

## Main asynchronous model: 19×19, edge_distance=5–8
Stone accuracy 98.79%; macro 98.55%; overcounts 31; undercounts 399
```
[[ 3018     6     0     0]
 [   24  4615    14     0]
 [  187   180  7578    11]
 [    0     0     8 19783]]
```

Overcounts only:
```
[[ 0  6  0  0]
 [ 0  0 14  0]
 [ 0  0  0 11]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [ 24   0   0   0]
 [187 180   0   0]
 [  0   0   8   0]]
```

## Main asynchronous model: 19×19, edge_distance=9+
Stone accuracy 100.00%; macro 100.00%; overcounts 0; undercounts 0
```
[[ 9  0  0  0]
 [ 0 72  0  0]
 [ 0  0 45  0]
 [ 0  0  0 63]]
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

## Main asynchronous model: 25×25, all=all
Stone accuracy 75.40%; macro 73.38%; overcounts 7366; undercounts 103370
```
[[116590   7042     46      0]
 [ 54128  60163    205      2]
 [ 17759    411  36083     71]
 [ 26304   3624   1144 126590]]
```

Overcounts only:
```
[[   0 7042   46    0]
 [   0    0  205    2]
 [   0    0    0   71]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [54128     0     0     0]
 [17759   411     0     0]
 [26304  3624  1144     0]]
```

## Main asynchronous model: 25×25, diameter=0–4
Stone accuracy 99.85%; macro 99.80%; overcounts 87; undercounts 146
```
[[12193    14     6     0]
 [  125 32448    43     0]
 [    0    14 35008    24]
 [    0     0     7 74666]]
```

Overcounts only:
```
[[ 0 14  6  0]
 [ 0  0 43  0]
 [ 0  0  0 24]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [125   0   0   0]
 [  0  14   0   0]
 [  0   0   7   0]]
```

## Main asynchronous model: 25×25, diameter=128+
Stone accuracy 44.99%; macro 25.39%; overcounts 438; undercounts 50612
```
[[41169   435     3     0]
 [23305   338     0     0]
 [ 6267    51     0     0]
 [17980  2391   618   251]]
```

Overcounts only:
```
[[  0 435   3   0]
 [  0   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [23305     0     0     0]
 [ 6267    51     0     0]
 [17980  2391   618     0]]
```

## Main asynchronous model: 25×25, diameter=17–31
Stone accuracy 83.38%; macro 65.38%; overcounts 6609; undercounts 8350
```
[[47006  6507    37     0]
 [ 6701 21138    23     2]
 [  596   172    83    40]
 [  233   236   412  6832]]
```

Overcounts only:
```
[[   0 6507   37    0]
 [   0    0   23    2]
 [   0    0    0   40]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [6701    0    0    0]
 [ 596  172    0    0]
 [ 233  236  412    0]]
```

## Main asynchronous model: 25×25, diameter=32–63
Stone accuracy 50.74%; macro 43.45%; overcounts 21; undercounts 4944
```
[[2151    0    0    0]
 [2856  219   21    0]
 [ 720    0    0    0]
 [1255  113    0 2745]]
```

Overcounts only:
```
[[ 0  0  0  0]
 [ 0  0 21  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2856    0    0    0]
 [ 720    0    0    0]
 [1255  113    0    0]]
```

## Main asynchronous model: 25×25, diameter=5–8
Stone accuracy 97.98%; macro 93.22%; overcounts 80; undercounts 533
```
[[  582    12     0     0]
 [  489  1790    61     0]
 [    0     6   878     7]
 [    0     1    37 26548]]
```

Overcounts only:
```
[[ 0 12  0  0]
 [ 0  0 61  0]
 [ 0  0  0  7]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [489   0   0   0]
 [  0   6   0   0]
 [  0   1  37   0]]
```

## Main asynchronous model: 25×25, diameter=64–127
Stone accuracy 25.31%; macro 29.53%; overcounts 43; undercounts 37061
```
[[10440    18     0     0]
 [18980   894    25     0]
 [10176   156     0     0]
 [ 6836   881    32  1242]]
```

Overcounts only:
```
[[ 0 18  0  0]
 [ 0  0 25  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [18980     0     0     0]
 [10176   156     0     0]
 [ 6836   881    32     0]]
```

## Main asynchronous model: 25×25, diameter=9–16
Stone accuracy 91.99%; macro 88.65%; overcounts 88; undercounts 1724
```
[[ 3049    56     0     0]
 [ 1672  3336    32     0]
 [    0    12   114     0]
 [    0     2    38 14306]]
```

Overcounts only:
```
[[ 0 56  0  0]
 [ 0  0 32  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1672    0    0    0]
 [   0   12    0    0]
 [   0    2   38    0]]
```

## Main asynchronous model: 25×25, chain_distance_vs_depth=inside
Stone accuracy 94.08%; macro 93.46%; overcounts 6864; undercounts 10753
```
[[ 62830   6589     43      0]
 [  8987  58712    159      2]
 [   596    204  36083     71]
 [   233    239    494 122352]]
```

Overcounts only:
```
[[   0 6589   43    0]
 [   0    0  159    2]
 [   0    0    0   71]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [8987    0    0    0]
 [ 596  204    0    0]
 [ 233  239  494    0]]
```

## Main asynchronous model: 25×25, chain_distance_vs_depth=outside
Stone accuracy 38.97%; macro 28.65%; overcounts 502; undercounts 92617
```
[[53760   453     3     0]
 [45141  1451    46     0]
 [17163   207     0     0]
 [26071  3385   650  4238]]
```

Overcounts only:
```
[[  0 453   3   0]
 [  0   0  46   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [45141     0     0     0]
 [17163   207     0     0]
 [26071  3385   650     0]]
```

## Main asynchronous model: 25×25, liberties_vs_grid_light_cone=inside
Stone accuracy 75.40%; macro 73.38%; overcounts 7366; undercounts 103370
```
[[116590   7042     46      0]
 [ 54128  60163    205      2]
 [ 17759    411  36083     71]
 [ 26304   3624   1144 126590]]
```

Overcounts only:
```
[[   0 7042   46    0]
 [   0    0  205    2]
 [   0    0    0   71]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [54128     0     0     0]
 [17759   411     0     0]
 [26304  3624  1144     0]]
```

## Main asynchronous model: 25×25, cycle=acyclic
Stone accuracy 74.45%; macro 72.93%; overcounts 7239; undercounts 97629
```
[[114167   7017     46      0]
 [ 51134  59195    126      2]
 [ 16551    246  34626     48]
 [ 25049   3511   1138  97580]]
```

Overcounts only:
```
[[   0 7017   46    0]
 [   0    0  126    2]
 [   0    0    0   48]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [51134     0     0     0]
 [16551   246     0     0]
 [25049  3511  1138     0]]
```

## Main asynchronous model: 25×25, cycle=cyclic
Stone accuracy 85.23%; macro 67.37%; overcounts 127; undercounts 5741
```
[[ 2423    25     0     0]
 [ 2994   968    79     0]
 [ 1208   165  1457    23]
 [ 1255   113     6 29010]]
```

Overcounts only:
```
[[ 0 25  0  0]
 [ 0  0 79  0]
 [ 0  0  0 23]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2994    0    0    0]
 [1208  165    0    0]
 [1255  113    6    0]]
```

## Main asynchronous model: 25×25, chain_size=0–1
Stone accuracy 99.99%; macro 99.99%; overcounts 0; undercounts 4
```
[[ 8280     0     0     0]
 [    3 18582     0     0]
 [    0     1 18800     0]
 [    0     0     0 10044]]
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
 [3 0 0 0]
 [0 1 0 0]
 [0 0 0 0]]
```

## Main asynchronous model: 25×25, chain_size=129+
Stone accuracy 37.69%; macro 25.28%; overcounts 453; undercounts 81520
```
[[48903   450     3     0]
 [36132   426     0     0]
 [16443   207     0     0]
 [24816  3272   650   251]]
```

Overcounts only:
```
[[  0 450   3   0]
 [  0   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [36132     0     0     0]
 [16443   207     0     0]
 [24816  3272   650     0]]
```

## Main asynchronous model: 25×25, chain_size=17–32
Stone accuracy 86.03%; macro 69.84%; overcounts 6628; undercounts 6144
```
[[47266  6526    37     0]
 [ 5097 21248    23     2]
 [  108    19    40    40]
 [  233   238   449 10114]]
```

Overcounts only:
```
[[   0 6526   37    0]
 [   0    0   23    2]
 [   0    0    0   40]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5097    0    0    0]
 [ 108   19    0    0]
 [ 233  238  449    0]]
```

## Main asynchronous model: 25×25, chain_size=2–4
Stone accuracy 99.89%; macro 99.80%; overcounts 14; undercounts 70
```
[[ 3566     1     6     0]
 [   59 12186     4     0]
 [    0    11 14116     3]
 [    0     0     0 44613]]
```

Overcounts only:
```
[[0 1 6 0]
 [0 0 4 0]
 [0 0 0 3]
 [0 0 0 0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [59  0  0  0]
 [ 0 11  0  0]
 [ 0  0  0  0]]
```

## Main asynchronous model: 25×25, chain_size=33–64
Stone accuracy 57.12%; macro 52.87%; overcounts 21; undercounts 4101
```
[[1575    0    0    0]
 [3460  191   21    0]
 [ 488  153   43    0]
 [   0    0    0 3681]]
```

Overcounts only:
```
[[ 0  0  0  0]
 [ 0  0 21  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3460    0    0    0]
 [ 488  153    0    0]
 [   0    0    0    0]]
```

## Main asynchronous model: 25×25, chain_size=5–8
Stone accuracy 98.68%; macro 95.96%; overcounts 75; undercounts 443
```
[[  842    13     0     0]
 [  411  2887    41     0]
 [    0     8  2788    21]
 [    0     0    24 32133]]
```

Overcounts only:
```
[[ 0 13  0  0]
 [ 0  0 41  0]
 [ 0  0  0 21]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [411   0   0   0]
 [  0   8   0   0]
 [  0   0  24   0]]
```

## Main asynchronous model: 25×25, chain_size=65–128
Stone accuracy 41.94%; macro 42.14%; overcounts 28; undercounts 9436
```
[[4074    3    0    0]
 [7348  835   25    0]
 [ 720    0    0    0]
 [1255  113    0 1926]]
```

Overcounts only:
```
[[ 0  3  0  0]
 [ 0  0 25  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [7348    0    0    0]
 [ 720    0    0    0]
 [1255  113    0    0]]
```

## Main asynchronous model: 25×25, chain_size=9–16
Stone accuracy 94.35%; macro 90.15%; overcounts 147; undercounts 1652
```
[[ 2084    49     0     0]
 [ 1618  3808    91     0]
 [    0    12   296     7]
 [    0     1    21 23828]]
```

Overcounts only:
```
[[ 0 49  0  0]
 [ 0  0 91  0]
 [ 0  0  0  7]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1618    0    0    0]
 [   0   12    0    0]
 [   0    1   21    0]]
```

## Main asynchronous model: 25×25, edge_distance=0–0
Stone accuracy 95.61%; macro 97.78%; overcounts 95; undercounts 3584
```
[[ 4901    13     0     0]
 [ 3569 39604    81     0]
 [    0    13  9166     1]
 [    0     1     1 26485]]
```

Overcounts only:
```
[[ 0 13  0  0]
 [ 0  0 81  0]
 [ 0  0  0  1]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3569    0    0    0]
 [   0   13    0    0]
 [   0    1    1    0]]
```

## Main asynchronous model: 25×25, edge_distance=1–1
Stone accuracy 53.80%; macro 40.72%; overcounts 6913; undercounts 92206
```
[[86503  6715    40     0]
 [44437  5608   101     2]
 [16551   232  4519    55]
 [26304  3621  1061 18811]]
```

Overcounts only:
```
[[   0 6715   40    0]
 [   0    0  101    2]
 [   0    0    0   55]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [44437     0     0     0]
 [16551   232     0     0]
 [26304  3621  1061     0]]
```

## Main asynchronous model: 25×25, edge_distance=2–2
Stone accuracy 92.89%; macro 85.71%; overcounts 298; undercounts 2603
```
[[13094   298     0     0]
 [ 1827  2763     0     0]
 [  720     3  4155     0]
 [    0     2    51 17911]]
```

Overcounts only:
```
[[  0 298   0   0]
 [  0   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1827    0    0    0]
 [ 720    3    0    0]
 [   0    2   51    0]]
```

## Main asynchronous model: 25×25, edge_distance=3–4
Stone accuracy 92.10%; macro 87.90%; overcounts 34; undercounts 3778
```
[[ 5021    13     6     0]
 [ 3109  4809     2     0]
 [  488   157  6929    13]
 [    0     0    24 27705]]
```

Overcounts only:
```
[[ 0 13  6  0]
 [ 0  0  2  0]
 [ 0  0  0 13]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [3109    0    0    0]
 [ 488  157    0    0]
 [   0    0   24    0]]
```

## Main asynchronous model: 25×25, edge_distance=5–8
Stone accuracy 97.68%; macro 95.66%; overcounts 26; undercounts 1198
```
[[ 6369     3     0     0]
 [ 1186  5813    21     0]
 [    0     6  9028     2]
 [    0     0     6 30216]]
```

Overcounts only:
```
[[ 0  3  0  0]
 [ 0  0 21  0]
 [ 0  0  0  2]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1186    0    0    0]
 [   0    6    0    0]
 [   0    0    6    0]]
```

## Main asynchronous model: 25×25, edge_distance=9+
Stone accuracy 99.99%; macro 100.00%; overcounts 0; undercounts 1
```
[[ 702    0    0    0]
 [   0 1566    0    0]
 [   0    0 2286    0]
 [   0    0    1 5462]]
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
 [0 0 1 0]]
```

## Main asynchronous model: 37×37, all=all
Stone accuracy 65.42%; macro 62.23%; overcounts 9571; undercounts 168332
```
[[128038   9123    207     26]
 [ 69178  52299     50      0]
 [ 45127    945  35105    165]
 [ 51227   1510    345 121140]]
```

Overcounts only:
```
[[   0 9123  207   26]
 [   0    0   50    0]
 [   0    0    0  165]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [69178     0     0     0]
 [45127   945     0     0]
 [51227  1510   345     0]]
```

## Main asynchronous model: 37×37, diameter=0–4
Stone accuracy 99.86%; macro 99.81%; overcounts 107; undercounts 105
```
[[10714    23     0     0]
 [   30 28416    21     0]
 [    0    43 34184    63]
 [    0     0    32 77692]]
```

Overcounts only:
```
[[ 0 23  0  0]
 [ 0  0 21  0]
 [ 0  0  0 63]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [30  0  0  0]
 [ 0 43  0  0]
 [ 0  0 32  0]]
```

## Main asynchronous model: 37×37, diameter=128+
Stone accuracy 22.93%; macro 26.30%; overcounts 224; undercounts 87383
```
[[24113   223     0     0]
 [30250  1933     1     0]
 [27498   520    26     0]
 [28083   903   129     0]]
```

Overcounts only:
```
[[  0 223   0   0]
 [  0   0   1   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [30250     0     0     0]
 [27498   520     0     0]
 [28083   903   129     0]]
```

## Main asynchronous model: 37×37, diameter=17–31
Stone accuracy 69.99%; macro 59.18%; overcounts 140; undercounts 4382
```
[[3460  118   13    0]
 [4011 2847    9    0]
 [ 306   18    0    0]
 [   0   21   26 4237]]
```

Overcounts only:
```
[[  0 118  13   0]
 [  0   0   9   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4011    0    0    0]
 [ 306   18    0    0]
 [   0   21   26    0]]
```

## Main asynchronous model: 37×37, diameter=32–63
Stone accuracy 85.58%; macro 63.92%; overcounts 8978; undercounts 7034
```
[[76797  8717   194    26]
 [ 6253 16481     0     0]
 [  165    51    58    41]
 [  323   113   129  1712]]
```

Overcounts only:
```
[[   0 8717  194   26]
 [   0    0    0    0]
 [   0    0    0   41]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [6253    0    0    0]
 [ 165   51    0    0]
 [ 323  113  129    0]]
```

## Main asynchronous model: 37×37, diameter=5–8
Stone accuracy 99.00%; macro 92.70%; overcounts 106; undercounts 175
```
[[  413    28     0     0]
 [  164   971    17     0]
 [    0     3   836    61]
 [    0     0     8 25678]]
```

Overcounts only:
```
[[ 0 28  0  0]
 [ 0  0 17  0]
 [ 0  0  0 61]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [164   0   0   0]
 [  0   3   0   0]
 [  0   0   8   0]]
```

## Main asynchronous model: 37×37, diameter=64–127
Stone accuracy 16.22%; macro 26.49%; overcounts 6; undercounts 68071
```
[[11640     6     0     0]
 [27311   688     0     0]
 [17158   310     1     0]
 [22821   471     0   855]]
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
[[    0     0     0     0]
 [27311     0     0     0]
 [17158   310     0     0]
 [22821   471     0     0]]
```

## Main asynchronous model: 37×37, diameter=9–16
Stone accuracy 91.50%; macro 81.42%; overcounts 10; undercounts 1182
```
[[  901     8     0     0]
 [ 1159   963     2     0]
 [    0     0     0     0]
 [    0     2    21 10966]]
```

Overcounts only:
```
[[0 8 0 0]
 [0 0 2 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1159    0    0    0]
 [   0    0    0    0]
 [   0    2   21    0]]
```

## Main asynchronous model: 37×37, chain_distance_vs_depth=inside
Stone accuracy 97.02%; macro 95.82%; overcounts 363; undercounts 5844
```
[[ 15488    177     13      0]
 [  5364  33197     49      0]
 [   306     64  35020    124]
 [     0     23     87 118573]]
```

Overcounts only:
```
[[  0 177  13   0]
 [  0   0  49   0]
 [  0   0   0 124]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5364    0    0    0]
 [ 306   64    0    0]
 [   0   23   87    0]]
```

## Main asynchronous model: 37×37, chain_distance_vs_depth=outside
Stone accuracy 43.89%; macro 30.08%; overcounts 9208; undercounts 162488
```
[[112550   8946    194     26]
 [ 63814  19102      1      0]
 [ 44821    881     85     41]
 [ 51227   1487    258   2567]]
```

Overcounts only:
```
[[   0 8946  194   26]
 [   0    0    1    0]
 [   0    0    0   41]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [63814     0     0     0]
 [44821   881     0     0]
 [51227  1487   258     0]]
```

## Main asynchronous model: 37×37, liberties_vs_grid_light_cone=inside
Stone accuracy 66.84%; macro 63.44%; overcounts 9569; undercounts 153134
```
[[122838   9121    207     26]
 [ 64897  48930     50      0]
 [ 40789    927  35105    165]
 [ 44860   1329    332 121122]]
```

Overcounts only:
```
[[   0 9121  207   26]
 [   0    0   50    0]
 [   0    0    0  165]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [64897     0     0     0]
 [40789   927     0     0]
 [44860  1329   332     0]]
```

## Main asynchronous model: 37×37, liberties_vs_grid_light_cone=outside
Stone accuracy 36.10%; macro 36.07%; overcounts 2; undercounts 15198
```
[[5200    2    0    0]
 [4281 3369    0    0]
 [4338   18    0    0]
 [6367  181   13   18]]
```

Overcounts only:
```
[[0 2 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4281    0    0    0]
 [4338   18    0    0]
 [6367  181   13    0]]
```

## Main asynchronous model: 37×37, cycle=acyclic
Stone accuracy 63.29%; macro 60.49%; overcounts 9447; undercounts 167047
```
[[127049   9095    207     26]
 [ 68231  51358     39      0]
 [ 44821    926  33760     80]
 [ 51227   1510    332  92074]]
```

Overcounts only:
```
[[   0 9095  207   26]
 [   0    0   39    0]
 [   0    0    0   80]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [68231     0     0     0]
 [44821   926     0     0]
 [51227  1510   332     0]]
```

## Main asynchronous model: 37×37, cycle=cyclic
Stone accuracy 95.83%; macro 80.85%; overcounts 124; undercounts 1285
```
[[  989    28     0     0]
 [  947   941    11     0]
 [  306    19  1345    85]
 [    0     0    13 29066]]
```

Overcounts only:
```
[[ 0 28  0  0]
 [ 0  0 11  0]
 [ 0  0  0 85]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [947   0   0   0]
 [306  19   0   0]
 [  0   0  13   0]]
```

## Main asynchronous model: 37×37, chain_size=0–1
Stone accuracy 100.00%; macro 100.00%; overcounts 0; undercounts 1
```
[[ 7326     0     0     0]
 [    1 17981     0     0]
 [    0     0 20475     0]
 [    0     0     0 15012]]
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
 [1 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```

## Main asynchronous model: 37×37, chain_size=129+
Stone accuracy 20.12%; macro 25.90%; overcounts 230; undercounts 151049
```
[[35753   229     0     0]
 [53156  2319     1     0]
 [44656   830    27     0]
 [50904  1374   129     0]]
```

Overcounts only:
```
[[  0 229   0   0]
 [  0   0   1   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [53156     0     0     0]
 [44656   830     0     0]
 [50904  1374   129     0]]
```

## Main asynchronous model: 37×37, chain_size=17–32
Stone accuracy 78.31%; macro 78.76%; overcounts 142; undercounts 4413
```
[[3613  118   13    0]
 [4365 2950   11    0]
 [   0    0    0    0]
 [   0   21   27 9879]]
```

Overcounts only:
```
[[  0 118  13   0]
 [  0   0  11   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [4365    0    0    0]
 [   0    0    0    0]
 [   0   21   27    0]]
```

## Main asynchronous model: 37×37, chain_size=2–4
Stone accuracy 99.92%; macro 99.84%; overcounts 47; undercounts 9
```
[[ 2903     4     0     0]
 [    5  8932    18     0]
 [    0     4 11644    25]
 [    0     0     0 44901]]
```

Overcounts only:
```
[[ 0  4  0  0]
 [ 0  0 18  0]
 [ 0  0  0 25]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [5 0 0 0]
 [0 4 0 0]
 [0 0 0 0]]
```

## Main asynchronous model: 37×37, chain_size=33–64
Stone accuracy 86.07%; macro 64.11%; overcounts 8978; undercounts 6422
```
[[76005  8717   194    26]
 [ 5317 16481     0     0]
 [  471    69    58    41]
 [  323   113   129  2621]]
```

Overcounts only:
```
[[   0 8717  194   26]
 [   0    0    0    0]
 [   0    0    0   41]
 [   0    0    0    0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5317    0    0    0]
 [ 471   69    0    0]
 [ 323  113  129    0]]
```

## Main asynchronous model: 37×37, chain_size=5–8
Stone accuracy 99.08%; macro 96.73%; overcounts 86; undercounts 207
```
[[  593    19     0     0]
 [  133  2207     9     0]
 [    0    41  2511    58]
 [    0     0    33 26337]]
```

Overcounts only:
```
[[ 0 19  0  0]
 [ 0  0  9  0]
 [ 0  0  0 58]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [133   0   0   0]
 [  0  41   0   0]
 [  0   0  33   0]]
```

## Main asynchronous model: 37×37, chain_size=65–128
Stone accuracy 33.32%; macro 68.45%; overcounts 0; undercounts 5341
```
[[ 792    0    0    0]
 [5341  302    0    0]
 [   0    0    0    0]
 [   0    0    0 1575]]
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
[[   0    0    0    0]
 [5341    0    0    0]
 [   0    0    0    0]
 [   0    0    0    0]]
```

## Main asynchronous model: 37×37, chain_size=9–16
Stone accuracy 95.99%; macro 85.81%; overcounts 88; undercounts 890
```
[[ 1053    36     0     0]
 [  860  1127    11     0]
 [    0     1   390    41]
 [    0     2    27 20815]]
```

Overcounts only:
```
[[ 0 36  0  0]
 [ 0  0 11  0]
 [ 0  0  0 41]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [860   0   0   0]
 [  0   1   0   0]
 [  0   2  27   0]]
```

## Main asynchronous model: 37×37, edge_distance=0–0
Stone accuracy 91.89%; macro 96.21%; overcounts 37; undercounts 5116
```
[[ 2588    13     0     0]
 [ 5111 30646     0     0]
 [    0     0  6717    24]
 [    0     0     5 18472]]
```

Overcounts only:
```
[[ 0 13  0  0]
 [ 0  0  0  0]
 [ 0  0  0 24]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5111    0    0    0]
 [   0    0    0    0]
 [   0    0    5    0]]
```

## Main asynchronous model: 37×37, edge_distance=1–1
Stone accuracy 43.70%; macro 32.16%; overcounts 9031; undercounts 150505
```
[[101374   8755    194     26]
 [ 51784   5693     15      0]
 [ 44821    881   3154     41]
 [ 51227   1508    284  13590]]
```

Overcounts only:
```
[[   0 8755  194   26]
 [   0    0   15    0]
 [   0    0    0   41]
 [   0    0    0    0]]
```

Undercounts only:
```
[[    0     0     0     0]
 [51784     0     0     0]
 [44821   881     0     0]
 [51227  1508   284     0]]
```

## Main asynchronous model: 37×37, edge_distance=2–2
Stone accuracy 89.13%; macro 84.67%; overcounts 376; undercounts 2667
```
[[ 9983   345    13     0]
 [ 2661  1966    17     0]
 [    0     4  2713     1]
 [    0     0     2 10294]]
```

Overcounts only:
```
[[  0 345  13   0]
 [  0   0  17   0]
 [  0   0   0   1]
 [  0   0   0   0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2661    0    0    0]
 [   0    4    0    0]
 [   0    0    2    0]]
```

## Main asynchronous model: 37×37, edge_distance=3–4
Stone accuracy 93.96%; macro 90.90%; overcounts 55; undercounts 2014
```
[[ 1529     1     0     0]
 [ 1968  3627    12     0]
 [    0     2  5374    42]
 [    0     2    42 21646]]
```

Overcounts only:
```
[[ 0  1  0  0]
 [ 0  0 12  0]
 [ 0  0  0 42]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [1968    0    0    0]
 [   0    2    0    0]
 [   0    2   42    0]]
```

## Main asynchronous model: 37×37, edge_distance=5–8
Stone accuracy 90.82%; macro 87.66%; overcounts 68; undercounts 5308
```
[[ 7884     9     0     0]
 [ 5257  5667     2     0]
 [    0    40  9011    57]
 [    0     0    11 30652]]
```

Overcounts only:
```
[[ 0  9  0  0]
 [ 0  0  2  0]
 [ 0  0  0 57]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [5257    0    0    0]
 [   0   40    0    0]
 [   0    0   11    0]]
```

## Main asynchronous model: 37×37, edge_distance=9+
Stone accuracy 94.17%; macro 90.59%; overcounts 4; undercounts 2722
```
[[ 4680     0     0     0]
 [ 2397  4700     4     0]
 [  306    18  8136     0]
 [    0     0     1 26486]]
```

Overcounts only:
```
[[0 0 0 0]
 [0 0 4 0]
 [0 0 0 0]
 [0 0 0 0]]
```

Undercounts only:
```
[[   0    0    0    0]
 [2397    0    0    0]
 [ 306   18    0    0]
 [   0    0    1    0]]
```

## All witness confusion matrices

20261006T183555928117Z_a0ccc727_s0 size=13 depth=8: over=0 under=192
```
[[192   0   0   0]
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
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
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```
20261006T183555928117Z_a0ccc727_s0 size=13 depth=16: over=0 under=192
```
[[192   0   0   0]
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
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
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```
20261006T183555928117Z_a0ccc727_s0 size=13 depth=32: over=227 under=77
```
[[ 80   1   0 111]
 [ 77   0   0 115]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[  0   1   0 111]
 [  0   0   0 115]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [77  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
20261006T183555928117Z_a0ccc727_s0 size=13 depth=64: over=384 under=0
```
[[  0   0   1 191]
 [  0   0   0 192]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[  0   0   1 191]
 [  0   0   0 192]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T183555928117Z_a0ccc727_s0 size=13 depth=128: over=384 under=0
```
[[  0   0   0 192]
 [  0   0   0 192]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[  0   0   0 192]
 [  0   0   0 192]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T183555928117Z_a0ccc727_s0 size=13 depth=256: over=384 under=0
```
[[  0   0   0 192]
 [  0   0   0 192]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[  0   0   0 192]
 [  0   0   0 192]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T184135582937Z_88b2ee3f_s0 size=13 depth=8: over=0 under=64
```
[[64  0  0  0]
 [64  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
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
 [64  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
20261006T184135582937Z_88b2ee3f_s0 size=13 depth=16: over=0 under=64
```
[[64  0  0  0]
 [64  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
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
 [64  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
20261006T184135582937Z_88b2ee3f_s0 size=13 depth=32: over=0 under=63
```
[[64  0  0  0]
 [63  1  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
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
 [63  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
20261006T184135582937Z_88b2ee3f_s0 size=13 depth=64: over=0 under=52
```
[[64  0  0  0]
 [52 12  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
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
 [52  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
20261006T184135582937Z_88b2ee3f_s0 size=13 depth=128: over=54 under=21
```
[[21 43  0  0]
 [21 32 11  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0 43  0  0]
 [ 0  0 11  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [21  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
20261006T184135582937Z_88b2ee3f_s0 size=13 depth=256: over=115 under=0
```
[[ 0 22 41  1]
 [ 0 13 39 12]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0 22 41  1]
 [ 0  0 39 12]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T185959689439Z_3c9250e5_s0 size=13 depth=8: over=0 under=64
```
[[64  0  0  0]
 [64  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
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
 [64  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
20261006T185959689439Z_3c9250e5_s0 size=13 depth=16: over=0 under=42
```
[[64  0  0  0]
 [42 22  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
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
 [42  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
20261006T185959689439Z_3c9250e5_s0 size=13 depth=32: over=0 under=53
```
[[64  0  0  0]
 [53 11  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
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
 [53  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
20261006T185959689439Z_3c9250e5_s0 size=13 depth=64: over=0 under=58
```
[[64  0  0  0]
 [58  6  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
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
 [58  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
20261006T185959689439Z_3c9250e5_s0 size=13 depth=128: over=0 under=63
```
[[64  0  0  0]
 [63  1  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
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
 [63  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
20261006T185959689439Z_3c9250e5_s0 size=13 depth=256: over=0 under=63
```
[[64  0  0  0]
 [63  1  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
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
 [63  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
20261006T200156953891Z_3768a5c8_s0 size=13 depth=8: over=0 under=64
```
[[64  0  0  0]
 [64  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
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
 [64  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
20261006T200156953891Z_3768a5c8_s0 size=13 depth=16: over=62 under=0
```
[[33 31  0  0]
 [ 0 33 31  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0 31  0  0]
 [ 0  0 31  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T200156953891Z_3768a5c8_s0 size=13 depth=32: over=19 under=7
```
[[64  0  0  0]
 [ 7 38 19  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0  0  0  0]
 [ 0  0 19  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [7 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T200156953891Z_3768a5c8_s0 size=13 depth=64: over=14 under=0
```
[[64  0  0  0]
 [ 0 50 14  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0  0  0  0]
 [ 0  0 14  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T200156953891Z_3768a5c8_s0 size=13 depth=128: over=14 under=0
```
[[64  0  0  0]
 [ 0 50 14  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0  0  0  0]
 [ 0  0 14  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T200156953891Z_3768a5c8_s0 size=13 depth=256: over=9 under=0
```
[[64  0  0  0]
 [ 0 55  9  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
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
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T200156953891Z_3768a5c8_s0 size=13 depth=8: over=0 under=64
```
[[64  0  0  0]
 [64  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
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
 [64  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
20261006T200156953891Z_3768a5c8_s0 size=13 depth=16: over=76 under=0
```
[[26 38  0  0]
 [ 0 26 38  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0 38  0  0]
 [ 0  0 38  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T200156953891Z_3768a5c8_s0 size=13 depth=32: over=29 under=4
```
[[64  0  0  0]
 [ 4 31 29  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0  0  0  0]
 [ 0  0 29  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [4 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T200156953891Z_3768a5c8_s0 size=13 depth=64: over=20 under=0
```
[[64  0  0  0]
 [ 0 44 20  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0  0  0  0]
 [ 0  0 20  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T200156953891Z_3768a5c8_s0 size=13 depth=128: over=20 under=0
```
[[64  0  0  0]
 [ 0 44 20  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0  0  0  0]
 [ 0  0 20  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T200156953891Z_3768a5c8_s0 size=13 depth=256: over=19 under=0
```
[[64  0  0  0]
 [ 0 45 19  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0  0  0  0]
 [ 0  0 19  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T200156953891Z_3768a5c8_s0 size=19 depth=8: over=0 under=64
```
[[64  0  0  0]
 [64  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
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
 [64  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
20261006T200156953891Z_3768a5c8_s0 size=19 depth=16: over=0 under=64
```
[[64  0  0  0]
 [64  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
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
 [64  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
20261006T200156953891Z_3768a5c8_s0 size=19 depth=32: over=36 under=7
```
[[50 14  0  0]
 [ 7 35 22  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0 14  0  0]
 [ 0  0 22  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [7 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T200156953891Z_3768a5c8_s0 size=19 depth=64: over=36 under=3
```
[[50 14  0  0]
 [ 3 39 22  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0 14  0  0]
 [ 0  0 22  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [3 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T200156953891Z_3768a5c8_s0 size=19 depth=128: over=32 under=0
```
[[50 14  0  0]
 [ 0 46 18  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0 14  0  0]
 [ 0  0 18  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T200156953891Z_3768a5c8_s0 size=19 depth=256: over=32 under=0
```
[[50 14  0  0]
 [ 0 46 18  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0 14  0  0]
 [ 0  0 18  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T200156953891Z_3768a5c8_s0 size=25 depth=8: over=0 under=64
```
[[64  0  0  0]
 [64  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
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
 [64  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
20261006T200156953891Z_3768a5c8_s0 size=25 depth=16: over=0 under=64
```
[[64  0  0  0]
 [64  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
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
 [64  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
20261006T200156953891Z_3768a5c8_s0 size=25 depth=32: over=45 under=8
```
[[48 16  0  0]
 [ 8 27  9 20]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0 16  0  0]
 [ 0  0  9 20]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [8 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T200156953891Z_3768a5c8_s0 size=25 depth=64: over=41 under=0
```
[[48 16  0  0]
 [ 0 39  5 20]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0 16  0  0]
 [ 0  0  5 20]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T200156953891Z_3768a5c8_s0 size=25 depth=128: over=41 under=0
```
[[48 16  0  0]
 [ 0 39  3 22]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0 16  0  0]
 [ 0  0  3 22]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T200156953891Z_3768a5c8_s0 size=25 depth=256: over=41 under=0
```
[[48 16  0  0]
 [ 0 39  3 22]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0 16  0  0]
 [ 0  0  3 22]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T200156953891Z_3768a5c8_s0 size=37 depth=8: over=0 under=64
```
[[64  0  0  0]
 [64  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
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
 [64  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
20261006T200156953891Z_3768a5c8_s0 size=37 depth=16: over=0 under=64
```
[[64  0  0  0]
 [64  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
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
 [64  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
20261006T200156953891Z_3768a5c8_s0 size=37 depth=32: over=0 under=64
```
[[64  0  0  0]
 [64  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
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
 [64  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
20261006T200156953891Z_3768a5c8_s0 size=37 depth=64: over=46 under=0
```
[[48 16  0  0]
 [ 0 34 14 16]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0 16  0  0]
 [ 0  0 14 16]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T200156953891Z_3768a5c8_s0 size=37 depth=128: over=39 under=0
```
[[48 16  0  0]
 [ 0 41  0 23]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0 16  0  0]
 [ 0  0  0 23]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T200156953891Z_3768a5c8_s0 size=37 depth=256: over=61 under=0
```
[[48 13  3  0]
 [ 0 19  9 36]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0 13  3  0]
 [ 0  0  9 36]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T201026705778Z_5c97d885_s0 size=13 depth=8: over=0 under=192
```
[[192   0   0   0]
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
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
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```
20261006T201026705778Z_5c97d885_s0 size=13 depth=16: over=128 under=14
```
[[136  53   3   0]
 [ 14 106  72   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[ 0 53  3  0]
 [ 0  0 72  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [14  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
20261006T201026705778Z_5c97d885_s0 size=13 depth=32: over=110 under=0
```
[[ 98  94   0   0]
 [  0 176  16   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[ 0 94  0  0]
 [ 0  0 16  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T201026705778Z_5c97d885_s0 size=13 depth=64: over=132 under=0
```
[[ 97  95   0   0]
 [  0 155  37   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[ 0 95  0  0]
 [ 0  0 37  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T201026705778Z_5c97d885_s0 size=13 depth=128: over=195 under=0
```
[[ 97  95   0   0]
 [  0  92 100   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[  0  95   0   0]
 [  0   0 100   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T201026705778Z_5c97d885_s0 size=13 depth=256: over=205 under=0
```
[[ 97  95   0   0]
 [  0  82 110   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[  0  95   0   0]
 [  0   0 110   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T201026705778Z_5c97d885_s0 size=19 depth=8: over=0 under=192
```
[[192   0   0   0]
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
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
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```
20261006T201026705778Z_5c97d885_s0 size=19 depth=16: over=0 under=192
```
[[192   0   0   0]
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
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
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```
20261006T201026705778Z_5c97d885_s0 size=19 depth=32: over=95 under=0
```
[[ 97  95   0   0]
 [  0 192   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[ 0 95  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T201026705778Z_5c97d885_s0 size=19 depth=64: over=146 under=0
```
[[ 95  97   0   0]
 [  0 143  49   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[ 0 97  0  0]
 [ 0  0 49  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T201026705778Z_5c97d885_s0 size=19 depth=128: over=218 under=0
```
[[ 95  97   0   0]
 [  0  71 121   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[  0  97   0   0]
 [  0   0 121   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T201026705778Z_5c97d885_s0 size=19 depth=256: over=233 under=0
```
[[ 95  97   0   0]
 [  0  56 136   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[  0  97   0   0]
 [  0   0 136   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T201026705778Z_5c97d885_s0 size=25 depth=8: over=0 under=192
```
[[192   0   0   0]
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
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
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```
20261006T201026705778Z_5c97d885_s0 size=25 depth=16: over=0 under=192
```
[[192   0   0   0]
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
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
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```
20261006T201026705778Z_5c97d885_s0 size=25 depth=32: over=71 under=68
```
[[121  71   0   0]
 [ 68 124   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[ 0 71  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [68  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
20261006T201026705778Z_5c97d885_s0 size=25 depth=64: over=162 under=0
```
[[ 77 115   0   0]
 [  0 145  47   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[  0 115   0   0]
 [  0   0  47   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T201026705778Z_5c97d885_s0 size=25 depth=128: over=224 under=0
```
[[ 77 115   0   0]
 [  0  83 109   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[  0 115   0   0]
 [  0   0 109   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T201026705778Z_5c97d885_s0 size=25 depth=256: over=233 under=0
```
[[ 77 115   0   0]
 [  0  74 118   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[  0 115   0   0]
 [  0   0 118   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T201026705778Z_5c97d885_s0 size=37 depth=8: over=0 under=192
```
[[192   0   0   0]
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
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
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```
20261006T201026705778Z_5c97d885_s0 size=37 depth=16: over=0 under=192
```
[[192   0   0   0]
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
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
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```
20261006T201026705778Z_5c97d885_s0 size=37 depth=32: over=0 under=192
```
[[192   0   0   0]
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
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
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```
20261006T201026705778Z_5c97d885_s0 size=37 depth=64: over=93 under=4
```
[[103  89   0   0]
 [  4 184   4   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[ 0 89  0  0]
 [ 0  0  4  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [4 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T201026705778Z_5c97d885_s0 size=37 depth=128: over=203 under=0
```
[[102  90   0   0]
 [  0  79 113   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[  0  90   0   0]
 [  0   0 113   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T201026705778Z_5c97d885_s0 size=37 depth=256: over=220 under=0
```
[[102  90   0   0]
 [  0  62 123   7]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[  0  90   0   0]
 [  0   0 123   7]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T203954573173Z_e14d292b_s0 size=13 depth=8: over=0 under=192
```
[[192   0   0   0]
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
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
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```
20261006T203954573173Z_e14d292b_s0 size=13 depth=16: over=50 under=141
```
[[154  37   1   0]
 [141  39  12   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[ 0 37  1  0]
 [ 0  0 12  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [141   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```
20261006T203954573173Z_e14d292b_s0 size=13 depth=32: over=309 under=0
```
[[  0 192   0   0]
 [  0  75 117   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[  0 192   0   0]
 [  0   0 117   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T203954573173Z_e14d292b_s0 size=13 depth=64: over=83 under=0
```
[[190   2   0   0]
 [  0 111  81   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[ 0  2  0  0]
 [ 0  0 81  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T203954573173Z_e14d292b_s0 size=13 depth=128: over=136 under=0
```
[[192   0   0   0]
 [  0  56 134   2]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[  0   0   0   0]
 [  0   0 134   2]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T203954573173Z_e14d292b_s0 size=13 depth=256: over=181 under=0
```
[[164  28   0   0]
 [  0  39 133  20]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[  0  28   0   0]
 [  0   0 133  20]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T203954573173Z_e14d292b_s0 size=19 depth=8: over=0 under=192
```
[[192   0   0   0]
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
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
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```
20261006T203954573173Z_e14d292b_s0 size=19 depth=16: over=0 under=192
```
[[192   0   0   0]
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
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
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```
20261006T203954573173Z_e14d292b_s0 size=19 depth=32: over=169 under=51
```
[[ 69 122   1   0]
 [ 51  95  46   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[  0 122   1   0]
 [  0   0  46   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [51  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
20261006T203954573173Z_e14d292b_s0 size=19 depth=64: over=148 under=0
```
[[185   7   0   0]
 [  0  51  79  62]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[ 0  7  0  0]
 [ 0  0 79 62]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T203954573173Z_e14d292b_s0 size=19 depth=128: over=149 under=0
```
[[184   7   1   0]
 [  0  51  64  77]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[ 0  7  1  0]
 [ 0  0 64 77]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T203954573173Z_e14d292b_s0 size=19 depth=256: over=192 under=0
```
[[138  50   3   1]
 [  0  54  45  93]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[ 0 50  3  1]
 [ 0  0 45 93]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T203954573173Z_e14d292b_s0 size=25 depth=8: over=0 under=192
```
[[192   0   0   0]
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
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
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```
20261006T203954573173Z_e14d292b_s0 size=25 depth=16: over=0 under=192
```
[[192   0   0   0]
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
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
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```
20261006T203954573173Z_e14d292b_s0 size=25 depth=32: over=11 under=179
```
[[181  11   0   0]
 [179  13   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[ 0 11  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[  0   0   0   0]
 [179   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```
20261006T203954573173Z_e14d292b_s0 size=25 depth=64: over=293 under=0
```
[[ 58 110  22   2]
 [  0  33  97  62]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[  0 110  22   2]
 [  0   0  97  62]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T203954573173Z_e14d292b_s0 size=25 depth=128: over=298 under=0
```
[[53 59 69 11]
 [ 0 33 63 96]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0 59 69 11]
 [ 0  0 63 96]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T203954573173Z_e14d292b_s0 size=25 depth=256: over=311 under=2
```
[[ 35  10  92  55]
 [  2  36  41 113]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Overcounts only:
```
[[  0  10  92  55]
 [  0   0  41 113]
 [  0   0   0   0]
 [  0   0   0   0]]
```

Undercounts only:
```
[[0 0 0 0]
 [2 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T203954573173Z_e14d292b_s0 size=37 depth=8: over=0 under=192
```
[[192   0   0   0]
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
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
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```
20261006T203954573173Z_e14d292b_s0 size=37 depth=16: over=0 under=192
```
[[192   0   0   0]
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
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
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```
20261006T203954573173Z_e14d292b_s0 size=37 depth=32: over=0 under=192
```
[[192   0   0   0]
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
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
 [192   0   0   0]
 [  0   0   0   0]
 [  0   0   0   0]]
```
20261006T203954573173Z_e14d292b_s0 size=37 depth=64: over=204 under=15
```
[[76 88 28  0]
 [15 89 67 21]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0 88 28  0]
 [ 0  0 67 21]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [15  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
20261006T203954573173Z_e14d292b_s0 size=37 depth=128: over=241 under=0
```
[[80  7 51 54]
 [ 0 63 30 99]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0  7 51 54]
 [ 0  0 30 99]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]
 [0 0 0 0]]
```
20261006T203954573173Z_e14d292b_s0 size=37 depth=256: over=264 under=13
```
[[42  4 65 81]
 [13 65 21 93]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Overcounts only:
```
[[ 0  4 65 81]
 [ 0  0 21 93]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```

Undercounts only:
```
[[ 0  0  0  0]
 [13  0  0  0]
 [ 0  0  0  0]
 [ 0  0  0  0]]
```
