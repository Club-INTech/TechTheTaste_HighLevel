# LPAStar - Path Finder

This repository contains a LPA* algorithm implementation for the French robotic national cup. Below, you have the basic explanation of the algorithm and the architecture of the project. Check out python [documentation](https://sudogauss.github.io/LPAstar-PF/) 

# What is LPA*?

LPA* is an algorithm which allows us to find the shortest path from the start vertex to the goal vertex. It proceeds exactly as A*, but is adapted to the dynamic changes of the map in condition that the map is known at every instant of time.

The implementation of this algorithm is based on the [***Sven Koeing, Maxim Likhachev D\* Lite***](http://idm-lab.org/bib/abstracts/papers/aaai02b.pdf) paper. Here is a pseudocode and intuitive explanation of the algorithm:

## Pseudocode

---

![LPA* Pseudocode](./doc/assets/lpa_star_pseudocode.png "LPA\* pseudocode")

## Algorithm Explanation

---

***Three functions:***
----------------------

LPA* uses 3 functions **g**, **rhs** and **h**.

1. **g(s)** represents the minimal distance from ![equation](https://latex.codecogs.com/svg.image?s_{start}) to *s*.
2. **rhs(s)** is a one-step lookup based on **g** values. ![equation](https://latex.codecogs.com/svg.image?rhs(s)&space;=&space;&space;min_{s'&space;\in&space;{Pred(s)}}[g(s')&space;&plus;&space;c(s',&space;s)]&space;\&space;and&space;\&space;rhs(s_{start})&space;=&space;0), where *c(s', s)* is a transition cost from *s'* to *s*. **rhs** has more information and influences the expansion of the vertices.
3. **h(s, s')** is a heuristics. It is used by LPA* to expand only on vertices "which make sense" before expand on the other vertices if the obstacles are present on the way.

***Main routine:***
-------------------

***Main*** function initializes all variables that matter for path-finding. It assigns all ***g-values*** and ***rhs-values*** to infinity and then puts ![equation](https://latex.codecogs.com/svg.image?rhs(s_{start})&space;=&space;0). Then, while our agent (robot for example) does not reach the goal we compute the shortest path with current map configuration. We rescan the full map then and we update each vertex for which the edge cost has been changed.


***Update vertex***
-------------------

***UpdateVertex*** function recalculates the ***rhs-value*** of the vertex using the following formula: ![equation](https://latex.codecogs.com/svg.image?rhs(s)&space;=&space;&space;min_{s'&space;\in&space;{Pred(s)}}[g(s')&space;&plus;&space;c(s',&space;s)]&space;\&space;and&space;\&space;rhs(s_{start})&space;=&space;0). Then it removes the vertex from priority queue and reinserts it if ***g-value*** of the vertex is not equal to its ***rhs-value*** (there is possible optimization).


## Architecture

---

Here is the UML-diagram of the project that can help you in better understanding of the architecture:

<img src="./doc/assets/architecture_lpastarProcess.png" style="background-color: white">
