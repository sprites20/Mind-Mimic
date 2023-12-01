import asyncio
import os
from urllib.parse import quote
from playwright.async_api import async_playwright, TimeoutError

async def scrape_links(url, depth=2, output_directory='output'):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # Open a new page
        page = await context.new_page()

        # Navigate to the main URL
        try:
            await page.goto(url, timeout=60000)
        except TimeoutError:
            print(f"Timeout navigating to {url}. Exiting...")
            await browser.close()
            return set()

        # Create the output directory if it doesn't exist
        os.makedirs(output_directory, exist_ok=True)

        # Extract links from the main page and download pages
        all_links = await extract_links_from_element(page, depth, output_directory)

        # Close the browser
        await browser.close()

        return all_links

async def extract_links_from_element(page, current_depth, output_directory):
    if current_depth <= 0:
        return set()

    links = set()

    # Evaluate JavaScript to get links
    try:
        links_on_page = await page.eval_on_selector_all('a', 'elements => elements.map(el => el.href)')
        print(links_on_page)
    except TimeoutError:
        print(f"Timeout extracting links from {page.url}. Skipping...")
        return links

    links.update(links_on_page)

    # Save HTML content to a file in the specified directory
    html_content = await page.content()
    
    # Replace invalid characters in the URL with underscores
    sanitized_url = quote(page.url, safe='')
    
    filename = f"{sanitized_url}.html"
    file_path = os.path.join(output_directory, filename)

    with open(file_path, "w", encoding="utf-8") as html_file:
        html_file.write(html_content)

    # Recursively extract links from the linked pages
    for link in links_on_page:
        try:
            await page.click('a[href="' + link + '"]', timeout=60000)
        except TimeoutError:
            print(f"Timeout clicking link {link}. Skipping...")
            continue

        nested_links = await extract_links_from_element(page, current_depth - 1, output_directory)
        links.update(nested_links)

        # Go back to the previous page
        await page.goBack()

    return links

# Example usage
main_url = 'https://www.geeksforgeeks.org/fundamentals-of-algorithms/?ref=shm_outind'
all_links = asyncio.run(scrape_links(main_url))

print('All Links:')
for link in all_links:
    print(link)
