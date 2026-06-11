from typing import Any, Dict, List, Optional

from app.services.siliconflow_client import SiliconFlowClient, extract_json_object
from app.services.resume_ocr import truncate_for_llm
from app.services.constants import CONTENT_PROCESSING_RULES


JOB_POSITIONS = {
    "tech": {
        "name": "技术研发",
        "icon": "💻",
        "positions": [
            {"id": "frontend", "name": "前端开发工程师", "keywords": ["Vue", "React", "JavaScript", "TypeScript", "CSS", "HTML", "Webpack", "Vite"]},
            {"id": "backend", "name": "后端开发工程师", "keywords": ["Java", "Python", "Go", "Node.js", "MySQL", "Redis", "微服务", "分布式"]},
            {"id": "fullstack", "name": "全栈开发工程师", "keywords": ["全栈", "前后端", "系统架构", "数据库", "API设计"]},
            {"id": "mobile", "name": "移动端开发工程师", "keywords": ["iOS", "Android", "Flutter", "React Native", "小程序"]},
            {"id": "data", "name": "数据开发工程师", "keywords": ["大数据", "Hadoop", "Spark", "Flink", "数据仓库", "ETL"]},
            {"id": "ai", "name": "AI/算法工程师", "keywords": ["机器学习", "深度学习", "NLP", "CV", "PyTorch", "TensorFlow"]},
            {"id": "devops", "name": "DevOps工程师", "keywords": ["Docker", "Kubernetes", "CI/CD", "运维", "自动化", "云原生"]},
            {"id": "qa", "name": "测试开发工程师", "keywords": ["自动化测试", "性能测试", "测试框架", "Selenium", "接口测试"]},
        ]
    },
    "product": {
        "name": "产品运营",
        "icon": "📊",
        "positions": [
            {"id": "pm", "name": "产品经理", "keywords": ["需求分析", "用户研究", "原型设计", "PRD", "数据分析", "竞品分析"]},
            {"id": "po", "name": "产品运营", "keywords": ["用户增长", "活动策划", "内容运营", "社群运营", "数据分析"]},
            {"id": "ux", "name": "UX设计师", "keywords": ["用户体验", "交互设计", "用户研究", "原型", "Figma", "Sketch"]},
            {"id": "ui", "name": "UI设计师", "keywords": ["视觉设计", "界面设计", "设计规范", "Figma", "Adobe"]},
            {"id": "data_analyst", "name": "数据分析师", "keywords": ["SQL", "Python", "数据可视化", "业务分析", "报表", "BI"]},
        ]
    },
    "marketing": {
        "name": "市场营销",
        "icon": "📢",
        "positions": [
            {"id": "marketing", "name": "市场营销", "keywords": ["品牌推广", "市场策划", "渠道管理", "营销活动"]},
            {"id": "brand", "name": "品牌策划", "keywords": ["品牌定位", "品牌传播", "创意策划", "品牌管理"]},
            {"id": "pr", "name": "公关专员", "keywords": ["媒体关系", "危机公关", "活动策划", "新闻稿"]},
            {"id": "content", "name": "内容运营", "keywords": ["文案策划", "新媒体运营", "内容创作", "短视频"]},
        ]
    },
    "sales": {
        "name": "销售商务",
        "icon": "🤝",
        "positions": [
            {"id": "sales", "name": "销售代表", "keywords": ["客户开发", "销售技巧", "商务谈判", "客户关系"]},
            {"id": "bd", "name": "商务拓展(BD)", "keywords": ["合作伙伴", "渠道拓展", "商务谈判", "资源整合"]},
            {"id": "account", "name": "客户成功经理", "keywords": ["客户维护", "续约", "客户满意度", "解决方案"]},
            {"id": "pre_sales", "name": "售前工程师", "keywords": ["方案设计", "技术支持", "客户沟通", "招投标"]},
        ]
    },
    "finance": {
        "name": "金融财务",
        "icon": "💰",
        "positions": [
            {"id": "accountant", "name": "会计/财务", "keywords": ["财务报表", "税务", "成本核算", "审计", "Excel"]},
            {"id": "investment", "name": "投资分析师", "keywords": ["行业研究", "财务分析", "估值模型", "尽职调查"]},
            {"id": "risk", "name": "风控专员", "keywords": ["风险评估", "合规", "信用分析", "风险控制"]},
            {"id": "audit", "name": "审计专员", "keywords": ["内部审计", "财务审计", "合规检查", "风险识别"]},
        ]
    },
    "hr": {
        "name": "人力资源",
        "icon": "👥",
        "positions": [
            {"id": "hr", "name": "HR专员", "keywords": ["招聘", "员工关系", "薪酬福利", "绩效管理"]},
            {"id": "recruiter", "name": "招聘专员", "keywords": ["人才寻访", "面试", "招聘渠道", "人才库"]},
            {"id": "training", "name": "培训专员", "keywords": ["培训体系", "课程开发", "人才发展", "学习平台"]},
            {"id": "hrbp", "name": "HRBP", "keywords": ["业务伙伴", "组织发展", "人才盘点", "绩效改进"]},
        ]
    },
    "admin": {
        "name": "行政职能",
        "icon": "📋",
        "positions": [
            {"id": "admin", "name": "行政专员", "keywords": ["行政管理", "会议组织", "档案管理", "办公协调"]},
            {"id": "assistant", "name": "助理/秘书", "keywords": ["日程管理", "会议纪要", "文件处理", "沟通协调"]},
            {"id": "legal", "name": "法务专员", "keywords": ["合同审核", "法律咨询", "合规管理", "知识产权"]},
        ]
    },
    "supply": {
        "name": "供应链",
        "icon": "🚚",
        "positions": [
            {"id": "procurement", "name": "采购专员", "keywords": ["供应商管理", "采购谈判", "成本控制", "采购流程"]},
            {"id": "logistics", "name": "物流专员", "keywords": ["仓储管理", "配送优化", "物流成本", "供应链"]},
            {"id": "planning", "name": "计划专员", "keywords": ["需求预测", "库存管理", "生产计划", "MRP"]},
        ]
    }
}


