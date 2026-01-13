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
