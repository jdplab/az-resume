const functionApi = "https://jpolanskyresume-functionapp.azurewebsites.net/api/visitorcount";
const testApi = "url";

const getVisitCount = () => {
    return new Promise((resolve, reject) => {
        let repeatVisit = 0;

        // Check if local storage is available
        if (typeof(Storage) !== "undefined") {
            let lastVisit = localStorage.getItem('lastVisit');
            let now = Date.now();

            // If the user has not visited in the last 15 minutes
            if (!lastVisit || now - lastVisit > 15 * 60 * 1000) {
                repeatVisit = 0;
                // Try to update the last visit time
                try {
                    localStorage.setItem('lastVisit', now);
                } catch (e) {
                    if (e.name === 'QuotaExceededError') {
                        console.log('Local storage quota exceeded');
                    } else {
                        console.log('Cannot access local storage');
                    }
                }
            } else {
                repeatVisit = 1;
            }
        } else {
            console.log('Local storage is not supported by this browser');
            repeatVisit = 0; // Treat every visit as a new visit
        }

        // Fetch the visit count from the server
        fetch(`${functionApi}?repeatVisit=${repeatVisit}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('unique_visitors').innerText = data.unique_visitors;
            document.getElementById('total_visits').innerText = data.total_visits;
            document.getElementById('visits').innerText = data.visits;
            resolve(data);
        })
        .catch(function(error) {
            console.log('There has been a problem with your fetch operation: ', error);
            reject(error);
        });
    });
};

window.addEventListener('DOMContentLoaded', (event) => {
    getVisitCount()
    .catch(error => {
        console.log('Error getting visit count:', error);
    });
});