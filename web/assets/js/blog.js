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
                    document.getElementById('image').addEventListener('change', function() {
                        var filename = this.files[0].name;
                        document.getElementById('filename').textContent = filename;
                    });
                    tinymce.init({
                        selector: '#editor',
                        placeholder: 'Type here...',
                        min_height: 500,
                        resize: true,
                        menubar: 'file edit view insert format tools table help',
                        plugins: 'preview searchreplace autolink directionality code visualblocks visualchars fullscreen image link media codesample table charmap pagebreak nonbreaking anchor insertdatetime advlist lists wordcount help charmap quickbars emoticons accordion',
                        toolbar: "undo redo | accordion accordionremove | blocks fontfamily fontsize | bold italic underline strikethrough | align numlist bullist | link image media | table codesample | lineheight outdent indent| forecolor backcolor removeformat | charmap emoticons | code fullscreen preview",
                        content_style: 'body { font-family:Helvetica,Arial,sans-serif; font-size:16px } img {max-width: 100%; height: auto;}',
                        toolbar_mode: 'wrap',
                    })
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
    const image = document.getElementById('image').files[0];
    const tags = document.getElementById('tags').value;
    const html = tinymce.get('editor').getContent();
    let formData = new FormData();
    formData.append('title', title);
    formData.append('description', description);
    formData.append('html', html);
    formData.append('image', image);
    formData.append('tags', tags);
    fetch('https://jpolanskyresume-functionapp.azurewebsites.net/api/saveblog', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer ' + sessionStorage.getItem('id_token')
        },
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.text();
    })
    .then(data => {
        alert('Post saved successfully.');
        setTimeout(function() {
            window.location.href = '/blogindex.html';
        }, 3000);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to save post. Please try again.');
    });
}

var posts = [];

var xhr = new XMLHttpRequest();
xhr.open('GET', 'https://jpolanskyresume-functionapp.azurewebsites.net/api/getrecentposts', true);
xhr.onreadystatechange = function () {
    if (xhr.readyState == 4 && xhr.status == 200) {
        posts = JSON.parse(xhr.responseText);
        displayPosts(posts);
    }
};
xhr.send();

function displayPosts(postsToDisplay) {
    var html = '';
    for (var i = 0; i < postsToDisplay.length; i++) {
        var post = postsToDisplay[i];

        var date = new Date(post.timestamp);
        var formattedDate = date.toDateString();

        html += `
            <article class="col-6 col-12-xsmall work-item project-item">
            <a href="/posts/${post.id}.html" class="image fit thumb"><img src="${post.image_url}" alt="${post.title}" /></a>
                <h3>${post.title}</h3>
                <p>${formattedDate}</p>
                <p>${post.description}</p>
            </article>
        `;
    }
    document.getElementById('blogShortDescriptions').innerHTML = html;
    searchBar = document.getElementById('searchBar');
    if (searchBar) {
        searchBar.style.opacity = '1';
        searchBar.style.visibility = 'visible';
        searchBar.style.display = 'block';
    }
}

function searchBlog() {
    var searchText = document.getElementById('searchBar').value.toLowerCase();
    var sanitizedSearchText = encodeURIComponent(searchText);
    var filteredPosts = posts.filter(function(post) {
        return post.title.toLowerCase().includes(sanitizedSearchText) || post.description.toLowerCase().includes(sanitizedSearchText);
    });
    displayPosts(filteredPosts);
}