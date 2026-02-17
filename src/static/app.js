document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;
        
        // Create participants list
        let participantsList = '';
        if (details.participants.length > 0) {
          const participantsItems = details.participants.map(email => 
            `<li class="participant-item">
               <span class="participant-email">${email}</span>
               <button class="delete-participant-btn" onclick="removeParticipant('${name}', '${email}')" title="Remove participant">
                 <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                   <path d="M3 6h18"></path>
                   <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
                   <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
                   <line x1="10" y1="11" x2="10" y2="17"></line>
                   <line x1="14" y1="11" x2="14" y2="17"></line>
                 </svg>
               </button>
             </li>`
          ).join('');
          participantsList = `
            <div class="participants-section">
              <p><strong>Participants:</strong></p>
              <ul class="participants-list">
                ${participantsItems}
              </ul>
            </div>
          `;
        } else {
          participantsList = `
            <div class="participants-section">
              <p><strong>Participants:</strong> <em>No participants yet</em></p>
            </div>
          `;
        }

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          ${participantsList}
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
      
      // Refresh activities to show updated participant list
      const activitiesListElement = document.getElementById("activities-list");
      const activitySelectElement = document.getElementById("activity");
      
      // Show loading state
      activitiesListElement.innerHTML = "<p>Refreshing...</p>";
      activitySelectElement.innerHTML = '<option value="">-- Select an activity --</option>';
      
      // Fetch updated activities
      fetchActivities();

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});

// Function to remove participant from activity
async function removeParticipant(activityName, email) {
  if (!confirm(`Are you sure you want to remove ${email} from ${activityName}?`)) {
    return;
  }

  try {
    const response = await fetch(
      `/activities/${encodeURIComponent(activityName)}/participants/${encodeURIComponent(email)}`,
      {
        method: "DELETE",
      }
    );

    const result = await response.json();

    if (response.ok) {
      // Show success message
      const messageDiv = document.getElementById("message");
      messageDiv.textContent = result.message;
      messageDiv.className = "success";
      messageDiv.classList.remove("hidden");

      // Hide message after 3 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 3000);

      // Refresh activities to show updated participant list
      const activitiesList = document.getElementById("activities-list");
      const activitySelect = document.getElementById("activity");
      
      // Clear current content
      activitiesList.innerHTML = "<p>Refreshing...</p>";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';
      
      // Fetch updated activities
      fetchActivities();
    } else {
      alert(result.detail || "Failed to remove participant");
    }
  } catch (error) {
    alert("Failed to remove participant. Please try again.");
    console.error("Error removing participant:", error);
  }
}
