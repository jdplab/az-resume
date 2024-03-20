function blogCreate() {
    var createPostButton = document.getElementById('blogCreate');
    if (createPostButton) {
        createPostButton.onclick = function() {
            if (sessionStorage.getItem('id_token')) {
                fetch('https://jpolanskyresume-functionapp.azurewebsites.net/api/newblog', {
                    headers: {
                        'Authorization': sessionStorage.getItem('id_token')
                    }
                })
                .then(response => response.text())
                .then(blobUrlWithSas => {
                    // Fetch the blob content
                    fetch(blobUrlWithSas)
                    .then(response => response.text())
                    .then(blobContent => {
                        // Insert the blob content into a container on your page
                        document.getElementById('newBlog').innerHTML = blobContent;
                    });
                })
                .catch(error => console.error('Error:', error));
            }
        };
    }
}