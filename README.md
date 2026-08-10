# 模型指纹技术研究进展

> 更新时间：2026-08-10  
> 主题：模型指纹、模型水印、训练数据溯源与生成内容来源标识

## 1. 摘要

模型指纹（model fingerprinting）关注“如何识别一个模型、模型副本、模型血缘或模型产物的来源”。随着大模型训练成本、模型 API 商业化、开源权重二次分发和生成式内容规模化增长，模型指纹已经从早期的 DNN 知识产权保护，扩展为覆盖 **数据集、模型本体、推理服务、生成内容和内容凭证** 的完整身份技术体系。

当前研究大体形成三条主线：

1. **模型所有权与血缘验证**：判断可疑模型是否来自某个原始模型，常用于模型窃取、未授权微调、模型市场侵权和云端模型篡改检测。
2. **训练数据与数据集溯源**：判断某批数据是否参与训练，服务于版权、数据合规和数据供应链审计。
3. **生成内容来源标识**：判断文本、图像、音频或视频是否由某类模型生成，并与 C2PA/Content Credentials 等内容来源标准结合。

研究趋势从“在模型中嵌入触发器或后门式水印”转向“非侵入式、统计化、可部署、可审计”的方法：例如黑盒行为指纹、表示空间相似度、假设检验、可扩展多指纹、训练数据统计推断，以及与内容凭证结合的耐久水印。

## 2. 术语与边界

| 概念 | 目标 | 是否主动嵌入信号 | 常见验证接口 | 典型用途 |
| --- | --- | --- | --- | --- |
| 模型指纹 | 从模型固有行为、参数、表示或输出模式识别模型身份/血缘 | 通常不需要，也可包含预生成秘密查询 | 白盒、灰盒、黑盒 API | 模型窃取检测、模型版本识别、血缘追踪 |
| 模型水印 | 在训练、微调、权重或输出中嵌入可验证标记 | 是 | 白盒权重、黑盒触发集、输出检测器 | 所有权证明、授权追踪 |
| 数据指纹/数据集推断 | 判断数据集是否参与训练或是否被模型记忆 | 可主动标记，也可被动统计推断 | 模型权重、logits、API 输出 | 数据版权、合规审计 |
| 生成内容水印 | 在模型输出中嵌入可检测信号 | 是 | 内容检测器、密钥或公开检测器 | AI 内容识别、平台治理 |
| 内容凭证/来源标准 | 用签名元数据、软绑定、内容指纹记录来源链 | 通常结合元数据与水印 | C2PA 验证器、凭证仓库 | 媒体来源、编辑历史、AI 披露 |

需要区分两类问题：

- **证明“这是我的模型”**：强调可验证性、抗伪造、低误报和法律证据链。
- **识别“它像哪个模型/版本”**：强调分类准确率、查询效率和对系统提示、RAG、采样随机性的鲁棒性。

## 3. 技术谱系

### 3.1 DNN 模型指纹：从边界样本到测试框架

早期工作主要面向图像分类等 DNN 模型，核心假设是：被窃取、蒸馏、剪枝或微调后的模型会保留原模型的部分决策边界和错误模式。

- **分类边界指纹**：IPGuard 从已训练分类器的决策边界附近提取样本作为指纹。验证时比较目标模型与原模型在这些边界样本上的标签一致率。优点是不修改原模型、理论上不损害精度；缺点是依赖分类任务和边界样本生成质量。
- **可传递对抗样本**：Conferrable Adversarial Examples 设计一类更容易从原模型传递到其派生模型、但不易传递到无关模型的目标对抗样本，用作模型血缘指纹。其价值在于把模型窃取检测与对抗样本迁移性联系起来。
- **多层测试框架**：DeepJudge 把版权保护问题建模为模型相似性测试，结合神经元行为、边界行为、鲁棒性距离和测试用例生成，适合在不同攻击和后处理场景下综合评估。