def get_job_positions() -> Dict[str, Any]:
    return JOB_POSITIONS


EXPERIENCE_QUESTIONS = [
    {
        "key": "course_projects",
        "question": "大学期间做过哪些课程项目？请描述项目背景、你的角色和最终成果。",
        "hint": "例如：数据库课程设计了一个学生管理系统，负责后端开发...",
        "type": "text",
    },
    {
        "key": "competitions",
        "question": "参加过哪些比赛或竞赛？获得了什么成绩？",
        "hint": "例如：参加互联网+大赛获得省级二等奖，负责产品原型设计...",
        "type": "text",
    },
    {
        "key": "internships",
        "question": "有过实习经历吗？在什么公司、什么岗位？主要做了什么？",
        "hint": "例如：在XX公司实习，担任运营助理，负责社群运营...",
        "type": "text",
    },
    {
        "key": "student_activities",
        "question": "参加过学生组织或社团吗？担任过什么职务？组织过什么活动？",
        "hint": "例如：学生会外联部部长，组织过校园歌手大赛...",
        "type": "text",
    },
    {
        "key": "skills",
        "question": "你掌握哪些技能？（编程语言、工具软件、语言能力等）",
        "hint": "例如：Python、Excel、英语六级...",
        "type": "text",
    },
    {
        "key": "volunteer",
        "question": "有过志愿服务或社会实践经历吗？",
        "hint": "例如：暑期支教、社区志愿服务...",
        "type": "text",
    },
    {
        "key": "certificates",
        "question": "获得过哪些证书或荣誉？",
        "hint": "例如：计算机二级证书、优秀学生干部...",
        "type": "text",
    },
    {
        "key": "hobbies",
        "question": "有什么特长或兴趣爱好？是否取得过相关成就？",
        "hint": "例如：摄影、写作、运动...",
        "type": "text",
    },
]


