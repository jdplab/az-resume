// Get the ID of the post from the query parameters
var urlParams = new URLSearchParams(window.location.search);
var postId = urlParams.get('id');

// Make an AJAX request to the Azure function
var xhr = new XMLHttpRequest();
xhr.open('GET', 'https://jpolanskyresume-functionapp.azurewebsites.net/api/getpost?id=' + postId, true);
xhr.onreadystatechange = function () {
    if (xhr.readyState == 4 && xhr.status == 200) {
        var response = JSON.parse(xhr.responseText);
        var data = response.data;
        var imageUrl = response.image_url;

        document.getElementById('fullBlogPost').innerHTML = `
            <h3>${data.title}</h3>
            <img src="${imageUrl}" alt="${data.title}" />
            <p>${data.description}</p>
            <div>${data.html}</div>
        `;
    }
};
xhr.send();