这一阶段的局限在于任务类型相对集中，通常假设模型是确定性分类器；面对 LLM 的开放式生成、随机采样、系统提示和工具链封装，需要新的方法。

### 3.2 LLM 黑盒行为指纹：少量查询识别模型或篡改

LLM 常以 API 或应用形式部署，审计者无法访问权重，只能通过输入输出行为推断身份。2024 年后，黑盒 LLM 指纹成为热点。

- **LLMmap（2024/USENIX Security 2025）**：通过精心设计的主动查询识别应用背后的 LLM 版本。论文报告在 42 个常见模型版本上，仅需约 3-8 次交互即可达到较高识别率，并对未知系统提示、采样参数、RAG 和 Chain-of-Thought 场景保持鲁棒。
- **RoFL（2025）**：把指纹定义为“提示-响应”的统计模式，目标是在不修改模型的情况下，通过少量黑盒查询识别同一模型血缘。它强调可用密码学承诺提前登记指纹，降低事后伪造风险。
- **ESF/RESF（2025）**：面向云端 LLM 篡改检测，使用敏感提示和统计检验处理随机输出。ESF 引入随机性集合一致性检查，RESF 使用熵梯度范数选择更敏感的指纹样本，并用两级序贯检验控制误报。

这一方向的关键挑战是：LLM 输出天然随机，系统提示、温度、上下文窗口、RAG、工具调用和安全过滤会改变观测分布。因此，研究正在从“单次输出匹配”转向“分布级证据、假设检验和校准误报率”。

### 3.3 LLM 表示/参数指纹：从相似度到功能子空间

当审计者能访问权重或中间表示时，可以直接比较模型内部结构。

- **REEF（ICLR 2025）**：使用相同样本下的表示相似度，特别是 CKA（Centered Kernel Alignment），判断可疑模型是否源自受害模型。该方法不需要再训练，不影响模型能力，并报告了对微调、剪枝、模型合并和维度变换的鲁棒性。
- **白盒水印与权重分布方法**：例如 ELLMark 等方法尝试在模型权重统计特征中编码比特，用于在线模型市场的 IP 保护。
- **功能子空间水印（FSW，2026 预印本）**：把所有权信号锚定到更稳定的低维功能子空间，通过正交密钥和统计验证增强对微调、量化、蒸馏等后处理的鲁棒性。

表示/参数指纹的优势是证据更直接，适合开源权重、模型市场和企业内部审计；不足是对黑盒 API 场景不适用，并且需要处理架构变化、参数重排、量化和模型合并带来的比较难题。

### 3.4 嵌入式 LLM 指纹与可扩展水印

有些场景允许模型发布者在发布前主动嵌入指纹或水印。

- **Instructional Fingerprinting（NAACL 2024）**：通过轻量指令微调植入私钥触发行为，使模型在包含特定密钥时输出指定文本。研究强调对正常能力影响较小，并能在后续微调中保留。
- **Scalable Fingerprinting / Perinucleus Sampling（NeurIPS 2025）**：把“可扩展性”作为核心需求，目标是在一个模型中嵌入大量指纹，以降低误报、抵抗指纹泄露和合谋攻击。论文报告在 Llama-3.1-8B 中嵌入 24,576 个指纹且不明显损害能力。
- **SEAL（2025 预印本）**：把多比特签名锚定到表示子空间，兼顾白盒和黑盒验证，试图避免传统后门水印对模型行为的异常影响。

这类方法的主要优势是可形成明确的所有权证据；主要风险是触发器泄露、被自适应攻击移除、影响模型行为或被质疑为后门。

### 3.5 训练数据与数据集溯源

数据层面的指纹回答的是“某个数据集是否被用于训练”，与模型所有权问题互补。

