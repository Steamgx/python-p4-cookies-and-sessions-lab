import warnings
from flask import Flask, jsonify, session

# Suppress all deprecation and runtime warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", module="werkzeug")
warnings.filterwarnings("ignore", module="flask")
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'dev-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Article(db.Model):
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    content = db.Column(db.String)
    author = db.Column(db.String)
    date = db.Column(db.String)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'author': self.author,
            'date': self.date,
            'preview': self.content[:100] if self.content else '',
            'minutes_to_read': max(1, len(self.content.split()) // 200) if self.content else 1
        }

@app.route('/clear')
def clear_session():
    session.clear()
    return {'message': 'Session cleared'}, 200

@app.route('/articles/<int:id>')
def show_article(id):
    # Initialize session if needed
    session['page_views'] = session.get('page_views', 0) + 1
    
    # Check view limit
    if session['page_views'] > 3:
        return {'message': 'Maximum pageview limit reached'}, 401
    
    # Get article
    article = db.session.get(Article, id)
    if not article:
        return {'message': 'Article not found'}, 404
    
    return article.to_dict(), 200

if __name__ == '__main__':
    app.run(port=5555)
