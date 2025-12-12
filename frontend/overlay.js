// overlay.js
function showOverlay() {
  const overlay = document.getElementById("eye-break");
  overlay.style.display = "flex";
}

function hideOverlay() {
  const overlay = document.getElementById("eye-break");
  overlay.style.display = "none";
}

function initOverlayInteractions() {
  const card1 = document.getElementById("card1");
  const card2 = document.getElementById("card2");
  const card3 = document.getElementById("card3");
  const card4 = document.getElementById("card4");
  const blinkCard = document.getElementById("blinkCard");
  const doneCard = document.getElementById("doneCard");
  const bar = document.getElementById("progressBar");
  
  // Buttons
  const nextToDidYouKnowBtn = document.getElementById("nextToDidYouKnow");
  const nextToGameBtn = document.getElementById("nextToGame");
  const nextToBlinkBtn = document.getElementById("nextToBlink");
  const holdBtn = document.getElementById("holdBtn");

  let holdTimer;
  let progress = 0;

  // Card 1 → Card 2
  nextToDidYouKnowBtn.addEventListener("click", () => {
    card1.style.display = "none";
    card2.style.display = "block";
  });

  // Card 2 → Card 3 (Game)
  nextToGameBtn.addEventListener("click", () => {
    card2.style.display = "none";
    card3.style.display = "block";
  });

  // Card 4 → Blink Card
  nextToBlinkBtn.addEventListener("click", () => {
    card4.style.display = "none";
    blinkCard.style.display = "block";
  });

  // Eye Game Logic
  initEyeGame();

  // Hold-to-fill logic for blink card
  function startHold() {
    holdTimer = setInterval(() => {
      progress += 2;
      bar.style.width = progress + "%";
      if (progress >= 100) {
        clearInterval(holdTimer);
        blinkCard.style.display = "none";
        doneCard.style.display = "flex";
        setTimeout(hideOverlay, 3000);
      }
    }, 60);
  }

  function stopHold() {
    clearInterval(holdTimer);
    progress = Math.max(progress - 15, 0);
    bar.style.width = progress + "%";
  }

  holdBtn.addEventListener("mousedown", startHold);
  holdBtn.addEventListener("touchstart", startHold);
  holdBtn.addEventListener("mouseup", stopHold);
  holdBtn.addEventListener("mouseleave", stopHold);
  holdBtn.addEventListener("touchend", stopHold);
}

function initEyeGame() {
  const card3 = document.getElementById("card3");
  const card4 = document.getElementById("card4");
  const gameArea = document.getElementById("eyeGameArea");
  const targetCircle = document.getElementById("targetCircle");
  const scoreDisplay = document.getElementById("gameScore");
  const startBtn = document.getElementById("startGameBtn");
  
  let score = 0;
  const maxTargets = 8;
  let isGameActive = false;

  function getRandomPosition() {
    const margin = 40;
    const width = gameArea.offsetWidth;
    const height = gameArea.offsetHeight;
    
    const x = margin + Math.random() * (width - margin * 2);
    const y = margin + Math.random() * (height - margin * 2);
    
    return { x, y };
  }

  function showTarget() {
    if (!isGameActive) return;
    
    const pos = getRandomPosition();
    targetCircle.style.left = pos.x + "px";
    targetCircle.style.top = pos.y + "px";
    targetCircle.style.display = "block";
    targetCircle.classList.add("active");
  }

  function hideTarget() {
    targetCircle.classList.remove("active");
  }

  function handleTargetClick(e) {
    if (e) e.stopPropagation();
    if (!isGameActive) return;
    
    score++;
    scoreDisplay.textContent = `${score} / ${maxTargets}`;
    hideTarget();
    
    if (score >= maxTargets) {
      isGameActive = false;
      setTimeout(() => {
        // Game complete! Show CVS facts card
        card3.style.display = "none";
        card4.style.display = "block";
      }, 500);
    } else {
      setTimeout(showTarget, 400);
    }
  }

  function startGame() {
    score = 0;
    isGameActive = true;
    scoreDisplay.textContent = `${score} / ${maxTargets}`;
    startBtn.style.display = "none";
    
    setTimeout(showTarget, 500);
  }

  startBtn.addEventListener("click", startGame);
  targetCircle.addEventListener("click", handleTargetClick);
}

// Automatically initialize when the overlay is shown
document.addEventListener("DOMContentLoaded", () => {
  showOverlay();
  initOverlayInteractions();
});