- **Radioactive Data（2020）**：在图像数据中加入人眼不可见的标记，使训练出的模型携带可检测信号。论文报告即使标记数据只占训练集一小部分，也可通过统计检验检测其使用。
- **Dataset Inference（2021 之后）**：从单样本 membership inference 转向集合级统计推断，判断一批数据是否参与训练。
- **LLM Dataset Inference（NeurIPS 2024）**：指出许多 LLM 单样本成员推断结果会被时间分布漂移等混杂因素夸大，因此主张以作者、书籍或语料集合为单位做数据集推断，并聚合多个弱信号进行统计检验。

这一方向与版权诉讼、数据合规和训练语料透明度高度相关，但需要谨慎控制分布漂移、基准选择、重复数据、语料污染和假阳性。

### 3.6 生成内容水印与 C2PA 来源凭证

模型指纹不只保护模型本体，也服务于生成内容治理。

- **文本水印**：SynthID-Text（Nature 2024）在采样阶段调制 token 分布，保持文本质量并支持高效检测；Google 也开源了相关参考实现。它说明文本水印可以进入大规模生产系统，但仍会受到重写、翻译、摘要和混合编辑的影响。
- **图像/视频/音频水印**：扩散模型和多模态生成内容通常依赖不可见水印、频域标记或检测器，但跨平台压缩、裁剪、截图、重录和再生成会削弱信号。
- **C2PA / Content Credentials**：C2PA 通过签名元数据记录内容来源、编辑历史和 AI 参与信息。新版规范支持软绑定、不可见水印和内容指纹，用于在元数据被剥离时恢复或关联凭证。它不是单一水印算法，而是把元数据、签名、内容指纹和凭证仓库组合成来源基础设施。

实践中，生成内容治理更可能采用“多层防线”：生成时水印 + 发布时内容凭证 + 平台侧检测 + 审计日志，而不是依赖单一检测器。

## 4. 2024-2026 研究进展概览

| 时间 | 进展 | 代表方向 |
| --- | --- | --- |
| 2024 | LLM 模型指纹开始系统化；指令触发式 LLM 指纹出现；LLM 数据集推断强调集合级证据；SynthID-Text 展示生产级文本水印 | Instructional Fingerprinting、LLM Dataset Inference、SynthID-Text |
| 2025 | 黑盒 LLM 版本识别、鲁棒行为指纹、表示相似度和可扩展多指纹成为热点；出现面向 LLM 指纹的 SoK/Benchmark | LLMmap、REEF、RoFL、ESF/RESF、Scalable Fingerprinting、LEAFBENCH |
| 2026 | 研究更关注统一术语、生命周期分类和部署评估；模型、水印、数据与内容凭证被纳入“隐式身份/Implicit-ID”框架 | Implicit Identity 技术综述、部署导向 LLM 水印综述、功能子空间水印 |

总体趋势：

1. **从单点算法到生命周期治理**：覆盖数据收集、训练、发布、API 调用、内容生成、转载和取证。
2. **从确定性匹配到统计检验**：特别是 LLM 场景，需要用分布、置信区间、p-value、序贯检验和误报控制。
3. **从单一指纹到可扩展指纹库**：多用户授权、泄露追踪和合谋攻击要求能生成大量独立指纹。
4. **从实验室指标到部署指标**：查询成本、延迟、密钥管理、检测器公开性、法律证据链和平台互操作性变得同样重要。

## 5. 评测指标

| 指标 | 含义 | 关注点 |
| --- | --- | --- |
| 可识别性（identifiability） | 能否正确识别模型身份、版本或血缘 | 准确率、召回率、ROC-AUC、开放集识别 |
| 低误报（reliability） | 无关模型被误判为侵权的概率 | false positive rate、校准、统计显著性 |
| 无害性（harmlessness/fidelity） | 指纹是否影响模型能力或输出质量 | clean accuracy、benchmark 分数、用户反馈 |
| 鲁棒性（robustness） | 面对后处理或攻击是否仍可验证 | 微调、剪枝、量化、蒸馏、合并、提示封装 |
| 隐蔽性与安全性（stealth/security） | 指纹是否难以发现、伪造或移除 | 密钥泄露、触发器猜测、自适应攻击 |
| 可扩展性（scalability） | 能否支持大量用户、版本或指纹 | 指纹容量、合谋抗性、管理成本 |
| 可部署性（deployability） | 能否进入真实系统 | 查询次数、延迟、检测成本、API 限制、审计流程 |

