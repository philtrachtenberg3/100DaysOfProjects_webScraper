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
        # Check if the link_selector is 'self' or another tag
        if link_selector == "self":
            # Assume the selector targets <a> tags directly
            text = headline.get_text(strip=True)
            link = headline.get('href')
        else:
            # Find the parent or child <a> tag for the headline
            link_element = headline.find_parent(link_selector) or headline.find(link_selector)
            text = headline.get_text(strip=True)
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
        "New York Times": {
            "url": "https://www.nytimes.com/",
            "selector": "p.indicate-hover",
            "link_selector": "a"
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
    "Fox News": {
        "url": "https://www.foxnews.com/",
        "selector": "header.info-header h3.title a",
        "link_selector": "self"
    },
    "NBC News": {
        "url": "https://www.nbcnews.com/",
        "selector": "h2.tease-card__headline",
        "link_selector": "a"
    },
    }

    headlines = {}
    for source, details in sources.items():
        headlines[source] = get_headlines(details["url"], details["selector"], details["link_selector"])

    return render_template('index.html', headlines=headlines)

if __name__ == '__main__':
    app.run(debug=True)
