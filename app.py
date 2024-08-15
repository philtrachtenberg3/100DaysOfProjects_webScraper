from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_headlines(url, selector, limit=5):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    headlines = soup.select(selector)  # Using CSS selectors for more flexibility
    return [headline.get_text(strip=True) for headline in headlines[:limit]]

@app.route('/')
def index():
    # Define the websites and their respective selectors for headlines
    sources = {
        "BBC": {"url": "https://www.bbc.com/news", "selector": "h3"},
        "CNN World": {"url": "https://edition.cnn.com/world", "selector": "span.container__headline-text"},
        "CNN US": {
            "url": "https://cnn.com",
            "selector": "body div.scope span.container__headline-text"
        },
        "Al Jazeera": {"url": "https://www.aljazeera.com/", "selector": "h3.article-card__title span"},
    }

    headlines = {}
    for source, details in sources.items():
        headlines[source] = get_headlines(details["url"], details["selector"])

    return render_template('index.html', headlines=headlines)

if __name__ == '__main__':
    app.run(debug=True)
