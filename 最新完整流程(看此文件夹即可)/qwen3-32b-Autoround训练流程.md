# **训练流程**

这个流程借鉴于之前的训练流程

# **训练/量化流程（2026年2月最新优化版）**

这个流程已验证在 Vast.ai A100 80GB 上成功跑通 Mistral-Small-3.1-24B / Qwen2.5-32B 的 4bit GGUF 量化。

1. **使用 VastAI**
   打开 https://vast.ai/，点击 Get Started。

2. **算力市场选择**
   - 1张 A100-SXM4 80GB（不要 40GB）
   - 容器磁盘：500GB+（模型 ~60GB + 中间文件 + GGUF）
   - 优先选 Reliability > 98%、Max CUDA 13.0 的实例
   - 整个流程花费大概5-10刀

3. **镜像选择**
   - NVIDIA CUDA（默认）
   - 推荐 PyTorch 2.10+ cu130 或 CUDA 13.0 模板

4. **租用后进入 JupyterLab**
   Instance → Jupyter 图标 → View → Open JupyterLab

5. **Terminal 更新系统 & pip**
   ```bash
   sudo apt update && sudo apt upgrade -y
   pip install --upgrade pip setuptools wheel

6. **安装核心包（一键合并）**

   ```bash
      # 基础包
      pip install auto-round transformers[torch] accelerate safetensors huggingface_hub[cli] hf_transfer scipy einops ninja protobuf sentencepiece

      # torch cu130（确保匹配 CUDA 13.0）
      pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130

      # 升级 auto-round 到最新
      pip install --upgrade auto-round

      # gguf 从 llama.cpp master 安装（必须，支持 Mistral/Qwen）
      pip uninstall gguf -y
      pip install git+https://github.com/ggerganov/llama.cpp.git@master#subdirectory=gguf-py
   ```

   * 下载这些python packages可能会非常耗费时间，可以在等待的时候打开一个新的terminal进行下一个步骤

7. **如果json文件是QA对**
   * 运行convert.py来修改格式到jsonl
   ```bash
   import json

   input_file = "./dataset.json"     # 替换成你的文件
   output_file = "./dataset.jsonl"

   with open(input_file, 'r', encoding='utf-8') as f:
      data = json.load(f)   # 假设是 list of dicts

   with open(output_file, 'w', encoding='utf-8') as f:
      for item in data:
         # 拼接 Q + A，中间加换行或空格
         q = item.get("instruction", "") or item.get("question", "")
         a = item.get("output", "") or item.get("answer", "")
         text = text = f"instruction: {q}\noutput: {a}"
         if text:
               f.write(json.dumps({"text": text}, ensure_ascii=False) + '\n')

   print(f"转换完成，保存为 {output_file}，共 {len(data)} 条")
   ```

8. **下载flash-attn来配合(加速量化的插件)**
   * 这个步骤可能会非常慢而且出bug，推荐直接从Github上下载

   * 检查torch和cuda的版本
   ```bash
      pip show torch | grep Version   # e.g., 2.1.0  (可能是2.10,目前能跑,有问题请咨询维护)
      python -c "import torch; print(torch.version.cuda)"   # e.g., 13.0
   ```

   * 之后可以把版本和GOU信息提供给你的LLM来帮助你寻找相应的Github版本：
   ```bash
      pip install flash_attn_3 --find-links https://windreamer.github.io/flash-attention3-wheels/cu130_torch2100 --extra-index-url https://download.pytorch.org/whl/cu130
      python -c 'import flash_attn; print("Flash-attn version:", flash_attn.__version__); print("Import OK!")' #检查下载成功了没
      python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No GPU')"
   ``` 
   * 我的版本是 torch 2.1.0，CUDA 13.0，根据你的版本修改，确认torch是cuda版本，检查能否使用attn

   ```bash
      python -c '
      import torch
      from flash_attn_interface import flash_attn_func  # 常见 FA3 接口函数名
      print("✅ Flash Attention 3 接口导入成功！")

      q = torch.randn(1, 12, 128, 64, dtype=torch.bfloat16, device="cuda")
      k = torch.randn(1, 12, 128, 64, dtype=torch.bfloat16, device="cuda")
      v = torch.randn(1, 12, 128, 64, dtype=torch.bfloat16, device="cuda")

      try:
         out = flash_attn_func(q, k, v, causal=True)
         print("🚀 Flash Attention 3 计算测试成功！输出形状:", out.shape)
      except Exception as e:
         print("❌ 计算失败:", str(e))
      '
   ```

   **避坑指南：如果找不到匹配的 Github Wheel 怎么办？**
   * 如果你发现自己的版本太特殊（比如 CUDA 12.8 这种极新版本），Github 上没有现成的 .whl：

   * 直接安装源码版（耗时但稳）：
   * 只要你有 A100，性能足够强，直接强装attn，通常 10 分钟也能好(命令行里敲以下代码)
   ```bash
   MAX_JOBS=8 pip install flash-attn --no-build-isolation
   ```
   * 放弃强求： 对于 AutoRound 量化过程来说，Flash Attention 不是必须的。它主要加速的是推理和训练。如果量化过程中报 FlashAttention not found，它会自动回退到 sdpa (PyTorch 原生注意力)，速度只慢一点点，不影响量化质量。

9. **登录Huggingface下载需要被量化的微调模型**
   * 下载Hugging face并登录：
   
   ```bash
      pip install -U huggingface_hub[cli]
      pip install --upgrade huggingface_hub
      hf auth login
   ```
   * 输入你的key，确认登陆后方可下载微调模型
   * 要注意该模型必须要在Huggingface上显示是public的才可以被下载
   ```bash
      pip install --upgrade transformers #安全起见
      hf download XXXX/XXX --local-dir ./workModel #特定地址
   ```

   * 下载后检查：
   ```bash
      du -sh ./workModel   # Shows current downloaded size
      ls -lh ./workModel   # Lists files as they appear
      df -h                # Ensure >80 GB free disk
   ```

   * 再次检查，没有报错基本就是成功
   ```bash
      python -c "from transformers import AutoModelForCausalLM, AutoTokenizer; \
      model_path = './workModel'; \
      print('Loading tokenizer...'); \
      tokenizer = AutoTokenizer.from_pretrained(model_path); \
      print('Tokenizer OK'); \
      print('Loading config...'); \
      config = AutoModelForCausalLM.from_pretrained(model_path, trust_remote_code=False).config; \
      print('Config OK'); \
      print('Layers:', config.num_hidden_layers); \
      print('Hidden size:', config.hidden_size); \
      print('Model type:', config.model_type)"
   ```

10. **核心烹饪：编写并执行量化脚本**

   * 在 JupyterLab 中新建一个 quantize.py 文件，复制以下代码。该脚本专门针对 A100-80GB 环境进行了显存优化：
   ```bash
   import torch
   from transformers import AutoModelForCausalLM, AutoTokenizer
   from auto_round import AutoRound

   # 清理缓存（防止 OOM爆显存）同时杀以下其他进程，如失败的量化，可能在后台占用！！！
   torch.cuda.empty_cache()

   model_path = "./workModel"
   output_dir = "./Qwen3-32B-GGUF-Q4KM"

   tokenizer = AutoTokenizer.from_pretrained(
      model_path,
      trust_remote_code=True
   )

   model = AutoModelForCausalLM.from_pretrained(
      model_path,
      torch_dtype=torch.bfloat16,
      device_map="auto",
      trust_remote_code=True,
      low_cpu_mem_usage=True
   )

   print("启动量化：4bit | gguf:q4_k_m")

   autoround = AutoRound(
      model,
      tokenizer,
      bits=4,
      group_size=128,                 # 关键修正：降到 64，显存更稳
      iters=200,                     # 保持最高质量
      nsamples=256,
      seqlen=512,
      dataset="/workspace/xxx_dataset.jsonl", # 根据数据集修改
      scheme="GGUF:Q4_K_M",
      low_gpu_mem_usage=True,
      disable_opt_rtn=True,
      enable_torch_compile=False,
      # 可选：如果还吃内存，加下面两行
      # percdamp=0.01,
      # act_order=True,
   )

   try:
      autoround.quantize_and_save(output_dir)
      print(f"完成！GGUF 文件在：{output_dir}")
   except Exception as e:
      print("量化或保存失败:", str(e))
      print("请检查 sentencepiece 是否安装，路径是否正确，或显存是否足够。")
   ```
   
11. **执行与监控**
   在另外一个 Terminal 中运行脚本：

   ```bash
      export PYTORCH_ALLOC_CONF=expandable_segments:True
      tmux new -s quant
      nohup python quantize.py > quant.log 2>&1 &
      tail -f quant.log
   ```
   监控建议：

   显存占用： 你会看到显存占用飙升至 70GB+。这是因为 A100 正在全力计算梯度的符号（Sign-gradient descent）。

   时间预期： 对于 32B 模型，AutoRound 的“精细化”量化大约需要 45 到 90 分钟。如果进度条看起来像卡住了，不要慌，它正在一层层地优化。

12. 最后一步：导出与测试(可能有bug，出问题请咨询维护)(lmstudio是否需要下列参数需查看)
```bash
   # 安装 vLLM（推荐最新版，支持 CUDA 13.0）
   pip install vllm --upgrade

   # 启动 vLLM 服务（限制显存使用，避免 OOM）
   python -m vllm.entrypoints.openai.api_server \
   --model /workspace/Qwen3-32B-GGUF-Q4KM/workModel-33B-Q4_K_M.gguf \
   --dtype bfloat16 \
   --gpu-memory-utilization 0.85 \   # 只用 85% 显存（≈68 GB），留余量
   --max-model-len 8192 \            # 最大上下文 8K，够用
   --tensor-parallel-size 1 \        # 单 GPU
   --port 8000
