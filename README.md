# ACA-AI

本项目意在为 ACA 开发微调模型用于网站端QA

## 本地开发

### 1. 环境要求

```
python>=3.10
```

### 📦 项目安装

```bash
git clone https://github.com/UGcraft/ACA-AI.git
cd ACA-AI
pip install -e .
```

> 当前版本假设你已配置 Google AI studio key 或者 OpenAI API Key
> `export GOOGLE_AI_STUDIO_API_KEY=xxxx`
> `export OPENAI_API_KEY=xxxx`

- CI/CD：GitHub Actions

- 版本控制：Git & GitHub

---

### 📁 目录结构

```
src/
  qgen/
   ├─ schemas.py          # 数据结构 & JSON Schema
   ├─ generator.py        # 生成器主逻辑
   ├─ client.py           # OpenAI Responses API 封装
   ├─ templates/          # Jinja2 prompt 模板
   ├─ temporal.py         # 时间解析/验证
   ├─ utils.py            # 工具函数
   ├─ dataset_types.py    # 适配语料行到 TextRecord
   └─ demo_run.ipynb      # 示例ipynb运行时
tests/
docs/
```

---

## 🧪 示例使用

```python
from qgen.generator import QGen
from qgen.dataset_types import row_to_textrecord

row = {
    "text": "周二，比利时内阁通过了10%关税下调，将于2025年11月15日生效。",
    "source": "policy_watch.md",
    "title": "关税调整",
    "line_number": 42,
}

rec = row_to_textrecord(row)
qg = QGen(model="Gemini-2.5-flash-lite")  # 支持 Structured Output 的模型

batch = qg.generate_extractive_batch(
    rec,
    K=4,
    article_date="2025-11-12",
    dateline_location="Brussels, Belgium"
)

print(batch.model_dump_json(indent=2))
```

### 生成示例（节选）：

```json
{
  "question": "关税下调何时生效？",
  "answer": "2025年11月15日生效",
  "event_when_iso": "2025-11-15",
  "event_where": "布鲁塞尔，比利时",
  "actors": ["比利时内阁"],
  "progression": "ongoing",
  "analysis_tags": ["policy"],
  "stance": "neutral"
}
```

## 工作流

本项目使用 GitHub Flow。所有工作都应遵循以下流程：（[具体请参考项目工作流指南](WORKFLOW.md)）

1. 分配任务：从项目看板领取一个 `To Do` 状态的 Issue。

2. 创建分支：基于 `main` 分支创建新分支。

3. 开发与提交：完成开发，并使用规范的 Commit Message 提交代码。

4. 发起 PR：推送分支并发起 Pull Request (PR) 到 `main` 分支。

5. 审查与合并：PR 必须通过所有 CI 检查并获得其他成员审查后，方可合并。
