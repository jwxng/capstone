let timerInterval = null;

function startExercise() {
    const movingDot = document.getElementById('movingDot');
    const timerDisplay = document.getElementById('timerDisplay');
    
    document.querySelector('.alert').style.display = 'none';
    document.querySelector('.exercise').style.display = 'flex';
    document.querySelector('.close-button').addEventListener('click', function() {
        document.querySelector('.reward').style.display = 'none';
    });

    let elapsed = 0;
    const duration = 20000;

    timerInterval = setInterval(() => {
        elapsed += 100;
        const secondsLeft = Math.ceil((duration - elapsed) / 1000);
        timerDisplay.textContent = secondsLeft + 's';
        movingDot.style.left = `calc(${(elapsed / duration) * 100}% - 10px)`;

        if (elapsed >= duration) {
        clearInterval(timerInterval);
        document.querySelector('.exercise').style.display = 'none';
        document.querySelector('.reward').style.display = 'flex';
        eel.add_points(20)(function(newTotal) {
        if (window.electronAPI) window.electronAPI.updatePoints(newTotal);
        });
        }
    }, 100);
}

document.querySelector('.alert button:not(.modal-close)').addEventListener('click', startExercise);