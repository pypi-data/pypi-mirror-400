"""
AI 客户端模块

调用 AI Chat Completions API 生成文本。
"""

from __future__ import annotations

from typing import Any

import httpx

from esn_tool.utils.config import get_config_value

# API 端点路径
CHAT_COMPLETIONS_PATH = "/chat/completions"

# 默认超时时间
DEFAULT_TIMEOUT = 120


class AIClient:
    """AI 客户端"""
    
    def __init__(self, model: str | None = None):
        """
        初始化 AI 客户端。
        
        配置从 esntool config 获取。
        
        Args:
            model: 模型名称，覆盖配置文件中的模型
        """
        # 从配置文件获取
        self.api_key = get_config_value("ai.api_key")
        self.base_url = get_config_value("ai.base_url")
        self.model = model or get_config_value("ai.model")
        self.timeout = DEFAULT_TIMEOUT
        
        # 验证必要配置
        if not self.api_key:
            raise ValueError(
                "未配置 API Key。请运行 'esntool config' 进行配置。"
            )
        
        if not self.base_url:
            raise ValueError(
                "未配置 Base URL。请运行 'esntool config' 进行配置。"
            )
        
        if not self.model:
            raise ValueError(
                "未配置 Model。请运行 'esntool config' 进行配置。"
            )
        
        # 确保 base_url 不以 / 结尾
        self.base_url = self.base_url.rstrip("/")
    
    def chat(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """
        发送聊天请求并获取回复。
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大生成 token 数
            
        Returns:
            AI 生成的文本
        """
        messages: list[dict[str, str]] = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "enable_thinking": False,  # 禁用深度思考
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        # 拼接完整的 API URL
        url = f"{self.base_url}{CHAT_COMPLETIONS_PATH}"
        
        with httpx.Client(timeout=self.timeout) as client:
            try:
                response = client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except httpx.HTTPStatusError as e:
                # 尝试获取响应体中的错误信息
                try:
                    error_detail = e.response.json()
                    error_msg = error_detail.get("error", {}).get("message", str(e))
                except Exception:
                    error_msg = e.response.text or str(e)
                raise Exception(f"API 请求失败 ({e.response.status_code}): {error_msg}")
            except httpx.TimeoutException:
                raise Exception(f"请求超时 (超过 {self.timeout} 秒)")
            except Exception as e:
                raise Exception(f"请求异常: {e}")


# Git 提交信息生成的系统提示词
COMMIT_MESSAGE_SYSTEM_PROMPT = """
# Role: Senior Git Commit message Generator

## Profile
As a Git expert, you analyze `git diff` outputs and generate highly professional commit messages following the Conventional Commits 1.0.0 specification. You excel at synthesizing technical changes into concise, human-readable summaries.

## Constraints & Rules
1. **Core Format**: `<type>(<scope>): <subject>` followed by a `<body>` if necessary.
2. **Type Vocabulary**:
   - `feat`: A new feature
   - `fix`: A bug fix
   - `docs`: Documentation only changes
   - `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc)
   - `refactor`: A code change that neither fixes a bug nor adds a feature
   - `perf`: A code change that improves performance
   - `test`: Adding missing tests or correcting existing tests
   - `chore`: Changes to the build process or auxiliary tools and libraries
3. **Language Policy**: 
   - **The `<subject>` and `<body>` MUST be written in Chinese.**
   - The `<type>` and `<scope>` must remain in English as per the convention.
4. **Subject Line**: 
   - Use Chinese.
   - Keep it concise (under 50 characters).
   - Use the imperative mood (e.g., "修复" instead of "修复了").
5. **Body Section**:
   - Required if the diff contains multiple logic changes or exceeds 20 lines of modification.
   - Use a hyphenated list in Chinese to explain "why" and "what" changed.
6. **Scope**: Identify the affected module/component based on the file paths (e.g., `auth`, `parser`, `ui`). Omit brackets if the scope is global or unclear.
7. **Pure Output**: Output the commit message ONLY. No conversational filler, no markdown block wrappers (unless specified by the user), and no explanations.

## Workflow
1. Scan the `git diff` to identify the primary intent of the change.
2. Select the most appropriate `type`.
3. Determine the `scope` from the file paths.
4. Compose a clear `subject` in **Chinese**.
5. If the change is complex, draft a `body` in **Chinese** listing the details.

## Output Example
feat(auth): 新增用户登录验证逻辑

- 增加 JWT 解析中间件
- 优化了过期 Token 的错误处理机制

## Input:
"""


def generate_commit_message(diff_content: str, client: AIClient | None = None) -> str:
    """
    根据 diff 内容生成提交信息。
    
    Args:
        diff_content: git diff 输出内容
        client: AI 客户端实例，如果为 None 则创建新实例
        
    Returns:
        生成的提交信息
    """
    if client is None:
        client = AIClient()
    
    prompt = f"\n\n```diff\n{diff_content}\n```"
    
    return client.chat(
        prompt=prompt,
        system_prompt=COMMIT_MESSAGE_SYSTEM_PROMPT,
        temperature=0.3,  # 较低的温度使输出更稳定
        max_tokens=1024,
    )


# 代码审查的系统提示词
CODE_REVIEW_SYSTEM_PROMPT = """
# Role: Efficient Code Reviewer

## Profile:
You are an expert developer focusing on code quality and correctness. Your reviews are direct, efficient, and visual.

## Task:
Review the provided `git diff`. For each issue, provide a brief description and show the code comparison.

## Rules:
1.  **Language**: Output in **Chinese (中文)**.
2.  **Descriptive Style**: Keep explanations concise (1-2 sentences maximum).
3.  **Code Visuality**: You MUST show the problematic code and the suggested fix.
4.  **Categories**: `[逻辑]`, `[性能]`, `[安全]`, `[规范]`.

## Output Format:

## [Tag] (Brief Description of the Issue)
- ❌ **原代码**: `(Quote the specific bad code snippet)`

- ✅ **建议**: `(Show the fixed code or brief solution)`

*(Repeat this block for each issue found)*

## Workflow:
1.  Analyze `git diff`.
2.  If code is good, reply: "✅ 代码无明显问题。"
3.  Otherwise, list issues using the format above.

## Input (`git diff`):
"""


def generate_code_review(diff_content: str, client: AIClient | None = None) -> str:
    """
    根据 diff 内容生成代码审查建议。
    
    Args:
        diff_content: git diff 输出内容
        client: AI 客户端实例，如果为 None 则创建新实例
        
    Returns:
        代码审查建议
    """
    if client is None:
        client = AIClient()
    
    prompt = f"\n\n```diff\n{diff_content}\n```"
    
    return client.chat(
        prompt=prompt,
        system_prompt=CODE_REVIEW_SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=4096,
    )


# MR Review 系统提示词
MR_REVIEW_SYSTEM_PROMPT = """
# Role: Expert Code Reviewer (Golang/Java/Python Polyglot)

## Task Description
You are a senior software architect conducting a rigorous code review. Your goal is to analyze the provided `Diff to Review`, identify **critical** issues, and output specific, line-level feedback in valid JSON format.

## Input Data Format
The input diff uses a custom annotation format for line numbers. You must strictly parse these distinct markers:
- `[NEW LINE {n}]`: Indicates an added line. Use `{n}` as `new_line`.
- `[OLD LINE {n}]`: Indicates a removed line. Use `{n}` as `old_line`.
- `[LINE old:{m} new:{n}]`: Indicates a context line (unchanged).

## Workflow
1. **Analyze**: Scan the code for Logic Bugs, Security Vulnerabilities (OWASP Top 10), Performance Bottlenecks, and Race Conditions.
2. **Filter**: Discard any feedback related to:
   - Code style / Formatting / Indentation.
   - Resource files (XML, JSON, YAML) or imports/package declarations.
   - Comments or documentation.
   - Trivial suggestions that do not impact system stability.
3. **Map**: For each valid issue, precise the exact line number from the annotation tags.
4. **Format**: Construct the final JSON array.

## Review Rules
1. **Language**: Review comments must be in **Chinese (中文)**.
2. **Quality Bar**: Only comment if the issue is *significant*. Better to return an empty array `[]` than to nitpick.
3. **Quantity Limit**: Select the top 3 most critical issues.
4. **Line Number Precision**: 
   - Extract numbers **EXACTLY** from the `[NEW LINE n]` or `[OLD LINE n]` tags relative to the code line.
   - Do NOT invent line numbers. If a tag is missing, do not comment on that line.

## Output Schema
Output **ONLY** a raw JSON array. No markdown formatting (```json), no explanations.

**JSON Object Structure:**
```json
{
  "file": "String (File path from '=== File: path ===')",
  "old_line": "Integer or null (from [OLD LINE n])",
  "new_line": "Integer or null (from [NEW LINE n])",
  "content": "String (Concise, actionable feedback in Chinese, < 30 words)"
}


## Diff to Review:
"""


def parse_diff_with_line_numbers(diff_text: str, file_path: str) -> str:
    """
    解析 diff 文本，为每行添加显式行号注释。
    
    Args:
        diff_text: GitLab 返回的 diff 文本
        file_path: 文件路径
        
    Returns:
        带行号注释的 diff 文本
    """
    import re
    
    lines = diff_text.split('\n')
    result_lines = [f"=== File: {file_path} ==="]
    
    old_line = 0
    new_line = 0
    
    for line in lines:
        # 解析 @@ hunk header
        # 格式: @@ -old_start,old_count +new_start,new_count @@
        hunk_match = re.match(r'^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
        if hunk_match:
            old_line = int(hunk_match.group(1))
            new_line = int(hunk_match.group(2))
            result_lines.append(line)
            continue
        
        if line.startswith('+') and not line.startswith('+++'):
            # 新增行
            result_lines.append(f"[NEW LINE {new_line}] {line}")
            new_line += 1
        elif line.startswith('-') and not line.startswith('---'):
            # 删除行
            result_lines.append(f"[OLD LINE {old_line}] {line}")
            old_line += 1
        elif line.startswith(' ') or (line and not line.startswith('\\') and not line.startswith('diff') and not line.startswith('index')):
            # 上下文行（未修改）
            if old_line > 0 or new_line > 0:
                result_lines.append(f"[LINE old:{old_line} new:{new_line}] {line}")
                old_line += 1
                new_line += 1
            else:
                result_lines.append(line)
        else:
            result_lines.append(line)
    
    return '\n'.join(result_lines)


def parse_mr_review_comments(ai_response: str) -> list[dict]:
    """解析 AI 返回的 MR 审查评论"""
    import json
    import re
    import logging
    
    logger = logging.getLogger(__name__)
    
    # 尝试提取 JSON 内容
    json_match = re.search(r'```json\s*(.*?)\s*```', ai_response, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # 尝试直接解析
        json_str = ai_response.strip()
    
    try:
        comments = json.loads(json_str)
        if isinstance(comments, list):
            return comments
        else:
            logger.warning(f"AI 响应不是数组格式: {type(comments)}")
    except json.JSONDecodeError as e:
        logger.warning(f"AI 响应 JSON 解析失败: {e}, 原始响应: {ai_response[:200]}...")
    
    return []


def generate_mr_review(diff_content: str, client: AIClient | None = None) -> list[dict]:
    """
    使用 AI 生成 MR 审查评论。
    
    Args:
        diff_content: 带行号注释的 diff 内容
        client: AI 客户端实例，如果为 None 则创建新实例
        
    Returns:
        审查评论列表，每个评论包含 file, old_line, new_line, content
    """
    if client is None:
        client = AIClient()
    
    prompt = f"\n\n```diff\n{diff_content}\n```"
    
    response = client.chat(
        prompt=prompt,
        system_prompt=MR_REVIEW_SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=4096,
    )
    
    return parse_mr_review_comments(response)