## 6. 主要攻击与失效模式

| 攻击/变化 | 对指纹的影响 | 应对思路 |
| --- | --- | --- |
| 微调与指令微调 | 改变行为分布，可能覆盖触发器 | 使用边界/表示/统计多信号；定期重校准 |
| 剪枝、量化、权重重排 | 破坏参数级特征 | 使用功能或表示相似度；选择不变量 |
| 蒸馏与模型抽取 | 保留功能但改变参数 | 行为指纹、对抗样本、输出分布检验 |
| 模型合并与 LoRA 组合 | 模糊血缘，稀释水印 | 设计合并鲁棒指纹；引入多父模型判别 |
| 系统提示、RAG、工具调用 | 黑盒输出受应用层干扰 | 选择跨上下文稳定提示；建模应用层噪声 |
| 高温采样与随机性 | 单次响应不稳定 | 多次采样、序贯检验、集合一致性检查 |
| 指纹泄露与合谋 | 攻击者可屏蔽或移除已知触发器 | 多指纹库、密码学承诺、最小暴露验证 |
| 内容重写/翻译/再生成 | 削弱输出水印 | 结合来源凭证、平台日志和语义级检测 |

## 7. 实践建议

1. **先定义资产与威胁模型**：要保护的是训练数据、基础模型、微调模型、API 服务，还是生成内容？攻击者能访问权重、logits、API 还是只看内容？
2. **组合多种证据**：模型所有权场景可结合发布前水印、发布后行为指纹、权重/表示相似度、训练日志和密钥承诺。
3. **避免只看单次命中率**：应报告误报率、置信度、开放集表现、攻击后表现和查询预算。
4. **为 LLM 随机性设计验证流程**：黑盒验证应多次采样，并用统计检验区分篡改、温度变化和正常随机波动。
5. **重视证据链**：对可能进入法律或合规流程的指纹，应提前登记哈希、密钥、时间戳、实验配置和验证脚本。
6. **把内容水印与 C2PA 结合**：单独水印容易被编辑削弱；签名凭证、软绑定、内容指纹和远程凭证仓库能提升耐久性。

## 8. 开放问题

- **标准化基准不足**：不同论文的模型、攻击、查询预算和误报设定差异很大，难以横向比较。
- **自适应攻击评估不充分**：攻击者若知道算法细节，可能通过微调、过滤、重写或合谋削弱指纹。
- **模型合并和多源血缘复杂**：开源生态中模型常由多个基座、LoRA 和数据集组合而成，二元“是否侵权”判断不够。
- **隐私与合规边界**：数据集推断和成员推断可能暴露训练语料或用户隐私，需要合规约束。
- **法律可采性仍待验证**：技术显著性、误报控制、密钥保管、实验可复现性和专家证词都会影响证据价值。
- **多模态与代理系统更复杂**：多模态模型、RAG、工具调用和 agent 工作流使“模型身份”和“系统行为”更难分离。

## 9. 代表性论文与资源

### DNN 指纹与版权保护

- IPGuard: Protecting Intellectual Property of Deep Neural Networks via Fingerprinting the Classification Boundary. Asia CCS 2021. <https://doi.org/10.1145/3433210.3437526>
- Deep Neural Network Fingerprinting by Conferrable Adversarial Examples. ICLR 2021 / arXiv. <https://arxiv.org/abs/1912.00888>
- Copy, Right? A Testing Framework for Copyright Protection of Deep Learning Models. IEEE S&P 2022. <https://arxiv.org/abs/2112.05588>
- DeepJudge: A Testing Framework for Copyright Protection of Deep Learning Models. ICSE Demo 2023. <https://pure.manchester.ac.uk/ws/portalfiles/portal/251925084/ICSE_DEMO2023_DeepJudge.pdf>