def get_experience_questions() -> List[Dict[str, str]]:
    return EXPERIENCE_QUESTIONS


def llm_refine_experience(client: SiliconFlowClient, answers: Dict[str, str]) -> Dict[str, Any]:
    answers_text = "\n\n".join(
        f"【{q['question']}】\n{answers.get(q['key'], '未回答')}"
        for q in EXPERIENCE_QUESTIONS
    )

    system = (
        f"""你是一位专业的简历顾问，擅长帮助大学生挖掘和提炼经历。
你的任务是将用户的口语化回答转化为专业的简历内容。
输出必须是 JSON，不要输出任何 JSON 之外的文字。

{CONTENT_PROCESSING_RULES}"""
    )

    user = f"""
用户是一位大学生，正在准备简历。以下是他对一系列问题的回答：

{answers_text}

请根据这些回答，生成以下内容：
1. 提炼出可以写入简历的项目/实习/活动经历（每个经历包含：标题、时间、描述、成果）
2. 提取技能清单
3. 提取证书荣誉清单
4. 给出简历写作建议

输出 JSON 格式：
{{
  "experiences": [
    {{
      "title": "经历标题",
      "type": "项目/实习/活动/竞赛",
      "time": "时间范围（如用户未提供可写'待补充'）",
      "description": "专业化的经历描述（2-4句话，突出职责和成果）",
      "achievements": ["成果1", "成果2"]
    }}
  ],
  "skills": ["技能1", "技能2"],
  "certificates": ["证书1", "证书2"],
  "suggestions": ["建议1", "建议2"]
}}
"""

    content = client.chat(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.3,
        max_tokens=3000,
    )
    return extract_json_object(content)


