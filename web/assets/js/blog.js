function blogCreate() {
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
                const newBlog = document.getElementById('newBlog');
                if (newBlog) {
                    newBlog.style.opacity = '1';
                    newBlog.style.visibility = 'visible';
                    newBlog.style.display = 'block';
                    newBlog.innerHTML = blobContent;
                    const quill = new Quill('#editor', {
                        theme: 'snow'
                    });
                }
            })
            .catch(error => console.error('Error fetching blob:', error));
        })
        .catch(error => console.error('Error fetching blob URL:', error));
    } else {
        displayModal('You must be logged in to create a blog post.')
    }
};

function savePost() {
    const title = document.getElementById('title').value;
    const description = document.getElementById('description').value;
    const html = quill.root.innerHTML;
    fetch('https://jpolanskyresume-functionapp.azurewebsites.net/api/saveblog', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + sessionStorage.getItem('id_token')
    },
    body: JSON.stringify({title: title, description: description, html: html})
    })
    .then(response => {
    if (response.ok) {
        alert('Post saved successfully.');
    } else {
        alert('Failed to save post.');
    }
    });
}