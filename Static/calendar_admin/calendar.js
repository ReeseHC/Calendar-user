const calendarDatesElement = document.getElementById("calendarDaysContainer");
const monthYearElement = document.getElementById("monthYear");
const prevButton = document.querySelector(".prev-button");
const nextButton = document.querySelector(".next-button");
const selectedDateHeading = document.getElementById("selectedDateHeading");
const eventsList = document.getElementById("eventsList");
const addAppointmentBtn = document.getElementById("addAppointmentBtn");
const appointmentForm = document.getElementById("appointmentForm");
const submitAppointmentBtn = document.getElementById("submitAppointmentBtn");
const cancelAppointmentBtn = document.getElementById("cancelAppointmentBtn");
const appointmentTimeInput = document.getElementById("appointmentTime");
const staffIdInput = document.getElementById("staffId");
const locationIdInput = document.getElementById("locationId");

const API_BASE_URL = 'http://localhost:5000'; // Update if your Flask server runs on a different URL

let currentDate = new Date();
let selectedDate = new Date();
let appointments = {}; // Store appointments by date

// Initialize
generateCalendarDays();
updateSelectedDateDisplay();

// Event Listeners
prevButton.addEventListener("click", () => {
  currentDate.setMonth(currentDate.getMonth() - 1);
  generateCalendarDays();
});

nextButton.addEventListener("click", () => {
  currentDate.setMonth(currentDate.getMonth() + 1);
  generateCalendarDays();
});

addAppointmentBtn.addEventListener("click", showAppointmentForm);
submitAppointmentBtn.addEventListener("click", submitAppointment);
cancelAppointmentBtn.addEventListener("click", hideAppointmentForm);

// API Functions
async function fetchAppointments(date) {
  try {
    const dateStr = date.toISOString().split('T')[0];
    const response = await fetch(`${API_BASE_URL}/admin/schedule?date=${dateStr}`);
    if (!response.ok) throw new Error('Failed to fetch appointments');
    return await response.json();
  } catch (error) {
    console.error('Error fetching appointments:', error);
    return [];
  }
}

async function createAppointment(appointmentData) {
  try {
    const response = await fetch(`${API_BASE_URL}/admin/schedule`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(appointmentData)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to create appointment');
    }

    return await response.json();
  } catch (error) {
    console.error('Error creating appointment:', error);
    throw error;
  }
}

async function deleteAppointment(appointmentData) {
  try {
    const response = await fetch(`${API_BASE_URL}/admin/schedule`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(appointmentData)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to delete appointment');
    }

    return await response.json();
  } catch (error) {
    console.error('Error deleting appointment:', error);
    throw error;
  }
}

// Calendar Functions
function formatMonthYear(date) {
  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];
  return `${monthNames[date.getMonth()]} ${date.getFullYear()}`;
}

async function generateCalendarDays() {
  const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
  const lastDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
  const firstDayIndex = firstDayOfMonth.getDay();
  const totalDaysInMonth = lastDayOfMonth.getDate();

  calendarDatesElement.innerHTML = '';

  // Empty days before the 1st of the month
  for (let i = 0; i < firstDayIndex; i++) {
    const emptyDay = document.createElement("div");
    emptyDay.classList.add("date-container", "empty-day");
    calendarDatesElement.appendChild(emptyDay);
  }

  // Days of the month
  for (let i = 1; i <= totalDaysInMonth; i++) {
    const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), i);
    const dateKey = date.toISOString().split('T')[0];
    const isToday = date.toDateString() === new Date().toDateString();
    const isSelected = selectedDate && date.toDateString() === selectedDate.toDateString();

    const dateButton = document.createElement("button");
    dateButton.classList.add("date");
    dateButton.textContent = i;
    dateButton.setAttribute("aria-label", `${i} ${formatMonthYear(currentDate)}`);

    // Apply today's class if it's today (but not if it's selected)
    if (isToday && !isSelected) {
      dateButton.classList.add("today");
      dateButton.setAttribute("aria-current", "date");
    }

    // Apply selected class if it's selected (overrides today's styling)
    if (isSelected) {
      dateButton.classList.add("selected");
    }

    // Add indicator if date has appointments
    if (appointments[dateKey] && appointments[dateKey].length > 0) {
      const indicator = document.createElement("div");
      indicator.classList.add("appointment-indicator");
      dateButton.appendChild(indicator);
    }

    dateButton.addEventListener('click', () => selectDate(dateButton, date));

    const dateContainer = document.createElement("div");
    dateContainer.classList.add("date-container");
    dateContainer.appendChild(dateButton);
    calendarDatesElement.appendChild(dateContainer);
  }

  monthYearElement.textContent = formatMonthYear(currentDate);
}

