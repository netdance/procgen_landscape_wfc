# Procgen Landscape Wave Function Collapse

Demo of using the WFC algorithm to generate a landscape map, 
such as might be used in a fantasy game.

The code has numerous older, unused functions and classes,
since I'm using it to show the development process. (YouTube link
will be posted here once it's available.)

Overall, I'm reasonably happy with how this turned out.

You can experiment with using a first index or random placement for
equally weighted entropies in WFC.  (USE_RANDOM in the Grid class)
They produce markedly different results, since filling a cell will change 
the entropy map.  First index will tend to make patterns that flow down and 
to the right, while random will make wispy, curling shapes.

The three different Grid implementations are as follows:

1) lgrid - Implements the grid in Lists of Lists, and only implements the 
nearest neighbor portion of WFC.  Fastest version.
2) grid - Implements the grid in Numpy, and surprisingly is the slowest 
implementation.  Using numpy to hold dataclasses is like using a screwdriver as 
a chisel.  It'll work, but that's not what it's for.
3) cgrid - List of List implementation, that fully cascades changes throughout 
the entropy map.  Surprisingly performant.  a 150x75 grid can fully render in less
that 15 seconds on a M1 Mac.