STYLE_PROMPTS = {
    "campus": {
        "name": "校招版",
        "description": "突出学习能力、竞赛/科研含金量、发展潜力",
        "system": f"""你是一位资深校招面试官，擅长挖掘应届生的潜力与可塑性。你的任务是以校招视角优化简历内容。输出必须是 JSON，不要输出任何 JSON 之外的文字。

{CONTENT_PROCESSING_RULES}""",
        "prompt_template": """请以"挖掘校招候选人潜力与可塑性"为核心，逐模块优化简历。

目标岗位：{target_job}

原始简历模块：
```json
{sections}
```

【重要规则 - 必须严格遵守】
1. 必须保持原始模块名称不变，不得重命名、合并或拆分模块
2. 必须保持所有原始模块，不得删除任何模块
3. 必须保持模块顺序与原始简历一致
4. 如果某个模块内容无需优化，直接保留原文内容，不得省略
5. 只优化内容表达，不改变信息结构和模块划分

对每个模块，请执行以下优化：

1. 模块诊断：指出描述中过于学生思维的地方（如：过分强调上课成绩而忽略实践，或者竞赛经历像流水账，没有突出个人贡献）。

2. 优化与包装建议：指导如何将"学术项目"、"创新创业大赛"或"毕业设计"包装成具有完整商业/技术逻辑的项目。提示如何提炼竞赛中的难点，以及个人在团队中发挥的核心作用（如：统筹协调、技术攻坚）。

3. 黄金重构：提供优化后的改写版本，示范如"作为队长带队参加'挑战杯'，从0到1主导项目方向，攻克具体技术/落地难点，最终在X支队伍中脱颖而出斩获国家级奖项"。

输出 JSON 格式：
{{
  "sections": [
    {{
      "name": "模块名称（必须与原始模块名称完全一致）",
      "content": "优化后的内容"
    }}
  ],
  "style_notes": ["调整说明1", "调整说明2"]
}}""",
    },
    "intern": {
        "name": "实习版",
        "description": "突出执行力、快速上手能力、边缘经验转化",
        "system": f"""你是一位实习招聘专家，擅长帮助零经验同学将边缘经验转化为核心竞争力。输出必须是 JSON，不要输出任何 JSON 之外的文字。

{CONTENT_PROCESSING_RULES}""",
        "prompt_template": """请以"将边缘经验转化为核心竞争力"为核心，逐模块优化简历。找实习的同学通常完全没有相关经验，你需要帮他们转化。

目标岗位：{target_job}

原始简历模块：
```json
{sections}
```

【重要规则 - 必须严格遵守】
1. 必须保持原始模块名称不变，不得重命名、合并或拆分模块
2. 必须保持所有原始模块，不得删除任何模块
3. 必须保持模块顺序与原始简历一致
4. 如果某个模块内容无需优化，直接保留原文内容，不得省略
5. 只优化内容表达，不改变信息结构和模块划分

对每个模块，请执行以下优化：

1. 模块诊断：指出简历中是否充斥着与岗位无关的无效信息（如无关的兼职、过于冗长的兴趣爱好），以及是否缺乏对"执行力"的体现。

2. 经验转化建议：指导如何将学生会工作（如权益部、外联部）或日常兼职，转化为职场所需的"通用软技能"（沟通反馈、抗压、信息搜集）。强调在描述中加入"闭环思维"（即不仅做了，还拿到了什么结果）。

3. 黄金重构：提供优化后的改写版本，示范如"在学生会权益部期间，负责建立X维度的信息收集渠道，系统处理并跟进Y条反馈，将响应解决效率提升了Z%"。

输出 JSON 格式：
{{
  "sections": [
    {{
      "name": "模块名称（必须与原始模块名称完全一致）",
      "content": "优化后的内容"
    }}
  ],
  "style_notes": ["调整说明1", "调整说明2"]
}}""",
    },
    "tech": {
        "name": "技术岗版",
        "description": "突出技术栈深度、系统架构思维、性能优化",
        "system": f"""你是一位资深技术Leader，以严苛的技术视角审查简历。输出必须是 JSON，不要输出任何 JSON 之外的文字。

{CONTENT_PROCESSING_RULES}""",
        "prompt_template": """你是一位资深的技术Leader。请以严苛的技术视角审查并优化该简历。

目标岗位：{target_job}

原始简历模块：
```json
{sections}
```

【重要规则 - 必须严格遵守】
1. 必须保持原始模块名称不变，不得重命名、合并或拆分模块
2. 必须保持所有原始模块，不得删除任何模块
3. 必须保持模块顺序与原始简历一致
4. 如果某个模块内容无需优化，直接保留原文内容，不得省略
5. 只优化内容表达，不改变信息结构和模块划分

对每个模块，请执行以下优化：

1. 模块诊断：严厉指出是否在"堆砌名词"（如把所有知道的框架都写上），缺乏对技术深度的描述。检查是否缺少对"难点解决"和"性能指标"的量化说明。

2. 技术深度挖掘建议：强制要求补充项目的并发量、数据量级或性能优化前后的对比（如首屏加载、查询速度、内存占用）。指导如何描述"为什么选型这个技术"以及"踩了什么坑，如何解决的"。

3. 黄金重构：提供极具极客精神的改写版本，示范如"使用Vue3和Vite独立构建前端工程，针对大数据量列表渲染进行虚拟列表优化，将页面渲染耗时从Xs降至Ys，帧率稳定在Zfps"。

输出 JSON 格式：
{{
  "sections": [
    {{
      "name": "模块名称（必须与原始模块名称完全一致）",
      "content": "优化后的内容"
    }}
  ],
  "style_notes": ["调整说明1", "调整说明2"]
}}""",
    },
    "product": {
        "name": "产品岗版",
        "description": "突出用户同理心、需求拆解、数据驱动决策",
        "system": f"""你是一位拥有千万级日活产品的产品总监，以产品思维审查简历。输出必须是 JSON，不要输出任何 JSON 之外的文字。

{CONTENT_PROCESSING_RULES}""",
        "prompt_template": """你是一位拥有千万级日活产品的产品总监。请以"产品思维"审查并优化该简历。

目标岗位：{target_job}

原始简历模块：
```json
{sections}
```

【重要规则 - 必须严格遵守】
1. 必须保持原始模块名称不变，不得重命名、合并或拆分模块
2. 必须保持所有原始模块，不得删除任何模块
3. 必须保持模块顺序与原始简历一致
4. 如果某个模块内容无需优化，直接保留原文内容，不得省略
5. 只优化内容表达，不改变信息结构和模块划分

对每个模块，请执行以下优化：

1. 模块诊断：指出描述是否变成了"交互设计师"或"项目跟进员"的自白，缺乏对"用户痛点"和"商业价值"的思考。

2. 产品力优化建议：引导候选人补充：发现什么需求→用什么逻辑拆解→上线后数据表现如何。强调补充跨部门协作（与研发、UI、运营的沟通效率）的细节。

3. 黄金重构：提供产品思维改写版本，示范如"通过分析X项用户数据/反馈，挖掘出Y痛点，主导设计了Z功能，上线后次日留存率提升A%，直接带动营收增长B%"。

输出 JSON 格式：
{{
  "sections": [
    {{
      "name": "模块名称（必须与原始模块名称完全一致）",
      "content": "优化后的内容"
    }}
  ],
  "style_notes": ["调整说明1", "调整说明2"]
}}""",
    },
    "operation": {
        "name": "运营岗版",
        "description": "突出转化率、ROI、拉新促活留存指标",
        "system": f"""你是一位运营总监，以ROI导向审查简历。输出必须是 JSON，不要输出任何 JSON 之外的文字。

{CONTENT_PROCESSING_RULES}""",
        "prompt_template": """运营是极其看重结果和数据的岗位。请以"ROI导向"审查并优化该简历。

目标岗位：{target_job}

原始简历模块：
```json
{sections}
```

【重要规则 - 必须严格遵守】
1. 必须保持原始模块名称不变，不得重命名、合并或拆分模块
2. 必须保持所有原始模块，不得删除任何模块
3. 必须保持模块顺序与原始简历一致
4. 如果某个模块内容无需优化，直接保留原文内容，不得省略
5. 只优化内容表达，不改变信息结构和模块划分

对每个模块，请执行以下优化：

1. 模块诊断：批评那些只有"过程（产出了什么）"没有"结果（带来了什么）"的流水账描述。

2. 数据化驱动建议：强制要求候选人回忆并补充核心指标：阅读量、涨粉量、UV/PV、线索转化率（Leads）、转化成本等。建议突出自己对目标人群的洞察以及渠道分发策略。

3. 黄金重构：提供数据化改写版本，示范如"负责社交媒体账号的内容规划与视频剪辑，针对X受众提炼差异化卖点，单月产出Y条破播视频，累计带来Z条高意向线索，转化率达W%"。

输出 JSON 格式：
{{
  "sections": [
    {{
      "name": "模块名称（必须与原始模块名称完全一致）",
      "content": "优化后的内容"
    }}
  ],
  "style_notes": ["调整说明1", "调整说明2"]
}}""",
    },
    "english": {
        "name": "外企英文版",
        "description": "跨文化沟通、Action Verbs、Leadership Principles",
        "system": f"""你是一位Global 500强企业的亚太区HRBP，精通外企简历规范。输出必须是 JSON，不要输出任何 JSON 之外的文字。

{CONTENT_PROCESSING_RULES}""",
        "prompt_template": """你是一位Global 500强企业的亚太区HRBP。外企看重主动性、影响力以及专业的职场表达。请优化该简历。

目标岗位：{target_job}

原始简历模块：
```json
{sections}
```

【重要规则 - 必须严格遵守】
1. 必须保持原始模块名称不变，不得重命名、合并或拆分模块
2. 必须保持所有原始模块，不得删除任何模块
3. 必须保持模块顺序与原始简历一致
4. 如果某个模块内容无需优化，直接保留原文内容，不得省略
5. 只优化内容表达，不改变信息结构和模块划分

对每个模块，请执行以下优化：

1. 模块诊断：指出描述中是否过于"谦逊"或使用被动语态，导致无法突出个人的Leadership和Owner意识。

2. 跨国企业文化对齐建议：建议全面替换弱动词（参与了、做过），改用强有力的行动动词（Spearheaded主导、Optimized优化、Initiated发起、Delivered交付）。提示补充跨部门/跨国团队沟通协作、打破信息壁垒、推动流程标准化（SOP）的经验。

3. 黄金重构：提供具有外企风格的、结构清晰的改写版本（自带强大的气场），示范如"Initiated and spearheaded某项目，跨越X个时区与全球Y个团队协同，建立标准化SOP，使整体沟通成本下降Z%"。

输出 JSON 格式：
{{
  "sections": [
    {{
      "name": "模块名称（必须与原始模块名称完全一致）",
      "content": "优化后的内容（中文，但使用外企风格表达）"
    }}
  ],
  "style_notes": ["调整说明1", "调整说明2"]
}}""",
    },
}


