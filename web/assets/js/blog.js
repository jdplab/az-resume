function blogCreate() {
    var createPostButton = document.getElementById('blogCreate');
    if (createPostButton) {
        createPostButton.onclick = function() {
            if (sessionStorage.getItem('id_token')) {
                fetch('https://jpolanskyresume-functionapp.azurewebsites.net/api/newblog', {
                    headers: {
                        'Authorization': 'Bearer ' + sessionStorage.getItem('id_token')
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.text();
                })
                .then(blobUrlWithSas => {
                    // Fetch the blob content
                    fetch(blobUrlWithSas)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.text();
                    })
                    .then(blobContent => {
                        // Insert the blob content into a container on your page
                        document.getElementById('newBlog').innerHTML = blobContent;
                    })
                    .catch(error => console.error('Error fetching blob:', error));
                })
                .catch(error => console.error('Error fetching blob URL:', error));
            } else {
                displayModal('You must be logged in to create a blog post.')
            }
        };
    }
}