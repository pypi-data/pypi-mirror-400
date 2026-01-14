"""
mem1 + LangChain 集成示例

演示三层记忆架构：
- Tier 1 (短期): LangChain 管理的当前会话
- Tier 2 (画像): mem1 用户画像，注入 system prompt
- Tier 3 (长期): ES 存储的历史对话

最新功能：
- 使用自定义画像模板
- 周期性任务和关键数字记忆
- 时间范围控制
"""
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory

from mem1 import Mem1Memory, Mem1Config
from mem1.prompts import YUQING_PROFILE_TEMPLATE

load_dotenv()

config = Mem1Config.from_env()
config.memory.auto_update_profile = True
config.memory.update_interval_rounds = 3

USER_ID = "langchain_demo_user"


def demo_manual_integration():
    """方式1: 手动集成（更灵活，推荐）"""
    print("\n" + "="*60)
    print("方式1: 手动集成 mem1 到 LangChain")
    print("="*60)
    
    # 使用舆情行业模板，指定话题
    memory = Mem1Memory(
        config, 
        user_id=USER_ID,
        topic_id="yuqing_daily",  # 日常舆情话题
        profile_template=YUQING_PROFILE_TEMPLATE
    )
    
    print("\n清空旧数据...")
    memory.delete_user()
    
    # 先添加一些背景对话
    print("添加背景对话...")
    memory.add_conversation(
        messages=[
            {"role": "user", "content": "我是李科，市网信办舆情监测科，每周一要交周报。"},
            {"role": "assistant", "content": "李科您好！已记录：周一交周报。"}
        ]
    )
    
    memory.add_conversation(
        messages=[
            {"role": "user", "content": "报告要简洁，控制在500字以内，多用数据。"},
            {"role": "assistant", "content": "明白，报告风格：简洁、数据化。"}
        ]
    )
    
    memory.add_conversation(
        messages=[
            {"role": "user", "content": "本月处理了97起舆情，重大舆情11起。"},
            {"role": "assistant", "content": "本月数据已记录：97起（重大11起）。"}
        ]
    )
    
    # 获取用户画像 (Tier 2)
    ctx = memory.get_context(query="帮我写报告", days_limit=7)
    
    # 构建 system prompt
    system_prompt = f"""你是网信办舆情监测助手。

## 用户画像
{ctx['import_content']}

## 最近对话
{ctx['normal_content'] if ctx['normal_content'] else '（无历史对话）'}

## 当前时间
{ctx['current_time']}

请根据用户画像中的偏好和习惯来回答问题。
"""
    
    # LangChain LLM（使用 mem1 配置）
    llm = ChatOpenAI(
        model=config.llm.model,
        api_key=config.llm.api_key,
        base_url=config.llm.base_url
    )
    
    # Tier 1: 当前会话
    messages = [SystemMessage(content=system_prompt)]
    conversation_to_save = []
    
    # 多轮对话
    user_inputs = [
        "你好，还记得我吗？",
        "帮我写个本月舆情数据的简报"
    ]
    
    for user_input in user_inputs:
        print(f"\n👤 用户: {user_input}")
        messages.append(HumanMessage(content=user_input))
        
        response = llm.invoke(messages)
        print(f"🤖 助手: {response.content[:200]}...")
        
        messages.append(response)
        conversation_to_save.append({"role": "user", "content": user_input})
        conversation_to_save.append({"role": "assistant", "content": response.content})
    
    # 保存到 Tier 3
    memory.add_conversation(
        messages=conversation_to_save,
        metadata={"session": "manual_demo", "type": "langchain"}
    )
    print("\n✓ 会话已保存到 ES")


def demo_chain_integration():
    """方式2: 使用 LangChain Chain"""
    print("\n" + "="*60)
    print("方式2: LangChain Chain + mem1")
    print("="*60)
    
    memory = Mem1Memory(
        config, 
        user_id=USER_ID + "_chain",
        topic_id="weekly_plan",  # 周计划话题
        profile_template=YUQING_PROFILE_TEMPLATE
    )
    memory.delete_user()
    
    # 添加背景
    memory.add_conversation(
        messages=[
            {"role": "user", "content": "我是王科长，每周五要做下周计划。"},
            {"role": "assistant", "content": "王科长您好！已记录：周五做计划。"}
        ]
    )
    
    ctx = memory.get_context(query="", days_limit=7)
    
    llm = ChatOpenAI(
        model=config.llm.model,
        api_key=config.llm.api_key,
        base_url=config.llm.base_url
    )
    
    # Tier 1: LangChain 短期记忆
    chat_history = InMemoryChatMessageHistory()
    
    # 注入 Tier 2 画像
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""你是网信办舆情监测助手。