def get_style_types() -> Dict[str, Dict[str, str]]:
    return {
        key: {
            "name": val["name"],
            "description": val["description"],
        }
        for key, val in STYLE_PROMPTS.items()
    }


def llm_transform_style(
    client: SiliconFlowClient,
    sections: Any,
    style_type: str,
    target_job: str = "",
) -> Dict[str, Any]:
    if style_type not in STYLE_PROMPTS:
        raise ValueError(f"未知的风格类型: {style_type}")

    style_info = STYLE_PROMPTS[style_type]

    system = style_info["system"]

    user = style_info["prompt_template"].format(
        target_job=target_job or "未指定",
        sections=sections,
    )

    content = client.chat(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.3,
        max_tokens=4000,
    )
    return extract_json_object(content)


def llm_ats_check(client: SiliconFlowClient, resume_text: str, sections: Any) -> Dict[str, Any]:
    truncated = truncate_for_llm(resume_text, max_chars=10000)

    system = (
        f"""你是一位 ATS（招聘管理系统）优化专家。
你的任务是诊断简历能否顺利通过企业 HR 系统的机器初筛。
输出必须是 JSON，不要输出任何 JSON 之外的文字。

{CONTENT_PROCESSING_RULES}"""
    )

    user = f"""
请对以下简历进行 ATS 友好度检测，评估其能否通过企业 HR 系统的机器初筛。

简历文本：
```text
{truncated}
```

简历模块：
```json
{sections}
```

请检测以下方面：
1. 格式问题（特殊字符、表格、图片等可能导致解析失败的因素）
2. 关键词匹配度（是否包含常见岗位关键词）
3. 结构完整性（是否包含必要模块）
4. 可读性（联系方式、日期格式等是否规范）

输出 JSON 格式：
{{
  "score": 85,
  "issues": [
    "问题1：描述具体问题",
    "问题2：..."
  ],
  "suggestions": [
    "建议1：具体改进建议",
    "建议2：..."
  ],
  "keywords_found": ["关键词1", "关键词2"],
  "keywords_missing": ["建议补充的关键词1", "关键词2"]
}}

评分标准：
- 90-100：ATS 友好度极高，几乎不会因格式问题被筛掉
- 70-89：ATS 友好度良好，有少量可优化项
- 50-69：ATS 友好度一般，存在一些问题需要修复
- 0-49：ATS 友好度较差，很可能被系统误杀
"""

    content = client.chat(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.2,
        max_tokens=2500,
    )
    return extract_json_object(content)


