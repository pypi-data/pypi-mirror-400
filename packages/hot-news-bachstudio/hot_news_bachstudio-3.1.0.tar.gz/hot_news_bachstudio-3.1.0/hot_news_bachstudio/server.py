#!/usr/bin/env python3
"""
超级今日热点 MCP 服务器
获取全网主流平台的新闻热点 - 返回简洁的标题+链接列表
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List
import aiohttp
import ssl
from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
)
import mcp.server.stdio

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hot-news-server")

# 创建服务器实例
app = Server("hot-news-server")


class HotNewsAPI:
    """热点新闻API类 - 统一返回格式: {title, url, platform, rank}"""
    
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    async def ensure_session(self):
        """确保session已创建"""
        if self.session is None or self.session.closed:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            self.session = aiohttp.ClientSession(headers=self.headers, connector=connector)
    
    async def close(self):
        """关闭session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_weibo_hot(self) -> List[Dict[str, Any]]:
        """获取微博热搜"""
        try:
            await self.ensure_session()
            url = "https://weibo.com/ajax/side/hotSearch"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('ok') == 1:
                        hot_list = data.get('data', {}).get('realtime', [])
                        return [{
                            'title': item.get('word', ''),
                            'url': f"https://s.weibo.com/weibo?q=%23{item.get('word', '')}%23",
                            'platform': '微博',
                            'rank': idx
                        } for idx, item in enumerate(hot_list[:30], 1) if item.get('word')]
        except Exception as e:
            logger.error(f"获取微博热搜失败: {e}")
        return []
    
    async def get_zhihu_hot(self) -> List[Dict[str, Any]]:
        """获取知乎热榜"""
        try:
            await self.ensure_session()
            url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"
            params = {'limit': 30}
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    hot_list = data.get('data', [])
                    return [{
                        'title': item.get('target', {}).get('title', ''),
                        'url': item.get('target', {}).get('url', ''),
                        'platform': '知乎',
                        'rank': idx
                    } for idx, item in enumerate(hot_list, 1) if item.get('target', {}).get('title')]
        except Exception as e:
            logger.error(f"获取知乎热榜失败: {e}")
        return []
    
    async def get_baidu_hot(self) -> List[Dict[str, Any]]:
        """获取百度热搜"""
        try:
            await self.ensure_session()
            url = "https://top.baidu.com/api/board"
            params = {'platform': 'wise', 'tab': 'realtime'}
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    cards = data.get('data', {}).get('cards', [])
                    if cards:
                        hot_list = cards[0].get('content', [])
                        return [{
                            'title': item.get('word', ''),
                            'url': item.get('url', ''),
                            'platform': '百度',
                            'rank': idx
                        } for idx, item in enumerate(hot_list[:30], 1) if item.get('word')]
        except Exception as e:
            logger.error(f"获取百度热搜失败: {e}")
        return []
    
    async def get_douyin_hot(self) -> List[Dict[str, Any]]:
        """获取抖音热点"""
        try:
            await self.ensure_session()
            url = "https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    hot_list = data.get('word_list', [])
                    return [{
                        'title': item.get('word', ''),
                        'url': f"https://www.douyin.com/search/{item.get('word', '')}",
                        'platform': '抖音',
                        'rank': idx
                    } for idx, item in enumerate(hot_list[:30], 1) if item.get('word')]
        except Exception as e:
            logger.error(f"获取抖音热点失败: {e}")
        return []
    
    async def get_bilibili_hot(self) -> List[Dict[str, Any]]:
        """获取B站热门"""
        try:
            await self.ensure_session()
            url = "https://api.bilibili.com/x/web-interface/popular"
            params = {'ps': 30, 'pn': 1}
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('code') == 0:
                        hot_list = data.get('data', {}).get('list', [])
                        return [{
                            'title': item.get('title', ''),
                            'url': item.get('short_link_v2', '') or f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                            'platform': 'B站',
                            'rank': idx
                        } for idx, item in enumerate(hot_list, 1) if item.get('title')]
        except Exception as e:
            logger.error(f"获取B站热门失败: {e}")
        return []
    
    async def get_toutiao_hot(self) -> List[Dict[str, Any]]:
        """获取今日头条热点"""
        try:
            await self.ensure_session()
            url = "https://www.toutiao.com/hot-event/hot-board/"
            params = {'origin': 'toutiao_pc'}
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    hot_list = data.get('data', [])
                    return [{
                        'title': item.get('Title', ''),
                        'url': item.get('Url', ''),
                        'platform': '今日头条',
                        'rank': idx
                    } for idx, item in enumerate(hot_list[:30], 1) if item.get('Title')]
        except Exception as e:
            logger.error(f"获取今日头条热点失败: {e}")
        return []
    
    async def get_36kr_hot(self) -> List[Dict[str, Any]]:
        """获取36氪热榜"""
        try:
            await self.ensure_session()
            url = "https://36kr.com/api/newsflash"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get('data', {}).get('items', [])
                    return [{
                        'title': item.get('title', ''),
                        'url': f"https://36kr.com/newsflashes/{item.get('id', '')}",
                        'platform': '36氪',
                        'rank': idx
                    } for idx, item in enumerate(items[:30], 1) if item.get('title')]
        except Exception as e:
            logger.error(f"获取36氪热榜失败: {e}")
        return []
    
    async def get_ithome_hot(self) -> List[Dict[str, Any]]:
        """获取IT之家热榜"""
        try:
            await self.ensure_session()
            url = "https://m.ithome.com/api/news/newslistpageget"
            params = {'type': 'quanbu', 'page': 1, 'pagesize': 30}
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    news_list = data.get('data', {}).get('newslist', [])
                    return [{
                        'title': item.get('title', ''),
                        'url': item.get('url', ''),
                        'platform': 'IT之家',
                        'rank': idx
                    } for idx, item in enumerate(news_list, 1) if item.get('title')]
        except Exception as e:
            logger.error(f"获取IT之家热榜失败: {e}")
        return []
    
    async def get_thepaper_hot(self) -> List[Dict[str, Any]]:
        """获取澎湃新闻热榜"""
        try:
            await self.ensure_session()
            url = "https://cache.thepaper.cn/contentapi/wwwIndex/rightSidebar"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    hot_list = data.get('data', {}).get('hotNews', [])
                    return [{
                        'title': item.get('name', ''),
                        'url': f"https://www.thepaper.cn/newsDetail_forward_{item.get('contId', '')}",
                        'platform': '澎湃新闻',
                        'rank': idx
                    } for idx, item in enumerate(hot_list[:30], 1) if item.get('name')]
        except Exception as e:
            logger.error(f"获取澎湃新闻热榜失败: {e}")
        return []
    
    async def get_163_hot(self) -> List[Dict[str, Any]]:
        """获取网易新闻热榜"""
        try:
            await self.ensure_session()
            url = "https://temp.163.com/special/00804KVA/cm_guonei.js"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    # 简单解析（实际可能需要更复杂的处理）
                    if 'data' in text:
                        # 这里需要根据实际API格式调整
                        return []
        except Exception as e:
            logger.error(f"获取网易新闻热榜失败: {e}")
        return []
    
    async def get_v2ex_hot(self) -> List[Dict[str, Any]]:
        """获取V2EX热榜"""
        try:
            await self.ensure_session()
            url = "https://www.v2ex.com/api/topics/hot.json"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    hot_list = await response.json()
                    return [{
                        'title': item.get('title', ''),
                        'url': f"https://www.v2ex.com/t/{item.get('id', '')}",
                        'platform': 'V2EX',
                        'rank': idx
                    } for idx, item in enumerate(hot_list[:30], 1) if item.get('title')]
        except Exception as e:
            logger.error(f"获取V2EX热榜失败: {e}")
        return []
    
    async def get_juejin_hot(self) -> List[Dict[str, Any]]:
        """获取掘金热榜"""
        try:
            await self.ensure_session()
            url = "https://api.juejin.cn/recommend_api/v1/article/recommend_all_feed"
            payload = {
                "id_type": 2,
                "sort_type": 200,
                "cate_id": "1",
                "cursor": "0",
                "limit": 30
            }
            async with self.session.post(url, json=payload, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    hot_list = data.get('data', [])
                    return [{
                        'title': item.get('article_info', {}).get('title', ''),
                        'url': f"https://juejin.cn/post/{item.get('article_info', {}).get('article_id', '')}",
                        'platform': '掘金',
                        'rank': idx
                    } for idx, item in enumerate(hot_list[:30], 1) if item.get('article_info', {}).get('title')]
        except Exception as e:
            logger.error(f"获取掘金热榜失败: {e}")
        return []
    
    async def get_github_trending(self) -> List[Dict[str, Any]]:
        """获取GitHub Trending"""
        try:
            await self.ensure_session()
            # 使用GitHub API获取trending（需要解析HTML或使用第三方API）
            url = "https://api.github.com/search/repositories"
            params = {
                'q': 'created:>2024-01-01',
                'sort': 'stars',
                'order': 'desc',
                'per_page': 30
            }
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get('items', [])
                    return [{
                        'title': item.get('full_name', ''),
                        'url': item.get('html_url', ''),
                        'platform': 'GitHub',
                        'rank': idx
                    } for idx, item in enumerate(items, 1) if item.get('full_name')]
        except Exception as e:
            logger.error(f"获取GitHub Trending失败: {e}")
        return []
    
    async def get_sspai_hot(self) -> List[Dict[str, Any]]:
        """获取少数派热榜"""
        try:
            await self.ensure_session()
            url = "https://sspai.com/api/v1/article/tag/page/get"
            params = {'limit': 30, 'offset': 0, 'sort': 'hot'}
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get('data', [])
                    return [{
                        'title': item.get('title', ''),
                        'url': f"https://sspai.com/post/{item.get('id', '')}",
                        'platform': '少数派',
                        'rank': idx
                    } for idx, item in enumerate(items, 1) if item.get('title')]
        except Exception as e:
            logger.error(f"获取少数派热榜失败: {e}")
        return []
    
    async def get_csdn_hot(self) -> List[Dict[str, Any]]:
        """获取CSDN热榜"""
        try:
            await self.ensure_session()
            url = "https://blog.csdn.net/phoenix/web/blog/hotRank"
            params = {'page': 0, 'pageSize': 30}
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    hot_list = data.get('data', [])
                    return [{
                        'title': item.get('articleTitle', ''),
                        'url': item.get('articleDetailUrl', ''),
                        'platform': 'CSDN',
                        'rank': idx
                    } for idx, item in enumerate(hot_list, 1) if item.get('articleTitle')]
        except Exception as e:
            logger.error(f"获取CSDN热榜失败: {e}")
        return []
    
    async def get_oschina_hot(self) -> List[Dict[str, Any]]:
        """获取开源中国热榜"""
        try:
            await self.ensure_session()
            url = "https://www.oschina.net/action/ajax/get_recommend_list"
            params = {'type': 'blog', 'page': 1, 'pageSize': 30}
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    hot_list = data.get('result', [])
                    return [{
                        'title': item.get('title', ''),
                        'url': item.get('href', ''),
                        'platform': '开源中国',
                        'rank': idx
                    } for idx, item in enumerate(hot_list, 1) if item.get('title')]
        except Exception as e:
            logger.error(f"获取开源中国热榜失败: {e}")
        return []
    
    async def get_segmentfault_hot(self) -> List[Dict[str, Any]]:
        """获取SegmentFault热榜"""
        try:
            await self.ensure_session()
            url = "https://segmentfault.com/gateway/homepage/data"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    hot_list = data.get('rows', {}).get('hottest', [])
                    return [{
                        'title': item.get('title', ''),
                        'url': f"https://segmentfault.com/a/{item.get('url', '')}",
                        'platform': 'SegmentFault',
                        'rank': idx
                    } for idx, item in enumerate(hot_list[:30], 1) if item.get('title')]
        except Exception as e:
            logger.error(f"获取SegmentFault热榜失败: {e}")
        return []
    
    async def get_cnblogs_hot(self) -> List[Dict[str, Any]]:
        """获取博客园热榜"""
        try:
            await self.ensure_session()
            url = "https://www.cnblogs.com/aggsite/headline"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    hot_list = data.get('data', [])
                    return [{
                        'title': item.get('Title', ''),
                        'url': item.get('Url', ''),
                        'platform': '博客园',
                        'rank': idx
                    } for idx, item in enumerate(hot_list[:30], 1) if item.get('Title')]
        except Exception as e:
            logger.error(f"获取博客园热榜失败: {e}")
        return []
    
    async def get_infoq_hot(self) -> List[Dict[str, Any]]:
        """获取InfoQ热榜"""
        try:
            await self.ensure_session()
            url = "https://www.infoq.cn/public/v1/article/getList"
            params = {'type': 2, 'size': 30}
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    hot_list = data.get('data', [])
                    return [{
                        'title': item.get('article_title', ''),
                        'url': f"https://www.infoq.cn/article/{item.get('uuid', '')}",
                        'platform': 'InfoQ',
                        'rank': idx
                    } for idx, item in enumerate(hot_list, 1) if item.get('article_title')]
        except Exception as e:
            logger.error(f"获取InfoQ热榜失败: {e}")
        return []
    
    async def get_jianshu_hot(self) -> List[Dict[str, Any]]:
        """获取简书科技热榜"""
        try:
            await self.ensure_session()
            url = "https://www.jianshu.com/asimov/subscriptions/recommended_collections"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    hot_list = data.get('data', [])
                    return [{
                        'title': item.get('title', ''),
                        'url': f"https://www.jianshu.com/c/{item.get('slug', '')}",
                        'platform': '简书',
                        'rank': idx
                    } for idx, item in enumerate(hot_list[:30], 1) if item.get('title')]
        except Exception as e:
            logger.error(f"获取简书热榜失败: {e}")
        return []
    
    async def get_zaobao_hot(self) -> List[Dict[str, Any]]:
        """获取前端早报"""
        try:
            await self.ensure_session()
            url = "https://wubaiqing.github.io/zaobao/data.json"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list) and len(data) > 0:
                        latest = data[0]
                        items = latest.get('items', [])
                        return [{
                            'title': item,
                            'url': latest.get('url', ''),
                            'platform': '前端早报',
                            'rank': idx
                        } for idx, item in enumerate(items[:30], 1) if item]
        except Exception as e:
            logger.error(f"获取前端早报失败: {e}")
        return []
    
    async def get_all_hot(self) -> Dict[str, List[Dict[str, Any]]]:
        """获取所有平台热点"""
        tasks = {
            'weibo': self.get_weibo_hot(),
            'zhihu': self.get_zhihu_hot(),
            'baidu': self.get_baidu_hot(),
            'douyin': self.get_douyin_hot(),
            'bilibili': self.get_bilibili_hot(),
            'toutiao': self.get_toutiao_hot(),
            '36kr': self.get_36kr_hot(),
            'ithome': self.get_ithome_hot(),
            'thepaper': self.get_thepaper_hot(),
            'v2ex': self.get_v2ex_hot(),
            'juejin': self.get_juejin_hot(),
            'github': self.get_github_trending(),
            'sspai': self.get_sspai_hot(),
            'csdn': self.get_csdn_hot(),
            'oschina': self.get_oschina_hot(),
            'segmentfault': self.get_segmentfault_hot(),
            'cnblogs': self.get_cnblogs_hot(),
            'infoq': self.get_infoq_hot(),
            'jianshu': self.get_jianshu_hot(),
            'zaobao': self.get_zaobao_hot(),
        }
        
        results = {}
        for platform, task in tasks.items():
            try:
                results[platform] = await task
            except Exception as e:
                logger.error(f"获取{platform}热点失败: {e}")
                results[platform] = []
        
        return results
    
    def format_simple_list(self, data: List[Dict[str, Any]]) -> str:
        """格式化为简洁列表"""
        if not data:
            return "暂无数据"
        
        lines = []
        for item in data:
            rank = item.get('rank', '')
            title = item.get('title', '')
            url = item.get('url', '')
            lines.append(f"{rank}. {title}\n   🔗 {url}")
        
        return "\n\n".join(lines)


