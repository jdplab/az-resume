let quill;

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
                    tinymce.init({
                        selector: '#editor',
                        height: 500,
                        plugins: [
                            'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
                            'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
                            'insertdatetime', 'media', 'table', 'help', 'wordcount'
                        ],
                        toolbar: 'undo redo | blocks | ' +
                        'bold italic backcolor | alignleft aligncenter ' +
                        'alignright alignjustify | bullist numlist outdent indent | ' +
                        'removeformat | help',
                        content_style: 'body { font-family:Helvetica,Arial,sans-serif; font-size:16px }',
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
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to save post. Please try again.');
    });
}

// Make an AJAX request to the Azure function
var xhr = new XMLHttpRequest();
xhr.open('GET', 'https://jpolanskyresume-functionapp.azurewebsites.net/api/getrecentposts', true);
xhr.onreadystatechange = function () {
    if (xhr.readyState == 4 && xhr.status == 200) {
        // Parse the response
        var posts = JSON.parse(xhr.responseText);

        var html = '';
        for (var i = 0; i < posts.length; i++) {
            var post = posts[i];
            html += `
                <article class="col-6 col-12-xsmall work-item project-item">
                    <a href="/blog.html?id=${post.id}" class="image fit"><img src="${post.image_url}" alt="${post.data.title}" /></a>
                    <h3>${post.data.title}</h3>
                    <p>${post.data.description}</p>
                </article>
            `;
        }
        document.getElementById('blogShortDescriptions').innerHTML = html;
    }
};
xhr.send();