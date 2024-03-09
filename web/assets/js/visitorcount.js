const functionApi = "https://jpolanskyresume-functionapp.azurewebsites.net/api/app";
const testApi = "url";
    const getVisitCount = () => {
        return fetch(functionApi)
        .then(response => response.json())
        .then(data => {
            document.getElementById('unique_visitors').innerText = data.unique_visitors;
            document.getElementById('total_visits').innerText = data.total_visits;
            document.getElementById('visits').innerText = data.visits;
        }).catch(function(error) {
            console.log(error);
        });
    };
    getVisitCount();