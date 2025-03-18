# MemGame

MemGame is a memory testing game that challanges you to remember the pattern shown by the computer.

## Usage

Simpley load the html file and press the 'Start Round' button to begin.

## Difficulties and Wins Summary

One of the more difficult parts of the project was limiting when the player had access to click the boxes to prevent them from making selections before the computer. I had a similar issue with the start button as players could start the game mutiple times how ever since the start button was a 'button' element I was able to just disable it. The boxes however are just 'Div' elements so it took some reseach on how to disable and reenable the click events once they had been madde, and to ensure it effects all the boxes. In the end I feel that using a combination of w2school, and stackoverflow to peice together an effective solution was my greatest win. Additionally I feel my comfotability with CSS has greatly improved with this project over our first assignment. When it came to showing the player the boxes selected by the computer I also encountered some difficulties. I was not able to simpley run the same function as when a player clicks a box as it stores those clicks in the playerList array. I was able to figure it out though recreating parts of the function within a for loop that ran though all the computer choices.

## Authors

Alice Henry