# 创建API实例
api = HotNewsAPI()


# Resources 已移除，只保留 Tools


@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用的工具"""
    return [
        Tool(
            name="search_news",
            description="搜索当天的热点新闻。可以指定平台搜索，也可以搜索所有平台。支持的平台: douyin(抖音), bilibili(B站), toutiao(今日头条), thepaper(澎湃新闻), csdn(CSDN), github(GitHub), v2ex(V2EX), 36kr(36氪), all(所有平台)",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索关键词，留空则返回所有热点"
                    },
                    "platform": {
                        "type": "string",
                        "description": "平台名称，默认搜索所有平台",
                        "enum": ["douyin", "bilibili", "toutiao", "thepaper", "csdn", "github", "v2ex", "36kr", "all"],
                        "default": "all"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回数量，默认20",
                        "default": 20
                    }
                },
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """调用工具"""
    if name == "search_news":
        keyword = arguments.get("keyword", "")
        platform = arguments.get("platform", "all")
        limit = arguments.get("limit", 20)
        
        # 平台映射（只包含可用的）
        platform_map = {
            "douyin": api.get_douyin_hot,
            "bilibili": api.get_bilibili_hot,
            "toutiao": api.get_toutiao_hot,
            "thepaper": api.get_thepaper_hot,
            "csdn": api.get_csdn_hot,
            "github": api.get_github_trending,
            "v2ex": api.get_v2ex_hot,
            "36kr": api.get_36kr_hot,
        }
        
        # 获取数据
        if platform == "all":
            # 获取所有平台
            all_data = await api.get_all_hot()
            results = []
            for platform_key, items in all_data.items():
                results.extend(items)
        else:
            # 获取指定平台
            if platform not in platform_map:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"不支持的平台: {platform}",
                        "available_platforms": list(platform_map.keys())
                    }, ensure_ascii=False)
                )]
            
            func = platform_map[platform]
            results = await func()
        
        # 关键词过滤
        if keyword:
            results = [
                item for item in results 
                if keyword.lower() in item.get('title', '').lower()
            ]
        
        # 限制数量
        results = results[:limit]
        
        # 返回简单的数组格式
        news_list = [
            {
                "title": item.get('title', ''),
                "url": item.get('url', '')
            }
            for item in results
        ]
        
        return [TextContent(
            type="text",
            text=json.dumps(news_list, ensure_ascii=False, indent=2)
        )]
    
    raise ValueError(f"未知的工具: {name}")


async def async_main():
    """异步主函数"""
    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("超级今日热点 MCP 服务器启动中...")
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    finally:
        await api.close()


def main():
    """同步入口点，供命令行调用"""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
