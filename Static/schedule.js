
function setRefreshFlag() {
  sessionStorage.setItem('backFromBooking', 'true');
}

function showSuccessMessage(message) {
  const successMessage = document.getElementById('successMessage');
  if (successMessage) {
    successMessage.textContent = message;
    successMessage.style.display = 'block';

    // Hide after 3 seconds
    setTimeout(() => {
      successMessage.style.display = 'none';
    }, 3000);
  }
}

function showErrorMessage(message) {
  const errorMessage = document.getElementById('errorMessage');
  if (errorMessage) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';

    // Hide after 3 seconds
    setTimeout(() => {
      errorMessage.style.display = 'none';
    }, 3000);
  }
}

function bookAppointmentWithAPI(time, elementId) {
  // Get the date from the page
  const dateString = document.getElementById('selectedDate').textContent;
  
  // Make sure we have a valid date string
  if (!dateString) {
    showErrorMessage('Selected date not found');
    console.error('Missing date information');
    return;
  }

  // Parse the date to get the ISO format (YYYY-MM-DD)
  try {
    const date = new Date(dateString);
    // Check if date is valid
    if (isNaN(date.getTime())) {
      showErrorMessage('Invalid date format');
      console.error('Invalid date:', dateString);
      return;
    }
    var isoDate = date.toISOString().split('T')[0];
  } catch (e) {
    showErrorMessage('Error processing date');
    console.error('Date parsing error:', e);
    return;
  }

  // Get staff_id and location_id from the schedule item
  const scheduleItem = document.querySelector(`.schedule-item[data-time="${time}"]`);
  
  if (!scheduleItem) {
    showErrorMessage('Could not find schedule information for the selected time');
    console.error('Schedule item not found for time:', time);
    return;
  }
  
  const staffId = scheduleItem.getAttribute('data-staff-id');
  const locationId = scheduleItem.getAttribute('data-location-id');
  
  // Validate required data before sending
  if (!isoDate || !time || !staffId || !locationId) {
    showErrorMessage('Missing required booking information');
    console.error('Missing data:', { isoDate, time, staffId, locationId });
    return;
  }

  // Create appointment data object
  const appointmentData = {
    date: isoDate,
    time: time,
    staff_id: staffId,
    location_id: locationId
  };

  // Show loading state
  const bookButton = document.getElementById(elementId);
  if (bookButton) {
    bookButton.disabled = true;
    bookButton.textContent = 'Booking...';
  }

  // Log the request payload for debugging
  console.log('Sending booking request:', appointmentData);

  // Send the request to the server
  fetch('/api/book-appointment', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    },
    credentials: 'same-origin',
    body: JSON.stringify(appointmentData),
  })
    .then(response => {
      // First check if response is OK
      if (!response.ok) {
        // Try to get error details from response
        return response.json().catch(() => {
          // If response is not JSON, convert to text and wrap in an object
          return response.text().then(text => {
            throw new Error(`Server error (${response.status}): ${text || 'Unknown error'}`);
          });
        }).then(errorData => {
          // If we got JSON with error details, throw it
          throw new Error(errorData.error || `Server error (${response.status})`);
        });
      }
      return response.json();
    })
    .then(data => {
      // Reset button state
      if (bookButton) {
        bookButton.disabled = false;
        bookButton.textContent = 'Book';
      }

      if (data.success) {
        // Show success message
        showSuccessMessage(data.message || 'Appointment booked successfully!');

        // Update the appointment counts
        if (data.appointments) {
          const bookedCountEl = document.getElementById('bookedCount');
          const openCountEl = document.getElementById('openCount');
          
          if (bookedCountEl) bookedCountEl.textContent = data.appointments.booked;
          if (openCountEl) openCountEl.textContent = data.appointments.open;
        }

        // Reload the page after a delay
        setTimeout(() => {
          location.reload();
        }, 1500);
      } else {
        showErrorMessage(data.error || 'Failed to book appointment');
      }
    })
    .catch(error => {
      // Reset button state
      if (bookButton) {
        bookButton.disabled = false;
        bookButton.textContent = 'Book';
      }
      
      showErrorMessage(error.message || 'An error occurred while booking the appointment');
      console.error('Error:', error);
    });
}

function startCancelAppointment(time, elementId) {
  // Show confirmation modal
  const modal = document.getElementById('confirmationModal');
  if (modal) {
    modal.style.display = 'block';

    // Store time and elementId for the confirmation action
    document.getElementById('confirmCancelButton').onclick = function () {
      cancelAppointmentWithAPI(time, elementId);
      modal.style.display = 'none';
    };
  } else {
    // If modal not found, proceed directly
    cancelAppointmentWithAPI(time, elementId);
  }
}

function cancelAppointmentWithAPI(time, elementId) {
  // Get the date from the page
  const dateString = document.getElementById('selectedDate').textContent;

  // Parse the date to get the ISO format (YYYY-MM-DD)
  const date = new Date(dateString);
  const isoDate = date.toISOString().split('T')[0];

  // Get staff_id from the schedule item
  const scheduleItem = document.querySelector(`.schedule-item[data-time="${time}"]`);
  
  if (!scheduleItem) {
    showErrorMessage('Could not find schedule information for the selected time');
    return;
  }
  
  const staffId = scheduleItem.getAttribute('data-staff-id');

  // Show loading state
  const cancelButton = document.getElementById(elementId);
  if (cancelButton) {
    cancelButton.disabled = true;
    cancelButton.textContent = 'Cancelling...';
  }

  // Send the request to the server
  fetch('/api/cancel-appointment', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    },
    credentials: 'same-origin',
    body: JSON.stringify({
      date: isoDate,
      time: time,
      staff_id: staffId,
      confirmed: true
    }),
  })
    .then(response => {
      if (!response.ok) {
        return response.json().catch(() => {
          // If response is not JSON, convert to text and wrap in an object
          return response.text().then(text => {
            return { error: `Server error (${response.status}): ${text}` };
          });
        });
      }
      return response.json();
    })
    .then(data => {
      // Reset button state
      if (cancelButton) {
        cancelButton.disabled = false;
        cancelButton.textContent = 'Cancel';
      }

      if (data.success) {
        // Show success message
        showSuccessMessage(data.message || 'Appointment cancelled successfully!');

        // Update the appointment counts if available
        if (data.appointments) {
          document.getElementById('bookedCount').textContent = data.appointments.booked;
          document.getElementById('openCount').textContent = data.appointments.open;
        }

        // Redirect to feedback form
        setTimeout(() => {
          window.location.href = `/calendar/feedback?date=${isoDate}&time=${time}&staff_id=${staffId}`;
        }, 250);
      } else {
        showErrorMessage(data.error || 'Failed to cancel appointment');
      }
    })
    .catch(error => {
      // Reset button state
      if (cancelButton) {
        cancelButton.disabled = false;
        cancelButton.textContent = 'Cancel';
      }
      
      showErrorMessage('An error occurred while cancelling the appointment');
      console.error('Error:', error);
    });
}
