document.addEventListener("DOMContentLoaded", function () {
    let timer;
    let isRunning = false;
    let isWorkSession = true;

    let workMinutes = 25;
    let breakMinutes = 5;
    let totalCycles = 4;
    let currentCycle = 1;
    let timeLeft = workMinutes * 60;

    const timerDisplay = document.getElementById("timer");
    const sessionType = document.getElementById("sessionType");
    const startBtn = document.getElementById("startBtn");
    const pauseBtn = document.getElementById("pauseBtn");
    const resetBtn = document.getElementById("resetBtn");
    const applySettings = document.getElementById("applySettings");

    function updateTimerDisplay() {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        timerDisplay.textContent = `${minutes.toString().padStart(2, "0")}:${seconds
            .toString()
            .padStart(2, "0")}`;
        sessionType.textContent = `${isWorkSession ? "Work" : "Break"} Session ${currentCycle} of ${totalCycles}`;
    }

    function startTimer() {
        if (isRunning) return;
        isRunning = true;
        timer = setInterval(() => {
            timeLeft--;
            updateTimerDisplay();

            if (timeLeft <= 0) {
                clearInterval(timer);
                isRunning = false;

                if (isWorkSession) {
                    alert("Work session over! Take a break.");
                    isWorkSession = false;
                    timeLeft = breakMinutes * 60;
                } else {
                    currentCycle++;
                    if (currentCycle > totalCycles) {
                        alert("🎉 All sessions complete!");
                        resetTimer();
                        return;
                    }
                    alert("Break over! Back to work.");
                    isWorkSession = true;
                    timeLeft = workMinutes * 60;
                }
                updateTimerDisplay();
                startTimer();
            }
        }, 1000);
    }

    function pauseTimer() {
        clearInterval(timer);
        isRunning = false;
    }

    function resetTimer() {
        clearInterval(timer);
        isRunning = false;
        isWorkSession = true;
        currentCycle = 1;
        timeLeft = workMinutes * 60;
        updateTimerDisplay();
    }

    function applyUserSettings() {
        const workInput = parseInt(document.getElementById("workDuration").value);
        const breakInput = parseInt(document.getElementById("breakDuration").value);
        const cycleInput = parseInt(document.getElementById("cycles").value);

        if (workInput > 0) workMinutes = workInput;
        if (breakInput > 0) breakMinutes = breakInput;
        if (cycleInput > 0) totalCycles = cycleInput;

        resetTimer();
        alert(`✅ Settings Applied!\nWork: ${workMinutes} min\nBreak: ${breakMinutes} min\nCycles: ${totalCycles}`);
    }

    startBtn.addEventListener("click", startTimer);
    pauseBtn.addEventListener("click", pauseTimer);
    resetBtn.addEventListener("click", resetTimer);
    applySettings.addEventListener("click", applyUserSettings);

    updateTimerDisplay();
});
