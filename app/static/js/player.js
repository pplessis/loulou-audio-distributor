// Script pour gérer le lecteur audio et les interactions
function playChapter(audioUrl, chapterTitle) {
    const audioPlayer = document.getElementById('audioPlayer');
    const audioSource = document.getElementById('audioSource');
    const playerInfo = document.getElementById('playerInfo');

    // Mettre à jour la source audio
    audioSource.src = audioUrl;
    
    // Charger l'audio
    audioPlayer.load();
    
    // Jouer l'audio
    audioPlayer.play()
        .then(() => {
            // Mettre à jour l'affichage
            playerInfo.innerHTML = `
                <p><strong>En cours de lecture :</strong> ${chapterTitle}</p>
                <p>Profite bien de l'histoire ! 😊</p>
            `;
        })
        .catch(error => {
            console.error("Erreur lors de la lecture :", error);
            playerInfo.innerHTML = "<p>Impossible de lire ce chapitre. Vérifie ta connexion ou réessaye plus tard.</p>";
        });
}

// Ajouter un écouteur pour détecter la fin de la lecture
const audioPlayer = document.getElementById('audioPlayer');
audioPlayer.addEventListener('ended', () => {
    const playerInfo = document.getElementById('playerInfo');
    playerInfo.innerHTML = "<p>Chapitre terminé ! 🎉 Sélectionne un autre chapitre pour continuer l'histoire.</p>";
});

// Afficher un message si le navigateur ne supporte pas l'audio
audioPlayer.addEventListener('error', () => {
    const playerInfo = document.getElementById('playerInfo');
    playerInfo.innerHTML = "<p>Votre navigateur ne supporte pas la lecture audio. Essayez avec un autre navigateur comme Chrome ou Firefox.</p>";
});
