let timerInterval = null;
let endToneTimeout = null;
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

async function startExercise() {
    if (window.parent && window.parent.eel) {
        window.parent.eel.set_active_exercise('20-20-20')();
    }
    const progressBar = document.getElementById('progressBar');
    const timerDisplay = document.getElementById('timerDisplay');

    progressBar.style.width = '0%';
    timerDisplay.textContent = '20s';
    
    document.querySelector('.alert').style.display = 'none';
    document.querySelector('.exercise').style.display = 'flex';
    document.querySelector('.close-button').addEventListener('click', function() {
        document.querySelector('.reward').style.display = 'none';
    });

    let elapsed = 0;
    const duration = 20000;

    playTone(520, 1.0);                          

    endToneTimeout = setTimeout(() => playTone(380, 1.0), 20000);

    timerInterval = setInterval(async () => {
        elapsed += 100;
        const secondsLeft = Math.ceil((duration - elapsed) / 1000);
        timerDisplay.textContent = secondsLeft + 's';
        progressBar.style.width = (elapsed / duration * 100) + '%';

        if (elapsed >= duration) {
            clearInterval(timerInterval);
            if (window.parent && window.parent.eel) {
                const compliant = await window.parent.eel.finish_exercise('20-20-20')(); 
                document.querySelector('.exercise').style.display = 'none';
                if (compliant) {
                    document.querySelector('.reward').style.display = 'flex';
                    const newTotal = await window.parent.eel.add_points(15)();
                    window.parent.updatePoints(newTotal);
                } else {
                    document.querySelector('.compliance-failed-prompt').style.display = 'flex';
                }
            }
        }
    }, 100);
}

document.querySelector('.alert button:not(.modal-close)').addEventListener('click', startExercise);
document.querySelector('.compliance-failed-prompt button:not(.modal-close)').addEventListener('click', function() {
    document.querySelector('.compliance-failed-prompt').style.display = 'none';
    document.querySelector('.alert').style.display = 'flex';
});