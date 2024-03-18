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

    document.body.appendChild(modal);

    modal.style.display = 'block';
}