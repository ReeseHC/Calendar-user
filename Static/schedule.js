
function setRefreshFlag() {
  sessionStorage.setItem('backFromBooking', 'true');
}

function bookAppointmentWithAPI(time, elementId) {
  // Get the date from the page
  const dateString = document.getElementById('selectedDate').textContent;
  
  // Parse the date to get the ISO format (YYYY-MM-DD)
  const date = new Date(dateString);
  const isoDate = date.toISOString().split('T')[0];
  
  // Send the request to the server
  fetch('/api/book', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      date: isoDate,
      time: time
    }),
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Update the UI as in the inline script
      showSuccessMessage(data.message);
      
      // Update the appointment counts
      document.getElementById('bookedCount').textContent = data.appointments.booked;
      document.getElementById('openCount').textContent = data.appointments.open;
    } else {
      showErrorMessage(data.message);
    }
  })
  .catch(error => {
    showErrorMessage('An error occurred while booking the appointment');
    console.error('Error:', error);
    document.addEventListener('DOMContentLoaded', function() {
      // Add event listener to back button to set refresh flag
      const backButton = document.querySelector('.back-button');
      if (backButton) {
        backButton.addEventListener('click', setRefreshFlag);
      }
    });
  });
}

function cancelAppointmentWithAPI(time, elementId) {
  // Get the date from the page
  const dateString = document.getElementById('selectedDate').textContent;
  
  // Parse the date to get the ISO format (YYYY-MM-DD)
  const date = new Date(dateString);
  const isoDate = date.toISOString().split('T')[0];
  
  // Send the request to the server
  fetch('/api/cancel', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      date: isoDate,
      time: time
    }),
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Update the UI as in the inline script
      showSuccessMessage(data.message);
      
      // Update the appointment counts
      document.getElementById('bookedCount').textContent = data.appointments.booked;
      document.getElementById('openCount').textContent = data.appointments.open;
    } else {
      showErrorMessage(data.message);
    }
  })
  .catch(error => {
    showErrorMessage('An error occurred while cancelling the appointment');
    console.error('Error:', error);
  });
  document.addEventListener('DOMContentLoaded', function() {
    // Add event listener to back button to set refresh flag
    const backButton = document.querySelector('.back-button');
    if (backButton) {
      backButton.addEventListener('click', setRefreshFlag);
    }
  });
}
