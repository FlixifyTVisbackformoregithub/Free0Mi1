import re
from flask import Flask, request, Response, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Middleware to log requests and responses
@app.before_request
def before_request():
    print(f"Incoming Request: {request.method} {request.url}")

@app.after_request
def after_request(response):
    print(f"Outbound Response: {response.status}")
    return response

# Function to fetch content from the target URL
def fetch_url(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# Function to parse and modify the HTML if needed
def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Modify links to ensure they remain within the proxy
    for link in soup.find_all('a', href=True):
        original_href = link['href']
        if not original_href.startswith('http'):
            # Construct the full URL
            link['href'] = f"{request.url_root}?url={original_href}"

    return str(soup)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/proxy')
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return "No URL provided!", 400
    
    # Validate the target URL (basic check)
    if not re.match(r'^https?://', target_url):
        return "Invalid URL!", 400
    
    # Fetch the content from the provided URL
    content = fetch_url(target_url)
    if content is None:
        return "Could not fetch the page.", 500

    # Parse and potentially modify the HTML
    modified_content = parse_html(content)

    # Return the modified content
    return Response(modified_content, content_type='text/html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