def llm_generate_cover_letter(
    client: SiliconFlowClient,
    sections: Any,
    target_job: str = "",
    company: str = "",
) -> Dict[str, Any]:
    system = (
        f"""你是一位专业的求职信撰写专家，擅长根据简历内容生成个性化的求职信。
输出必须是 JSON，不要输出任何 JSON 之外的文字。

{CONTENT_PROCESSING_RULES}"""
    )

    user = f"""根据以下简历内容，生成求职信和HR沟通话术。

目标岗位：{target_job or "未指定"}
目标公司：{company or "未指定"}

简历模块：
{sections}

请生成：
1. 一封正式的求职信（Cover Letter）
2. 一段简洁的HR邮件正文
3. 一段微信/即时通讯风格的简短自荐

输出JSON：
{{{{
  "cover_letter": "正式求职信全文",
  "email_body": "HR邮件正文",
  "quick_pitch": "简短自荐话术",
  "highlights": ["亮点1", "亮点2", "亮点3"]
}}}}"""

    content = client.chat(
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.4,
        max_tokens=3000,
    )
    return extract_json_object(content)


def llm_resume_assistant(
    client: SiliconFlowClient,
    sections: Any,
    job_position: str,
    job_keywords: List[str],
) -> Dict[str, Any]:
    system = (
        f"""你是一位专业的简历助手，能够根据简历内容回答用户的问题。
你的回答应该专业、准确、有帮助。
输出必须是 JSON，不要输出任何 JSON 之外的文字。

{CONTENT_PROCESSING_RULES}"""
    )

    user = f"""请作为简历助手，帮助用户针对目标岗位优化简历。

目标岗位：{job_position}
岗位关键词：{', '.join(job_keywords)}

用户当前简历模块：
{sections}

请完成以下任务：

1. **岗位匹配分析**：分析用户简历与目标岗位的匹配程度，指出优势和不足

2. **简历优化问题**：生成5-8个针对性的问题，帮助用户补充或完善简历内容
   - 问题要具体，与岗位关键词相关
   - 引导用户思考如何展示与岗位相关的能力和经历

3. **模块优化建议**：针对简历的每个模块，给出具体的优化建议
   - 指出当前描述的问题
   - 提供优化方向
   - 给出改写示例

4. **关键词优化**：建议用户如何在简历中自然融入岗位关键词

输出JSON格式：
{{
  "match_analysis": {{
    "score": 75,
    "strengths": ["优势1", "优势2"],
    "gaps": ["不足1", "不足2"],
    "summary": "整体匹配度分析"
  }},
  "guided_questions": [
    {{
      "id": "q1",
      "question": "具体问题",
      "purpose": "问题目的",
      "hint": "回答提示",
      "related_keyword": "关联的岗位关键词"
    }}
  ],
  "module_suggestions": [
    {{
      "module": "模块名称",
      "current_issue": "当前问题",
      "optimization": "优化建议",
      "example": "改写示例"
    }}
  ],
  "keyword_integration": [
    {{
      "keyword": "关键词",
      "suggestion": "如何在简历中融入该关键词",
      "example": "示例句子"
    }}
  ],
  "quick_tips": ["快速优化建议1", "快速优化建议2", "快速优化建议3"]
}}"""

    content = client.chat(
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.3,
        max_tokens=4000,
    )
    return extract_json_object(content)


