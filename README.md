# Anno 117 Island Selection

This utility uses Simulated Annealing to attempt to find an optimal (or close to optimal) set of Anno 117 islands to settle.  This is a variant of the classic "Traveling Salesman" problem, which attempts to find the fastest possible route that visits all locations, when it is prohibitive to just run every case and do the math for each.  This utility is doing something similar, in that it is trying to find the set of islands, and their settling order, that gives access to every fertility and highest 'value'.

The Simulated Annealing technique works by assigning a value to each island, then attempting to find an optimal set of islands, and their order, that provide the highest value.  This utility assigns island value based on the fertilities, with higher weights being given to fertilities that are useful at population Tier 2 production chains, slightly less at Tier 3 production chains, and so on.  Additional weight is given to fertilities which are used in multiple production chains.  There are a few other tweaks to the value determination as well.  The gory details of those weights can be seen in the LatiumIsland.define_weights() and AlbionIsland.define_weights() functions, which of course are prime candidates for further adjustments or tweaking to better optimize the solver.

Note that the Simulated Annealing technique is pretty good at finding *A GOOD* solution, but it does not guarantee that it will find *THE BEST* solution.  It doesn't run every combination and permutation and determine the absolute best, it is running a subset of those cases and using the "simulated annealing" tricks to try and find *A GOOD* solution, which is hopefully at least close to *THE BEST* solution.  True simulated-annealing-nerd-warriors may want to play with the initial "temperature" of the system and the rate at which the "temperature" cools (see the LatiumSolver and AlbionSolver classes).  I have tinkered with those and set them to what seem to be giving pretty good results.

Input:  The ideal case would be to extract the island location and island fertility information from a savegame file, but since I'm not smart enough to know how to do that, this one works by reading that information in from a user-prepared .CSV file.  Hopefully smarter Anno-warriors who have a better understanding than me can offer suggestions / pull requests on how to better perform this step.

Example of .csv file format shown.  Note that the island name can be anything, I tend to select names using compass bearings, but there is nothing magic about the name selection:
```
#Name,Mackerel,Lavender,Resin,Olive,Grapes,Flax,Murex Snail,Sandarac,Oyster,Sturgeon,Marble,Iron,Mineral,Gold Ore,Mountains,Rivers,Size
W,1,,,,1,,1,,,1,,1,,1,7,13,XL
270,,1,1,1,,,1,,1,,1,,,,8,9,L
340,,1,,,,1,1,1,,,,1,1,,6,5,M
N,,1,,,,1,1,,1,1,,1,,,6,10,XL
E,1,,,,,1,1,,1,,,1,,1,8,9,XL
S,,1,,,1,1,,,1,,,1,,1,6,13,XL
225,,1,1,1,,1,1,,,,1,,,,4,0,S
290,1,,1,1,,1,1,,,,,1,,,5,7,M
315,1,,1,1,1,1,,,,,,1,,,4,0,S
000,1,,,,1,,,1,1,,,1,1,,4,5,M
010,,1,,,,,,1,,1,1,,1,1,4,2,S
030,1,,1,1,,,1,,1,,,1,,,5,2,M
045,,1,,,1,,,1,1,,1,,1,,3,0,S
090,1,,,,,,,1,,1,,1,1,1,8,10,L
100,1,,,,1,1,,1,,,1,,1,,5,0,S
135,,1,,,1,,,1,,1,1,,1,,8,9,L
160,1,,1,1,1,,,,1,,1,,,,3,0,S
200,,1,1,1,,,,,,1,,1,,1,6,12,L
```

