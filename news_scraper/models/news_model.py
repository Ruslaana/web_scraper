class NewsModel:
    def __init__(self, source, title, content, date, image_url, author, related_links):
        self.source = source
        self.title = title
        self.content = content
        self.date = date
        self.image_url = image_url
        self.author = author
        self.related_links = related_links

    def to_dict(self):
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
                    "author": self.author,
                    "related_links": self.related_links,
                    "attachments": []
                }
            }
        }
