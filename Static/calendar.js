const calendarDates = document.getElementById('calendarDates');
const monthYear = document.getElementById('monthYear');

let currentDate = new Date();
let appointmentData = {};

const months = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
];

// Fetch appointment data from the server
async function fetchAppointmentData() {
  try {
    const response = await fetch('/api/appointments');
    const data = await response.json();
    appointmentData = data;
    renderCalendar(currentDate);
  } catch (error) {
    console.error('Error fetching appointment data:', error);
  }
}

function renderCalendar(date) {
  const month = date.getMonth();
  const year = date.getFullYear();
  const today = new Date();
  
  // Get the first day of the month (0 = Sunday, 1 = Monday, etc.)
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  
  monthYear.textContent = `${months[month]} ${year}`;
  calendarDates.innerHTML = "";
  
  // Add empty spaces for days before the first day of the month
  for (let i = 0; i < firstDay; i++) {
    const emptyDay = document.createElement('div');
    emptyDay.className = 'empty-day';
    calendarDates.appendChild(emptyDay);
  }
  
  // Add buttons for each day of the month
  for (let day = 1; day <= daysInMonth; day++) {
    const isToday = day === today.getDate() && month === today.getMonth() && year === today.getFullYear();
    const dateContainer = document.createElement('div');
    dateContainer.className = 'date-container';
    
    const btn = document.createElement('button');
    if (isToday) {
      btn.className = 'today';
    }
    btn.textContent = day;
    
    // Format date for URL and data lookup: YYYY-MM-DD
    const dateString = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    btn.onclick = () => {
      window.location.href = `/schedule.html?date=${dateString}`;
    };
    
    dateContainer.appendChild(btn);
    
    // Add appointment indicators
    const appointmentIndicators = document.createElement('div');
    appointmentIndicators.className = 'appointment-indicators';
    
    // Check if there are any appointments for this date
    if (appointmentData[dateString]) {
      const appts = appointmentData[dateString];
      
      // Add yellow dots for booked appointments
      for (let i = 0; i < appts.booked; i++) {
        const bookedDot = document.createElement('span');
        bookedDot.className = 'appointment-dot booked';
        appointmentIndicators.appendChild(bookedDot);
      }
      
      // Add gray dots for open appointments
      for (let i = 0; i < appts.open; i++) {
        const openDot = document.createElement('span');
        openDot.className = 'appointment-dot open';
        appointmentIndicators.appendChild(openDot);
      }
    }
    
    dateContainer.appendChild(appointmentIndicators);
    calendarDates.appendChild(dateContainer);
  }
}

function changeMonth(direction) {
  currentDate.setMonth(currentDate.getMonth() + direction);
  // Refresh appointment data when changing months
  fetchAppointmentData();
}

// Initialize the calendar when the page loads
document.addEventListener('DOMContentLoaded', function() {
  fetchAppointmentData();
  
  // Check if returning from booking/cancellation
  const backFromBooking = sessionStorage.getItem('backFromBooking');
  if (backFromBooking === 'true') {
    // Clear the flag
    sessionStorage.removeItem('backFromBooking');
    // Refresh the data
    fetchAppointmentData();
  }
});

// Function to refresh calendar data (called after booking/canceling)
function refreshCalendarData() {
  fetchAppointmentData();
}