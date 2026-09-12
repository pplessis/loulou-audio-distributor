class ReadingPosition:
    def __init__(self, user_id, book_id, last_chapter, last_updated=None):
        self.user_id = user_id
        self.book_id = book_id
        self.last_chapter = last_chapter
        self.last_updated = last_updated

    def validate(self, total_chapters=None):
        if self.last_chapter < 1:
            raise ValueError("last_chapter must be >= 1")
        if total_chapters is not None and self.last_chapter > total_chapters:
            raise ValueError("last_chapter exceeds total chapters in book")
