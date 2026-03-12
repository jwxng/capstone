let timerInterval = null;

function startExercise() {
    if (window.parent && window.parent.eel) {
        window.parent.eel.set_active_exercise('palming')();
    }
    const progressBar = document.getElementById('progressBar');
    const timerDisplay = document.getElementById('timerDisplay');
    
    document.querySelector('.alert').style.display = 'none';
    document.querySelector('.exercise').style.display = 'flex';
    document.querySelector('.close-button').addEventListener('click', function() {
        document.querySelector('.reward').style.display = 'none';
    });

    let elapsed = 0;
    const duration = 60000;

    timerInterval = setInterval(() => {
        elapsed += 100;
        const secondsLeft = Math.ceil((duration - elapsed) / 1000);
        timerDisplay.textContent = secondsLeft + 's';
        progressBar.style.width = (elapsed / duration * 100) + '%';

        if (elapsed >= duration) {
            clearInterval(timerInterval);
            if (window.parent && window.parent.eel) {
                window.parent.eel.clear_active_exercise()();
            }
            document.querySelector('.exercise').style.display = 'none';
            document.querySelector('.reward').style.display = 'flex';
        }
    }, 100);
}

document.querySelector('.alert button:not(.modal-close)').addEventListener('click', startExercise);