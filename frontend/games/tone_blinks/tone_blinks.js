let timerInterval = null;
function playTone(frequency, duration) {
  const ctx = new AudioContext();
  const oscillator = ctx.createOscillator();
  const gainNode = ctx.createGain();
  oscillator.connect(gainNode);
  gainNode.connect(ctx.destination);
  oscillator.frequency.value = frequency;
  oscillator.start();
  gainNode.gain.setValueAtTime(1.0, ctx.currentTime);
  gainNode.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
  oscillator.stop(ctx.currentTime + duration);
}

function startExercise() {
    const timerDisplay = document.getElementById('timerDisplay');
    
    document.querySelector('.alert').style.display = 'none';
    document.querySelector('.exercise').style.display = 'flex';
    document.querySelector('.close-button').addEventListener('click', function() {
        document.querySelector('.reward').style.display = 'none';
    });

    let elapsed = 0;
    const duration = 30000;

    for (let i = 0; i < 10; i++) {
        setTimeout(() => playTone(520, 1.0), i * 3000);         
        setTimeout(() => playTone(380, 1.0), i * 3000 + 1500); 
    }

    timerInterval = setInterval(() => {
        elapsed += 100;
        const secondsLeft = Math.max(0, Math.ceil((duration - elapsed) / 1000));
        timerDisplay.textContent = secondsLeft + 's';

        if (elapsed >= duration) {
            clearInterval(timerInterval);
            document.querySelector('.exercise').style.display = 'none';
            document.querySelector('.reward').style.display = 'flex';
            eel.add_points(25)(function(newTotal) {
            if (window.electronAPI) window.electronAPI.updatePoints(newTotal);
            });
        }
    }, 100);
}

document.querySelector('.alert button:not(.modal-close)').addEventListener('click', startExercise);