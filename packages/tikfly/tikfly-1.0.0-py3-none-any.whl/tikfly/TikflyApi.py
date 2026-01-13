import ssl
import aiohttp
import certifi
from typing import Literal, Any
from types import SimpleNamespace

from .exceptions.TikflyApiError import TikflyAPIError

from .schemas import UserInfoResponse
from .schemas import UserPostResponse
from .schemas import UserStoryResponse
from .schemas import UserFollowerResponse
from .schemas import UserPlaylistResponse
from .schemas import UserFollowingResponse

from .schemas import EffectInfoResponse
from .schemas import PostDetailResponse

from .schemas import SearchLiveResponse
from .schemas import SearchVideoResponse
from .schemas import SearchGeneralResponse
from .schemas import SearchAccountResponse

from .schemas import PlaceInfoResponse
from .schemas import MusicInfoResponse
from .schemas import CommentListResponse
from .schemas import ChallengeInfoResponse

from .schemas import DownloadVideoResponse, DownloadMusicResponse

class TikflyApi():
  def __init__(self, x_rapidapi_key: str):
    """
    Initialize the TikflyApi instance.

    Args:
      x_rapidapi_key (str): The API key for accessing the Tikfly API.

    Raises:
      ValueError: If the x_rapidapi_key is not provided.
    """
    if not x_rapidapi_key:
      print(self.__get_api_key_tutorial())
      raise ValueError('x_rapidapi_key is required')

    self.x_rapidapi_key = x_rapidapi_key
    self.host = 'tiktok-api23.p.rapidapi.com'
    self.base_api_url = f'https://{self.host}/api'
    self.headers = {
      'x-rapidapi-key': self.x_rapidapi_key,
      'x-rapidapi-host': self.host
    }

  @staticmethod
  def __get_api_key_tutorial():
    """
    Provides a tutorial on how to obtain the API key for accessing the Tikfly API: https://dub.sh/tikfly

    Returns:
      str: A step-by-step guide to obtain the API key.
    """
    tutorial = """
    To obtain the API key for accessing the Tikfly API, follow these steps: https://docs.tikfly.io/getting-started/quickstart

    Note: Keep your API key secure and do not share it publicly.
    """
    return tutorial
  
  def __to_namespace(self, obj):
    if isinstance(obj, dict):
      return SimpleNamespace(
        **{k: self.__to_namespace(v) for k, v in obj.items()}
      )
    if isinstance(obj, list):
      return [self.__to_namespace(v) for v in obj]
    return obj
  
  def __wrap_namespace(self, *dicts, **named):
    """
    Merge multiple dicts and named fields,
    then convert to SimpleNamespace (deep).
    """
    merged = {}

    for d in dicts:
      if isinstance(d, dict):
        merged.update(d)

    merged.update(named)

    return self.__to_namespace(merged)
  
  def __dict_to_obj(self, data: Any):
    if isinstance(data, dict):
      return SimpleNamespace(**{
        k: self.__dict_to_obj(v)
        for k, v in data.items()
      })

    if isinstance(data, list):
      return [self.__dict_to_obj(i) for i in data]

    return data

  async def __get_request(
    self,
    url: str,
    params: dict,
    to_dict: bool = True
  ):
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    try:
      async with aiohttp.ClientSession(
        headers=self.headers,
      ) as session:
        async with session.get(url, params=params, ssl=ssl_context) as res:
          if res.status >= 400:
            text = await res.text()
            raise TikflyAPIError(
              message=f'Tikfly API HTTP error occurred: {res.status} - {text}',
              status_code=res.status,
              response=text
            )

          res_json = await res.json()

          if to_dict:
            return self.__dict_to_obj(res_json)
          return res_json
    except aiohttp.ClientError as err:
      raise TikflyAPIError(
        message=f'Tikfly API client error: {err}'
      ) from err

    except Exception as err:
      raise TikflyAPIError(
        message=f'Unexpected error: {err}'
      ) from err
    
  # User Endpoints
  async def get_user_info(self, unique_id: str) -> UserInfoResponse:
    """
    Get public user profile information by TikTok uniqueId.

    This method calls the Tikfly API to retrieve user information such as
    profile details, statistics, and related metadata.

    Args:
      unique_id (str): TikTok username (e.g. "taylorswift").

    Returns:
      UserInfoResponse: An object containing userInfo and statusCode.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/user/info'
    params = {
      'uniqueId': unique_id
    }

    return await self.__get_request(url, params)
  
  async def get_user_followers(
    self,
    sec_uid: str,
    count: int = 30,
    min_cursor: int = 0
  ) -> UserFollowerResponse:
    """
    Get the list of followers for a TikTok user by secUid.

    This method calls the Tikfly API to retrieve a paginated list of followers
    for the specified TikTok user.

    Args:
      sec_uid (str): TikTok user secUid (e.g. "MS4wLjABAAAAqB08cUbXaDWqbD6MCga2RbGTuhfO2EsHayBYx08NDrN7IE3jQuRDNNN6YwyfH6_6").
      count (int): Number of followers to return per request.
        The default and maximum value is 30.
      min_cursor (int): Cursor used for pagination.
        Use 0 for the first request. For subsequent requests,
        use the minCursor value returned from the previous response.

    Returns:
      UserFollowersResponse: An object containing follower list data and pagination info.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/user/followers'
    params = {
      'secUid': sec_uid,
      'count': count,
      'minCursor': min_cursor
    }
    return await self.__get_request(url, params)
  
  async def get_user_following(
    self,
    sec_uid: str,
    count: int = 30,
    min_cursor: int = 0
  ) -> UserFollowingResponse:
    """
    Get the list of following for a TikTok user by secUid.

    This method calls the Tikfly API to retrieve a paginated list of following
    for the specified TikTok user.

    Args:
      sec_uid (str): TikTok user secUid (e.g. "MS4wLjABAAAAqB08cUbXaDWqbD6MCga2RbGTuhfO2EsHayBYx08NDrN7IE3jQuRDNNN6YwyfH6_6").
      count (int): Number of following to return per request.
        The default and maximum value is 30.
      min_cursor (int): Cursor used for pagination.
        Use 0 for the first request. For subsequent requests,
        use the minCursor value returned from the previous response.

    Returns:
      UserFollowingResponse: An object containing following list data and pagination info.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/user/followings'
    params = {
      'secUid': sec_uid,
      'count': count,
      'minCursor': min_cursor
    }
    return await self.__get_request(url, params)
  
  async def get_user_posts(
    self,
    sec_uid: str,
    count: int = 15,
    cursor: int = 0,
    sort_by: Literal['latest', 'popular', 'oldest'] = 'latest'
  ) -> UserPostResponse:
    """
    Get a list of posts for a TikTok user by secUid.

    This method calls the Tikfly API to retrieve a paginated list of posts
    published by the specified TikTok user. The result can be sorted by
    latest, popular, or oldest posts.

    Args:
      sec_uid (str): TikTok user secUid.
      count (int): Number of posts to return per request.
        The default value is 15.
      cursor (int): Cursor used for pagination.
        Use 0 for the first request. For subsequent requests,
        use the cursor value returned from the previous response.
      sort_by (Literal['latest', 'popular', 'oldest']): Sorting method for posts.
        - "latest": Most recent posts (default).
        - "popular": Posts with highest engagement.
        - "oldest": Oldest published posts.

    Returns:
      UserPostResponse: An object containing post list data and pagination info.

    Raises:
      TikflyAPIError: If the API request fails or returnss an error response.
    """
    if sort_by == 'popular':
      type = 'popular-posts'
    elif sort_by == 'oldest':
      type = 'oldest-posts'
    else:
      type = 'posts'
 
    url = f'{self.base_api_url}/user/{type}'
    params = {
      'secUid': sec_uid,
      'count': count,
      'cursor': cursor
    }

    res = await self.__get_request(url, params, to_dict=False)

    data = self.__wrap_namespace(
      cursor=res.get('data', {}).get('cursor') or res.get('cursor'),
      hasMore=res.get('data', {}).get('hasMore') or res.get('hasMore'),
      itemList=res.get('data', {}).get('itemList') or res.get('itemList')
    )
 
    return data
  
  async def get_user_liked_posts(
    self,
    sec_uid: str,
    count: int = 30,
    cursor: int = 0
  ) -> UserPostResponse:
    """
    Get a list of posts liked by a TikTok user by secUid.

    This method calls the Tikfly API to retrieve a paginated list of posts
    that the specified TikTok user has liked.

    Args:
      sec_uid (str): TikTok user secUid.
      count (int): Number of liked posts to return per request.
        The default value is 30.
      cursor (int): Cursor used for pagination.
        Use 0 for the first request. For subsequent requests,
        use the cursor value returned from the previous response.

    Returns:
      UserPostResponse: An object containing liked post data and pagination info.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/user/liked-posts'
    params = {
      'secUid': sec_uid,
      'count': count,
      'cursor': cursor
    }
    return await self.__get_request(url, params)
  
  async def get_user_playlist(
    self,
    sec_uid: str,
    count: int = 20,
    cursor: int = 0
  ) -> UserPlaylistResponse:
    """
    Get the list of playlists for a TikTok user by secUid.

    This method calls the Tikfly API to retrieve a paginated list of playlists
    created by the specified TikTok user.

    Args:
      sec_uid (str): TikTok user secUid.
      count (int): Number of playlists to return per request.
        The default value is 20.
      cursor (int): Cursor used for pagination.
        Use 0 for the first request. For subsequent requests,
        use the cursor value returned from the previous response.

    Returns:
      UserPlaylistResponse: An object containing playlist data and pagination info.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/user/playlist'
    params = {
      'secUid': sec_uid,
      'count': count,
      'cursor': cursor
    }
    return await self.__get_request(url, params)
  
  async def get_user_repost(
    self,
    sec_uid: str,
    count: int = 30,
    cursor: int = 0
  ) -> UserPostResponse:
    """
    Get the list of reposted posts for a TikTok user by secUid.

    This method calls the Tikfly API to retrieve a paginated list of posts
    that the specified TikTok user has reposted.

    Args:
      sec_uid (str): TikTok user secUid.
      count (int): Number of reposted posts to return per request.
        The default value is 30.
      cursor (int): Cursor used for pagination.
        Use 0 for the first request. For subsequent requests,
        use the cursor value returned from the previous response.

    Returns:
      UserPostResponse: An object containing reposted post data and pagination info.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/user/repost'
    params = {
      'secUid': sec_uid,
      'count': count,
      'cursor': cursor
    }
    return await self.__get_request(url, params)
  
  async def get_user_story(
    self,
    user_id: str,
    max_cursor: str = '0'
  ) -> UserStoryResponse:
    """
    Get the list of stories for a TikTok user by userId.

    This method calls the Tikfly API to retrieve a paginated list of stories
    published by the specified TikTok user.

    Args:
      user_id (str): TikTok user ID.
      max_cursor (str): Cursor used for pagination.
        Use "0" for the first request. For subsequent requests,
        use the maxCursor value returned from the previous response.

    Returns:
      UserStoryResponse: An object containing story data and pagination info.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/user/story'
    params = {
      'userId': user_id,
      'maxCursor': max_cursor
    }
    return await self.__get_request(url, params)
  
  # Search Endpoints
  async def search_general(
    self,
    keyword: str,
    cursor: int = 0,
    search_id: str = '0'
  ) -> SearchGeneralResponse:
    """
    Perform a general search on TikTok using a keyword.

    This method calls the Tikfly API to perform a general search and retrieve
    mixed search results (such as users, videos, and hashtags) based on
    the provided keyword.

    Args:
      keyword (str): Search keyword.
      cursor (int): Cursor used for pagination.
        Use 0 for the first request. For subsequent requests,
        use the cursor value returned from the previous response.
        In search endpoints, both cursor and search_id must be provided
        when pagination is used.
      search_id (str): Search ID used for pagination.
        Use "0" for the first request. For subsequent requests,
        use the search_id value returned from the previous response
        (from log_pb.impr_id).
        In search endpoints, both cursor and search_id must be provided
        when pagination is used.

    Returns:
      SearchGeneralResponse: An object containing search results and pagination info.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/search/general'
    params = {
      'keyword': keyword,
      'cursor': cursor,
      'search_id': search_id
    }
    return await self.__get_request(url, params)
  
  async def search_videos(
    self,
    keyword: str,
    cursor: int = 0,
    search_id: str = '0'
  ) -> SearchVideoResponse:
    """
    Search TikTok videos using a keyword.

    This method calls the Tikfly API to search for TikTok videos
    based on the provided keyword and returns a paginated list
    of matching video results.

    Args:
      keyword (str): Search keyword.
      cursor (int): Cursor used for pagination.
        Use 0 for the first request. For subsequent requests,
        use the cursor value returned from the previous response.
        In search endpoints, both cursor and search_id must be provided
        when pagination is used.
      search_id (str): Search ID used for pagination.
        Use "0" for the first request. For subsequent requests,
        use the search_id value returned from the previous response
        (from log_pb.impr_id).
        In search endpoints, both cursor and search_id must be provided
        when pagination is used.

    Returns:
      SearchVideoResponse: An object containing video search results and pagination info.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/search/video'
    params = {
      'keyword': keyword,
      'cursor': cursor,
      'search_id': search_id
    }
    return await self.__get_request(url, params)
  
  async def search_accounts(
    self,
    keyword: str,
    cursor: int = 0,
    search_id: str = '0'
  ) -> SearchAccountResponse:
    """
    Search TikTok accounts using a keyword.

    This method calls the Tikfly API to search for TikTok user accounts
    based on the provided keyword and returns a paginated list of
    matching account results.

    Args:
      keyword (str): Search keyword.
      cursor (int): Cursor used for pagination.
        Use 0 for the first request. For subsequent requests,
        use the cursor value returned from the previous response.
        In search endpoints, both cursor and search_id must be provided
        when pagination is used.
      search_id (str): Search ID used for pagination.
        Use "0" for the first request. For subsequent requests,
        use the search_id value returned from the previous response
        (from log_pb.impr_id).
        In search endpoints, both cursor and search_id must be provided
        when pagination is used.

    Returns:
      SearchAccountResponse: An object containing account search results and pagination info.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/search/account'
    params = {
      'keyword': keyword,
      'cursor': cursor,
      'search_id': search_id
    }
    return await self.__get_request(url, params)
  
  async def search_live(
    self,
    keyword: str,
    cursor: int = 0,
    search_id: str = '0'
  ) -> SearchLiveResponse:
    """
    Search TikTok live streams using a keyword.

    This method calls the Tikfly API to search for TikTok live streams
    based on the provided keyword and returns a paginated list of
    matching live stream results.

    Args:
      keyword (str): Search keyword.
      cursor (int): Cursor used for pagination.
        Use 0 for the first request. For subsequent requests,
        use the cursor value returned from the previous response.
        In search endpoints, both cursor and search_id must be provided
        when pagination is used.
      search_id (str): Search ID used for pagination.
        Use "0" for the first request. For subsequent requests,
        use the search_id value returned from the previous response
        (from log_pb.impr_id).
        In search endpoints, both cursor and search_id must be provided
        when pagination is used.

    Returns:
      SearchLiveResponse: An object containing live stream search results and pagination info.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/search/live'
    params = {
      'keyword': keyword,
      'cursor': cursor,
      'search_id': search_id
    }
    return await self.__get_request(url, params)
  
  # Post Endpoints
  async def get_post_detail(
    self,
    video_id: str
  ) -> PostDetailResponse:
    """
    Get detailed information of a TikTok post by video ID.

    This method calls the Tikfly API to retrieve full details of a TikTok post,
    including item metadata, author information, music data, statistics,
    and related attributes.

    Args:
      video_id (str): TikTok video ID (e.g. "7572198435487501598").

    Returns:
      PostDetailResponse: An object containing itemInfo and statusCode.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/post/detail'
    params = {
      'videoId': video_id
    }
    return await self.__get_request(url, params)
  
  async def get_post_comments(
    self,
    video_id: str,
    count: int = 50,
    cursor: int = 0
  ) -> CommentListResponse:
    """
    Get comments of a TikTok post by video ID.

    This method calls the Tikfly API to retrieve a list of comments
    associated with a specific TikTok post. The results are returned
    in a paginated format.

    Args:
      video_id (str): TikTok video ID.
      count (int): Number of comments to return per request.
        The default value is 50.
      cursor (int): Cursor used for pagination.
        Use 0 for the first request. For subsequent requests,
        use the cursor value returned from the previous response.

    Returns:
      CommentListResponse: An object containing comments data and pagination info.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/post/comments'
    params = {
      'videoId': video_id,
      'count': count,
      'cursor': cursor
    }
    return await self.__get_request(url, params)
  
  async def get_post_replies_comment(
    self,
    video_id: str,
    comment_id: str,
    count: int = 6,
    cursor: int = 0
  ) -> CommentListResponse:
    """
    Get reply comments of a specific TikTok comment.

    This method calls the Tikfly API to retrieve replies to a given
    comment on a TikTok post. The results are returned in a paginated
    format.

    Args:
      video_id (str): TikTok video ID.
      comment_id (str): Comment ID for which to retrieve replies.
      count (int): Number of reply comments to return per request.
        The default value is 6.
      cursor (int): Cursor used for pagination.
        Use 0 for the first request. For subsequent requests,
        use the cursor value returned from the previous response.

    Returns:
      CommentListResponse: An object containing reply comments data
      and pagination info.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/post/comment/replies'
    params = {
      'videoId': video_id,
      'commentId': comment_id,
      'count': count,
      'cursor': cursor
    }
    return await self.__get_request(url, params)
  
  # Hashtag Endpoints
  async def get_hashtag_info(
    self,
    hashtag: str
  ) -> ChallengeInfoResponse:
    """
    Get hashtag (challenge) information by hashtag name.

    This method calls the Tikfly API to retrieve metadata about a TikTok
    hashtag, including basic information, statistics, and related details.

    Args:
      hashtag (str): Hashtag name without the "#" prefix
        (e.g. "fyp").

    Returns:
      ChallengeInfoResponse: An object containing hashtag information
      and status code.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/challenge/info'
    params = {
      'challengeName': hashtag
    }
    return await self.__get_request(url, params)
  
  async def get_hashtag_posts(
    self,
    hashtag_id: str,
    count: int = 30,
    cursor: int = 0
  ) -> UserPostResponse:
    """
    Get posts associated with a specific TikTok hashtag (challenge).

    This method calls the Tikfly API to retrieve a list of videos
    published under a given hashtag. The results are returned
    in a paginated format.

    Args:
      hashtag_id (str): Hashtag (challenge) ID.
      count (int): Number of posts to return per request.
        The default and maximum value is 30.
      cursor (int): Cursor used for pagination.
        Use 0 for the first request. For subsequent requests,
        use the cursor value returned from the previous response.

    Returns:
      UserPostResponse: An object containing hashtag posts data
      and pagination information.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/challenge/posts'
    params = {
      'challengeId': hashtag_id,
      'count': count,
      'cursor': cursor
    }
    return await self.__get_request(url, params)
  
  # Music Endpoints
  async def get_music_info(
    self,
    music_id: str
  ) -> MusicInfoResponse:
    """
    Get music (sound) information by music ID.

    This method calls the Tikfly API to retrieve metadata about a TikTok
    sound, including title, author, duration, cover images, and usage
    statistics.

    Args:
      music_id (str): TikTok music (sound) ID.

    Returns:
      MusicInfoResponse: An object containing music information
      and status code.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/music/info'
    params = {
      'musicId': music_id
    }
    return await self.__get_request(url, params)
  
  async def get_music_posts(
    self,
    music_id: str,
    count: int = 30,
    cursor: int = 0
  ) -> UserPostResponse:
    """
    Get posts associated with a specific TikTok music (sound).

    This method calls the Tikfly API to retrieve a list of videos
    that use a given music track. The results are returned
    in a paginated format.

    Args:
      music_id (str): TikTok music (sound) ID.
      count (int): Number of posts to return per request.
        The default and maximum value is 30.
      cursor (int): Cursor used for pagination.
        Use 0 for the first request. For subsequent requests,
        use the cursor value returned from the previous response.

    Returns:
      UserPostResponse: An object containing music posts data
      and pagination information.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/music/posts'
    params = {
      'musicId': music_id,
      'count': count,
      'cursor': cursor
    }
    return await self.__get_request(url, params)
  
  # Place Endpoints
  async def get_place_info(
    self,
    place_id: str
  ) -> PlaceInfoResponse:
    """
    Get place (location) information by place ID.

    This method calls the Tikfly API to retrieve metadata about a TikTok
    place or location, including name, address, category, and related
    details if available.

    Args:
      place_id (str): TikTok place (location) ID.

    Returns:
      PlaceInfoResponse: An object containing place information
      and status code.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/place/info'
    params = {
      'placeId': place_id
    }
    return await self.__get_request(url, params)
  
  async def get_place_posts(
    self,
    place_id: str,
    count: int = 30,
    cursor: int = 0
  ) -> UserPostResponse:
    """
    Get posts associated with a specific TikTok place (location).

    This method calls the Tikfly API to retrieve a list of videos
    that are tagged with a given place or location. The results
    are returned in a paginated format.

    Args:
      place_id (str): TikTok place (location) ID.
      count (int): Number of posts to return per request.
        The default and maximum value is 30.
      cursor (int): Cursor used for pagination.
        Use 0 for the first request. For subsequent requests,
        use the cursor value returned from the previous response.

    Returns:
      UserPostResponse: An object containing place posts data
      and pagination information.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/place/posts'
    params = {
      'placeId': place_id,
      'count': count,
      'cursor': cursor
    }
    return await self.__get_request(url, params)

  # Effect Endpoints
  async def get_effect_info(
    self,
    effect_id: str
  ) -> EffectInfoResponse:
    """
    Get effect (sticker) information by effect ID.

    This method calls the Tikfly API to retrieve metadata about a TikTok
    effect, including name, cover images, author, and usage
    statistics.

    Args:
      effect_id (str): TikTok effect (sticker) ID.

    Returns:
      EffectInfoResponse: An object containing effect information
      and status code.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/effect/info'
    params = {
      'effectId': effect_id
    }
    return await self.__get_request(url, params)
  
  async def get_effect_posts(
    self,
    effect_id: str,
    count: int = 30,
    cursor: int = 0
  ):
    """
    Get posts associated with a specific TikTok effect (sticker).

    This method calls the Tikfly API to retrieve a list of videos
    that use a given effect. The results are returned
    in a paginated format.

    Args:
      effect_id (str): TikTok effect (sticker) ID.
      count (int): Number of posts to return per request.
        The default and maximum value is 30.
      cursor (int): Cursor used for pagination.
        Use 0 for the first request. For subsequent requests,
        use the cursor value returned from the previous response.

    Returns:
      EffectPostsResponse: An object containing effect posts data
      and pagination information.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/effect/posts'
    params = {
      'effectId': effect_id,
      'count': count,
      'cursor': cursor
    }
    return await self.__get_request(url, params)
  
  # Collection Endpoints
  async def get_collection_info(
    self,
    collection_id: str
  ):
    """
    Get collection information by collection ID.

    This method calls the Tikfly API to retrieve metadata about a TikTok
    collection, including title, description, cover, owner, and related
    statistics.

    Args:
      collection_id (str): TikTok collection ID.

    Returns:
      CollectionInfoResponse: An object containing collection information
      and status code.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/collection/info'
    params = {
      'collectionId': collection_id
    }
    return await self.__get_request(url, params)
  
  async def get_collection_posts(
    self,
    collection_id: str,
    count: int = 30,
    cursor: str = '0'
  ) -> UserPostResponse:
    """
    Get posts associated with a specific TikTok collection.

    This method calls the Tikfly API to retrieve a list of videos
    that belong to a given collection. The results are returned
    in a paginated format.

    Args:
      collection_id (str): TikTok collection ID.
      count (int): Number of posts to return per request.
        The default and maximum value is 30.
      cursor (str): Cursor used for pagination.
        Use "0" for the first request. For subsequent requests,
        use the cursor value returned from the previous response.

    Returns:
      UserPostResponse: An object containing collection posts data
      and pagination information.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/collection/posts'
    params = {
      'collectionId': collection_id,
      'count': count,
      'cursor': cursor
    }
    return await self.__get_request(url, params)
  
  # Download Endpoints
  async def download_video(
    self,
    video_url: str
  ) -> DownloadVideoResponse:
    """
    Download a TikTok video by video URL.

    This method calls the Tikfly API to retrieve the direct download link

    Args:
      video_url (str): Full TikTok video URL.

    Returns:
      DownloadVideoResponse: An object containing download URL.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/download/video'
    params = {
      'url': video_url
    }
    return await self.__get_request(url, params)
  
  async def download_music(
    self,
    video_url: str
  ) -> DownloadMusicResponse:
    """
    Download music (audio) from a TikTok video URL.

    This method calls the Tikfly API to extract and retrieve the
    audio track used in a TikTok video.

    Args:
      video_url (str): Full TikTok video URL.

    Returns:
      DownloadMusicResponse: An object containing download URL.

    Raises:
      TikflyAPIError: If the API request fails or returns an error response.
    """
    url = f'{self.base_api_url}/download/music'
    params = {
      'url': video_url
    }
    return await self.__get_request(url, params)
  