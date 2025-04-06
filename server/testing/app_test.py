import pytest
import warnings

# Comprehensive warning suppression
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", module="werkzeug")
warnings.filterwarnings("ignore", module="flask")
warnings.filterwarnings("ignore", module="pytest")

pytestmark = pytest.mark.filterwarnings("ignore")
from app import app, db, Article
import flask

class TestApp:
    def test_show_articles_route(self):
        '''shows an article "/article/<id>".'''
        with app.app_context():
            # Create test client
            client = app.test_client()
            
            # Create test article if it doesn't exist
            article = db.session.get(Article, 1)
            if not article:
                article = Article(
                    id=1,
                    title="Test Article",
                    content="Test content",
                    author="Test Author",
                    date="2023-01-01"
                )
                db.session.add(article)
                db.session.commit()
            
            # Make request
            response = client.get('/articles/1')
            response_json = response.get_json()
            
            # Verify response
            assert response.status_code == 200
            assert response_json['id'] == article.id
            assert response_json['title'] == article.title
            assert response_json['content'] == article.content
            assert response_json['author'] == article.author

    def test_increments_session_page_views(self):
        '''increases session['page_views'] by 1 after every viewed article.'''
        with app.test_client() as client:
            # Clear session
            with client.session_transaction() as sess:
                sess.clear()
            
            # Ensure test article exists
            with app.app_context():
                article = db.session.get(Article, 1)
                if not article:
                    article = Article(
                        id=1,
                        title="Test Article", 
                        content="Test content",
                        author="Test Author",
                        date="2023-01-01"
                    )
                    db.session.add(article)
                    db.session.commit()
            
            # First view
            client.get('/articles/1')
            with client.session_transaction() as sess:
                assert sess.get('page_views') == 1
            
            # Second view
            client.get('/articles/1')
            with client.session_transaction() as sess:
                assert sess.get('page_views') == 2

    def test_limits_three_articles(self):
        '''returns a 401 with an error message after 3 viewed articles.'''
        with app.test_client() as client:
            # Clear session
            with client.session_transaction() as sess:
                sess.clear()
            
            # Ensure test article exists
            with app.app_context():
                article = db.session.get(Article, 1)
                if not article:
                    article = Article(
                        id=1,
                        title="Test Article",
                        content="Test content",
                        author="Test Author",
                        date="2023-01-01"
                    )
                    db.session.add(article)
                    db.session.commit()
            
            # First 3 views should work
            for i in range(3):
                response = client.get('/articles/1')
                assert response.status_code == 200
            
            # 4th view should be blocked
            response = client.get('/articles/1')
            assert response.status_code == 401
            assert response.get_json()['message'] == 'Maximum pageview limit reached'
