from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///headlines.db'  # Use SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Adding in the database storage
class Headline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100), nullable=False)
    headline = db.Column(db.String(500), nullable=False)
    link = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize the database
with app.app_context():
    db.create_all()

# Function to fetch headlines
def get_headlines(url, selector, link_selector, limit=5):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    headlines = soup.select(selector)

    unique_headlines = []
    seen = set()
    
    for headline in headlines:
        text = headline.get_text(strip=True)
        
        if link_selector == "self":
            # The selector directly targets <a> tags
            link = headline.get('href')
        else:
            # Find the parent or sibling element containing the link
            link_element = headline.find_parent(link_selector) or headline.find(link_selector)
            link = link_element.get('href') if link_element else None

        if link:  # Ensure the link exists
            # Handle relative URLs
            full_link = link if link.startswith('http') else url.rstrip('/') + '/' + link.lstrip('/')
            
            if text not in seen:
                seen.add(text)
                unique_headlines.append((text, full_link))  # Store both text and link
            
            if len(unique_headlines) == limit:
                break
        else:
            print(f"Warning: No link found for headline '{text}' on {url}")

    return unique_headlines

def save_headlines_to_db(source, headlines):
    for headline, link in headlines:
        # Check if the headline already exists to avoid duplicates
        exists = db.session.query(Headline).filter_by(source=source, headline=headline).first()
        if not exists:
            new_headline = Headline(source=source, headline=headline, link=link)
            db.session.add(new_headline)
    db.session.commit()









@app.route('/')
def index():
    # Define the websites and their respective selectors for headlines
    sources = {
    "BBC": {"url": "https://www.bbc.com/", "selector": "h2[data-testid='card-headline']", "link_selector": "a"},
    "CNN World": {"url": "https://edition.cnn.com/world", "selector": "span.container__headline-text", "link_selector": "a"},
    "CNN US": {
        "url": "https://cnn.com",
        "selector": "div.container__headline.container_lead-package__headline span.container__headline-text",
        "link_selector": "a"
    },
    "Al Jazeera": {"url": "https://www.aljazeera.com/", "selector": "h3.article-card__title span", "link_selector": "a"},
    "New York Times": {
        "url": "https://www.nytimes.com/",
        "selector": "p.indicate-hover",
        "link_selector": "a"
    },
    "Fox News": {
        "url": "https://www.foxnews.com/",
        "selector": "header.info-header h3.title a",
        "link_selector": "self"
    },
    "The Guardian": {
        "url": "https://www.theguardian.com/",
        "selector": "a.u-faux-block-link__overlay",
        "link_selector": "self"
    },
    "Reuters": {
        "url": "https://www.reuters.com/",
        "selector": "h3.story-title",
        "link_selector": "a"
    },
    "NBC News": {
        "url": "https://www.nbcnews.com/",
        "selector": "h2.tease-card__headline",
        "link_selector": "a"
    },
}


    headlines = {}
    for source, details in sources.items():
        # Get headlines
        headlines[source] = get_headlines(details["url"], details["selector"], details["link_selector"])

        # Save to the database
        save_headlines_to_db(source, headlines[source])

    return render_template('index.html', headlines=headlines)

if __name__ == '__main__':
    app.run(debug=True)