## 用户画像
{ctx['import_content']}

## 当前时间
{ctx['current_time']}
"""),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])
    
    chain = prompt | llm
    
    # 对话
    queries = [
        "你好",
        "我的工作习惯是什么？"
    ]
    
    for query in queries:
        print(f"\n👤 用户: {query}")
        
        result = chain.invoke({"input": query, "history": chat_history.messages})
        print(f"🤖 助手: {result.content[:200]}...")
        
        # 更新短期记忆
        chat_history.add_user_message(query)
        chat_history.add_ai_message(result.content)
        
        # 保存到 Tier 3
        memory.add_conversation(
            messages=[
                {"role": "user", "content": query},
                {"role": "assistant", "content": result.content}
            ],
            metadata={"session": "chain_demo", "type": "langchain"}
        )
    
    print("\n✓ 会话已保存到 ES")


def demo_with_image():
    """方式3: 带图片的集成 - 演示图片记忆召回"""
    print("\n" + "="*60)
    print("方式3: 带图片的 LangChain 集成")
    print("="*60)
    
    from pathlib import Path
    
    memory = Mem1Memory(
        config,
        user_id=USER_ID + "_image",
        topic_id="yuqing_events",  # 舆情事件话题
        profile_template=YUQING_PROFILE_TEMPLATE
    )
    memory.delete_user()
    
    # 检查图片
    sample_image = Path(__file__).parent / "天价麻花.png"
    if not sample_image.exists():
        print("⚠️ 示例图片不存在，跳过图片演示")
        return
    
    # 1. 添加带图片的对话（模拟用户上传截图）
    print("\n1. 添加带图片的舆情对话...")
    memory.add_conversation(
        messages=[
            {"role": "user", "content": "发现一个舆情，广东江门景区天价麻花，60元一根，这是截图。"},
            {"role": "assistant", "content": "收到截图。这是消费维权类舆情，建议关注后续发展。"}
        ],
        images=[{"filename": "天价麻花.png", "path": str(sample_image)}],
        metadata={"event": "天价麻花", "type": "舆情发现"}
    )
    
    # 2. 添加后续对话
    memory.add_conversation(
        messages=[
            {"role": "user", "content": "市场监管局介入调查了，商家暂停营业。"},
            {"role": "assistant", "content": "事件进展已记录：监管介入，商家暂停。"}
        ],
        metadata={"event": "天价麻花", "type": "舆情跟进"}
    )
    
    memory.add_conversation(
        messages=[
            {"role": "user", "content": "调查结果出来了：不构成价格欺诈，但存在服务态度问题。"},
            {"role": "assistant", "content": "调查结论已记录。"}
        ],
        metadata={"event": "天价麻花", "type": "舆情结论"}
    )
    print("✓ 已添加 3 条对话（含 1 张图片）")
    
    # 3. 用户提问关于图片的问题
    print("\n2. 用户提问关于图片...")
    
    llm = ChatOpenAI(
        model=config.llm.model,
        api_key=config.llm.api_key,
        base_url=config.llm.base_url
    )
    
    # 获取上下文
    ctx = memory.get_context(query="天价麻花", days_limit=7)
    
    # 搜索相关图片
    images = memory.search_images(query="麻花 天价 江门")
    image_info = ""
    if images:
        image_info = "\n## 相关图片\n"
        for img in images:
            image_info += f"- {img['filename']}: {img['description']}\n"
    
    system_prompt = f"""你是网信办舆情监测助手。

## 用户画像
{ctx['import_content']}

## 最近对话
{ctx['normal_content']}
{image_info}
## 当前时间
{ctx['current_time']}

