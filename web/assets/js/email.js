document.getElementById('emailForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const formData = new FormData(this);

    try {
        const response = await fetch('https://jpolanskyresume-functionapp.azurewebsites.net/api/sendemail', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(Object.fromEntries(formData))
        });

        if (response.ok) {
            showModal('Email sent successfully!');
            this.reset();
        } else {
            showModal('Failed to send email.');
        }
    } catch (error) {
        console.error('Error:', error);
        showModal('An error occurred while sending the email.');
    }
});

function showModal(message) {
    const modal = document.getElementById("emailSuccessOrFail");
    const modalMessage = document.getElementById("emailMessage");
    modal.style.display = "block";
    modalMessage.textContent = message;

    // Close the modal when user clicks on the close button
    const closeBtn = document.getElementsByClassName("close")[0];
    closeBtn.onclick = function() {
        modal.style.display = "none";
    }

    // Close the modal when user clicks anywhere outside of it
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
}