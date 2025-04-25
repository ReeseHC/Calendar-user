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
  
  // Parse the date to get the ISO format (YYYY-MM-DD)
  const date = new Date(dateString);
  const isoDate = date.toISOString().split('T')[0];
  
  // Send the request to the server
  fetch('/api/book-appointment', {
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
      // Show success message
      showSuccessMessage(data.message || 'Appointment booked successfully!');
      
      // Update the appointment counts
      if (data.appointments) {
        document.getElementById('bookedCount').textContent = data.appointments.booked;
        document.getElementById('openCount').textContent = data.appointments.open;
      }
      
      // You could update the UI here or reload the page
      setTimeout(() => {
        location.reload();
      }, 1500);
    } else {
      showErrorMessage(data.error || 'Failed to book appointment');
    }
  })
  .catch(error => {
    showErrorMessage('An error occurred while booking the appointment');
    console.error('Error:', error);
  });
}

function startCancelAppointment(time, elementId) {
  // Show confirmation modal
  const modal = document.getElementById('confirmationModal');
  if (modal) {
    modal.style.display = 'block';
    
    // Store time and elementId for the confirmation action
    document.getElementById('confirmCancelButton').onclick = function() {
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
  
  // Send the request to the server
  fetch('/api/cancel-appointment', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      date: isoDate,
      time: time,
      confirmed: true
    }),
  })
  .then(response => response.json())
  .then(data => {
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
        window.location.href = `/feedback?date=${isoDate}&time=${time}`;
      }, 1500);
    } else {
      showErrorMessage(data.error || 'Failed to cancel appointment');
    }
  })
  .catch(error => {
    showErrorMessage('An error occurred while cancelling the appointment');
    console.error('Error:', error);
  });
}

// Add event listener when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Add event listener to back button to set refresh flag
  const backButton = document.querySelector('.back-button');
  if (backButton) {
    backButton.addEventListener('click', setRefreshFlag);
  }
  
  // Close the modal when clicking the close button or outside the modal
  const closeModalButtons = document.querySelectorAll('.cancel-modal-button');
  closeModalButtons.forEach(button => {
    button.addEventListener('click', function() {
      const modal = this.closest('.modal');
      if (modal) {
        modal.style.display = 'none';
      }
    });
  });
  
  // Close modal when clicking outside
  window.addEventListener('click', function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
      if (event.target === modal) {
        modal.style.display = 'none';
      }
    });
  });
});