请根据对话记录和图片信息回答用户问题。
"""
    
    # 用户提问
    user_questions = [
        "之前那个天价麻花的截图还在吗？是什么内容？",
        "这个事件最后怎么处理的？"
    ]
    
    messages = [SystemMessage(content=system_prompt)]
    
    for question in user_questions:
        print(f"\n👤 用户: {question}")
        messages.append(HumanMessage(content=question))
        
        response = llm.invoke(messages)
        print(f"🤖 助手: {response.content[:300]}...")
        
        messages.append(response)
    
    print("\n✓ 图片记忆召回演示完成")


def demo_progressive_retrieval():
    """方式4: 渐进式检索 - 省 token 的智能检索"""
    print("\n" + "="*60)
    print("方式4: 渐进式检索（先查近期，不够再扩展）")
    print("="*60)
    
    memory = Mem1Memory(
        config,
        user_id=USER_ID + "_progressive",
        topic_id="daily_work",
        profile_template=YUQING_PROFILE_TEMPLATE
    )
    memory.delete_user()
    
    # 添加一些对话
    print("\n添加测试对话...")
    memory.add_conversation(messages=[
        {"role": "user", "content": "今天处理了3起舆情。"},
        {"role": "assistant", "content": "已记录。"}
    ])
    
    llm = ChatOpenAI(
        model=config.llm.model,
        api_key=config.llm.api_key,
        base_url=config.llm.base_url
    )
    
    # 使用渐进式检索
    user_question = "今天处理了多少舆情？"
    print(f"\n👤 用户: {user_question}")
    
    ctx = memory.get_context_progressive(
        query=user_question,
        max_days=31,
        step=7
    )
    
    print(f"📖 实际检索了 {ctx.get('searched_days', '?')} 天，{ctx['conversations_count']} 条对话")
    
    system_prompt = f"""你是舆情助手。

## 用户画像
{ctx['import_content']}

## 对话记录
{ctx['normal_content']}

## 当前时间
{ctx['current_time']}
"""
    
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_question)]
    response = llm.invoke(messages)
    print(f"🤖 助手: {response.content}")
    
    print("\n✓ 渐进式检索演示完成")


def demo_remote_memory_search():
    """方式5: 远期记忆检索 - 作为 Tool 供 LLM 调用"""
    print("\n" + "="*60)
    print("方式5: 远期记忆检索（search_conversations 作为 Tool）")
    print("="*60)
    
    from langchain.tools import tool
    
    memory = Mem1Memory(
        config,
        user_id=USER_ID + "_remote",
        topic_id="history_events",
        profile_template=YUQING_PROFILE_TEMPLATE
    )
    memory.delete_user()
    
    # 模拟添加"半年前"的对话（实际是今天，演示用）
    print("\n添加测试对话（模拟历史数据）...")
    memory.add_conversation(messages=[
        {"role": "user", "content": "去年双十一期间处理了156起消费投诉舆情。"},
        {"role": "assistant", "content": "已记录双十一数据。"}
    ])
    
    # 定义 Tool
    @tool
    def search_memory(start_days: int, end_days: int) -> str:
        """搜索用户历史对话记录。
        
        Args:
            start_days: 起始天数（距今多少天，较近的一端）
            end_days: 结束天数（距今多少天，较远的一端）
        
        示例:
            search_memory(0, 7) - 搜索最近7天
            search_memory(170, 180) - 搜索约半年前的记录
        """
        convs = memory.search_conversations(start_days=start_days, end_days=end_days)
        if not convs:
            return "该时间段无对话记录"
        return memory._format_conversations_for_llm(convs)
    
    print("\n已定义 search_memory Tool，可供 LLM 调用")
    print(f"Tool 描述: {search_memory.description}")
    
    # 演示直接调用
    print("\n直接调用示例:")
    print("  search_memory(0, 7) = 最近7天的对话")
    result = search_memory.invoke({"start_days": 0, "end_days": 7})
    print(f"  结果: {result[:100]}..." if len(result) > 100 else f"  结果: {result}")
    
    print("\n✓ 远期记忆检索演示完成")
    print("\n提示: 实际使用时，将 search_memory 绑定到 LLM，让 LLM 根据用户问题自动调用")


if __name__ == "__main__":
    demo_manual_integration()
    # demo_chain_integration()
    # demo_with_image()
    # demo_progressive_retrieval()
    # demo_remote_memory_search()
