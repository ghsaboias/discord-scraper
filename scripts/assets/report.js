function sortMessages(order) {
    const messagesDiv = document.querySelector('.messages');
    const messages = Array.from(messagesDiv.children);
    
    messages.sort((a, b) => {
        const timeA = new Date(a.querySelector('.timestamp').textContent.split(' (')[0]);
        const timeB = new Date(b.querySelector('.timestamp').textContent.split(' (')[0]);
        return order === 'newest' ? timeB - timeA : timeA - timeB;
    });
    
    messagesDiv.innerHTML = '';
    messages.forEach(msg => messagesDiv.appendChild(msg));
}

document.addEventListener('DOMContentLoaded', function() {
    // Initial sort
    sortMessages('newest');
    
    // Create modal elements
    const modal = document.createElement('div');
    modal.className = 'modal';
    const modalImg = document.createElement('img');
    modalImg.className = 'modal-content';
    const closeBtn = document.createElement('span');
    closeBtn.className = 'modal-close';
    closeBtn.innerHTML = '&times;';
    
    modal.appendChild(modalImg);
    modal.appendChild(closeBtn);
    document.body.appendChild(modal);
    
    // Add click handlers to all images
    document.querySelectorAll('.attachment-img').forEach(img => {
        img.onclick = function() {
            modal.style.display = 'flex';
            modalImg.src = this.src;
        }
    });
    
    // Close modal handlers
    closeBtn.onclick = function() {
        modal.style.display = 'none';
    }
    
    modal.onclick = function(e) {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    }
    
    // Close on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            modal.style.display = 'none';
        }
    });
}); 