def llm_resume_question_answer(
    client: SiliconFlowClient,
    sections: Any,
    question_id: str,
    question: str,
    user_answer: str,
    job_position: str,
) -> Dict[str, Any]:
    system = (
        f"""你是一位专业的简历顾问，帮助用户将回答转化为简历内容。
输出必须是 JSON，不要输出任何 JSON 之外的文字。

{CONTENT_PROCESSING_RULES}"""
    )

    user = f"""用户正在针对"{job_position}"岗位优化简历。

当前简历模块：
{sections}

问题：{question}
用户回答：{user_answer}

请根据用户的回答：
1. 提取可以写入简历的关键信息
2. 将口语化回答转化为专业简历语言
3. 建议应该放在简历的哪个模块
4. 提供改写示例

输出JSON：
{{
  "extracted_info": ["提取的关键信息1", "提取的关键信息2"],
  "suggested_module": "建议放入的模块",
  "rewrite": "专业简历改写",
  "placement_suggestion": "具体放置建议"
}}"""

    content = client.chat(
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.3,
        max_tokens=2000,
    )
    return extract_json_object(content)


def llm_career_recommend(
    client: SiliconFlowClient,
    sections: Any,
    target_job: str = "",
) -> Dict[str, Any]:
    system = (
        f"""你是一位资深职业规划师和猎头顾问，擅长分析人才画像并推荐匹配的职业机会。
输出必须是 JSON，不要输出任何 JSON 之外的文字。

{CONTENT_PROCESSING_RULES}"""
    )

    user = f"""根据以下简历内容，分析用户的能力画像并推荐匹配的职业机会。

目标岗位方向：{target_job or "未指定"}

简历模块：
{sections}

请生成：
1. 能力画像分析
2. 推荐的匹配岗位（3-5个）
3. 能力短板分析
4. 职业发展路径建议

输出JSON：
{{{{
  "profile": {{{{
    "strengths": ["核心优势1", "核心优势2"],
    "skills_summary": "技能概要",
    "experience_level": "经验等级"
  }}}},
  "recommended_jobs": [
    {{{{"title": "岗位名称", "match_score": 90, "reason": "匹配原因", "jd_summary": "岗位JD概要", "salary_range": "薪资范围"}}}}
  ],
  "skill_gaps": [
    {{{{"skill": "缺失技能", "importance": "重要性(高/中/低)", "how_to_improve": "提升建议"}}}}
  ],
  "career_path": {{{{
    "short_term": "1-2年短期目标",
    "mid_term": "3-5年中期目标",
    "long_term": "5年以上长期目标"
  }}}}
}}}}"""

    content = client.chat(
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.4,
        max_tokens=4000,
    )
    return extract_json_object(content)


