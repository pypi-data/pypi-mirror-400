# Weibo MCP Server 🚀

Weibo Data API Server powered by Model Context Protocol - Real-time access to Weibo user profiles, posts, trending topics, followers/following data. Supports user search, content analysis, and topic discovery for AI applications.

<a href="https://glama.ai/mcp/servers/@qinyuanpei/mcp-server-weibo">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@qinyuanpei/mcp-server-weibo/badge" alt="Weibo Server MCP server" />
</a>

[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/qinyuanpei-mcp-server-weibo-badge.png)](https://mseep.ai/app/qinyuanpei-mcp-server-weibo)

## Installation

* From source code:

```json
{
  "mcpServers": {
    "weibo": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/qinyuanpei/mcp-server-weibo.git",
        "mcp-server-weibo"
      ]
    }
  }
}
```
* From package manager:

```json
{
  "mcpServers": {
    "weibo": {
      "command": "uvx",
      "args": ["mcp-server-weibo"]
    }
  }
}
```
* From Docker:
```bash
docker build -t mcp-server-weibo .
docker run -d --name mcp-server-weibo -p 4200:4200 mcp-server-weibo
```
Reference config:
```json
{
  "mcpServers": {
    "weibo": {
      "url": "http://localhost:4200/mcp"
    }
  }
}
```

## Components

### Tools

#### search_users(keyword, limit)
Description: Search for Weibo users

Example return value:

```json
[
  {
    "id": 1749127163,
    "screen_name": "雷军",
    "profile_image_url": "https://tvax1.sinaimg.cn/crop.0.0.1080.1080.180/001Un9Srly8i1p6mooym8j60u00u10tu02.jpg?KID=imgbed,tva&Expires=1749109677&ssig=QzOuVFBlRp",
    "profile_url": "https://m.weibo.cn/u/1749127163?",
    "description": "小米董事长，金山软件董事长。业余爱好是天使投资。",
    "follow_count": 1562,
    "followers_count": "2671.2万",
    "avatar_hd": "https://wx1.sinaimg.cn/orj480/001Un9Srly8i1p6mooym8j60u00u10tu02.jpg",
    "verified": true,
    "verified_reason": "小米创办人，董事长兼CEO；金山软件董事长；天使投资人。",
    "gender": "m"
  }
]
```

#### get_profile(uid)
Description: Get detailed user information

Example return value:

```json
{
  "id": 1749127163,
  "screen_name": "雷军",
  "profile_image_url": "https://tvax1.sinaimg.cn/crop.0.0.1080.1080.180/001Un9Srly8i1p6mooym8j60u00u10tu02.jpg?KID=imgbed,tva&Expires=1749109733&ssig=5OrMoqbwcY",
  "profile_url": "https://m.weibo.cn/u/1749127163?",
  "description": "小米董事长，金山软件董事长。业余爱好是天使投资。",
  "follow_count": 1562,
  "followers_count": "2671.2万",
  "avatar_hd": "https://wx1.sinaimg.cn/orj480/001Un9Srly8i1p6mooym8j60u00u10tu02.jpg",
  "verified": true,
  "verified_reason": "小米创办人，董事长兼CEO；金山软件董事长；天使投资人。",
  "gender": "m"
}
```

#### get_feeds(uid, limit)
Description: Get user posts

Example return value:
```json
[
  {
    "id": 5167970394572058,
    "text": "今年是小米创业15周年。<br />早在11年前，2014年，我们就开始芯片研发之旅。<br /><br />2014年9月，澎湃项目立项。2017年，小米首款手机芯片“澎湃S1”正式亮相，定位中高端。后来，因为种种原因，遭遇挫折，我们暂停了SoC大芯片的研发。但我们还是保留了芯片研发的火种，转向了“小芯片”路线。再后来，小米澎湃各 ...<a href=\"/status/5167970394572058\">全文</a>",
    "source": "Xiaomi 15S Pro",
    "created_at": "Mon May 19 11:00:21 +0800 2025",
    "user": {
      "id": 1749127163,
      "screen_name": "雷军",
      "profile_image_url": "https://tvax1.sinaimg.cn/crop.0.0.1080.1080.180/001Un9Srly8i1p6mooym8j60u00u10tu02.jpg?KID=imgbed,tva&Expires=1749109794&ssig=29j5mGcswB",
      "profile_url": "https://m.weibo.cn/u/1749127163?",
      "description": "小米董事长，金山软件董事长。业余爱好是天使投资。",
      "follow_count": 1562,
      "followers_count": "2671.2万",
      "avatar_hd": "https://wx1.sinaimg.cn/orj480/001Un9Srly8i1p6mooym8j60u00u10tu02.jpg",
      "verified": true,
      "verified_reason": "小米创办人，董事长兼CEO；金山软件董事长；天使投资人。",
      "gender": "m"
    },
    "comments_count": 10183,
    "attitudes_count": 141025,
    "reposts_count": 5884,
    "raw_text": "",
    "region_name": "发布于 北京",
    "pics": [
      {
        "thumbnail": "https://wx2.sinaimg.cn/orj360/001Un9Srly1i1k4dr5djgj60u04gp7wh02.jpg",
        "large": "https://wx2.sinaimg.cn/large/001Un9Srly1i1k4dr5djgj60u04gp7wh02.jpg"
      }
    ],
    "videos": {}
  }
]
```

#### get_trendings(limit)
Description: Get Weibo trending topics

Example return value:

```json
[
  {
    "id": 0,
    "trending": 0,
    "description": "跟着总书记探寻中华文明",
    "url": "https://m.weibo.cn/search?containerid=100103type%3D1%26t%3D10%26q%3D%23%E8%B7%9F%E7%9D%80%E6%80%BB%E4%B9%A6%E8%AE%B0%E6%8E%A2%E5%AF%BB%E4%B8%AD%E5%8D%8E%E6%96%87%E6%98%8E%23&stream_entry_id=51&isnewpage=1&extparam=seat%3D1%26stream_entry_id%3D51%26c_type%3D51%26filter_type%3Drealtimehot%26pos%3D0%26cate%3D10103%26dgr%3D0%26q%3D%2523%25E8%25B7%259F%25E7%259D%2580%25E6%2580%25BB%25E4%25B9%25A6%25E8%25AE%25B0%25E6%258E%25A2%25E5%25AF%25BB%25E4%25B8%25AD%25E5%258D%258E%25E6%2596%2587%25E6%2598%258E%2523%26display_time%3D1749098276%26pre_seqid%3D17490982767230055147"
  },
  {
    "id": 3,
    "trending": 591855,
    "description": "建议大家要远离恋爱式友情",
    "url": "https://m.weibo.cn/search?containerid=100103type%3D1%26t%3D10%26q%3D%E5%BB%BA%E8%AE%AE%E5%A4%A7%E5%AE%B6%E8%A6%81%E8%BF%9C%E7%A6%BB%E6%81%8B%E7%88%B1%E5%BC%8F%E5%8F%8B%E6%83%85&stream_entry_id=31&isnewpage=1&extparam=seat%3D1%26dgr%3D0%26c_type%3D31%26cate%3D5001%26realpos%3D12%26stream_entry_id%3D31%26lcate%3D5001%26q%3D%25E5%25BB%25BA%25E8%25AE%25AE%25E5%25A4%25A7%25E5%25AE%25B6%25E8%25A6%2581%25E8%25BF%259C%25E7%25A6%25BB%25E6%2581%258B%25E7%2588%25B1%25E5%25BC%258F%25E5%258F%258B%25E6%2583%2585%26pos%3D11%26band_rank%3D12%26flag%3D1%26filter_type%3Drealtimehot%26display_time%3D1749098276%26pre_seqid%3D17490982767230055147"
  },
  {
    "id": 13,
    "trending": 584808,
    "description": "李昀锐的清爽感是夏日刚需",
    "url": "https://m.weibo.cn/search?containerid=100103type%3D1%26t%3D10%26q%3D%23%E6%9D%8E%E6%98%80%E9%94%90%E7%9A%84%E6%B8%85%E7%88%BD%E6%84%9F%E6%98%AF%E5%A4%8F%E6%97%A5%E5%88%9A%E9%9C%80%23&stream_entry_id=31&isnewpage=1&extparam=seat%3D1%26dgr%3D0%26c_type%3D31%26cate%3D5001%26realpos%3D13%26stream_entry_id%3D31%26lcate%3D5001%26q%3D%2523%25E6%259D%258E%25E6%2598%2580%25E9%2594%2590%25E7%259A%2584%25E6%25B8%2585%25E7%2588%25BD%25E6%2584%259F%25E6%2598%25AF%25E5%25A4%258F%25E6%2597%25A5%25E5%2588%259A%25E9%259C%2580%2523%26pos%3D12%26band_rank%3D13%26flag%3D1%26filter_type%3Drealtimehot%26display_time%3D1749098276%26pre_seqid%3D17490982767230055147"
  },
  {
    "id": 14,
    "trending": 573889,
    "description": "陈思诚张小斐首度合作",
    "url": "https://m.weibo.cn/search?containerid=100103type%3D1%26t%3D10%26q%3D%E9%99%88%E6%80%9D%E8%AF%9A%E5%BC%A0%E5%B0%8F%E6%96%90%E9%A6%96%E5%BA%A6%E5%90%88%E4%BD%9C&stream_entry_id=31&isnewpage=1&extparam=seat%3D1%26dgr%3D0%26c_type%3D31%26cate%3D5001%26realpos%3D14%26stream_entry_id%3D31%26lcate%3D5001%26q%3D%25E9%2599%2588%25E6%2580%259D%25E8%25AF%259A%25E5%25BC%25A0%25E5%25B0%258F%25E6%2596%2590%25E9%25A6%2596%25E5%25BA%25A6%25E5%2590%2588%25E4%25BD%259C%26pos%3D13%26band_rank%3D14%26flag%3D1%26filter_type%3Drealtimehot%26display_time%3D1749098276%26pre_seqid%3D17490982767230055147"
  }
]
```

#### search_content(keyword, limit, page)
Description: Search Weibo posts

Example return value:

```json
[
  {
    "id": 5173507416919189,
    "text": "<a  href=\"https://m.weibo.cn/search?containerid=231522type%3D1%26t%3D10%26q%3D%23%E5%90%89%E5%88%A9%E9%93%B6%E6%B2%B3%23&extparam=%23%E5%90%89%E5%88%A9%E9%93%B6%E6%B2%B3%23\" data-hide=\"\"><span class=\"surl-text\">#吉利银河#</span></a><br />省流：<br />1.推荐度系列分为四个等级，一般/可买/推荐/非常推荐。「一般/可买」车型减少展开，想看的人比较多的话，我们会给大家再出详细的视频<br />2.本期非常推荐的有吉利星愿、星耀8 ，推荐有熊猫mini、星舰7、银河E5<br />3.大家还有什么想看的品牌的年中横评也可以在评论下留言  ...<a href=\"/status/5173507416919189\">全文</a>",
    "source": "微博视频号",
    "created_at": "Tue Jun 03 17:42:30 +0800 2025",
    "user": {
      "id": 2098256142,
      "screen_name": "农民新八",
      "profile_image_url": "https://tvax2.sinaimg.cn/crop.0.0.1080.1080.180/7d10d90ely8hcufl69gx9j20u00u0mxu.jpg?KID=imgbed,tva&Expires=1749110036&ssig=cgiHgZmsMD",
      "profile_url": "https://m.weibo.cn/u/2098256142?",
      "description": "新八，26岁。喜机械，喜机车，喜汽车，喜摄影。",
      "follow_count": 429,
      "followers_count": "19.9万",
      "avatar_hd": "https://wx2.sinaimg.cn/orj480/7d10d90ely8hcufl69gx9j20u00u0mxu.jpg",
      "verified": true,
      "verified_reason": "微博原创视频博主",
      "gender": "m"
    },
    "comments_count": 14,
    "attitudes_count": 33,
    "reposts_count": 2,
    "raw_text": "",
    "region_name": "浙江",
    "pics": [],
    "videos": {
      "stream_url": "https://f.video.weibocdn.com/o0/Znlc5yrLlx08oKQqLjm8010412027DBU0E010.mp4?label=mp4_ld&template=640x360.25.0&ori=0&ps=1BVp4ysnknHVZu&Expires=1749102785&ssig=usxCRRQp1I&KID=unistore,video",
      "stream_url_hd": "https://f.video.weibocdn.com/o0/WTxFgJ3rlx08oKQqpRpC01041203hVWU0E020.mp4?label=mp4_hd&template=852x480.25.0&ori=0&ps=1BVp4ysnknHVZu&Expires=1749102785&ssig=qTWtMQ8ugG&KID=unistore,video"
    }
  },
  {
    "id": 5173089152273188,
    "text": "第十个🥰 ",
    "source": "iPhone 16 Pro",
    "created_at": "Mon Jun 02 14:00:28 +0800 2025",
    "user": {
      "id": 5205701205,
      "screen_name": "·MooNquake·",
      "profile_image_url": "https://tvax3.sinaimg.cn/crop.0.0.512.512.180/005GiAGFly8i0qxuw3pw6j30e80e8dg1.jpg?KID=imgbed,tva&Expires=1749110036&ssig=72lXbXDOmv",
      "profile_url": "https://m.weibo.cn/u/5205701205?",
      "description": "请享受无法回避的痛苦",
      "follow_count": 493,
      "followers_count": "1245",
      "avatar_hd": "https://wx3.sinaimg.cn/orj480/005GiAGFly8i0qxuw3pw6j30e80e8dg1.jpg",
      "verified": false,
      "verified_reason": "",
      "gender": "m"
    },
    "comments_count": 15,
    "attitudes_count": 21,
    "reposts_count": 0,
    "raw_text": "",
    "region_name": "浙江",
    "pics": [
      {
        "thumbnail": "https://wx3.sinaimg.cn/orj360/005GiAGFgy1i20y541pyij320u0xiqv5.jpg",
        "large": "https://wx3.sinaimg.cn/large/005GiAGFgy1i20y541pyij320u0xiqv5.jpg"
      },
      {
        "thumbnail": "https://wx3.sinaimg.cn/orj360/005GiAGFgy1i20y52tin9j320u0xiqv5.jpg",
        "large": "https://wx3.sinaimg.cn/large/005GiAGFgy1i20y52tin9j320u0xiqv5.jpg"
      },
      {
        "thumbnail": "https://wx2.sinaimg.cn/orj360/005GiAGFgy1i20y4jg6gaj31hc0oktl2.jpg",
        "large": "https://wx2.sinaimg.cn/large/005GiAGFgy1i20y4jg6gaj31hc0oktl2.jpg"
      },
      {
        "thumbnail": "https://wx3.sinaimg.cn/orj360/005GiAGFgy1i20y6fgcg3j320u0xib29.jpg",
        "large": "https://wx3.sinaimg.cn/large/005GiAGFgy1i20y6fgcg3j320u0xib29.jpg"
      }
    ],
    "videos": {}
  }
]
```

#### search_topics(keyword, limit, page)
Description: Search Weibo topics

Example return value:

```json
[
  {
    "title": "#许嵩#",
    "desc1": "",
    "desc2": "1913.8万讨论 26.8亿阅读",
    "url": "https://m.weibo.cn/search?containerid=231522type%3D1%26t%3D10%26q%3D%23%E8%AE%B8%E5%B5%A9%23&isnewpage=1"
  },
  {
    "title": "#许嵩呼吸之野演唱会#",
    "desc1": "",
    "desc2": "1738.4万讨论 6.9亿阅读",
    "url": "https://m.weibo.cn/search?containerid=231522type%3D1%26t%3D10%26q%3D%23%E8%AE%B8%E5%B5%A9%E5%91%BC%E5%90%B8%E4%B9%8B%E9%87%8E%E6%BC%94%E5%94%B1%E4%BC%9A%23&extparam=%23%E8%AE%B8%E5%B5%A9%E5%91%BC%E5%90%B8%E4%B9%8B%E9%87%8E%E6%BC%94%E5%94%B1%E4%BC%9A%23"
  },
  {
    "title": "#冯禧许嵩疑分手#",
    "desc1": "",
    "desc2": "6157讨论 8040.5万阅读",
    "url": "https://m.weibo.cn/search?containerid=231522type%3D1%26t%3D10%26q%3D%23%E5%86%AF%E7%A6%A7%E8%AE%B8%E5%B5%A9%E7%96%91%E5%88%86%E6%89%8B%23&extparam=%23%E5%86%AF%E7%A6%A7%E8%AE%B8%E5%B5%A9%E7%96%91%E5%88%86%E6%89%8B%23"
  }
]
```

#### get_comments(feed_id, page)
Description: Get comments under a specific Weibo post

Example return value:

```json
[{
  "id": 5176653778784993,
   "text": "回复<a href='https://m.weibo.cn/n/需要爱谁'>@需要爱谁</a>:这是openRouter的使用数据。ds除了那波发布的新鲜劲头，主要服务国内市场。国内用户没理由用国内ai还特意找openRouter这个海外中间商",
   "created_at": "55分钟前",
   "source": "来自广东",
   "user": {
      "id": 1784072130,
      "screen_name": "呗塔熊",
      "profile_image_url": "https://tva2.sinaimg.cn/crop.0.0.749.749.180/6a56c7c2jw8f2l1ermz4hj20ku0kt3z8.jpg?KID=imgbed,tva&Expires=1749708042&ssig=eLSiu6Jz5j",
      "profile_url": "https://m.weibo.cn/u/1784072130?",
      "description": "",
      "follow_count": 0,
      "followers_count": "158",
      "avatar_hd": "",
      "verified": false,
      "verified_reason": "",
      "gender": ""
   },
   "reply_id": 5176636326281776,
   "reply_text": "DS怎么是0%<span class=\"url-icon\"><img alt=[思考] src=\"https://h5.sinaimg.cn/m/emoticon/icon/default/d_sikao-ff9602dd08.png\" style=\"width:1em; height:1em;\" /></span>"
}]
```

#### get_hot_feeds(uid, limit)
Description: Get hot Weibo posts

Example return value:
```json
[{
  "id": 5188923573404794,
  "text": "《深度学习数学导论(Mathematical Introduction to Deep Learning: Methods, Implementations, and Theory)》｜全面掌握人工神经网络与优化理论！📚✨<br />📌【多样化ANN架构】全连接、卷积、残差、循环网络详尽解析，涵盖ReLU、GELU、Swish等丰富激活函数。🤖<br />📌【理论与实现并重】深入ANN的向量 ...<a href=\"/status/5188923573404794\">全文</a>",
  "source": "Mac客户端",
  "created_at": "Wed Jul 16 06:40:48 +0800 2025",
  "user": {
    "id": 1402400261,
    "screen_name": "爱可可-爱生活",
    "profile_image_url": "https://tva2.sinaimg.cn/crop.10.34.646.646.180/5396ee05jw1ena6co8qiwj20sg0izjxd.jpg?KID=imgbed,tva&Expires=1752744231&ssig=mKmwQ4f8aA",
    "profile_url": "https://m.weibo.cn/u/1402400261?",
    "description": "北邮PRIS模式识别实验室陈老师 商务合作 QQ:1289468869 Email:1289468869@qq.com",
    "follow_count": 760,
    "followers_count": "85.7万",
    "avatar_hd": "https://ww2.sinaimg.cn/orj480/5396ee05jw1ena6co8qiwj20sg0izjxd.jpg",
    "verified": true,
    "verified_reason": "AI博主",
    "gender": "m"
  },
  "comments_count": 4,
  "attitudes_count": 58,
  "reposts_count": 80,
  "raw_text": "",
  "region_name": "发布于 北京",
  "pics": [{
    "thumbnail": "https://wx2.sinaimg.cn/orj360/5396ee05ly8i3fgq9fm9fj20p610aq51.jpg",
    "large": "https://wx2.sinaimg.cn/large/5396ee05ly8i3fgq9fm9fj20p610aq51.jpg"
  }],
  "videos": {}
}]
```

#### get_followers(uid, limit, page)
Description: Get following list

Example return value:
```json
[{
  "id": 6486678714,
  "screen_name": "张小珺-Benita",
  "profile_image_url": "https://tvax1.sinaimg.cn/crop.0.0.1080.1080.180/0074Zrsely8hz0hg65fq8j30u00u0n1e.jpg?KID=imgbed,tva&Expires=1752744494&ssig=SZY8jaooks",
  "profile_url": "https://m.weibo.cn/u/6486678714?",
  "description": "喜欢无聊的小东西",
  "follow_count": 54,
  "followers_count": "10万",
  "avatar_hd": "https://wx1.sinaimg.cn/orj480/0074Zrsely8hz0hg65fq8j30u00u0n1e.jpg",
  "verified": true,
  "verified_reason": "财经作者、播客《张小珺Jùn｜商业访谈录》主理人",
  "gender": "f"
  },
  {
    "id": 3587960280,
    "screen_name": "粉丝头条官方微博",
    "profile_image_url": "https://tvax4.sinaimg.cn/crop.0.0.499.499.180/003UOIn6ly8h8vdmp57oyj60dv0dvq3502.jpg?KID=imgbed,tva&Expires=1752744494&ssig=1SFiIxbaYr",
    "profile_url": "https://m.weibo.cn/u/3587960280?",
    "description": "推广博文及账号的利器！助您快速积累社交资产！",
    "follow_count": 760,
    "followers_count": "1438.8万",
    "avatar_hd": "https://wx4.sinaimg.cn/orj480/003UOIn6ly8h8vdmp57oyj60dv0dvq3502.jpg",
    "verified": true,
    "verified_reason": "粉丝头条官方微博",
    "gender": "f"
}]
```

#### get_fans(uid, limit, page)
Description: Get followers list

Example return value:
```json
[{
  "id": 6486678714,
  "screen_name": "张小珺-Benita",
  "profile_image_url": "https://tvax1.sinaimg.cn/crop.0.0.1080.1080.180/0074Zrsely8hz0hg65fq8j30u00u0n1e.jpg?KID=imgbed,tva&Expires=1752744494&ssig=SZY8jaooks",
  "profile_url": "https://m.weibo.cn/u/6486678714?",
  "description": "喜欢无聊的小东西",
  "follow_count": 54,
  "followers_count": "10万",
  "avatar_hd": "https://wx1.sinaimg.cn/orj480/0074Zrsely8hz0hg65fq8j30u00u0n1e.jpg",
  "verified": true,
  "verified_reason": "财经作者、播客《张小珺Jùn｜商业访谈录》主理人",
  "gender": "f"
  },
  {
    "id": 3587960280,
    "screen_name": "粉丝头条官方微博",
    "profile_image_url": "https://tvax4.sinaimg.cn/crop.0.0.499.499.180/003UOIn6ly8h8vdmp57oyj60dv0dvq3502.jpg?KID=imgbed,tva&Expires=1752744494&ssig=1SFiIxbaYr",
    "profile_url": "https://m.weibo.cn/u/3587960280?",
    "description": "推广博文及账号的利器！助您快速积累社交资产！",
    "follow_count": 760,
    "followers_count": "1438.8万",
    "avatar_hd": "https://wx4.sinaimg.cn/orj480/003UOIn6ly8h8vdmp57oyj60dv0dvq3502.jpg",
    "verified": true,
    "verified_reason": "粉丝头条官方微博",
    "gender": "f"
}]
```

### Resources

None

### Prompts

None

## Requirements

- Python >= 3.10
- httpx >= 0.24.0

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Disclaimer

This project is not affiliated with Weibo and is intended for learning and research purposes only.
