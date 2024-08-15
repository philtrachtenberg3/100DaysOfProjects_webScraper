// static/debug.js

// Example: Log the number of headlines on the page
document.addEventListener('DOMContentLoaded', function() {
    const headlines = document.querySelectorAll('h3.article-card__title span');
    console.log(`Number of headlines: ${headlines.length}`);
    headlines.forEach((headline, index) => {
        console.log(`${index + 1}: ${headline.innerText}`);
    });
});
