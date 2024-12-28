document.addEventListener('DOMContentLoaded', () => {
    const profileForm = document.getElementById('profile-form');
    const chatForm = document.getElementById('chat-form');
    const chatMessages = document.getElementById('chat-messages');
    const cloneInteraction = document.getElementById('clone-interaction');
    const creationStatus = document.getElementById('creation-status');

    // Klon oluşturma formu gönderildiğinde
    profileForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const url = document.getElementById('profile-url').value;
        creationStatus.textContent = 'Klon oluşturuluyor...';
        creationStatus.className = 'status-message';
        
        try {
            const response = await fetch('/create_clone', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `url=${encodeURIComponent(url)}`
            });
            
            const data = await response.json();
            
            if (response.ok) {
                creationStatus.textContent = data.message;
                creationStatus.className = 'status-message success';
                cloneInteraction.classList.remove('hidden');
            } else {
                throw new Error(data.error || 'Bir hata oluştu');
            }
        } catch (error) {
            creationStatus.textContent = error.message;
            creationStatus.className = 'status-message error';
        }
    });

    // Sohbet formu gönderildiğinde
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const questionInput = document.getElementById('question');
        const question = questionInput.value;
        
        // Kullanıcı mesajını ekle
        addMessage(question, 'user-message');
        questionInput.value = '';
        
        try {
            const response = await fetch('/ask_clone', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `question=${encodeURIComponent(question)}`
            });
            
            const data = await response.json();
            
            if (response.ok) {
                addMessage(data.response, 'clone-message');
            } else {
                throw new Error(data.error || 'Bir hata oluştu');
            }
        } catch (error) {
            addMessage('Üzgünüm, bir hata oluştu: ' + error.message, 'clone-message error');
        }
    });

    // Mesaj ekleme fonksiyonu
    function addMessage(text, className) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${className}`;
        messageDiv.textContent = text;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}); 