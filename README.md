# Santorini
A digital recreation of the classic board game **Santorini**, built using **Python Arcade**. This game features **player vs player** and **AI modes** with intelligent decision-making using **Minimax** and **Alpha-Beta pruning**.


## Features

- **Multiple Game Modes**:  
  - Player vs Player  
  - Player vs AI (using `ai_mode2`)  
- **Game Assets**:  
  - Background: `bg_sant`  
  - Home screen: `home_arcade`  
  - Menu: `menu`  
  - Player sprites: `player2`  
  - Front page: `sant_front_page`
  - ai_mode2: `AI logic for computer player`
  - Coin sounds and other audio feedback  
- **AI Logic**:  
  - **Minimax algorithm** with **Alpha-Beta pruning**  
  - Heuristic evaluation to handle board scoring and move prioritization  
- **Gameplay Features**:  
  - Coin placement with sound effects  
  - Handles draw/tie cases gracefully  
  - Smooth turn-based gameplay with clear visual indicators  

---
## Tech Stack

- **Language**: Python 3.x  
- **Library**: [Python Arcade](https://arcade.academy/)  
- **AI Algorithms**: Minimax, Alpha-Beta pruning, Heuristic evaluation


---
## Installation & Setup
1. **Clone the repository**:

```bash
git clone <your-repo-link>
cd Santorini
```

2.**Install Python Arcade**
```bash
pip install arcade
```

3.Run the Game:
```bash
python home_arcade.py
```
----
## How to Play:
1. Launch the game (home_arcade.py)
2. Click on start game
3. Select any mode (Player VS Player or Player VS AI)
4. Place your workers
5. The first player to reach the third level of a tower wins
6. Coin placement plays sounds for interactive feedback
7. AI Uses smart moves based on **Minimax + Alpha-Beta pruning** with **heuristic evaluation**

----

## Demo Screenshots:
### Menu Screen
![Menu Screen](images/menu_page.png)
### Home Screen
![Home Screen](images/home_page.png)
### Game Screen
![Game Screen](images/game_board.png)
### AI Vs Player Screen
![AI Vs Player Screen](images/ai_vs_player.png)
### Win Screen
![Win Screen](images/ai_wins.png)






  
