<|channel|>analysis<|message|>We need to read the documents and produce 5 key findings for an engineer wanting to run local LLM on Apple Silicon. The documents include Apple M4 Pro/Max specs, a paper on local LLM inference on Apple Silicon (2511.05502), and other papers about quantization, speculative decoding, etc. The engineer wants to run local LLM. So we should focus on Apple Silicon performance, memory, GPU, Thunderbolt, unified memory, MLX, MLC-LLM, Ollama, llama.cpp, PyTorch MPS. Also mention quantization tradeoffs, long-context, speculative decoding, MoE, etc. Provide bullet points in Turkish. Provide 5 key findings.

We need to read Apple M4 Pro/Max: 3nm, up to 16-core CPU, 40-core GPU, 128GB memory, 546GB/s bandwidth, Thunderbolt 5, Neural Engine 2x faster, etc. Also mention that M4 Pro/Max support up to 120Gb/s Thunderbolt 5, 75% memory bandwidth increase, etc.

The local LLM inference paper: MLX highest throughput, MLC-LLM lower TTFT, Ollama developer ergonomics but lower throughput, PyTorch MPS limited by memory. All fully on-device, no telemetry. Provide recommendations.

Also mention quantization: 4-bit quantization reduces memory 70% but may degrade performance; 8-bit preserves accuracy; 2-bit may degrade but code-specific calibration helps. Also mention that low-bit quantization favors undertrained LLMs; but for large models trained with 100T tokens, low-bit may degrade.

Speculative decoding: can accelerate inference 2-3x for dense models; for MoE, can accelerate more; but need to consider acceptance rates, batch size, etc.

Also mention that Apple Silicon inference frameworks still trail NVIDIA GPU-based systems but are maturing.

Also mention security