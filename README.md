
## Explanation
The development of this program corresponds a modified version of the typical **minesweeper game**, in which it now allows a multiplayer mode through any local or extern network, whose interface is displayed only on the operating system console that runs it. The number of players is optional, from 1 to x players, of course, we could choose more than one hundred players at a time if we wanted, but I think wouldn't be much fun and would lose all its traditional style. So a few players should be enough.   


## Environment
Operating System - **Windows11/Ubuntu 22.04 LTS** - **Python3.10** or higher version 


Note: 

1. Start the server **server_buscaminas.py**

2. Start each player client **client_buscaminas.py**

3. Repeat previous step two according to the number of players present in the game.

4. First player connected will have the oppotunity to choose the number of players y level blur.

5. The server will wait for all the players to be connected

6. Each player should wait his turn to select any box of the game, so if it´s not the player's turn, any action within the console will be blocked.

7. Each selected box will be reflected in the player´s console, as well as the current state of the game. 

8. If any player loses in the game, automatically be reflected on each player's console ans end the game

9. Enjoy **mineesweper game**
