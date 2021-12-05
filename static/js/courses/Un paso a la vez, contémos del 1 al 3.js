let welcomeHasFinished = false;

window.addEventListener('load', (e) => {
    
    let player = new Audio('/static/audio/cursos/Numeros-B.mp3');
    let tiles = document.getElementsByClassName('clickable-tile');

    // play each tile audio on user click
    for (let idx = 0; idx < tiles.length; idx++) {
        tiles[idx].addEventListener('click', e => {
            if (welcomeHasFinished) {
                player.pause();
                player.src = tiles[idx].dataset.audio;
                player.currentTime = 0;
                player.play();
            }
        });
    }

    // play audio on user interaction
    window.addEventListener('click', e => {

        if (!welcomeHasFinished && player.paused) {
            
            player.play();

            player.addEventListener('ended', e => {
                welcomeHasFinished = true;
            });

        }

    });
});