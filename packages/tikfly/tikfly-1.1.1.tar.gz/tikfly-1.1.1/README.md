# Tikfly API

**Unofficial TikTok API** Wrapped in Python

[![GitHub Repo stars](https://img.shields.io/github/stars/tikfly/tikfly-api-py?style=social)](https://github.com/tikfly/tikfly-api-py/stargazers/)
[![GitHub forks](https://img.shields.io/github/forks/tikfly/tikfly-api-py?style=social)](https://github.com/tikfly/tikfly-api-py/network/)
[![Vistors](https://visitor-badge.laobi.icu/badge?page_id=tikfly.tikfly-api-py&title=Visitors)](https://github.com/tikfly/tikfly-api-py)
[![License](https://img.shields.io/github/license/tikfly/tikfly-api-py?label=License)](https://mit-license.org/)

## Available on [PyPi](https://pypi.org/project/tikfly)


## Installation

```bash
pip install tikfly
```

## Usage

### Get TikTok User Info

```python
import asyncio
from tikfly import TikflyApi

API_KEY = 'YOUR_API_KEY' # How to get your api key -> https://docs.tikfly.io/getting-started/quickstart
USERNAME = 'taylorswift' # Change to the user you want to get data from

async def get_tiktok_user_info():
  tikfly = TikflyApi(x_rapidapi_key=API_KEY)

  res_user_info = await tikfly.get_user_info(unique_id=USERNAME)

  print(res_user_info.userInfo)

asyncio.run(get_tiktok_user_info())
```

### Get Tiktok User Videos

```python
import asyncio
from tikfly import TikflyApi
from tikfly.schemas.UserPostSchema import VideoItem

API_KEY = 'YOUR_API_KEY' # How to get your api key -> https://docs.tikfly.io/getting-started/quickstart
USERNAME = 'taylorswift' # Change to the user you want to get data from
NUM = 50 # Max number of videos to fetch

async def get_tiktok_user_videos():
  tikfly = TikflyApi(x_rapidapi_key=API_KEY)

  print(f'Fetching {NUM} videos of user: {USERNAME}')
  res_user_info = await tikfly.get_user_info(USERNAME)

  user_sec_uid = res_user_info.userInfo.user.secUid
  print('User secUid:', user_sec_uid)

  results: list[VideoItem] = []
  cursor = 0
  count = 15
  has_more = True

  while has_more and len(results) < NUM:
    print(f'Current cursor: {cursor}')
    res_user_posts = await tikfly.get_user_posts(
      user_sec_uid,
      count=count,
      cursor=cursor
    )
    
    itemList = getattr(res_user_posts, 'itemList', [])

    if not itemList:
      break

    results.extend(itemList)

    remaining = NUM - len(results)
    results.extend(itemList[:remaining])

    has_more = res_user_posts.hasMore
    cursor = res_user_posts.cursor

  for video in results:
    print(f'- {video.id}: {video.desc}')

asyncio.run(get_tiktok_user_videos())
```

### Download Tiktok Videos (Without Watermark)

```python
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
```

## Examples
Go to the `/tests` and `/examples` folder to view more snippet code and example data.

## Tutorials
- [Tikfly API Documentation](https://docs.tikfly.io/api-reference)
- [How to get Rapid API Key](https://docs.tikfly.io/getting-started/quickstart)
- [Working with Cursor in TikTok API for Pagination](https://docs.tikfly.io/tutorial/working-with-cursor-in-tiktok-api-for-pagination)
- [What is Tiktok User secUid?](https://docs.tikfly.io/tutorial/what-is-tiktok-user-secuid)
- [How TikTok Classifies a Video?
](https://docs.tikfly.io/tutorial/how-tiktok-classifies-a-video)

## Contributing
Contributions are welcome! If you find this project helpful, please consider starring the repository on [GitHub](https://github.com/tikfly/tikfly-api) ⭐️

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Disclaimer
This project is an independent, open-source tool and is not affiliated, endorsed, or sponsored by TikTok.
