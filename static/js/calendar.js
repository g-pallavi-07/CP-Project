const monthYear = document.getElementById("month-year");
const datesContainer = document.getElementById("dates");
const prevBtn = document.getElementById("prev");
const nextBtn = document.getElementById("next");

let date = new Date();
let currentMonth = date.getMonth();
let currentYear = date.getFullYear();
let eventsData = [];

const months = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
];

// Fetch events from server
async function fetchEvents() {
  try {
    const response = await fetch('/api/events');
    const data = await response.json();
    console.log('Fetched events:', data); // Debug log
    if (data.success) {
      eventsData = data.events;
      console.log('Events data:', eventsData); // Debug log
      console.log('Total events loaded:', eventsData.length); // Debug log
      
      // Log sample event if exists
      if (eventsData.length > 0) {
        console.log('Sample event:', eventsData[0]);
      }
      
      renderCalendar();
    } else {
      console.error('Failed to fetch events:', data.error);
    }
  } catch (error) {
    console.error('Error fetching events:', error);
  }
}

// Get events for a specific date
function getEventsForDate(day, month, year) {
  const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
  console.log('Looking for events on:', dateStr); // Debug log
  const filtered = eventsData.filter(event => event.date === dateStr);
  console.log('Found events:', filtered); // Debug log
  return filtered;
}

// Show popup to add event
function showAddEventPopup(day, month, year) {
  const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
  
  const popup = document.createElement('div');
  popup.className = 'popup';
  popup.innerHTML = `
    <div class="popup-content">
      <h3>Add Event - ${months[month]} ${day}, ${year}</h3>
      <input type="text" id="event-title" placeholder="Event title" maxlength="50" />
      <input type="time" id="event-time" />
      <div style="margin-top: 15px;">
        <button id="save-event">Save</button>
        <button id="cancel-event">Cancel</button>
      </div>
    </div>
  `;
  
  document.body.appendChild(popup);
  
  // Focus on title input
  setTimeout(() => document.getElementById('event-title').focus(), 100);
  
  document.getElementById('save-event').addEventListener('click', async () => {
    const title = document.getElementById('event-title').value.trim();
    const time = document.getElementById('event-time').value;
    
    if (title) {
      await addEvent(dateStr, title, time);
      document.body.removeChild(popup);
    } else {
      alert('Please enter an event title');
    }
  });
  
  document.getElementById('cancel-event').addEventListener('click', () => {
    document.body.removeChild(popup);
  });
  
  // Close on outside click
  popup.addEventListener('click', (e) => {
    if (e.target === popup) {
      document.body.removeChild(popup);
    }
  });
}

// Show events for a date
function showEventsPopup(day, month, year) {
  const events = getEventsForDate(day, month, year);
  const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
  
  const popup = document.createElement('div');
  popup.className = 'popup';
  
  let eventsHTML = events.map((event, index) => `
    <div class="event-item">
      <div>
        <strong>${event.event_title}</strong>
        ${event.event_time ? `<br><small>${event.event_time}</small>` : ''}
      </div>
      <button class="delete-btn" data-date="${dateStr}" data-title="${event.event_title}" data-index="${index}">Delete</button>
    </div>
  `).join('');
  
  popup.innerHTML = `
    <div class="popup-content">
      <h3>Events - ${months[month]} ${day}, ${year}</h3>
      ${events.length > 0 ? eventsHTML : '<p style="color: #666;">No events for this day</p>'}
      <div style="margin-top: 20px;">
        <button id="add-new-event">Add New Event</button>
        <button id="close-popup">Close</button>
      </div>
    </div>
  `;
  
  document.body.appendChild(popup);
  
  // Add event listeners for delete buttons
  popup.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.stopPropagation();
      const dateVal = btn.dataset.date;
      const titleVal = btn.dataset.title;
      await deleteEvent(dateVal, titleVal);
    });
  });
  
  document.getElementById('add-new-event').addEventListener('click', () => {
    document.body.removeChild(popup);
    showAddEventPopup(day, month, year);
  });
  
  document.getElementById('close-popup').addEventListener('click', () => {
    document.body.removeChild(popup);
  });
  
  // Close on outside click
  popup.addEventListener('click', (e) => {
    if (e.target === popup) {
      document.body.removeChild(popup);
    }
  });
}

// Add event to server
async function addEvent(date, title, time) {
  try {
    const response = await fetch('/api/events', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        date: date,
        event_title: title,
        event_time: time
      })
    });
    
    const data = await response.json();
    if (data.success) {
      await fetchEvents();
    } else {
      alert('Error adding event: ' + data.error);
    }
  } catch (error) {
    console.error('Error adding event:', error);
    alert('Error adding event');
  }
}

// Delete event from server
async function deleteEvent(date, title) {
  if (!confirm('Are you sure you want to delete this event?')) {
    return;
  }
  
  try {
    const response = await fetch('/api/events', {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        date: date,
        event_title: title
      })
    });
    
    const data = await response.json();
    if (data.success) {
      await fetchEvents();
      // Close any open popups
      const popups = document.querySelectorAll('.popup');
      popups.forEach(popup => popup.remove());
    } else {
      alert('Error deleting event: ' + data.error);
    }
  } catch (error) {
    console.error('Error deleting event:', error);
    alert('Error deleting event');
  }
}

// Make deleteEvent available globally
window.deleteEvent = deleteEvent;

function renderCalendar() {
  const firstDay = new Date(currentYear, currentMonth, 1).getDay();
  const lastDate = new Date(currentYear, currentMonth + 1, 0).getDate();
  const prevLastDate = new Date(currentYear, currentMonth, 0).getDate();

  monthYear.textContent = `${months[currentMonth].toUpperCase()} ${currentYear}`;
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
    
    // Create a container for the day number
    const dayNumber = document.createElement("div");
    dayNumber.textContent = i;
    dayNumber.style.fontWeight = "bold";
    dayNumber.style.marginBottom = "4px";
    div.appendChild(dayNumber);
    
    // Add events for this date
    const events = getEventsForDate(i, currentMonth, currentYear);
    console.log(`Date ${i}: Found ${events.length} events`); // Debug log
    
    if (events.length > 0) {
      events.forEach(event => {
        const eventTag = document.createElement("div");
        eventTag.classList.add("event-tag");
        eventTag.textContent = event.event_title;
        eventTag.title = event.event_time ? `${event.event_title} at ${event.event_time}` : event.event_title;
        div.appendChild(eventTag);
      });
    }
    
    // Click handler - capture the current value of i
    const currentDay = i;
    div.addEventListener('click', () => {
      const dayEvents = getEventsForDate(currentDay, currentMonth, currentYear);
      if (dayEvents.length > 0) {
        showEventsPopup(currentDay, currentMonth, currentYear);
      } else {
        showAddEventPopup(currentDay, currentMonth, currentYear);
      }
    });
    
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

// Initialize
fetchEvents();