import os
import base64
import asyncio
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor

import atexit

import fitz  # PyMuPDF

from app.services.siliconflow_client import SiliconFlowClient, extract_json_object
from app.services.constants import CONTENT_PROCESSING_RULES

_executor = ThreadPoolExecutor(max_workers=4)
atexit.register(_executor.shutdown, wait=False)


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    parts: List[str] = []
    for page in doc:
        parts.append(page.get_text("text") or "")
    text = "\n".join(parts).strip()
    return text


def extract_images_from_pdf_bytes(pdf_bytes: bytes, max_images: int = 3) -> List[str]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    
    for page_num, page in enumerate(doc):
        image_list = page.get_images(full=True)
        
        for img_index, img_info in enumerate(image_list):
            try:
                xref = img_info[0]
                base_image = doc.extract_image(xref)
                
                if base_image:
                    image_bytes = base_image["image"]
                    image_ext = base_image.get("ext", "png")
                    
                    if len(image_bytes) < 1000:
                        continue
                    
                    b64_image = base64.b64encode(image_bytes).decode('utf-8')
                    mime_type = f"image/{image_ext}" if image_ext in ['png', 'jpeg', 'jpg', 'gif'] else "image/png"
                    data_url = f"data:{mime_type};base64,{b64_image}"
                    images.append(data_url)
                    
            except Exception as e:
                print(f"Error extracting image {img_index} from page {page_num}: {e}")
                continue
    
    images.sort(key=lambda x: len(x), reverse=True)
    
    return images[:max_images]


async def extract_text_async(pdf_bytes: bytes) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, extract_text_from_pdf_bytes, pdf_bytes)


async def extract_images_async(pdf_bytes: bytes, max_images: int = 3) -> List[str]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, extract_images_from_pdf_bytes, pdf_bytes, max_images)


def truncate_for_llm(text: str, max_chars: int = 8000) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    head = text[: int(max_chars * 0.75)]
    tail = text[-int(max_chars * 0.25) :]
    return head + "\n...\n" + tail


def llm_extract_sections(client: SiliconFlowClient, resume_text: str) -> Any:
    truncated = truncate_for_llm(resume_text, max_chars=8000)

    system = (
        "你是资深招聘官与简历编辑。"
        "你的任务是从简历文本中识别出主要模块，并返回结构化 JSON。"
        "不要输出任何与 JSON 无关的文字。"
        f"\n\n{CONTENT_PROCESSING_RULES}"
    )
    user = f"""
请读取下面的简历文本，并识别模块（尽量覆盖但不强行杜撰）：
1) 基本信息（姓名/联系方式/求职意向/教育背景概览）
2) 教育背景
3) 实习经历（含项目型实习）
4) 项目经历（含个人/团队项目）
5) 技能栈/技术能力
6) 校园经历/社团活动/学生组织（含学生会、社团、校内活动等经历）
7) 证书/获奖/荣誉（含竞赛获奖、奖学金、资格证书等）
8) 自我评价/个人总结/其他（如有）

重要规则：
- 请完整保留每个模块的原始内容，不得省略或截断
- 校园经历和获奖荣誉可以分开识别，也可以合并为一个模块

输出 JSON，格式如下：
{{
  "sections": [
    {{
      "name": "模块名称（中文，尽量用上面给的类别）",
      "content": "该模块对应的原文内容摘录/摘要"
    }}
  ],
  "notes": "简短说明：识别过程中遇到的缺失/不确定点"
}}

简历文本如下（可能包含噪声/排版）：
```text
{truncated}
```"""

    content = client.chat(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.1,
        max_tokens=3000,
    )
    parsed = extract_json_object(content)
    if isinstance(parsed, dict) and isinstance(parsed.get("sections"), list):
        return parsed["sections"]
    return parsed

