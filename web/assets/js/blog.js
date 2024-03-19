window.onload = function() {    
    if (sessionStorage.getItem('id_token')) {
        fetch('https://jpolanskyresume-functionapp.azurewebsites.net/api/verifytoken', {
            headers: {
                'Authorization': sessionStorage.getItem('id_token')
            }
        })
        .then(response => response.json())
        .then(data => {
            var createPostButton = document.getElementById('blogCreate');
            if (data.admin) {
                if (createPostButton) {
                    createPostButton.onclick = function() { displayModal('Create a blog.'); };
                }
            } else {
                if (createPostButton) {
                    createPostButton.onclick = function() { displayModal('Access Denied.'); };
                }
            }
        })
    }
}