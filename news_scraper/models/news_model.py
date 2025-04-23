class NewsModel:
    def __init__(self, source, title, content, date, image_url, image_path, author, related_links):
        self.source = source
        self.title = title
        self.content = content
        self.date = date
        self.image_url = image_url
        self.image_path = image_path
        self.author = author
        self.related_links = related_links

    def to_dict(self):
        """Convert the news model to a dictionary."""
        return {
            "version": "1.0",
            "document": {
                "id": self.source.replace(".", "_"),
                "title": self.title,
                "content": self.content,
                "metadata": {
                    "source": self.source,
                    "date": self.date,
                    "image_url": self.image_url,
                    "image_path": self.image_path,
                    "author": self.author,
                    "related_links": self.related_links,
                    "attachments": []
                }
            }
        }
