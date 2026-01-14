"""
mem1 图片功能示例

演示：
- 添加带图片的对话
- 图片自动描述生成
- 图片搜索
- 图片在画像中的记录
"""
from pathlib import Path
from dotenv import load_dotenv

from mem1 import Mem1Memory, Mem1Config
from mem1.prompts import YUQING_PROFILE_TEMPLATE

load_dotenv()

config = Mem1Config.from_env()
config.memory.auto_update_profile = True
config.memory.update_interval_rounds = 2

USER_ID = "image_demo_user"
# 示例图片路径
IMG_MAHUA = Path(__file__).parent / "天价麻花.png"
IMG_CURTAIN = Path(__file__).parent / "智能家电着火-窗帘.png"
IMG_TOILET = Path(__file__).parent / "智能家电着火-马桶.png"
IMG_ROBOT = Path(__file__).parent / "智能家电着火-扫地机器人.png"


def main():
    # 使用舆情行业模板
    memory = Mem1Memory(
        config, 
        user_id=USER_ID,
        profile_template=YUQING_PROFILE_TEMPLATE
    )
    
    print("="*60)
    print("mem1 图片功能演示")
    print("="*60)
    
    # 清空旧数据
    print("\n清空旧数据...")
    memory.delete_user()
    
    # 检查图片是否存在
    images = [IMG_MAHUA, IMG_CURTAIN, IMG_TOILET, IMG_ROBOT]
    for img in images:
        if not img.exists():
            print(f"\n⚠️ 示例图片不存在: {img}")
            return
    
    # 1. 添加天价麻花舆情（单图）
    print("\n" + "="*60)
    print("1. 添加舆情事件（含图片）")
    print("="*60)
    
    memory.add_conversation(
        messages=[
            {"role": "user", "content": "发现一个舆情，广东江门某景区卖天价麻花，一根60元。这是截图。"},
            {"role": "assistant", "content": "收到截图。这是消费维权类舆情，建议关注是否持续发酵。"}
        ],
        images=[{"filename": "天价麻花.png", "path": str(IMG_MAHUA)}],
        metadata={"topic": "舆情发现", "event_type": "消费维权"}
    )
    print("✓ 已添加天价麻花舆情")
    
    # 2. 添加智能家电着火舆情（多图）
    memory.add_conversation(
        messages=[
            {"role": "user", "content": "又发现一个舆情，多地出现智能家电着火事件，涉及智能窗帘、智能马桶、扫地机器人。这是三张现场图。"},
            {"role": "assistant", "content": "收到3张图片。这是产品安全类舆情，涉及多个品类，建议重点关注。"}
        ],
        images=[
            {"filename": "智能家电着火-窗帘.png", "path": str(IMG_CURTAIN)},
            {"filename": "智能家电着火-马桶.png", "path": str(IMG_TOILET)},
            {"filename": "智能家电着火-扫地机器人.png", "path": str(IMG_ROBOT)}
        ],
        metadata={"topic": "舆情发现", "event_type": "产品安全"}
    )
    print("✓ 已添加智能家电着火舆情（3张图）")
    
    # 3. 添加后续跟进对话
    memory.add_conversation(
        messages=[
            {"role": "user", "content": "天价麻花事件：市场监管局介入调查了，商家暂停营业。"},
            {"role": "assistant", "content": "事件进展：监管介入，商家暂停营业。"}
        ],
        metadata={"topic": "舆情跟进", "event": "天价麻花"}
    )
    
    memory.add_conversation(
        messages=[
            {"role": "user", "content": "智能家电着火事件：厂商发布召回公告，涉及3个批次产品。"},
            {"role": "assistant", "content": "已记录召回信息。"}
        ],
        metadata={"topic": "舆情跟进", "event": "智能家电着火"}
    )
    
    # 4. 搜索图片
    print("\n" + "="*60)
    print("2. 搜索图片")
    print("="*60)
    
    # 测试不同关键词的召回
    keywords = ["麻花", "着火", "窗帘", "马桶", "扫地机器人", "智能家电", "江门"]
    for keyword in keywords:
        results = memory.search_images(query=keyword)
        print(f"\n搜索 '{keyword}':")
        if results:
            for img in results:
                print(f"  ✓ {img['original_name']}")
        else:
            print(f"  ✗ 未找到")
    
    # 5. 查看画像中的图片记录
    print("\n" + "="*60)
    print("3. 查看用户画像")
    print("="*60)
    
    ctx = memory.get_context(query="")
    print("\n【用户画像】")
    print(ctx['import_content'])
    
    # 6. 测试图片相关的记忆召回
    print("\n" + "="*60)
    print("4. 测试记忆召回")
    print("="*60)
    
    test_queries = [
        "天价麻花事件的完整经过是什么？",
        "智能家电着火涉及哪些产品？",
        "我之前发过哪些图片？",
        "扫地机器人着火是怎么回事？"
    ]
    
    for query in test_queries:
        print(f"\n❓ {query}")
        
        # 搜索相关图片
        images = memory.search_images(query=query)
        if images:
            print(f"   📷 相关图片:")
            for img in images:
                print(f"      - {img['original_name']}")
        
        # 检查对话召回
        ctx = memory.get_context(query=query)
        recalled = []
        if "天价麻花" in ctx['normal_content']:
            recalled.append("天价麻花")
        if "智能家电" in ctx['normal_content'] or "着火" in ctx['normal_content']:
            recalled.append("智能家电着火")
        
        if recalled:
            print(f"   💬 召回对话: {', '.join(recalled)}")
    
    print("\n✓ 图片功能演示完成！")
    print("\n提示：")
    print("  - 图片会自动生成描述并存储")
    print("  - 可以通过关键词搜索图片")
    print("  - 图片信息会记录在用户画像中")
    print("  - 对话召回时会包含图片相关内容")


if __name__ == "__main__":
    main()
