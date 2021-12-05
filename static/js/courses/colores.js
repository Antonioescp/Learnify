let welcomeHasFinished = false;

window.addEventListener('load', (e) => {
    console.log('hello!')
    let welcomeAudio = new Audio('/static/audio/cursos/Colores-B.mp3');

    // play audio on user interaction
    window.addEventListener('click', e => {

        if (!welcomeHasFinished && welcomeAudio.paused) {
            
            welcomeAudio.play();

            welcomeAudio.addEventListener('ended', e => {
                welcomeHasFinished = true;
            });

        }

    });
});