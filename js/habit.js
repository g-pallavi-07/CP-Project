document.addEventListener("DOMContentLoaded", function() {
  const addButton = document.querySelector(".add-habit button");
  const input = document.querySelector(".add-habit input");
  const habitList = document.querySelector(".habit-list");

  // Create a new habit card
  function createHabitCard(habitName) {
    const card = document.createElement("div");
    card.classList.add("habit-card");

    card.innerHTML = `
      <div class="habit-header">
        <h3>${habitName}</h3>
        <span class="streak">🔥 0-day streak</span>
        <button class="delete-btn">✖</button>
      </div>
      <div class="habit-days">
        <label><input type="checkbox"> M</label>
        <label><input type="checkbox"> T</label>
        <label><input type="checkbox"> W</label>
        <label><input type="checkbox"> T</label>
        <label><input type="checkbox"> F</label>
        <label><input type="checkbox"> S</label>
        <label><input type="checkbox"> S</label>
      </div>
      <div class="progress-bar">
        <div class="progress"></div>
      </div>
    `;

    attachEvents(card);
    habitList.appendChild(card);
  }

  // Attach functionality for delete + checkboxes  + streak
  function attachEvents(card) {
    const deleteBtn = card.querySelector(".delete-btn");
    const checkboxes = card.querySelectorAll("input[type='checkbox']");
    const progress = card.querySelector(".progress");
    const streakSpan = card.querySelector(".streak");

    // Delete functionality
    deleteBtn.addEventListener("click", () => card.remove());

    // Checkbox progress and streak update
    checkboxes.forEach(checkbox => {
      checkbox.addEventListener("change", () => {
        const totalDays = checkboxes.length;
        const completedDays = card.querySelectorAll("input[type='checkbox']:checked").length;
        
        // Update progress bar

        const progressPercent = (completedDays / totalDays) * 100;
        progress.style.width = progressPercent + "%";

        // Update streak text
        streakSpan.textContent = `🔥 ${completedDays}-day streak`;
      });
    });
  }

  // Attach functionality to existing default cards
  document.querySelectorAll(".habit-card").forEach(card => attachEvents(card));

  // Add new habits dynamically
  addButton.addEventListener("click", () => {
    const habitName = input.value.trim();
    if (habitName === "") {
      alert("Please enter a habit name!");
      return;
    }

    createHabitCard(habitName);
    input.value = "";
  });
});