```
* 成功后(需要一定的context，如"...的专家")
```bash
curl http://127.0.0.1:8081/v1/chat/completions -H "Content-Type: application/json" -d '{"messages": [{"role": "system", "content": "你是一位精通加州财政政策和公共安全预算的专家。"}, {"role": "user", "content": "“水边选举”（Water Edge Election）制度是如何运作的，它每年导致加州损失多少税收？该政策如何与消防预算和救援人员培训产生关联？"}], "temperature": 0.7}'
```

## **注意事项**

* 在 JupyterLab 中如果将文件夹 **Move to Trash** 不会真正删除文件。
* 需运行以下命令彻底清空 Trash：

```bash
rm -rf ~/.local/share/Trash/*
```

## 🧩 Quantization Details
- **Method**: AutoRound (Sign-Gradient Descent Optimization)
- **Quantized by**: [Your Name/Team]
- **Hardware**: NVIDIA A100 80GB (Vast.ai)
- **Environment**: CUDA 13.0 / PyTorch 2.10
- **Configuration**: 
  - Bits: 4-bit
  - Group Size: 128 (Optimized for VRAM)
  - Scheme: GGUF (Q4_K_M)

## 🧪 Evaluation Case: California Fiscal Policy
This model has been specifically verified for high-stakes reasoning.
**Query**: "How does the 'Water Edge Election' impact CAL FIRE budgets?"
**Model Performance**: Corrected initial hallucinations regarding welfare policies and accurately identified the linkage between Corporate Tax (Worldwide Combined Reporting) and the State General Fund.