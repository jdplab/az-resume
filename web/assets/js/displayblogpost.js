var pathArray = window.location.pathname.split('/');
var postId = pathArray[pathArray.length - 1].replace('.html', '');

window.addEventListener('load', function() {
    if (sessionStorage.getItem('id_token')) {
        fetch('https://jpolanskyresume-functionapp.azurewebsites.net/api/verifytoken', {
            headers: {
                'Authorization': 'Bearer ' + sessionStorage.getItem('id_token')
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.admin) {
                var editdeletesection = document.getElementById('editDelete');
                if (editdeletesection) {
                    editdeletesection.style.opacity = '1';
                    editdeletesection.style.visibility = 'visible';
                    editdeletesection.style.display = 'block';
                }
                var fullBlogPost = document.getElementById('fullBlogPost');
                if (fullBlogPost) {
                    fullBlogPost.style.padding = '4em 0 0 0';
                    fullBlogPost.style.margin = '4em 0 0 0';
                    fullBlogPost.style.borderTop = 'solid 2px #efefef';
                }
            } else {
                console.log('User is not an admin.');
            }
        })
        .catch(error => {
            console.error('There was an error!', error);
        });
    } else {
        console.log('User is not logged in.');
    }
});

function deletePost() {
    displayDialogueModal('Are you sure you want to delete this post?', function() {
        fetch('https://jpolanskyresume-functionapp.azurewebsites.net/api/deletepost?id=' + postId, {
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
        .then(data => {
            displayModal('Post deleted successfully');
            setTimeout(function() {
                window.location.href = '/blogindex.html';
            }, 3000);
        })
        .catch(error => {
            console.error('There was an error!', error);
        });
    });
};

function editPost() {
    fetch('https://jpolanskyresume-functionapp.azurewebsites.net/api/editpost?id=' + postId, {
        headers: {
            'Authorization': 'Bearer ' + sessionStorage.getItem('id_token')
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Initialize TinyMCE with the post data
        tinymce.init({
            selector: '#editPostBox',
            min_height: 500,
            resize: true,
            menubar: 'file edit view insert format tools table help',
            plugins: 'preview searchreplace autolink directionality code visualblocks visualchars fullscreen image link media codesample table charmap pagebreak nonbreaking anchor insertdatetime advlist lists wordcount help charmap quickbars emoticons accordion',
            toolbar: "undo redo | accordion accordionremove | blocks fontfamily fontsize | bold italic underline strikethrough | align numlist bullist | link image media | table codesample | lineheight outdent indent| forecolor backcolor removeformat | charmap emoticons | code fullscreen preview",
            content_style: 'body { font-family:Helvetica,Arial,sans-serif; font-size:16px } img {max-width: 100%; height: auto;}',
            toolbar_mode: 'wrap',
            setup: function (editor) {
                editor.on('init', function () {
                    editor.setContent(data.html);
                });
            }
        });
        var saveEditButton = document.getElementById('saveEditButton');
        if (saveEditButton) {
            saveEditButton.style.opacity = '1';
            saveEditButton.style.visibility = 'visible';
            saveEditButton.style.display = 'block';
        }
        var titleField = document.getElementById('titleField');
        if (titleField) {
            titleField.style.opacity = '1';
            titleField.style.visibility = 'visible';
            titleField.style.display = 'block';
            titleField.value = data.title;
        }
        var descriptionField = document.getElementById('descriptionField');
        if (descriptionField) {
            descriptionField.style.opacity = '1';
            descriptionField.style.visibility = 'visible';
            descriptionField.style.display = 'block';
            descriptionField.value = data.description;
        }
        var tagsField = document.getElementById('tagsField');
        if (tagsField) {
            tagsField.style.opacity = '1';
            tagsField.style.visibility = 'visible';
            tagsField.style.display = 'block';
            tagsField.value = data.tags;
        }
        var editButton = document.getElementById('editButton');
        if (editButton) {
            editButton.style.opacity = '0';
            editButton.style.visibility = 'hidden';
            editButton.style.display = 'none';
        }
        var deleteButton = document.getElementById('deleteButton');
        if (deleteButton) {
            deleteButton.style.opacity = '0';
            deleteButton.style.visibility = 'hidden';
            deleteButton.style.display = 'none';
        }
    })
    .catch(error => {
        console.error('There was an error!', error);
    });
};

function editPostSave(){
    var content = tinymce.get('editPostBox').getContent();
    var title = document.getElementById('titleField').value;
    var description = document.getElementById('descriptionField').value;
    var tags = document.getElementById('tagsField').value;
    var formData = new FormData();
    formData.append('html', content);
    formData.append('title', title);
    formData.append('description', description);
    formData.append('tags', tags);
    fetch('https://jpolanskyresume-functionapp.azurewebsites.net/api/editpostsave?id=' + postId, {
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
        displayModal('Edit saved successfully');
        setTimeout(function() {
            location.reload();
        }, 3000);
    })
    .catch(error => {
        console.error('There was an error!', error);
    });
};

//var xhr = new XMLHttpRequest();
//xhr.open('GET', 'https://jpolanskyresume-functionapp.azurewebsites.net/api/getpost?id=' + postId, true);
//xhr.onreadystatechange = function () {
//    if (xhr.readyState == 4 && xhr.status == 200) {
//        var response = JSON.parse(xhr.responseText);
//        var data = response.data;
//
//        document.getElementById('fullBlogPost').innerHTML = `
//            <div class="fullpost">${data.html}</div>
//        `;
//    }
//};
//xhr.send();

function commentCreate() {
    if (sessionStorage.getItem('id_token')) {
        fetch('https://jpolanskyresume-functionapp.azurewebsites.net/api/verifytoken', {
            headers: {
                'Authorization': 'Bearer ' + sessionStorage.getItem('id_token')
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.hasOwnProperty('admin')) {
                const newCommentButton = document.getElementById('newComment');
                if (newCommentButton) {
                    newCommentButton.style.opacity = '0';
                    newCommentButton.style.visibility = 'hidden';
                    newCommentButton.style.display = 'none';
                }
                const newCommentForm = document.getElementById('newCommentForm');
                if (newCommentForm) {
                    newCommentForm.style.opacity = '1';
                    newCommentForm.style.visibility = 'visible';
                    newCommentForm.style.display = 'block';
                }
                const submitCommentButton = document.getElementById('submitComment');
                if (submitCommentButton) {
                    submitCommentButton.style.opacity = '1';
                    submitCommentButton.style.visibility = 'visible';
                    submitCommentButton.style.display = 'block';
                }
            } else {
                displayModal('You must be logged in to comment.')
            }
        })
        .catch(error => {
            console.error('There was an error!', error);
        });
    } else {
        displayModal('You must be logged in to comment.')
    }
};

function commentSubmit() {
    var form = document.getElementById("newCommentForm");
    var comment = document.getElementById("commentBox").value;
    
    //Input validation
    if (!comment) {
        console.error('Comment is required!');
        return;
    }
    if (comment.length > 1000) {
        console.error('Comment is too long!');
        return;
    }

    var formData = new FormData();
    formData.append('comment', comment);
    fetch('https://jpolanskyresume-functionapp.azurewebsites.net/api/submitComment?id=' + postId, {
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
        displayModal('Comment submitted successfully.');
        form.reset();
        const newCommentForm = document.getElementById('newCommentForm');
        if (newCommentForm) {
            newCommentForm.style.opacity = '0';
            newCommentForm.style.visibility = 'hidden';
            newCommentForm.style.display = 'none';
        }
        const submitCommentButton = document.getElementById('submitComment');
        if (submitCommentButton) {
            submitCommentButton.style.opacity = '0';
            submitCommentButton.style.visibility = 'hidden';
            submitCommentButton.style.display = 'none';
        }
        setTimeout(function() {
            location.reload();
        }, 3000);
    })
    .catch(error => {
        console.error('There was an error!', error);
        displayModal('There was an error submitting your comment.');
    });
}

var xhr2 = new XMLHttpRequest();
xhr2.open('GET', 'https://jpolanskyresume-functionapp.azurewebsites.net/api/getcomments?id=' + postId, true);
xhr2.onreadystatechange = function () {
    if (xhr2.readyState == 4 && xhr2.status == 200) {
        var comments = JSON.parse(xhr2.responseText);

        var html = '';
        if (comments.length === 0) {
            html = '<p>Be the first to comment!</p>';
        } else {
            for (var i = 0; i < comments.length; i++) {
                var comment = comments[i];

                var date = new Date(comment.timestamp);
                var options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true };
                var formattedDate = date.toLocaleString(navigator.language, options);
                var firstname = comment.firstname;
                var lastname = comment.lastname;
                var commentText = comment.comment;

                html += `
                    <div id="individual-comment" class="individual-comment">
                        <h3>${firstname} ${lastname}</h3>
                        <p>${formattedDate}</p>
                        <p>${commentText}</p>
                    </div>
                `;
            }
        }
        document.getElementById('comments').innerHTML = html;
    }
};
xhr2.send();