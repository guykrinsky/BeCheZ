# BeCheZ
Chess game with pygame library made from zero.
The game has an AI engine option.

## Why I Did This Project
That's was my first python project.
I did this project because I love chess and I wanted to practice and test my python skills.

## How To Use
All you need is python, pygame package and my code :)
Run the commands below to install and run the game.
```bash
git clone https://github.com/guykrinsky/BeCheZ.git
pip install pygame
python main.py
```

## Bot's Algorithm
First thing, every piece has a score that represent it's value, this is the base of the engine.

![pieces_score](pictures/pieces_score.jpeg "pieces score")

In addition, a knight in the corner of the board doesn't equal to a knight in the center, so the piece's score dependents on it's position.

The score of the game is the sum of the white team's pieces minus black team's pieces,
the black player want the score to be **minimal** and the white **maximum**.

This is how the bot works, for every move he can do he checks every white team move, and for every white move he checks his own moves,
and so on until 1 to 5 future moves. Every player will do his best move, white player will want to do a move that lead 
to max score and the black player to the min score.
That called **min-max algorithm**.

![minmax](pictures/minimax.png "minimax")
if you still don't understand and you want to hear more - (https://www.geeksforgeeks.org/minimax-algorithm-in-game-theory-set-1-introduction/) 

This isn't over ;), we can disqualify some paths by **Alpha–beta pruning**. 
This part is more complex, you can read here the more boring staff: (https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning)).
![alpha_beta_pruning](pictures/alphabetapruning.png "alpha_beta_pruning")
## Opening Screen
![starting_screen](pictures/opening_screen_picture.png"starting screen")

## Gameplay
![Game Play Of The Game](pictures/gameplay.gif)
