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

## 训练流程
[请参考PDF](src/训练流程.pdf)

## 工作流

本项目使用 GitHub Flow。所有工作都应遵循以下流程：（[具体请参考项目工作流指南](WORKFLOW.md)）

1. 分配任务：从项目看板领取一个 `To Do` 状态的 Issue。

2. 创建分支：基于 `main` 分支创建新分支。

3. 开发与提交：完成开发，并使用规范的 Commit Message 提交代码。

4. 发起 PR：推送分支并发起 Pull Request (PR) 到 `main` 分支。

5. 审查与合并：PR 必须通过所有 CI 检查并获得其他成员审查后，方可合并。
