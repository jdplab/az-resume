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
        var posts = JSON.parse(xhr.responseText);

        var html = '';
        for (var i = 0; i < posts.length; i++) {
            var post = posts[i];

            var date = new Date(post.timestamp);
            var formattedDate = date.toDateString();

            var tagsHtml = '';
            for (var j = 0; j < post.tags.length; j++) {
                tagsHtml += (j > 0 ? ' ' : '') + '<li class="button blogposttag">' + post.tags[j] + '</li>';
            }

            html += `
                <a href="/blog.html?id=${post.id}"><article class="col-6 col-12-xsmall work-item project-item article-preview">
                    <img src="${post.image_url}" alt="${post.title}" class="image fit">
                    <h3>${post.title}</h3>
                    <p>${formattedDate}</p>
                    <p>${post.description}</p>
                    <ul class="tags">
                        ${tagsHtml}
                    </ul>
                </article></a>
            `;
        }
        document.getElementById('blogShortDescriptions').innerHTML = html;
    }
};
xhr.send();