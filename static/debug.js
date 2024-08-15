// static/debug.js

// Example: Log the number of headlines on the page
document.addEventListener('DOMContentLoaded', function() {
    const headlines = document.querySelectorAll('span.container__headline-text');
    console.log(`Number of headlines: ${headlines.length}`);
    headlines.forEach((headline, index) => {
        console.log(`${index + 1}: ${headline.innerText}`);
    });
});
