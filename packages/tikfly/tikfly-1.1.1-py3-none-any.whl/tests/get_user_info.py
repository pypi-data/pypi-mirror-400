import asyncio
from tikfly import TikflyApi

API_KEY = 'YOUR_API_KEY' # How to get your api key -> https://docs.tikfly.io/getting-started/quickstart
USERNAME = 'taylorswift' # Change to the user you want to get data from

async def get_tiktok_user_info():
  tikfly = TikflyApi(x_rapidapi_key=API_KEY)

  res_user_info = await tikfly.get_user_info(unique_id=USERNAME)

  print(res_user_info.userInfo)

asyncio.run(get_tiktok_user_info())