### LLM 模型指纹与所有权验证

- Instructional Fingerprinting of Large Language Models. NAACL 2024. <https://aclanthology.org/2024.naacl-long.180/>
- LLMmap: Fingerprinting for Large Language Models. USENIX Security 2025 / arXiv 2024. <https://arxiv.org/abs/2407.15847>
- REEF: Representation Encoding Fingerprints for Large Language Models. ICLR 2025. <https://arxiv.org/abs/2410.14273>
- RoFL: Robust Fingerprinting of Language Models. arXiv 2025. <https://arxiv.org/abs/2505.12682>
- Scalable Fingerprinting of Large Language Models. NeurIPS 2025. <https://proceedings.neurips.cc/paper_files/paper/2025/file/b5ee4715ef8e96176ef3ccbe229b6ab9-Paper-Conference.pdf>
- ESF: Efficient Sensitive Fingerprinting for Black-Box Tamper Detection of Large Language Models. ACL Findings 2025. <https://aclanthology.org/2025.findings-acl.546/>
- RESF: Regularized-Entropy-Sensitive Fingerprinting for Black-Box Tamper Detection of Large Language Models. EMNLP 2025. <https://aclanthology.org/2025.emnlp-main.247/>
- SoK: Large Language Model Copyright Auditing via Fingerprinting. arXiv 2025. <https://arxiv.org/abs/2508.19843>
- Copyright Protection for Large Language Models: A Survey of Methods, Challenges, and Trends. arXiv 2025. <https://arxiv.org/abs/2508.11548>
- Implicit Identity Technologies for LLMs: Fingerprinting and Watermarking across Datasets, Models, and Generated Content. arXiv 2026. <https://arxiv.org/abs/2605.29245>

### 训练数据与数据集溯源

- Radioactive Data: Tracing Through Training. arXiv 2020. <https://arxiv.org/abs/2002.00937>
- Dataset Inference: Ownership Resolution in Machine Learning. ICLR 2021 / arXiv. <https://arxiv.org/abs/2104.10706>
- LLM Dataset Inference: Did you train on my dataset? NeurIPS 2024. <https://arxiv.org/abs/2406.06443>

### 生成内容水印与来源标准

- Scalable Watermarking for Identifying Large Language Model Outputs (SynthID-Text). Nature 2024. <https://doi.org/10.1038/s41586-024-08025-4>
- SynthID Text reference implementation. Google DeepMind. <https://github.com/google-deepmind/synthid-text>
- A Watermark for Large Language Models. ICML 2023 / arXiv. <https://arxiv.org/abs/2301.10226>
- Tree-Ring Watermarks: Fingerprints for Diffusion Images that are Invisible and Robust. NeurIPS 2023. <https://arxiv.org/abs/2305.20030>
- C2PA Technical Specification. <https://spec.c2pa.org/specifications/specifications/2.4/specs/C2PA_Specification.html>
- C2PA Implementation Guidance. <https://spec.c2pa.org/specifications/specifications/2.4/guidance/Guidance.html>

## 10. 后续可维护方向

- 建立 `papers/` 或 `resources/` 目录，按 DNN、LLM、数据溯源、内容水印分类维护 BibTeX。
- 增加方法对比表，记录访问假设、是否侵入、攻击评测、代码可用性和适用场景。
- 持续跟踪 LEAFBENCH、LLM 指纹 SoK、C2PA 版本更新和生产级文本水印案例。
- 如果仓库未来加入实验代码，建议优先复现黑盒 LLM 指纹的查询-响应统计流程，并固定随机种子、模型版本和采样参数。
