import requests
from bs4 import BeautifulSoup

def scrape_website(url, scraping_type, custom_selector=None):
    """
    Advanced web scraper that returns different types of content based on scraping_type.
    The scraped data is now consistently returned under the 'data' key.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  
    except requests.exceptions.RequestException as e:
        return {'error': f"Error fetching URL: {e}"}

    soup = BeautifulSoup(response.text, 'html.parser')
    
    
    scraped_content = [] 

    if scraping_type == 'title':
        scraped_content = soup.title.string if soup.title else 'No title found'
    elif scraping_type == 'paragraphs':
        scraped_content = [p.get_text() for p in soup.find_all('p')]
    elif scraping_type == 'links':
        scraped_content = [a['href'] for a in soup.find_all('a', href=True)]
    elif scraping_type == 'headings':
        headings = []
        for h_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            headings.extend([h.get_text() for h in soup.find_all(h_tag)])
        scraped_content = headings
    elif scraping_type == 'bold_words':
        scraped_content = [strong.get_text() for strong in soup.find_all(['b', 'strong'])]
    elif scraping_type == 'tables':
        tables_data = []
        for table in soup.find_all('table'):
            table_rows = []
            for row in table.find_all('tr'):
                cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                table_rows.append(cells)
            tables_data.append(table_rows)
        scraped_content = tables_data
    elif scraping_type == 'footer':
        footer_content_elem = soup.find('footer')
        if footer_content_elem:
            scraped_content = footer_content_elem.get_text(strip=True)
        else:
            scraped_content = 'No footer found (common tags: <footer>, <div class="footer">, etc.)'
    elif scraping_type == 'all_text':
        scraped_content = soup.get_text(separator='\n', strip=True)
    elif scraping_type == 'custom' and custom_selector:
        try:
            selected_elements = soup.select(custom_selector)
            scraped_content = [elem.get_text(strip=True) for elem in selected_elements]
            if not scraped_content:
                scraped_content = [f"No elements found for selector: {custom_selector}"]
        except Exception as e:
            return {'error': f"Error with custom selector '{custom_selector}': {e}"}
    else:
        return {'error': "Invalid scraping type or missing custom selector."}


    return {'data': scraped_content}