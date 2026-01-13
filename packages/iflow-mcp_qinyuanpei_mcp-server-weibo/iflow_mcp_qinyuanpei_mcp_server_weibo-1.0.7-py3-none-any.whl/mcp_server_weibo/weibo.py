import httpx
import re
import logging
from urllib.parse import urlencode
from .consts import DEFAULT_HEADERS, PROFILE_URL, FEEDS_URL, SEARCH_URL, COMMENTS_URL
from .schemas import PagedFeeds, TrendingItem, FeedItem, UserProfile, CommentItem


class WeiboCrawler:
    """
    A crawler class for extracting data from Weibo (Chinese social media platform).
    Provides functionality to fetch user profiles, feeds, and search for users.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def get_profile(self, uid: int) -> UserProfile:
        """
        Extract user profile information from Weibo.

        Args:
            uid (int): The unique identifier of the Weibo user

        Returns:
            UserProfile: User profile information or empty dict if extraction fails
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(PROFILE_URL.format(userId=uid), headers=DEFAULT_HEADERS)
                result = response.json()
                return self._to_user_profile(result["data"]["userInfo"])
            except httpx.HTTPError:
                self.logger.error(
                    f"Unable to eextract profile for uid '{str(uid)}'", exc_info=True)
                return {}

    async def get_feeds(self, uid: int, limit: int = 15) -> list[FeedItem]:
        """
        Extract user's Weibo feeds (posts) with pagination support.

        Args:
            uid (int): The unique identifier of the Weibo user
            limit (int): Maximum number of feeds to extract, defaults to 15

        Returns:
            list[FeedItem]: List of user's Weibo feeds
        """
        feeds = []
        sinceId = ''
        async with httpx.AsyncClient() as client:
            containerId = await self._get_container_id(client, uid)

            while len(feeds) < limit:
                pagedFeeds = await self._extract_feeds(client, uid, containerId, sinceId)
                if not pagedFeeds.Feeds:
                    break

                feeds.extend(pagedFeeds.Feeds)
                sinceId = pagedFeeds.SinceId
                if not sinceId:
                    break

        return feeds

    async def get_hot_feeds(self, uid: int, limit: int = 15) -> list[FeedItem]:
        """
        Extract hot feeds (posts) from a specific user's Weibo profile.

        Args:
            uid (int): The unique identifier of the Weibo user
            limit (int): Maximum number of hot feeds to extract, defaults to 15

        Returns:
            list[FeedItem]: List of hot feeds from the user's profile
        """
        async with httpx.AsyncClient() as client:
            try:
                params = {
                    'containerid': f'231002{str(uid)}_-_HOTMBLOG',
                    'type': 'uid',
                    'value': uid,
                }
                encoded_params = urlencode(params)

                response = await client.get(f'{SEARCH_URL}?{encoded_params}', headers=DEFAULT_HEADERS)
                result = response.json()
                cards = list(filter(lambda x:x['card_type'] == 9, result["data"]["cards"]))
                feeds = [self._to_feed_item(item['mblog']) for item in cards]
                return feeds[:limit]
            except httpx.HTTPError:
                self.logger.error(f"Unable to extract hot feeds for uid '{str(uid)}'", exc_info=True)
                return []

    async def search_users(self, keyword: str, limit: int = 5, page: int = 1) -> list[UserProfile]:
        """
        Search for Weibo users based on a keyword.

        Args:
            keyword (str): Search term to find users
            limit (int): Maximum number of users to return, defaults to 5

        Returns:
            list[UserProfile]: List of UserProfile objects containing user information
        """
        async with httpx.AsyncClient() as client:
            try:
                params = {
                    'containerid': f'100103type=3&q={keyword}',
                    'page_type': 'searchall',
                    'page': page,
                }
                encoded_params = urlencode(params)

                response = await client.get(f'{SEARCH_URL}?{encoded_params}', headers=DEFAULT_HEADERS)
                result = response.json()
                cards = result["data"]["cards"]
                if len(cards) < 2:
                    return []
                else:
                    cardGroup = cards[1]['card_group']
                    return [self._to_user_profile(item['user']) for item in cardGroup][:limit]
            except httpx.HTTPError:
                self.logger.error(
                    f"Unable to search users for keyword '{keyword}'", exc_info=True)
                return []

    async def get_trendings(self, limit: int = 15) -> list[TrendingItem]:
        """
        Get a list of hot search items from Weibo.

        Args:
            limit (int): Maximum number of hot search items to return, defaults to 15

        Returns:
            list[HotSearchItem]: List of HotSearchItem objects containing hot search information
        """
        try:
            params = {
                'containerid': f'106003type=25&t=3&disable_hot=1&filter_type=realtimehot',
            }
            encoded_params = urlencode(params)
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f'{SEARCH_URL}?{encoded_params}', headers=DEFAULT_HEADERS)
                data = response.json()
                cards = data.get('data', {}).get('cards', [])
                if not cards:
                    return []

                hot_search_card = next((card for card in cards if 'card_group' in card and isinstance(card['card_group'], list)), None)
                if not hot_search_card or 'card_group' not in hot_search_card:
                    return []

                items = [item for item in hot_search_card['card_group'] if item.get('desc')]
                trending_items = list(map(lambda pair: self._to_trending_item({**pair[1], 'id': pair[0]}), enumerate(items[:limit])))
                return trending_items
        except httpx.HTTPError:
            self.logger.error(
                'Unable to fetch Weibo hot search list', exc_info=True)
            return []

    async def search_content(self, keyword: str, limit: int = 15, page: int = 1) -> list[FeedItem]:
        """
        Search Weibo content (posts) by keyword.

        Args:
            keyword (str): The search keyword
            limit (int): Maximum number of content results to return, defaults to 15
            page (int, optional): The starting page number, defaults to 1

        Returns:
            list[FeedItem]: List of FeedItem objects containing content search results
        """
        results = []
        current_page = page
        try:
            while len(results) < limit:
                params = {
                    'containerid': f'100103type=1&q={keyword}',
                    'page_type': 'searchall',
                    'page': page,
                }
                encoded_params = urlencode(params)

                async with httpx.AsyncClient() as client:
                    response = await client.get(f'{SEARCH_URL}?{encoded_params}', headers=DEFAULT_HEADERS)
                    data = response.json()

                cards = data.get('data', {}).get('cards', [])
                content_cards = []
                for card in cards:
                    if card.get('card_type') == 9:
                        content_cards.append(card)
                    elif 'card_group' in card and isinstance(card['card_group'], list):
                        content_group = [
                            item for item in card['card_group'] if item.get('card_type') == 9]
                        content_cards.extend(content_group)

                if not content_cards:
                    break

                for card in content_cards:
                    if len(results) >= limit:
                        break

                    mblog = card.get('mblog')
                    if not mblog:
                        continue

                    content_result = self._to_feed_item(mblog)
                    results.append(content_result)

                current_page += 1
                cardlist_info = data.get('data', {}).get('cardlistInfo', {})
                if not cardlist_info.get('page') or str(cardlist_info.get('page')) == '1':
                    break
            return results[:limit]
        except httpx.HTTPError:
            self.logger.error(
                f"Unable to search Weibo content for keyword '{keyword}'", exc_info=True)
            return []

    async def search_topics(self, keyword: str, limit: int = 15, page: int = 1) -> list[dict]:
        """
        Search Weibo topics by keyword.

        Args:
            keyword (str): The search keyword
            limit (int): Maximum number of topic results to return, defaults to 15
            page (int, optional): The starting page number, defaults to 1

        Returns:
            list[dict: List of dict containing topic search results
        """
        async with httpx.AsyncClient() as client:
            try:
                params = {
                    'containerid': f'100103type=38&q={keyword}',
                    'page_type': 'searchall',
                    'page': page,
                }
                encoded_params = urlencode(params)

                response = await client.get(f'{SEARCH_URL}?{encoded_params}', headers=DEFAULT_HEADERS)
                result = response.json()
                cards = result["data"]["cards"]
                if len(cards) < 1:
                    return []
                else:
                    cardGroup = cards[0]['card_group']
                    return [self._to_topic_item(item) for item in cardGroup][:limit]
            except httpx.HTTPError:
                self.logger.error(
                    f"Unable to search users for keyword '{keyword}'", exc_info=True)
                return []

    async def get_comments(self, feed_id: str, page: int = 1) -> list[CommentItem]:
        """
        Get comments for a specific Weibo post.

        Args:
            feed_id (str): The ID of the Weibo post
            page (int): The page number for pagination, defaults to 1

        Returns:
            list[CommentItem]: List of comments for the specified Weibo post
        """
        try:
            async with httpx.AsyncClient() as client:
                url = COMMENTS_URL.format(feed_id=feed_id, page=page)
                response = await client.get(url, headers=DEFAULT_HEADERS)
                data = response.json()
                comments = data.get('data', {}).get('data', [])
                return [self._to_comment_item(comment) for comment in comments]
        except httpx.HTTPError:
            self.logger.error(f"Unable to fetch comments for feed_id '{feed_id}'", exc_info=True)
            return []
    
    async def get_followers(self, uid: int, limit: int = 15, page: int = 1) -> list[UserProfile]:
        """
        Get followers of a specific Weibo user.

        Args:
            uid (int): The unique identifier of the Weibo user
            limit (int): Maximum number of followers to return, defaults to 15
            page (int): The page number for pagination, defaults to 1

        Returns:
            list[UserProfile]: List of UserProfile objects containing follower information
        """
        async with httpx.AsyncClient() as client:
            try:
                params = {
                    'containerid': f'231051_-_followers_-_{str(uid)}',
                    'page': page,
                }
                encoded_params = urlencode(params)

                response = await client.get(f'{SEARCH_URL}?{encoded_params}', headers=DEFAULT_HEADERS)
                result = response.json()
                cards = result["data"]["cards"]
                if len(cards) < 1:
                    return []
                else:
                    cardGroup = cards[-1]['card_group']
                    return [self._to_user_profile(item['user']) for item in cardGroup][:limit]
            except httpx.HTTPError:
                self.logger.error(f"Unable to get followers for uid '{str(uid)}'", exc_info=True)
                return []

    async def get_fans(self, uid: int, limit: int = 15, page: int = 1) -> list[UserProfile]:
        """
        Get fans of a specific Weibo user.

        Args:
            uid (int): The unique identifier of the Weibo user
            limit (int): Maximum number of fans to return, defaults to 15
            page (int): The page number for pagination, defaults to 1

        Returns:
            list[UserProfile]: List of UserProfile objects containing fan information
        """
        async with httpx.AsyncClient() as client:
            try:
                params = {
                    'containerid': f'231051_-_fans_-_{str(uid)}',
                    'page': page,
                }
                encoded_params = urlencode(params)

                response = await client.get(f'{SEARCH_URL}?{encoded_params}', headers=DEFAULT_HEADERS)
                result = response.json()
                cards = result["data"]["cards"]
                if len(cards) < 1:
                    return []
                else:
                    cardGroup = cards[-1]['card_group']
                    return [self._to_user_profile(item['user']) for item in cardGroup][:limit]
            except httpx.HTTPError:
                self.logger.error(f"Unable to get fans for uid '{str(uid)}'", exc_info=True)
                return []
             
    async def _get_container_id(self, client, uid: int):
        """
        Get the container ID for a user's Weibo feed.

        Args:
            client (httpx.AsyncClient): HTTP client instance
            uid (int): The unique identifier of the Weibo user

        Returns:
            str: Container ID for the user's feed or None if extraction fails
        """
        try:
            response = await client.get(PROFILE_URL.format(userId=str(uid)), headers=DEFAULT_HEADERS)
            data = response.json()
            tabs_info = data.get("data", {}).get(
                "tabsInfo", {}).get("tabs", [])
            for tab in tabs_info:
                if tab.get("tabKey") == "weibo":
                    return tab.get("containerid")
        except httpx.HTTPError:
            self.logger.error(f"Unable to extract containerId for uid '{str(uid)}'", exc_info=True)
            return None

    async def _extract_feeds(self, client, uid: int, container_id: str, since_id: str):
        """
        Extract a single page of Weibo feeds for a user.

        Args:
            client (httpx.AsyncClient): HTTP client instance
            uid (int): The unique identifier of the Weibo user
            container_id (str): Container ID for the user's feed
            since_id (str): ID of the last feed for pagination

        Returns:
            PagedFeeds: Object containing feeds and next page's since_id
        """
        try:
            url = FEEDS_URL.format(userId=str(uid), containerId=container_id, sinceId=since_id)
            response = await client.get(url, headers=DEFAULT_HEADERS)
            data = response.json()

            new_since_id = data.get("data", {}).get("cardlistInfo", {}).get("since_id", "")
            cards = data.get("data", {}).get("cards", [])
            feeds = list(map(lambda x: self._to_feed_item(x.get('mblog', {})), cards))

            return PagedFeeds(SinceId=new_since_id, Feeds=feeds)
        except httpx.HTTPError:
            self.logger.error(
                f"Unable to extract feeds for uid '{str(uid)}'", exc_info=True)
            return PagedFeeds(SinceId=None, Feeds=[])
    
    def _to_trending_item(self, item: dict) -> TrendingItem:
        """
        Convert raw hot search item data to HotSearchItem object.

        Args:
            item (dict): Raw hot search item data from Weibo API

        Returns:
            HotSearchItem: Formatted hot search item information
        """
        extr_values = re.findall(r'\d+', str(item.get('desc_extr')))
        trending = int(extr_values[0]) if extr_values else 0
        return TrendingItem(
            id=item['id'],
            trending=trending,
            description=item['desc'],
            url=item.get('scheme', '')
        )

    def _to_feed_item(self, mblog: dict) -> FeedItem:
        """
        Convert a raw mblog data to FeedItem object.

        Args:
            mblog (dict): Raw mblog data from Weibo API

        Returns:
            FeedItem: Formatted feed item information
        """
        pics = [pic for pic in mblog.get('pics', []) if 'url' in pic] if mblog.get('pics') else []
        pics = [{'thumbnail': pic['url'], 'large': pic['large']['url']} for pic in pics] if pics else []

        videos = {}
        page_info = mblog.get('page_info')
        if page_info and page_info.get('type') == 'video':
            if 'media_info' in page_info:
                videos['stream_url'] = page_info['media_info'].get('stream_url', '')
                videos['stream_url_hd'] = page_info['media_info'].get('stream_url_hd', '')
            elif 'urls' in page_info:
                videos['mp4_720p_mp4'] = page_info['urls'].get('mp4_720p_mp4', '')
                videos['mp4_hd_mp4'] = page_info['urls'].get('mp4_hd_mp4', '')
                videos['mp4_ld_mp4'] = page_info['urls'].get('mp4_ld_mp4', '')
        
        user = self._to_user_profile(mblog.get('user', {})) if mblog.get('user') else {}
        return FeedItem(
            id = mblog.get('id'),
            text = mblog.get('text'),
            source = mblog.get('source'),
            created_at = mblog.get('created_at'),
            user = user,
            comments_count = mblog.get('comments_count', 0),
            attitudes_count = mblog.get('attitudes_count', 0),
            reposts_count = mblog.get('reposts_count', 0),
            raw_text = mblog.get('raw_text', ''),
            region_name = mblog.get('region_name', ''),
            pics = pics,
            videos = videos if videos else {}
        )

    def _to_user_profile(self, user: dict) -> UserProfile:
        """
        Convert raw user data to UserProfile object.

        Args:
            user (dict): Raw user data from Weibo API

        Returns:
            UserProfile: Formatted user profile information
        """
        return UserProfile(
            id = user['id'],
            screen_name = user['screen_name'],
            profile_image_url = user['profile_image_url'],
            profile_url = user['profile_url'], 
            description = user.get('description', ''),
            follow_count = user.get('follow_count', 0),
            followers_count = user.get('followers_count', ''),
            avatar_hd = user.get('avatar_hd', ''),
            verified = user.get('verified', False),
            verified_reason = user.get('verified_reason', ''),
            gender = user.get('gender', '')
        )
    
    def _to_topic_item(self, item: dict) -> dict:
        """
        Convert raw topic data to a formatted dictionary.

        Args:
            item (dict): Raw topic data from Weibo API

        Returns:
            dict: Formatted topic information
        """
        return {
            'title': item['title_sub'],
            'desc1': item.get('desc1', ''),
            'desc2': item.get('desc2', ''),
            'url': item.get('scheme', '')
        }
    
    def _to_comment_item(self, item: dict) -> CommentItem:
        """
        Convert raw comment data to CommentItem object.

        Args:
            item (dict): Raw comment data from Weibo API

        Returns:
            CommentItem: Formatted comment information
        """
        return CommentItem(
            id = item.get('id'),
            text = item.get('text'),
            created_at = item.get('created_at'),
            user = self._to_user_profile(item.get('user', {})),
            source=item.get('source', ''),
            reply_id = item.get('reply_id', None),
            reply_text = item.get('reply_text', ''),
        )
