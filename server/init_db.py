import warnings
from app import app, db, Article

# Suppress warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=UserWarning, module='werkzeug')

def init_db():
    with app.app_context():
        # Create all database tables
        db.create_all()
        
        # Clear existing articles
        db.session.query(Article).delete()
        
        # Add test articles if none exist
        if not db.session.query(Article).first():
            test_articles = [
                Article(
                    id=1,
                    title="Test Article 1",
                    content="This is test content for article 1",
                    author="Test Author",
                    date="2023-01-01"
                ),
                Article(
                    id=2,
                    title="Test Article 2",
                    content="This is test content for article 2",
                    author="Test Author",
                    date="2023-01-02"
                )
            ]
            db.session.add_all(test_articles)
            db.session.commit()
            print("Database initialized with test data")

if __name__ == '__main__':
    init_db()
