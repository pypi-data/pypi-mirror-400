#!/usr/bin/env python3
"""
测试脚本 - 测试所有平台的API
"""

import asyncio
from server import HotNewsAPI


async def test_all_platforms():
    """测试所有平台"""
    api = HotNewsAPI()
    
    print("=" * 70)
    print("🔥 超级今日热点 v3.0 - 测试所有平台（含科技类扩展）")
    print("=" * 70)
    
    platforms = [
        ("微博热搜", api.get_weibo_hot),
        ("知乎热榜", api.get_zhihu_hot),
        ("百度热搜", api.get_baidu_hot),
        ("抖音热点", api.get_douyin_hot),
        ("B站热门", api.get_bilibili_hot),
        ("今日头条", api.get_toutiao_hot),
        ("36氪", api.get_36kr_hot),
        ("IT之家", api.get_ithome_hot),
        ("澎湃新闻", api.get_thepaper_hot),
        ("V2EX", api.get_v2ex_hot),
        ("掘金", api.get_juejin_hot),
        ("GitHub", api.get_github_trending),
        ("少数派", api.get_sspai_hot),
        ("CSDN", api.get_csdn_hot),
        ("开源中国", api.get_oschina_hot),
        ("SegmentFault", api.get_segmentfault_hot),
        ("博客园", api.get_cnblogs_hot),
        ("InfoQ", api.get_infoq_hot),
        ("简书", api.get_jianshu_hot),
        ("前端早报", api.get_zaobao_hot),
    ]
    
    results = {}
    
    for name, func in platforms:
        print(f"\n{'='*70}")
        print(f"📱 测试平台: {name}")
        print(f"{'='*70}")
        try:
            data = await func()
            if data:
                print(f"✅ 成功获取 {len(data)} 条数据")
                print(f"\n前3条:")
                for item in data[:3]:
                    print(f"  {item['rank']}. {item['title'][:50]}...")
                    print(f"     🔗 {item['url'][:80]}...")
                results[name] = len(data)
            else:
                print(f"⚠️  暂无数据")
                results[name] = 0
        except Exception as e:
            print(f"❌ 错误: {e}")
            results[name] = 0
    
    print(f"\n{'='*70}")
    print("📊 测试结果汇总")
    print(f"{'='*70}")
    
    success_count = sum(1 for count in results.values() if count > 0)
    total_items = sum(results.values())
    
    # 分类显示
    print("\n【视频社交平台】")
    for name in ["抖音热点", "B站热门"]:
        count = results.get(name, 0)
        status = "✅" if count > 0 else "⚠️"
        print(f"{status} {name:15s}: {count:3d} 条")
    
    print("\n【新闻资讯平台】")
    for name in ["微博热搜", "知乎热榜", "百度热搜", "今日头条", "澎湃新闻"]:
        count = results.get(name, 0)
        status = "✅" if count > 0 else "⚠️"
        print(f"{status} {name:15s}: {count:3d} 条")
    
    print("\n【科技开发平台】")
    for name in ["CSDN", "掘金", "开源中国", "SegmentFault", "博客园", "InfoQ", "简书", "前端早报"]:
        count = results.get(name, 0)
        status = "✅" if count > 0 else "⚠️"
        print(f"{status} {name:15s}: {count:3d} 条")
    
    print("\n【技术社区平台】")
    for name in ["GitHub", "V2EX", "36氪", "IT之家", "少数派"]:
        count = results.get(name, 0)
        status = "✅" if count > 0 else "⚠️"
        print(f"{status} {name:15s}: {count:3d} 条")
    
    print(f"\n{'='*70}")
    print(f"✅ 成功平台: {success_count}/{len(platforms)} 个")
    print(f"📊 总数据量: {total_items} 条")
    print(f"🎯 成功率: {success_count/len(platforms)*100:.1f}%")
    print(f"{'='*70}")
    
    await api.close()
    print("\n✅ 测试完成\n")


if __name__ == "__main__":
    asyncio.run(test_all_platforms())
