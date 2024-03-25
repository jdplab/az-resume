var urlParams = new URLSearchParams(window.location.search);
var postId = urlParams.get('id');

// Make an AJAX request to the Azure function
var xhr = new XMLHttpRequest();
xhr.open('GET', 'https://jpolanskyresume-functionapp.azurewebsites.net/api/getpost?id=' + postId, true);
xhr.onreadystatechange = function () {
    if (xhr.readyState == 4 && xhr.status == 200) {
        var response = JSON.parse(xhr.responseText);
        var data = response.data;

        document.getElementById('fullBlogPost').innerHTML = `
            <div class="fullpost">${data.html}</div>
        `;
    }
};
xhr.send();

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
    })
    .catch(error => {
        console.error('There was an error!', error);
        displayModal('There was an error submitting your comment.');
    });
}

// Make an AJAX request to the Azure function
var xhr2 = new XMLHttpRequest();
xhr2.open('GET', 'https://jpolanskyresume-functionapp.azurewebsites.net/api/getcomments?id=' + postId, true);
xhr2.onreadystatechange = function () {
    if (xhr2.readyState == 4 && xhr2.status == 200) {
        var comments = JSON.parse(xhr2.responseText);

        var html = '';
        for (var i = 0; i < comments.length; i++) {
            var comment = comments[i];

            var date = new Date(comment.timestamp);
            var formattedDate = date.toDateString();
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
        document.getElementById('comments').innerHTML = html;
    }
};
xhr2.send();