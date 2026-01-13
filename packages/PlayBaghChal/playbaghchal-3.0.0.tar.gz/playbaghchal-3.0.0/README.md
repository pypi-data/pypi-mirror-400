 # Bagh Chal

Bagh-Chal (Nepali: बाघ चाल), also known as the Tiger Game or Tiger and Goat Game, is a traditional strategy game from Nepal. This will guide you through the game’s rules, setup, and objectives.

## Requirements

- Python > 3.9
- Pygame

## Objective

- **Tigers:** Capture the goats.
- **Goats:** Prevent the tigers from capturing all of them and trap the tigers so they cannot move.

## Board

The board is a 5x5 grid with additional diagonal lines connecting the corners, creating a star-like pattern. The intersections of these lines are the points where pieces can be placed.

## Pieces

- **Tigers:** 4 pieces
- **Goats:** 20 pieces

## Setup

1. **Tigers:** Start on the board in specific locations (typically at the four corners of the board).
2. **Goats:** Start off the board and are introduced into the game one at a time.

## Installation

You can install the game using pip:

```sh
pip install PlayBaghChal
```

## Usage

Run the game using:
```py
from playbaghchal.PlayGame import TigerGame

# Create an instance of the game and run it
game = TigerGame()
game.run()
```
OR, Using Command line


```sh
python -m playbaghchal
```

## Gameplay

### Tigers' Turn

- Tigers can move to any adjacent intersection along the lines (vertically, horizontally, or diagonally).
- Tigers capture goats by jumping over them to an empty spot directly on the other side (similar to a checkers capture).

### Goats' Turn

- Goats are placed on empty intersections, one at a time, until all 20 goats are on the board.
- After all goats are on the board, they can move to an adjacent intersection along the lines.


## Controls

- **Tigers and Goats movement**: Click on a piece and then on a valid position to move.

## Winning the Game

- **Tigers Win:** By capturing 6 goats so that it is impossible to block all tigers.
- **Goats Win:** By trapping all the tigers so they cannot make any legal moves.

## Strategy

- **For Tigers:** Focus on capturing goats efficiently and blocking their movement.
- **For Goats:** Aim to create a formation that limits the movement of tigers and avoid being captured.

## Additional Notes

- The game requires careful planning and strategic thinking from both players.
- The placement of goats can significantly influence the tigers' ability to capture or move.


## License

This project is licensed under the MIT License.

## Contributing

Pull requests are welcome! If you'd like to contribute, feel free to fork the repo and submit a PR.

## Author

Developed by **Bhishan Pangeni**. 🚀
Enjoy your game of Bagh Chal!
