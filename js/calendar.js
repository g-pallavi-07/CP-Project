const monthYear = document.getElementById("month-year");
const datesContainer = document.getElementById("dates");
const prevBtn = document.getElementById("prev");
const nextBtn = document.getElementById("next");

let date = new Date();
let currentMonth = date.getMonth();
let currentYear = date.getFullYear();

const months = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
];

function renderCalendar() {
  const firstDay = new Date(currentYear, currentMonth, 1).getDay();
  const lastDate = new Date(currentYear, currentMonth + 1, 0).getDate();
  const prevLastDate = new Date(currentYear, currentMonth, 0).getDate();

  monthYear.textContent = `${months[currentMonth]} ${currentYear}`;
  datesContainer.innerHTML = "";

  // Previous month's days
  for (let i = firstDay; i > 0; i--) {
    const div = document.createElement("div");
    div.classList.add("date", "inactive");
    div.textContent = prevLastDate - i + 1;
    datesContainer.appendChild(div);
  }

  // Current month
  for (let i = 1; i <= lastDate; i++) {
    const div = document.createElement("div");
    div.classList.add("date");
    if (
      i === date.getDate() &&
      currentMonth === new Date().getMonth() &&
      currentYear === new Date().getFullYear()
    ) {
      div.classList.add("today");
    }
    div.textContent = i;
    datesContainer.appendChild(div);
  }

  // Next month's days
  const totalBoxes = firstDay + lastDate;
  const nextDays = 7 - (totalBoxes % 7);
  if (nextDays < 7) {
    for (let i = 1; i <= nextDays; i++) {
      const div = document.createElement("div");
      div.classList.add("date", "inactive");
      div.textContent = i;
      datesContainer.appendChild(div);
    }
  }
}

prevBtn.addEventListener("click", () => {
  currentMonth--;
  if (currentMonth < 0) {
    currentMonth = 11;
    currentYear--;
  }
  renderCalendar();
});

nextBtn.addEventListener("click", () => {
  currentMonth++;
  if (currentMonth > 11) {
    currentMonth = 0;
    currentYear++;
  }
  renderCalendar();
});

renderCalendar();
