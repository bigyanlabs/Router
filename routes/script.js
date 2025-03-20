document.addEventListener('DOMContentLoaded', function() {
    console.log('Root page script loaded!');
    
    const themeButton = document.getElementById('themeButton');
    if (themeButton) {
        themeButton.addEventListener('click', function() {
            document.body.classList.toggle('dark-theme');
            
            const isDarkTheme = document.body.classList.contains('dark-theme');
            localStorage.setItem('darkTheme', isDarkTheme);
            showMessage(isDarkTheme ? 'Dark theme enabled' : 'Light theme enabled');
        });
        
        const savedTheme = localStorage.getItem('darkTheme');
        if (savedTheme === 'true') {
            document.body.classList.add('dark-theme');
        }
    }
    
    function showMessage(text) {
        let messageEl = document.getElementById('message-toast');
        if (!messageEl) {
            messageEl = document.createElement('div');
            messageEl.id = 'message-toast';
            messageEl.style.position = 'fixed';
            messageEl.style.bottom = '20px';
            messageEl.style.right = '20px';
            messageEl.style.backgroundColor = 'var(--primary)';
            messageEl.style.color = 'white';
            messageEl.style.padding = '10px 20px';
            messageEl.style.borderRadius = '4px';
            messageEl.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
            messageEl.style.transition = 'all 0.3s ease';
            messageEl.style.opacity = '0';
            document.body.appendChild(messageEl);
        }
        
        messageEl.textContent = text;
        messageEl.style.opacity = '1';
        
        setTimeout(() => {
            messageEl.style.opacity = '0';
        }, 3000);
    }
});