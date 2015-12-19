# Apocalypse (CPSC 231 Group Project)

Apocalypse is a simulataneous movement game based upon the rules of chess.
[Rules of Apocalypse](https://en.wikipedia.org/wiki/Apocalypse_(chess_variant))

# Status: Finished (12/19/15)

# Features

- Fully interactive GUI to play Apocalypse
- GUI that scales on any resolution
- Dark Theme Interface
- Main Menu Screen
- Saving and Loading game states
- Sounds that work on most platforms (Windows, Mac OSX)
- Classes to simplify code structure for the AI, board drawing, and buttons

# AI

- Advanced MiniMax AI w/ Fail Soft Alpha Beta Pruning (that handles the simultaneous nature of Apocalypse)
- Uses Recursion for the MiniMax AI
- Variable levels of AI difficulty (Can you beat it on hard?)
- Uses the "Killer Heuristic" to store moves that cause a beta cutoff and order them first when sorting
- Uses MVV ordering to speed up the AI and reduce the branching factor
- Uses Quiescence search on truncated terminal nodes to increase the overall evaluation of the AI and
  reduce the "Horizon Effect"

# How to Play

You can simply play the game on Windows by [downloading a standalone build](https://github.com/Step7750/Apocalypse/releases)

For other operating systems, we don't have a standalone build for you yet. If you have Python (3.4+) installed and the necessary dependencies, you can run it for yourself quite easily.


Licensed under MIT

Details in LICENSE.md