def llm_career_planning(
    client: SiliconFlowClient,
    sections: Any,
    target_job: str = "",
) -> Dict[str, Any]:
    system = (
        f"""你是一位资深职业发展顾问，擅长提供Offer对比分析、能力短板诊断和长期职涯规划。
输出必须是 JSON，不要输出任何 JSON 之外的文字。

{CONTENT_PROCESSING_RULES}"""
    )

    user = f"""根据以下简历内容，提供深度职涯规划辅导。

目标岗位方向：{target_job or "未指定"}

简历模块：
{sections}

请生成：
1. 当前能力评估
2. 能力短板与提升路径
3. 职业方向建议
4. 长期发展规划

输出JSON：
{{{{
  "current_assessment": {{{{
    "overall_level": "当前综合水平",
    "core_competencies": ["核心能力1", "核心能力2"],
    "areas_for_growth": ["成长空间1", "成长空间2"]
  }}}},
  "skill_development": [
    {{{{"skill": "需提升的技能", "current_level": "当前水平", "target_level": "目标水平", "action_plan": "具体行动计划", "timeline": "预计时间", "resources": ["学习资源1", "学习资源2"]}}}}
  ],
  "career_directions": [
    {{{{"direction": "方向名称", "fit_score": 85, "pros": ["优势1"], "cons": ["挑战1"], "transition_plan": "转型计划概要"}}}}
  ],
  "long_term_plan": {{{{
    "year_1": "第1年目标与行动",
    "year_3": "第3年目标与行动",
    "year_5": "第5年目标与行动",
    "milestones": ["里程碑1", "里程碑2", "里程碑3"]
  }}}}
}}}}"""

    content = client.chat(
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.4,
        max_tokens=4000,
    )
    return extract_json_object(content)
