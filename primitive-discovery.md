# Triangle Discovery and Rasterization

## Introduction
In order to draw primitives to the screen, the system uses a tile rasterization algorithm that I (mostly) made up after reading [Michael Abrash's Larabee algorithm](https://www.cs.cmu.edu/afs/cs/academic/class/15869-f11/www/readings/abrash09_lrbrast.pdf) and [Ned Greene's paper, Hierarchical Polygon Tiling with Coverage Masks](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.115.1646&rep=rep1&type=pdf). I'm not sure if this concept has been done before, but chances are it has and I just haven't read all there is to know about this concept.

This algorithm has a bunch of advantages over many of the 'standard' algorithms that I have researched.


##### Advantages
- primitive setup is easier, the edge equations just becomes setup of initial value, dx and dy (without multiplication of bounding box screen coordinates):

    ```
    Edge.dx = (ay - by)
    Edge.dy = (bx - ax)
    Edge = (ax)(by) - (ay)(bx)
    ```
- primitive setup doesn't require multiplication of initial value of edge equations with top left pixels of bounding box of primitive. discovery always starts at screen 0,0. In fact, it doesn't require using the bounding box for good reason.
- no pixel step rules inside barycentric primitive march, discovery walks through the entire screen (or tile blocks), subdividing efficiently in powers of 2.
- for each step subdivision it can detect: full coverage, no coverage, some coverage.
- tile discovery becomes embarrassingly parallel
- no storage/nesting of edge equations as it works through a primitive, steps are in clockwise fashion with total discovery ending back where it started.
- discovery steps are in clockwise fashion, incrementing the equations by:

    ```
    Edge += Edge.dx # step 1
    Edge += Edge.dy # step 2
    Edge -= Edge.dx # step 3
    Edge -= Edge.dy # step 4, (bringing it back to origin)```
    
##### Disadvantages

- it may do overwork finding covering tiles due to starting at screen coordinate 0,0 instead of computing and starting at the top left of the bounding box for each primitive. For very small primitives, this will definitely overwork, however, I hope to argue why it doesn't matter, and may actually be faster to do what I'm doing.
