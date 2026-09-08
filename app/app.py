from flask import Flask, render_template
import os
import json

app = Flask(__name__)

# Chemin vers les métadonnées des livres
BOOKS_METADATA_DIR = os.path.join(os.path.dirname(__file__), 'books', 'metadata')

@app.route('/')
def index():
    """Page d'accueil : Liste tous les livres disponibles."""
    books = []
    for filename in os.listdir(BOOKS_METADATA_DIR):
        if filename.endswith('.json'):
            with open(os.path.join(BOOKS_METADATA_DIR, filename), 'r', encoding='utf-8') as f:
                book_data = json.load(f)
                books.append(book_data)
    return render_template('index.html', books=books)

@app.route('/book/<book_id>')
def book(book_id):
    """Page d'un livre : Affiche les chapitres et le lecteur audio."""
    book_path = os.path.join(BOOKS_METADATA_DIR, f'{book_id}.json')
    if not os.path.exists(book_path):
        return "Livre introuvable", 404
    
    with open(book_path, 'r', encoding='utf-8') as f:
        book_data = json.load(f)
    
    return render_template('book.html', book=book_data)

@app.route('/chapter/<int:chapter_id>')
def chapter(chapter_id):
    """Page d'un chapitre : Redirige vers le lecteur avec le chapitre sélectionné."""
    # Cette route peut être utilisée pour des liens directs vers un chapitre
    return "Fonctionnalité avancée : À implémenter si besoin"

if __name__ == '__main__':
    app.run(debug=True)
