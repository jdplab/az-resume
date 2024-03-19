function blogCreate() {
    var createPostButton = document.getElementById('blogCreate');
    if (createPostButton) {
        createPostButton.onclick = function() {
            if (sessionStorage.getItem('id_token')) {
                fetch('https://jpolanskyresume-functionapp.azurewebsites.net/api/verifytoken', {
                    headers: {
                        'Authorization': sessionStorage.getItem('id_token')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.admin) {
                        displayModal('Create a blog.');
                    } else {
                        displayModal('Access Denied.');
                    }
                });
            } else {
                displayModal('You must be logged in as an admin to create a blog post.');
            }
        };
    }
}