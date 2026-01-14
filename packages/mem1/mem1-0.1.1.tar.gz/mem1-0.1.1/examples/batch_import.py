"""
批量导入对话数据示例

演示：
- 批量导入历史对话
- 使用自定义时间戳
- 自动画像更新
- 周期性任务和关键数字的批量记录
"""
from datetime import datetime, timedelta
from dotenv import load_dotenv

from mem1 import Mem1Memory, Mem1Config
from mem1.prompts import YUQING_PROFILE_TEMPLATE

load_dotenv()

config = Mem1Config.from_env()
config.memory.auto_update_profile = True  # 自动更新画像
config.memory.update_interval_rounds = 5  # 每 5 轮更新一次

USER_ID = "batch_demo_user"

# 示例数据：模拟一个月的舆情工作对话
SAMPLE_CONVERSATIONS = [
    # 第 1 天：自我介绍
    {
        "messages": [
            {"role": "user", "content": "你好，我是李科，市网信办舆情监测科科长。"},
            {"role": "assistant", "content": "李科您好！很高兴为您服务。"}
        ],
        "metadata": {"topic": "自我介绍"},
        "days_ago": 30
    },
    
    # 第 2 天：工作偏好
    {
        "messages": [
            {"role": "user", "content": "以后报告要简洁，控制在500字以内，多用数据和表格。"},
            {"role": "assistant", "content": "明白，报告风格：简洁、数据化、表格呈现。"}
        ],
        "metadata": {"topic": "偏好设置"},
        "days_ago": 29
    },
    
    # 第 3 天：周期性任务
    {
        "messages": [
            {"role": "user", "content": "每周一上午要交周报，每周五下午要做下周工作计划。"},
            {"role": "assistant", "content": "已记录：周一交周报，周五做计划。"}
        ],
        "metadata": {"topic": "工作习惯"},
        "days_ago": 28
    },
    
    # 第 7 天：第一周数据
    {
        "messages": [
            {"role": "user", "content": "本周处理舆情23起，其中重大舆情2起，一般舆情21起。"},
            {"role": "assistant", "content": "第一周数据已记录：23起（重大2起，一般21起）。"}
        ],
        "metadata": {"topic": "周报", "week": 1},
        "days_ago": 24
    },
    
    # 第 14 天：第二周数据
    {
        "messages": [
            {"role": "user", "content": "第二周：处理舆情31起，重大5起，一般26起。这周比较忙。"},
            {"role": "assistant", "content": "第二周数据：31起（重大5起，一般26起）。"}
        ],
        "metadata": {"topic": "周报", "week": 2},
        "days_ago": 17
    },
    
    # 第 15 天：应急事件
    {
        "messages": [
            {"role": "user", "content": "紧急！发现网络谣言：'本市自来水污染'，微博@本地爆料王发布，已有5000+转发。"},
            {"role": "assistant", "content": "收到紧急情况。谣言源头：@本地爆料王，转发5000+。建议立即启动应急响应。"}
        ],
        "metadata": {"topic": "应急处置", "priority": "urgent"},
        "days_ago": 16
    },
    
    # 第 16 天：应急处置结果
    {
        "messages": [
            {"role": "user", "content": "谣言已处置：水务局发布声明，谣言账号被禁言7天，辟谣阅读量12万。"},
            {"role": "assistant", "content": "处置完成。官方声明已发，账号禁言7天，辟谣阅读12万。"}
        ],
        "metadata": {"topic": "应急处置", "status": "resolved"},
        "days_ago": 15
    },
    
    # 第 21 天：第三周数据
    {
        "messages": [
            {"role": "user", "content": "第三周：舆情18起，重大1起，一般17起。另外处理投诉45件。"},
            {"role": "assistant", "content": "第三周：18起（重大1起，一般17起），投诉45件。"}
        ],
        "metadata": {"topic": "周报", "week": 3},
        "days_ago": 10
    },
    
    # 第 28 天：第四周数据
    {
        "messages": [
            {"role": "user", "content": "第四周：舆情25起，重大3起，一般22起。投诉38件。"},
            {"role": "assistant", "content": "第四周：25起（重大3起，一般22起），投诉38件。"}
        ],
        "metadata": {"topic": "周报", "week": 4},
        "days_ago": 3
    },
    
    # 第 30 天：月度总结
    {
        "messages": [
            {"role": "user", "content": "帮我汇总本月数据：舆情总数、重大舆情数、哪周最忙？"},
            {"role": "assistant", "content": "本月汇总：舆情97起（23+31+18+25），重大11起（2+5+1+3），第二周最忙（31起）。投诉83件。"}
        ],
        "metadata": {"topic": "月度总结"},
        "days_ago": 1
    },
]


def main():
    # 使用舆情行业模板
    memory = Mem1Memory(
        config, 
        user_id=USER_ID,
        profile_template=YUQING_PROFILE_TEMPLATE
    )
    
    # 清空旧数据
    print("="*60)
    print("批量导入对话数据")
    print("="*60)
    print("\n清空旧数据...")
    memory.delete_user()
    
    # 批量导入
    print("\n开始批量导入...")
    base_time = datetime.now()
    
    for i, conv in enumerate(SAMPLE_CONVERSATIONS, 1):
        # 计算时间戳
        fake_time = base_time - timedelta(days=conv['days_ago'])
        ts = fake_time.strftime('%Y-%m-%d %H:%M:%S')
        
        memory.add_conversation(
            messages=conv['messages'],
            metadata=conv['metadata'],
            timestamp=ts
        )
        
        topic = conv['metadata'].get('topic', '未知')
        print(f"  [{i:2d}/{len(SAMPLE_CONVERSATIONS)}] {topic:12s} ({conv['days_ago']:2d}天前)")
    
    print(f"\n✓ 已导入 {len(SAMPLE_CONVERSATIONS)} 条对话")
    
    # 手动触发画像更新（确保最终状态）
    print("\n更新用户画像...")
    memory.update_profile()
    
    # 验证结果
    print("\n" + "="*60)
    print("验证导入结果")
    print("="*60)
    
    # 1. 查看画像
    ctx = memory.get_context(query="")
    print("\n【用户画像】")
    print(ctx['import_content'])
    
    # 2. 测试记忆召回
    print("\n" + "="*60)
    print("测试记忆召回")
    print("="*60)
    
    test_queries = [
        "我的工作习惯是什么？",
        "本月处理了多少舆情？",
        "那个自来水谣言事件怎么处理的？"
    ]
    
    for query in test_queries:
        print(f"\n❓ {query}")
        ctx = memory.get_context(query=query, days_limit=31)
        
        # 统计召回的对话数
        conv_count = len([line for line in ctx['normal_content'].split('\n') if line.startswith('---')])
        print(f"   召回 {conv_count} 条相关对话")
    
    print("\n✓ 批量导入完成！")


if __name__ == "__main__":
    main()
