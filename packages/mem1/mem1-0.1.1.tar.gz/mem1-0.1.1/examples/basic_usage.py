"""
mem1 基础用法示例

演示最新功能：
- 使用自定义画像模板（ProfileTemplate）
- 周期性任务记忆
- 关键数字保留（加粗标记）
- 时间范围控制（days_limit）
- 自动画像更新
"""
from dotenv import load_dotenv

from mem1 import Mem1Memory, Mem1Config
from mem1.prompts import ProfileTemplate, YUQING_PROFILE_TEMPLATE

load_dotenv()

# 从环境变量加载配置
config = Mem1Config.from_env()
config.memory.auto_update_profile = True  # 自动更新画像
config.memory.update_interval_rounds = 3  # 每 3 轮对话更新一次

USER_ID = "demo_user"


def demo_default_template():
    """演示 1：使用默认模板"""
    print("\n" + "="*60)
    print("演示 1：默认模板 - 通用场景")
    print("="*60)
    
    memory = Mem1Memory(config, user_id=USER_ID)
    memory.delete_user()
    
    # 添加包含周期性任务和关键数字的对话
    memory.add_conversation(
        messages=[
            {"role": "user", "content": "你好，我是张明，在北京市网信办工作。"},
            {"role": "assistant", "content": "张明您好！很高兴认识您。"}
        ]
    )
    
    memory.add_conversation(
        messages=[
            {"role": "user", "content": "每周一上午要交周报，每周五下午要做下周计划。"},
            {"role": "assistant", "content": "已记录您的工作节奏：周一交周报，周五做计划。"}
        ]
    )
    
    memory.add_conversation(
        messages=[
            {"role": "user", "content": "本月处理了97起舆情，其中重大舆情11起，投诉83件。"},
            {"role": "assistant", "content": "已记录本月数据：97起舆情（重大11起），83件投诉。"}
        ]
    )
    
    # 获取上下文（查看画像）
    ctx = memory.get_context(query="")
    print("\n【用户画像】")
    print(ctx['import_content'])
    print("\n✓ 注意：周期性任务和关键数字（加粗）已被记录")


def demo_yuqing_template():
    """演示 2：使用舆情行业模板"""
    print("\n" + "="*60)
    print("演示 2：舆情行业模板 - 专业场景")
    print("="*60)
    
    # 使用舆情行业模板
    memory = Mem1Memory(
        config, 
        user_id=USER_ID + "_yuqing",
        profile_template=YUQING_PROFILE_TEMPLATE
    )
    memory.delete_user()
    
    # 添加舆情相关对话
    memory.add_conversation(
        messages=[
            {"role": "user", "content": "我是李科，市网信办舆情监测科，负责网络舆情监测和应急处置。"},
            {"role": "assistant", "content": "李科您好！了解您的职责范围。"}
        ]
    )
    
    memory.add_conversation(
        messages=[
            {"role": "user", "content": "报告要简洁，控制在500字以内，多用数据和表格。"},
            {"role": "assistant", "content": "明白，报告风格：简洁、数据化、表格呈现。"}
        ]
    )
    
    memory.add_conversation(
        messages=[
            {"role": "user", "content": "清朗行动第一周：排查平台12家，发现问题账号156个，处置89个，永久封禁23个。"},
            {"role": "assistant", "content": "第一周数据已记录：12家平台，156个问题账号，处置89个（永久封禁23个）。"}
        ]
    )
    
    ctx = memory.get_context(query="")
    print("\n【舆情行业用户画像】")
    print(ctx['import_content'])
    print("\n✓ 注意：使用了专业的舆情行业画像结构")


def demo_custom_template():
    """演示 3：自定义画像模板"""
    print("\n" + "="*60)
    print("演示 3：自定义模板 - 客服场景")
    print("="*60)
    
    # 自定义客服模板
    custom_template = ProfileTemplate(
        description="客服人员画像",
        sections="""## 基本信息
- 姓名/工号：
- 部门/岗位：

## 服务偏好
- 响应速度要求：
- 沟通风格：

## 周期性任务
（固定工作安排，格式：[周期] 任务）

## 关键数据
（重要指标，用加粗标记）

## 待办事项
（未完成的客户请求）"""
    )
    
    memory = Mem1Memory(
        config,
        user_id=USER_ID + "_custom",
        profile_template=custom_template
    )
    memory.delete_user()
    
    memory.add_conversation(
        messages=[
            {"role": "user", "content": "我是客服小王，工号CS001，负责售后咨询。"},
            {"role": "assistant", "content": "小王您好！"}
        ]
    )
    
    memory.add_conversation(
        messages=[
            {"role": "user", "content": "每天早上9点要查看待处理工单，下午5点前要完成当日回复。"},
            {"role": "assistant", "content": "已记录您的工作时间安排。"}
        ]
    )
    
    ctx = memory.get_context(query="")
    print("\n【自定义客服画像】")
    print(ctx['import_content'])
    print("\n✓ 注意：使用了自定义的画像结构")


def demo_days_limit():
    """演示 4：时间范围控制"""
    print("\n" + "="*60)
    print("演示 4：时间范围控制 - days_limit 参数")
    print("="*60)
    
    memory = Mem1Memory(config, user_id=USER_ID + "_days")
    memory.delete_user()
    
    # 添加对话
    for i in range(3):
        memory.add_conversation(
            messages=[
                {"role": "user", "content": f"这是第 {i+1} 条对话"},
                {"role": "assistant", "content": f"收到第 {i+1} 条"}
            ]
        )
    
    # 获取最近 7 天的上下文
    ctx_7days = memory.get_context(query="", days_limit=7)
    print(f"\n最近 7 天对话数：{len(ctx_7days['normal_content'].split('---')) - 1}")
    
    # 获取最近 1 天的上下文
    ctx_1day = memory.get_context(query="", days_limit=1)
    print(f"最近 1 天对话数：{len(ctx_1day['normal_content'].split('---')) - 1}")
    
    print("\n✓ 可以通过 days_limit 控制召回的时间范围")


if __name__ == "__main__":
    demo_default_template()
    demo_yuqing_template()
    demo_custom_template()
    demo_days_limit()
