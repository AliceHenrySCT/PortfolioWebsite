// Get all the boxes (elements with id box-1 to box-9)
const boxes = document.querySelectorAll('[id^="box-"]');//grabs all of the box divs and places them in an array
const startButton = document.getElementById('startButton');//grabs
//initalizes varibles used in the game
let highScore = 0;
let currentScore = 1;
let gameList = [];
let numberRounds = 3;
let gameRunning = false;
let currentPoints = 0;
let playerList = [];
let turn = 0;


//Add click event listeners to all boxes
boxes.forEach(box => {
    box.addEventListener('click', handleClick);
});

//disables game button until game starts
boxes.forEach(box => {
    box.style.pointerEvents = 'none';
});


startButton.addEventListener('click', function() {
    startButton.style.backgroundColor = "lightgrey"; //set the bg of the button to lightgrey
    startButton.disabled = true; //disables button to prevent starting mid game

    gameList = []; //ensures the gamelist is emtpy at the start of a round

    //Selects the random boxes the computer will show the player
    for (let i = 0; i < numberRounds; i++) {
        let j = getRandomIntInclusive(1, 9);//gets a random number between 1 and 9 to select the box combination
        //pushes the selected box to the gameList array
        switch(j) {
            case 1:
                gameList.push("box-" + j)
                break;
            case 2:
                gameList.push("box-" + j)
                break;
            case 3:
                gameList.push("box-" + j)
              break;
            case 4:
                gameList.push("box-" + j)
              break;
            case 5:
                gameList.push("box-" + j)
              break;
            case 6:
                gameList.push("box-" + j)
              break;
            case 7:
                gameList.push("box-" + j)
              break;
            case 8:
                gameList.push("box-" + j)
              break;
            case 9:
                gameList.push("box-" + j)
              break;
        }
        console.log(gameList);//outputs the selected boxes to console for testing uses        
    }

    //Shows the player the boxes selected by the computer
    for (let i = 0; i < numberRounds; i++) {
        function gameClick() {
            document.getElementById(gameList[i]).style.backgroundColor = "lightgreen"; //Set the bg of the box to green
        
            function returnBGcolorBot() {//Returns box bg to default value after 1 second
                document.getElementById(gameList[i]).style.backgroundColor = '';
            }
            setTimeout(returnBGcolorBot, 1000);
        }
        setTimeout(gameClick, i * 1100);//ensures the computers boxes flash with a delay for the player
        console.log(i);
    }

    //enables grid boxes to be clicked with game start
    function enableGame(){    
    boxes.forEach(box => {
        box.style.pointerEvents = 'auto';
    });
    }
    setTimeout(enableGame, numberRounds * 1100);

});

    //Generate a random number within the given range
    function getRandomIntInclusive(min, max) {
        const minCeiled = Math.ceil(min);//ensures the number may be the min value given
        const maxFloored = Math.floor(max);//ensures the number may be the max value given
        return Math.floor(Math.random() * (maxFloored - minCeiled + 1) + minCeiled);
    }
    
    //Function to process the click event for the boxes
    function handleClick(event) {
        const boxId = event.target.id; //Gets the ID of the clicked box
        playerList.push(boxId); //Stores the boxes the player has clicked in order
        console.log(playerList);
        console.log(turn);
        //checks if player hit correct button
        if (playerList[turn] == gameList[turn]){
            document.getElementById(boxId).style.backgroundColor = "lightgreen"; //Set the bg of the box to green
            currentPoints++;
        }
        else{
            document.getElementById(boxId).style.backgroundColor = "red"; //Set the bg of the box to green
        }
        //Returns box bg to default value after 1 second
        function returnBGcolor() {
            document.getElementById(boxId).style.backgroundColor = '';
        }
        setTimeout(returnBGcolor, 1000);
        turn++// Counts how many boxes have been clicked

        if (turn == numberRounds){//checks if player has clicked same amount of boxes as computer
            if (turn == currentPoints){//checks if all boxes were correct
                swal("You got them all correct!", "Keep going for a new High Score!", "success")//tells player they got it correct
                numberRounds++//increases number of boxes in next round
                //resets variables for new round
                turn = 0
                gameList = [];
                playerList = [];
                currentPoints = 0;
                currentScore++//adds 1 to current round counter displayed to player and then updates the value the player sees
                document.getElementById('currentScore').firstChild.data = currentScore;
                if(currentScore > highScore){//checks if player has beat the high score and updates it if so
                    document.getElementById('highScore').firstChild.data = currentScore;
                    highScore = currentScore;
                }

                //disables boxes from being clicked
                boxes.forEach(box => {
                    box.style.pointerEvents = 'none';
                });
                startButton.disabled = false; // enables start button to being new round
                startButton.style.backgroundColor = ""; //set the bg of the button to default

            }
            //
            else{//activates if player made a mistake in the round
                swal("You made a mistake", "Better luck next time!", "error")//tells player they made a mistake
                //resets variables for new round
                numberRounds = 3;
                turn = 0
                gameList = [];
                playerList = [];
                currentPoints = 0;
                currentScore = 1;
                document.getElementById('currentScore').firstChild.data = currentScore;//updates round counter displayed to player

                //disables boxes from being clicked
                boxes.forEach(box => {
                    box.style.pointerEvents = 'none';
                });
                startButton.disabled = false; // enables start button to being new round 
                startButton.style.backgroundColor = ""; //set the bg of the button to default
            }
        }
    }

