Welcome to the Spaceship course!

In 2020, most of us have learned how to operate a spaceship. In this course we'll play a small chess-like game featuring the spaceship! The game operates on an infinite 2D chess board, with the spaceship initially located on `(0,0)`. The spaceship has a velocity `vx` and `vy`, which are initially both set to `0`. In each turn the player can increase/decrease each of those numbers by at most one, and then the piece moves `vx` steps to the right and `vy` steps up.

Moves are represented with a single digit, inspired by the old numeric pad on a computer keyboard that we used to have in the old days on Earth. For example, `7` means decreasing `vx` and increasing `vy` by `1`, while `6` means increasing `vx` by `1` and keeping `vy` the same. A path can then be represented by a sequence of digits, e.g. the path `236659` visits, in this order, the following squares: `(0,0) (0,-1) (1,-3) (3,-5) (6,-7) (9,-9) (13,-10)`.

Now the challenge is the following: given a list of squares to be visited, find a sequence of moves that visits all those squares. Your solution may consist of at most `10,000,000` moves.

The following levels are available:
* [spaceship1] Your score: 15. Best score: 5.
* [spaceship2] Your score: 198. Best score: 49.
* [spaceship3] Your score: 48. Best score: 10.
* [spaceship4] Your score: 1707. Best score: 99.
* [spaceship5] Your score: 431. Best score: 116.
* [spaceship6] Your score: 1990. Best score: 117.
* [spaceship7] Your score: 225. Best score: 94.
* [spaceship8] Your score: 215. Best score: 90.
* [spaceship9] Your score: 1848. Best score: 206.
* [spaceship10] Your score: 4138. Best score: 304.
* [spaceship11] Your score: 130255. Best score: 8192.
* [spaceship12] Best score: 8192.
* [spaceship13] Best score: 23791.
* [spaceship14] Your score: 4450. Best score: 137.
* [spaceship15] Your score: 121. Best score: 39.
* [spaceship16] Your score: 9704. Best score: 1373.
* [spaceship17] Your score: 1934. Best score: 415.
* [spaceship18] Your score: 8822. Best score: 1839.
* [spaceship19] Your score: 169501. Best score: 11328.
* [spaceship20] Your score: 37011. Best score: 2351.
* [spaceship21] Your score: 37132. Best score: 2412.
* [spaceship22] Best score: 1136.
* [spaceship23] Best score: 165298.
* [spaceship24] Best score: 559159.
* [spaceship25] Best score: 594346.

To submit a solution, send an ICFP expression that evaluates to:

```
solve spaceshipX moves
```

Your score is the number of moves, so a lower score is better.

