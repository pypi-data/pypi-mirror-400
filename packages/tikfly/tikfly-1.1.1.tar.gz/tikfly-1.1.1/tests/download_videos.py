import ssl
import asyncio
import certifi
import aiohttp
from tikfly import TikflyApi

API_KEY = 'YOUR_API_KEY' # How to get your api key -> https://docs.tikfly.io/getting-started/quickstart
VIDEO_URLS = [
  'https://www.tiktok.com/@taylorswift/video/7558098574555254046'
]

async def download_video(url: str, save_path: str):
  CHUNK_SIZE = 1024 * 1024
  ssl_context = ssl.create_default_context(cafile=certifi.where())
  async with aiohttp.ClientSession() as session:
    async with session.get(url, ssl=ssl_context) as resp:
      resp.raise_for_status()

      with open(save_path, 'wb') as f:
        async for chunk in resp.content.iter_chunked(CHUNK_SIZE):
            f.write(chunk)

  print(f'Saved video to: {save_path}')

async def download_tiktok_videos():
  tikfly = TikflyApi(x_rapidapi_key=API_KEY)

  for url in VIDEO_URLS:
    res = await tikfly.download_video(url)
    download_url = res.play
    print(f'Download URL: {download_url}')

    if download_url:
      video_id = url.rstrip('/').split('/')[-1]
      await download_video(download_url, f'{video_id}.mp4')

asyncio.run(download_tiktok_videos())
