import requests
import base64
from PIL import Image
from io import BytesIO, TextIOWrapper
from website_url import website_url
import os


def scrape_and_process(url_item: dict[str, bool], md_file: TextIOWrapper):
    api_endpoint = "http://localhost/api/scraper"
    headers = {"Content-Type": "application/json"}
    response = requests.post(api_endpoint, headers=headers, json=url_item)
    data = response.json()

    if url_item["image_search"]:
        image_data = base64.b64decode(data["metadata"]["content"])
        image = Image.open(BytesIO(image_data))
        image_path = f"{image_directory}/{data['metadata']['url'].split('/')[-1]}.png"
        image.save(image_path)
        md_file.write(f"### URL: {data['metadata']['url']}\n\n")
        md_file.write(f"![Image]({image_path})\n")
    else:
        md_file.write(f"### URL: {data['metadata']['url']}\n")
        md_file.write(f"**Content:** {data['metadata']['content']}\n\n")

    md_file.write(f"---\n")

    print(f"Scraped: {data['metadata']['url']}")


if __name__ == "__main__":

    image_directory = "images"
    os.makedirs(image_directory, exist_ok=True)
    with open("output.md", "w") as md_file:
        for item in website_url:
            scrape_and_process(item, md_file)

    print("Scraping completed. Check output.md for the results.")
