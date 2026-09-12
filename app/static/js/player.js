// Script pour gérer le lecteur audio et les interactions
function playChapter(audioUrl, chapterTitle, chapterIndex) {
    const audioPlayer = document.getElementById('audioPlayer');
    const audioSource = document.getElementById('audioSource');
    const playerInfo = document.getElementById('playerInfo');
    const chaptersList = document.querySelector('.chapters-list');
    const bookId = chaptersList ? chaptersList.dataset.bookId : null;

    // Use the audio proxy to fetch through server (handles CORS and sharing)
    const proxyUrl = `/audio?url=${encodeURIComponent(audioUrl)}`;

    // Update audio source
    audioSource.src = proxyUrl;

    // Load audio
    audioPlayer.load();

    // Play audio
    audioPlayer.play()
        .then(() => {
            playerInfo.innerHTML = `
                <p><strong>En cours de lecture :</strong> ${chapterTitle}</p>
                <p>Profite bien de l'histoire ! 😊</p>
            `;
        })
        .catch(error => {
            console.error("Erreur lors de la lecture :", error);
            playerInfo.innerHTML = "<p>Impossible de lire ce chapitre. Vérifie le lien OneDrive (1drv.ws) et que le fichier est publiquement partagé.</p>";
        });

    // Send position update to server
    if (bookId && typeof chapterIndex === 'number') {
        fetch(`/book/${bookId}/position`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chapter_number: chapterIndex })
        }).catch(err => console.error('Failed to save position', err));
    }
}

// Ajouter un écouteur pour détecter la fin de la lecture
const audioPlayer = document.getElementById('audioPlayer');
audioPlayer.addEventListener('ended', () => {
    const playerInfo = document.getElementById('playerInfo');
    playerInfo.innerHTML = "<p>Chapitre terminé ! 🎉 Sélectionne un autre chapitre pour continuer l'histoire.</p>";
});

// Afficher un message détaillé en cas d'erreur
audioPlayer.addEventListener('error', (e) => {
    const playerInfo = document.getElementById('playerInfo');
    const error = e.target.error;
    let message = "Une erreur est survenue lors de la lecture.";
    if (error) {
        message = `Erreur de lecture (code ${error.code}) : ` +
            (error.code === 4 ? "Le fichier audio est introuvable ou invalide. Vérifiez le lien OneDrive." :
             error.code === 2 ? "Erreur de média. Problème CORS ou format non supporté." :
             error.code === 3 ? "Décodage impossible. Le format du fichier n'est pas supporté." :
             "Veuillez vérifier votre connexion ou réessayer plus tard.");
    }
    playerInfo.innerHTML = `<p>${message}</p>`;
});
