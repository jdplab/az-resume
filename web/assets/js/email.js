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
            displayModal('Email sent successfully!');
            this.reset();
        } else {
            displayModal('Failed to send email.');
        }
    } catch (error) {
        console.error('Error:', error);
        displayModal('An error occurred while sending the email.');
    }
});