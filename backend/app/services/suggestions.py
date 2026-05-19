from typing import Any, Dict

from app.services.siliconflow_client import SiliconFlowClient, extract_json_object
from app.services.resume_ocr import truncate_for_llm
from app.services.advanced_features import STYLE_PROMPTS
from app.services.constants import CONTENT_PROCESSING_RULES


def llm_generate_suggestions(
    client: SiliconFlowClient, 
    resume_text: str, 
    sections: Any,
    style_type: str = "",
    target_job: str = ""
) -> Any:
    truncated = truncate_for_llm(resume_text, max_chars=6000)

    if style_type and style_type in STYLE_PROMPTS:
        style_info = STYLE_PROMPTS[style_type]
        system = style_info["system"]
        
        user = f"""目标岗位：{target_job or "未指定"}

简历模块：
{sections}

【重要规则 - 必须严格遵守】
1. 分析每个模块的原始内容，指出存在的问题
2. 给出针对性的优化建议
3. rewrite_example（改写示例）要求：
   - 必须完整包含原始内容中的所有信息点（所有项目、经历、时间线）
   - 在保留全部原始信息的基础上进行表达优化
   - 不得删除、合并或省略任何原始内容中的条目
   - 不得编造新的经历或内容
   - 如果内容很长，优先确保所有条目都被包含，可以适当精简措辞，但不得丢失任何信息
4. 如果原始内容已经很完善，rewrite_example可以留空或写"无需改写"
5. 【关键】items数组中每个对象的name字段必须与输入的模块名称完全一致，不得修改或重命名模块

逐模块给出修改建议（每模块2-3条）。

输出JSON：
{{"overall_summary":"总结","items":[{{"name":"必须与原始模块名称一致","issues":["问题"],"recommendations":["建议"],"rewrite_example":"完整改写后的内容，保留所有原始信息"}}]}}"""
    else:
        system = (
            f"""你是简历优化专家。根据简历内容给出修改建议。
输出必须是 JSON，不要输出任何 JSON 之外的文字。

{CONTENT_PROCESSING_RULES}"""
        )

        user = f"""简历模块：
{sections}

【重要规则 - 必须严格遵守】
1. 分析每个模块的原始内容，指出存在的问题
2. 给出针对性的优化建议
3. rewrite_example（改写示例）要求：
   - 必须完整包含原始内容中的所有信息点（所有项目、经历、时间线）
   - 在保留全部原始信息的基础上进行表达优化
   - 不得删除、合并或省略任何原始内容中的条目
   - 不得编造新的经历或内容
   - 如果内容很长，优先确保所有条目都被包含，可以适当精简措辞，但不得丢失任何信息
4. 【关键】items数组中每个对象的name字段必须与输入的模块名称完全一致，不得修改或重命名模块

逐模块给出修改建议（每模块2-3条）。

输出JSON：
{{"overall_summary":"总结","items":[{{"name":"必须与原始模块名称一致","issues":["问题"],"recommendations":["建议"],"rewrite_example":"完整改写后的内容，保留所有原始信息"}}]}}"""

    content = client.chat(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.2,
        max_tokens=8000,
    )
    return extract_json_object(content)