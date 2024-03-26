function displayModal(message) {
    var modal = document.createElement('div');
    modal.className = 'modal';

    var modalContent = document.createElement('div');
    modalContent.className = 'modal-content';
    modal.appendChild(modalContent);

    var text = document.createElement('p');
    text.textContent = message;
    modalContent.appendChild(text);

    var closeButton = document.createElement('span');
    closeButton.className = 'close';
    closeButton.innerHTML = '&times;';
    closeButton.onclick = function() {
        modal.style.display = 'none';
    };
    modalContent.appendChild(closeButton);

    document.getElementById('main').appendChild(modal);

    modal.style.display = 'block';

    modal.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

function displayDialogueModal(message, confirmCallback, cancelCallback) {
    var modal = document.createElement('div');
    modal.className = 'modal';

    var modalContent = document.createElement('div');
    modalContent.className = 'modal-content';
    modal.appendChild(modalContent);

    var text = document.createElement('p');
    text.textContent = message;
    modalContent.appendChild(text);

    var yesButton = document.createElement('button');
    yesButton.textContent = 'Yes';
    yesButton.className = 'button';
    yesButton.onclick = function() {
        modal.style.display = 'none';
        if (confirmCallback) {
            confirmCallback();
        }
    };
    modalContent.appendChild(yesButton);

    var noButton = document.createElement('button');
    noButton.textContent = 'No';
    noButton.className = 'button';
    noButton.onclick = function() {
        modal.style.display = 'none';
        if (cancelCallback) {
            cancelCallback();
        }
    };
    modalContent.appendChild(noButton);

    document.getElementById('main').appendChild(modal);

    modal.style.display = 'block';

    modal.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}