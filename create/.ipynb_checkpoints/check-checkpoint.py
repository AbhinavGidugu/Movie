import asyncio
import aiohttp
from aiohttp import ClientSession
import pandas as pd
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin

BASE_URL = "https://www.imdb.com/title/"
MAX_CONCURRENT_REQUESTS = 10
RATE_LIMIT = 1  # requests per second

async def fetch_movie_data(session: ClientSession, movie_id: str) -> dict:
    url = urljoin(BASE_URL, movie_id)
    try:
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                title = soup.find('h1').text.strip()
                rating = soup.find('span', class_='AggregateRatingButton__RatingScore-sc-1ll29m0-1').text.strip()
                return {'id': movie_id, 'title': title, 'rating': rating}
            else:
                print(f"Error fetching {url}: Status {response.status}")
                return {'id': movie_id, 'title': None, 'rating': None}
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return {'id': movie_id, 'title': None, 'rating': None}

async def process_batch(session: ClientSession, movie_ids: list) -> list:
    tasks = []
    for movie_id in movie_ids:
        task = asyncio.ensure_future(fetch_movie_data(session, movie_id))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results

async def main(movie_ids: list):
    results = []
    async with aiohttp.ClientSession() as session:
        for i in range(0, len(movie_ids), MAX_CONCURRENT_REQUESTS):
            batch = movie_ids[i:i + MAX_CONCURRENT_REQUESTS]
            batch_results = await process_batch(session, batch)
            results.extend(batch_results)
            await asyncio.sleep(RATE_LIMIT)
    return results

if __name__ == "__main__":
    # Load your dataframe with movie IDs here
    df = pd.read_csv("movie_ids.csv")  # Assuming you have a CSV with movie IDs
    movie_ids = df['movie_id'].tolist()  # Adjust column name as needed

    start_time = time.time()
    results = asyncio.run(main(movie_ids))
    end_time = time.time()

    # Create a new dataframe with the results
    results_df = pd.DataFrame(results)
    results_df.to_csv("movie_data_results.csv", index=False)

    print(f"Scraped {len(results)} movies in {end_time - start_time:.2f} seconds")