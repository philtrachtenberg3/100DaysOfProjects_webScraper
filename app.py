from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_headlines(url, selector, link_selector, limit=5):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    headlines = soup.select(selector)

    unique_headlines = []
    seen = set()
    
    for headline in headlines:
        text = headline.get_text(strip=True)
        link = headline.find_parent(link_selector).get('href')  # Get the link
        full_link = link if link.startswith('http') else url.rstrip('/') + '/' + link.lstrip('/')  # Handle relative URLs
        
        if text not in seen:
            seen.add(text)
            unique_headlines.append((text, full_link))  # Store both text and link
        if len(unique_headlines) == limit:
            break

    return unique_headlines


@app.route('/')
def index():
    # Define the websites and their respective selectors for headlines
    sources = {
        "BBC": {"url": "https://www.bbc.com/", "selector": "h2[data-testid='card-headline']", "link_selector": "a"},
        "CNN World": {"url": "https://edition.cnn.com/world", "selector": "span.container__headline-text", "link_selector": "a"},
        "CNN US": {
            "url": "https://cnn.com",
            "selector": "body div.scope span.container__headline-text",
            "link_selector": "a"
        },
        "Al Jazeera": {"url": "https://www.aljazeera.com/", "selector": "h3.article-card__title span", "link_selector": "a"},
    }

    headlines = {}
    for source, details in sources.items():
        headlines[source] = get_headlines(details["url"], details["selector"], details["link_selector"])

    return render_template('index.html', headlines=headlines)

if __name__ == '__main__':
    app.run(debug=True)
