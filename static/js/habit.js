document.addEventListener("DOMContentLoaded", function () {
    const addButton = document.querySelector(".add-habit button");
    const input = document.querySelector(".add-habit input");
    const habitList = document.querySelector(".habit-list");

    /* ✅ Load saved habits */
    fetch("/get_habits")
        .then(res => res.json())
        .then(data => {
            habitList.innerHTML = ""; // clear existing
            data.forEach(habit => {
                createHabitCard(habit.name, habit.checkedDays);
            });
        });

    /* ✅ Save habits to backend */
    function saveHabits() {
        const habits = [];

        document.querySelectorAll(".habit-card").forEach(card => {
            const name = card.querySelector("h3").textContent;
            const checkedDays = Array.from(
                card.querySelectorAll("input[type='checkbox']")
            ).map(cb => cb.checked);

            habits.push({ name, checkedDays });
        });

        fetch("/save_habits", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(habits)
        });
    }

    /* ✅ Create a habit card */
    function createHabitCard(name, checkedDays = []) {
        const card = document.createElement("div");
        card.classList.add("habit-card");

        card.innerHTML = `
            <div class="habit-header">
                <h3>${name}</h3>
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

        habitList.appendChild(card);
        attachEvents(card);

        const checkboxes = card.querySelectorAll("input[type='checkbox']");
        checkedDays.forEach((v, i) => (checkboxes[i].checked = v));

        updateCard(card);
    }

    /* ✅ Update progress + streak */
    function updateCard(card) {
        const checkboxes = card.querySelectorAll("input[type='checkbox']");
        const progress = card.querySelector(".progress");
        const streakSpan = card.querySelector(".streak");

        const completed = card.querySelectorAll("input[type='checkbox']:checked").length;
        const percent = (completed / 7) * 100;

        progress.style.width = percent + "%";
        streakSpan.textContent = `🔥 ${completed}-day streak`;
    }

    /* ✅ Attach events */
    function attachEvents(card) {
        const deleteBtn = card.querySelector(".delete-btn");
        const checkboxes = card.querySelectorAll("input[type='checkbox']");

        deleteBtn.addEventListener("click", () => {
            card.remove();
            saveHabits();
        });

        checkboxes.forEach(cb =>
            cb.addEventListener("change", () => {
                updateCard(card);
                saveHabits();
            })
        );
    }

    /* ✅ Add a new habit */
    addButton.addEventListener("click", () => {
        const name = input.value.trim();
        if (!name) return alert("Enter a habit!");

        createHabitCard(name);
        saveHabits();
        input.value = "";
    });
});