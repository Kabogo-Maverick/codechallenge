from lib.models.author import Author
from lib.models.magazine import Magazine
from lib.models.article import Article

def quick_test():
    # Clear existing data (optional, depends on your setup)
    # Just recreate objects for now

    # Create and save an Author
    author = Author("Alice Wonderland")
    author.save()
    print(f"Author saved: {author.id} - {author.name}")

    # Create and save a Magazine
    magazine = Magazine("Tech Today", "Technology")
    magazine.save()
    print(f"Magazine saved: {magazine.id} - {magazine.name}")

    # Create and save Articles
    article1 = Article("The Future of AI", author.id, magazine.id)
    article1.save()
    article2 = Article("Quantum Computing", author.id, magazine.id)
    article2.save()

    print(f"Articles saved:")
    for article in [article1, article2]:
        print(f"- {article.id}: {article.title}")

    # Query back articles by author
    author_articles = author.articles()
    print(f"\nArticles by {author.name}:")
    for art in author_articles:
        print(f" * {art.title}")

    # Query contributors for magazine
    contributors = magazine.contributors()
    print(f"\nContributors for {magazine.name}:")
    for contrib in contributors:
        print(f" - {contrib.name}")

    # Use aggregate method: top author
    top_author = Author.top_author()
    print(f"\nTop author is: {top_author.name}")

if __name__ == "__main__":
    quick_test()