async function selectDate(dateButton, date) {
  // Remove selection from previously selected date
  const previouslySelected = document.querySelector(".date-container button.selected");
  if (previouslySelected) {
    previouslySelected.classList.remove("selected");

    // If the previously selected date was today, reapply today's styling
    const prevDate = new Date(selectedDate);
    if (prevDate.toDateString() === new Date().toDateString()) {
      const todayButtons = document.querySelectorAll(".date-container button");
      todayButtons.forEach(btn => {
        if (btn.textContent == prevDate.getDate() &&
          currentDate.getMonth() === prevDate.getMonth() &&
          currentDate.getFullYear() === prevDate.getFullYear()) {
          btn.classList.add("today");
        }
      });
    }
  }

  // Add selected class to clicked date
  dateButton.classList.add("selected");
  // Remove today's class if it exists (selected style takes precedence)
  dateButton.classList.remove("today");

  selectedDate = date;
  await updateSelectedDateDisplay();
}

async function updateSelectedDateDisplay() {
  if (selectedDate.getMonth() === currentDate.getMonth() &&
    selectedDate.getFullYear() === currentDate.getFullYear()) {
    const dateKey = selectedDate.toISOString().split('T')[0];
    selectedDateHeading.textContent = `Selected Date: ${selectedDate.toDateString()}`;

    // Fetch and display appointments
    try {
      const appointmentsForDate = await fetchAppointments(selectedDate);
      appointments[dateKey] = appointmentsForDate;

      eventsList.innerHTML = '';
      if (appointmentsForDate.length > 0) {
        appointmentsForDate.forEach(appointment => {
          const eventElement = document.createElement("div");
          eventElement.classList.add("event");
          eventElement.innerHTML = `
            <div class="event-time">${appointment.schedule_slot}</div>
            <div class="event-title">Appointment with Staff #${appointment.staff_id}</div>
            <div class="event-location">Location #${appointment.location_id}</div>
            <button class="delete-appointment" 
                    data-day="${appointment.schedule_day}"
                    data-slot="${appointment.schedule_slot}"
                    data-staff="${appointment.staff_id}">
              Delete
            </button>
          `;
          eventsList.appendChild(eventElement);
        });

        // Update delete button event listeners
        document.querySelectorAll('.delete-appointment').forEach(button => {
          button.addEventListener('click', async (e) => {
            if (confirm('Are you sure you want to delete this appointment?')) {
              try {
                await fetch(`${API_BASE_URL}/admin/schedule`, {
                  method: 'DELETE',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                    schedule_day: e.target.dataset.day,
                    schedule_slot: e.target.dataset.slot,
                    staff_id: parseInt(e.target.dataset.staff)
                  })
                });
                await updateSelectedDateDisplay();
                generateCalendarDays();
              } catch (error) {
                alert(error.message);
              }
            }
          });
        });
      } else {
        eventsList.innerHTML = '<div class="event">No appointments scheduled</div>';
      }
    } catch (error) {
      console.error('Error loading appointments:', error);
      eventsList.innerHTML = '<div class="event">Error loading appointments</div>';
    }
  } else {
    selectedDateHeading.textContent = "Select a date in this month to see appointments";
    eventsList.innerHTML = '';
    addAppointmentBtn.style.display = "none";
  }
}

function showAppointmentForm() {
  if (!selectedDate) {
    alert("Please select a date first");
    return;
  }
  appointmentForm.style.display = "block";
  addAppointmentBtn.style.display = "none";

  // Set default time to next full hour
  const now = new Date();
  const nextHour = new Date(now.getTime() + 60 * 60 * 1000);
  appointmentTimeInput.value = `${nextHour.getHours().toString().padStart(2, '0')}:00`;
  staffIdInput.focus();
}

function hideAppointmentForm() {
  appointmentForm.style.display = "none";
  addAppointmentBtn.style.display = "block";
  // Clear form inputs
  appointmentTimeInput.value = "";
  staffIdInput.value = "";
  locationIdInput.value = "";
}

async function submitAppointment() {
  if (!appointmentTimeInput.value || !staffIdInput.value || !locationIdInput.value) {
    alert("Please fill in all fields");
    return;
  }

  const appointmentData = {
    schedule_day: selectedDate.toISOString().split('T')[0],
    schedule_slot: appointmentTimeInput.value + ":00",
    staff_id: parseInt(staffIdInput.value),
    location_id: parseInt(locationIdInput.value)
  };

  try {
    const response = await fetch(`${API_BASE_URL}/admin/schedule`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(appointmentData)
    });

    if (!response.ok) throw new Error('Failed to create appointment');

    const newAppointment = await response.json();

    // Update local appointments cache (use composite key)
    const dateKey = newAppointment.schedule_day;
    if (!appointments[dateKey]) appointments[dateKey] = [];
    appointments[dateKey].push(newAppointment);

    hideAppointmentForm();
    await updateSelectedDateDisplay();
    generateCalendarDays();
  } catch (error) {
    alert(error.message);
  }
}
