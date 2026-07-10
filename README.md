# 模型指纹技术研究进展

> 更新时间：2026-07-10
> 主题：深度神经网络（DNN）与大语言模型（LLM）的模型指纹、模型水印、版权审计和溯源验证。

## 1. 一句话总结

模型指纹技术正在从早期的“给分类模型设计一组特殊查询样本”演进为覆盖数据、模型、生成内容全生命周期的身份技术体系。DNN 方向重点解决黑盒所有权验证、对抗样本指纹的稳健性与误报问题；LLM 方向则快速转向低查询成本、可证明/可加密验证、指纹去除攻防、模型派生关系审计，以及在微调、量化、剪枝、合并、RAG 和系统提示等真实部署变换下的标准化评测。

## 2. 术语与边界

| 概念 | 是否修改模型 | 典型访问条件 | 核心目标 | 说明 |
| --- | --- | --- | --- | --- |
| 模型指纹（model fingerprinting） | 通常不修改模型，也可泛化包含主动植入 | 黑盒、灰盒、白盒 | 判断可疑模型是否来自受保护模型，或识别模型版本/来源 | 狭义上强调从模型固有行为或表示中提取身份特征；LLM 研究中也常把触发式方案称为 fingerprinting。 |
| 模型水印（model watermarking） | 是 | 黑盒或白盒 | 在模型参数或行为中嵌入可验证标识 | 常见方案包括参数正则、后门/触发集、指令触发等；优点是验证信号强，缺点是可能影响性能且不能事后应用到已发布模型。 |
| 文本水印（text watermarking） | 不一定修改模型 | 生成文本可见 | 识别生成内容来源 | 保护的是生成内容；在某些配置下可作为模型身份信号的一部分。 |
| 数据集推断（dataset inference） | 否 | 多为黑盒 | 判断目标模型是否训练过某个数据集 | 与版权审计高度相关，但更多证明“数据被用过”，而非直接证明“模型被盗”。 |

## 3. 技术分类

### 3.1 按访问权限

- **黑盒指纹**：只能查询 API 或应用输出。优势是贴近商业模型和闭源服务；挑战是输出随机性、系统提示、后处理、拒答策略和查询限额会削弱信号。
- **灰盒指纹**：可获得部分概率、logits、嵌入、token 级置信度或有限内部信号。常用于提升统计检验能力，例如基于概率变化或记忆信号的验证。
- **白盒指纹**：可访问权重、梯度、激活、表示层。适合开源模型族谱分析和第三方审计，但对闭源 API 不现实。

### 3.2 按指纹来源

- **输入-输出行为指纹**：设计一组探针样本或提示词，比较模型在这些输入上的标签、文本、概率或响应风格。
- **决策边界指纹**：利用对抗样本、可转移样本、边界附近样本或轨迹来刻画分类器差异。
- **表示/权重指纹**：比较内部激活、隐藏状态、CKA 相似度、权重统计或梯度特征，用于判断模型派生关系。
- **记忆/隐私泄漏指纹**：利用训练数据记忆、成员推断、数据集推断或概率扰动来证明模型对特定数据/指纹样本的保留。
- **密钥/密码学指纹**：将秘密 key、哈希链、错误纠正码或外部编码器引入验证协议，增强不可伪造性与抗响应篡改能力。

## 4. DNN 模型指纹进展

### 4.1 早期主线：触发集、水印与对抗样本

DNN 知识产权保护早期主要围绕两类方案：

1. **水印式方案**：在训练时嵌入触发集或参数约束，验证时检查触发输入是否输出预设标签。
2. **非侵入式指纹**：不改动模型，而是从源模型提取一组能区分源模型、盗版模型和无关模型的样本。

代表性思路包括 conferrable adversarial examples，即构造只在源模型及其抽取模型之间转移、但不会普遍转移到无关模型的对抗样本，用于模型抽取后的黑盒验证。

### 4.2 新趋势：从单点对抗样本到更稳健的边界刻画

单个对抗样本容易受到决策边界轻微变化影响，导致误判或漏判。近年工作开始使用更连续、更结构化的边界刻画：

- **ADV-TRA / adversarial trajectories（NeurIPS 2024）**：用一串逐步增强的对抗样本轨迹刻画决策边界，而非依赖单个点；通过 surface trajectory 覆盖多类边界，提升对剪枝、微调、对抗训练等修改的容忍度。
- **NaturalFinger（2023）**：用 GAN 生成更自然的指纹样本，避免明显噪声样本被攻击者过滤；关注“决策差异区域”而不仅是边界点。
- **神经功能/正常样本指纹**：减少对异常样本的依赖，尝试用正常测试样本下的神经元功能或内部响应来识别模型复用。

### 4.3 数据集与隐私泄漏型指纹

数据集推断和隐私泄漏指纹把“模型记住了什么”作为证据：

- **Dataset Inference**：聚合多种成员推断信号，对一个数据集整体进行统计检验，比单条样本成员推断更贴近版权争议场景。
- **VeriDIP（2023）**：用成员推断估计隐私泄漏下界，把模型对训练数据的记忆模式作为指纹。
- **鲁棒性争议**：后续研究指出，数据集推断可能在同分布独立模型上产生高误报，也可能被对抗训练等正则化手段规避。因此这一路线需要更严格的同分布负样本、置信区间和攻击评估。

### 4.4 当前难点

- 同源模型、同数据集训练模型和真正盗版模型之间边界模糊，误报控制困难。
- 攻击者可通过微调、剪枝、蒸馏、对抗训练、查询过滤、输入检测、模型重训练来削弱指纹。
- 很多论文实验协议仍偏乐观，需要统一 benchmark、强自适应攻击和真实 API 限额评测。

## 5. LLM 模型指纹进展

### 5.1 为什么 LLM 指纹变得更重要

LLM 的训练成本、数据价值和商业部署规模远高于传统分类模型，同时派生方式更多：SFT、RLHF/RLAIF、LoRA、模型合并、量化、剪枝、知识编辑、RAG 包装、系统提示、代理框架等都可能改变输出行为。因此，LLM 指纹不只要回答“是不是同一个模型”，还要回答：

- 这个应用底层使用了哪个模型或哪个版本？
- 可疑模型是否从某个基础模型派生？
- 某个训练集、专有样本或指纹样本是否被保留？
- 指纹能否在下游微调、LoRA、量化、模型合并和输出后处理后仍可验证？

### 5.2 黑盒行为识别

- **LLMmap（USENIX Security 2025）**：通过 3 到 8 次精心设计的查询识别应用背后的 LLM 版本，在包含未知 system prompt、随机采样、RAG、CoT 等应用层变化时仍能保持较高识别准确率。它更像“模型版本扫描器”，也暴露了 LLM 应用的指纹化风险。
- **目标化提示与响应嵌入**：用诊断提示诱导模型暴露稳定差异，再用分类器或嵌入相似度判断来源。优点是查询少、部署简单；风险是探针泄漏后可被屏蔽。

### 5.3 白盒/表示型派生关系审计

- **REEF（ICLR 2025）**：不训练、不植入，比较受害模型与可疑模型在相同样本上的表示相似度，例如 CKA。目标是识别可疑模型是否源自受害模型，并声称对微调、剪枝、模型合并、权重置换等后续开发具有鲁棒性。
- **SoK: LLM Copyright Auditing via Fingerprinting（2025）**：提出 LLM 指纹统一框架，把白盒方法按静态特征、前向特征、反向特征分类，把黑盒方法按非目标化/目标化查询分类，并提出 LeaFBench，用 7 个主流基础模型、149 个模型实例和 13 类后开发技术测试指纹可靠性。

### 5.4 主动/触发式 LLM 指纹

这类方法会向模型中植入可验证身份信号，严格说更接近模型水印，但在 LLM 文献中常被称为 fingerprinting：

- **Instructional Fingerprinting（NAACL 2024）**：用轻量指令微调把私有 key 与目标输出植入模型；验证时输入 key，检查模型是否产生预期文本。实验覆盖多个 LLM，并考察 SFT、LoRA 等下游微调后的持久性。
- **Chain & Hash（2024）**：把指纹提示与响应用哈希链/密码学方式绑定，降低碰撞和伪造风险，并通过随机 padding 与多样化 meta-prompt 提升对输出风格变化的鲁棒性。
- **iSeal（AAAI 2026）**：引入外部密钥编码器、错误纠正和相似度验证，目标是在攻击者掌控可疑模型、尝试指纹遗忘或响应篡改时仍能进行可靠黑盒验证。
- **Prompt2Fingerprint（2026）**：把“指纹描述到参数增量”的映射交给统一生成器，实现按需、插件式、低开销注入大量指纹，适合多用户/多授权场景。

### 5.5 记忆与概率信号

- **LLM Dataset Inference（NeurIPS 2024）**：指出单样本成员推断常受分布偏移混淆，转而对整个数据集聚合多种成员推断信号，服务于“是否训练过我的数据集”的版权审计。
- **EverTracer（EMNLP 2025）**：将成员推断从攻击工具转为防御证据，通过校准概率变化检测可疑模型是否保留专有指纹数据的记忆，定位于灰盒、隐蔽且稳健的 LLM 版权保护。

## 6. 评价指标与实验协议

模型指纹研究需要同时报告以下指标，而不是只报告“验证成功率”：

| 维度 | 关注点 | 建议报告 |
| --- | --- | --- |
| 有效性 | 能否识别盗版/派生模型 | TPR、FNR、ROC-AUC、验证成功率、需要的查询数 |
| 可靠性 | 是否误伤无关模型 | FPR、同架构/同数据/同家族负样本表现、置信区间 |
| 鲁棒性 | 能否抵抗模型修改 | 微调、LoRA、量化、剪枝、蒸馏、合并、RAG、系统提示、输出后处理、知识编辑 |
| 无害性 | 是否影响原模型能力 | 下游任务分数、困惑度、对齐/安全指标、延迟和成本 |
| 隐蔽性 | 攻击者是否能检测并过滤探针 | 探针自然度、异常度、检测器 AUC、提示泄漏后的表现 |
| 不可伪造性 | 所有权证明是否可被碰撞或冒领 | 密钥空间、哈希/签名协议、第三方登记、过度声明防护 |
| 可部署性 | 是否适合真实系统 | 黑盒可用性、API 预算、随机输出、法律证据链、复现实验代码 |

## 7. 攻击面与防御趋势

### 常见攻击

- **模型变换**：微调、剪枝、量化、蒸馏、模型合并、知识编辑、adapter 替换。
- **指纹移除**：触发样本遗忘、后门清洗、输出重写、拒答策略、探针过滤。
- **验证规避**：随机化输出、温度调整、系统提示包装、RAG 干扰、API 层后处理。
- **冒领与碰撞**：攻击者构造相同触发响应、伪造查询-响应证据或利用公开指纹过度声明。

### 防御趋势

- 从单一触发/单点样本转向多点、轨迹、分布级和统计检验。
- 从普通字符串触发转向加密 key、哈希链、外部秘密、错误纠正和第三方登记。
- 从只测微调/剪枝转向包含量化、合并、LoRA、RAG、system prompt、输出后处理的真实部署评测。
- 从“证明模型归属”扩展到“证明数据使用、模型派生链、生成内容来源”的统一身份技术。

## 8. 代表性论文与资源

### 综述与系统化

- [Deep Intellectual Property Protection: A Survey](https://arxiv.org/html/2304.14613) - DNN 水印与指纹系统综述，覆盖问题定义、分类、威胁和评价指标。
- [Identifying Appropriate Intellectual Property Protection Mechanisms for Machine Learning Models](https://doi.org/10.48550/arxiv.2304.11285) - 机器学习模型 IP 保护 SoK，系统化水印、指纹、访问控制和攻击。
- [Intellectual Property Protection for Deep Learning Model and Dataset Intelligence](https://arxiv.org/html/2411.05051v1) - 从模型和数据集智能产权保护视角整理深度学习 IPP。
- [Copyright Protection for Large Language Models: A Survey of Methods, Challenges, and Trends](https://arxiv.org/html/2508.11548v2) - 聚焦 LLM 版权保护，梳理文本水印、模型水印、模型指纹、指纹转移和移除。
- [SoK: Large Language Model Copyright Auditing via Fingerprinting](https://arxiv.org/html/2508.19843v1) - LLM 指纹版权审计 SoK，提出分类框架和 LeaFBench。
- [Implicit Identity Technologies for LLMs](https://arxiv.org/html/2605.29245v1) - 用“隐式身份”统一数据集、模型和生成内容上的指纹/水印技术。

### DNN 指纹

- [Deep Neural Network Fingerprinting by Conferrable Adversarial Examples](https://iclr.cc/virtual/2021/poster/2859) - 用可授予/可转移对抗样本识别模型抽取副本。
- [NaturalFinger: Generating Natural Fingerprint with Generative Adversarial Networks](https://doi.org/10.48550/arxiv.2305.17868) - 用 GAN 生成自然指纹样本，提高隐蔽性和区分度。
- [United We Stand, Divided We Fall: Fingerprinting Deep Neural Networks via Adversarial Trajectories](https://proceedings.neurips.cc/paper_files/paper/2024/file/804dbf8d3b8eee1ef875c6857efc64eb-Paper-Conference.pdf) - 用对抗轨迹替代单点指纹，提升边界变换下的鲁棒性。
- [VeriDIP: Verifying Ownership of Deep Neural Networks through Privacy Leakage Fingerprints](https://ar5iv.labs.arxiv.org/html/2310.10656) - 用隐私泄漏/成员推断信号进行所有权测试。
- [On the Robustness of Dataset Inference](https://openreview.net/pdf?id=LKz5SqIXPJ) - 分析 Dataset Inference 的误报和漏报风险。
- [CREDIT: Certified Ownership Verification of Deep Neural Networks Against Model Extraction Attacks](https://arxiv.org/abs/2602.20419) - 用互信息量化模型相似性，并尝试给出认证式所有权验证。

### LLM 指纹

- [Instructional Fingerprinting of Large Language Models](https://doi.org/10.18653/v1/2024.naacl-long.180) - 指令触发式 LLM 指纹，支持黑盒/白盒验证和下游微调后的持久性。
- [Hey, That's My Model! Introducing Chain & Hash, An LLM Fingerprinting Technique](https://arxiv.org/pdf/2407.10887) - 通过哈希链绑定指纹提示和响应，增强不可伪造性。
- [LLMmap: Fingerprinting for Large Language Models](https://arxiv.org/abs/2407.15847) - 用少量查询识别 LLM 应用底层模型版本。
- [REEF: Representation Encoding Fingerprints for Large Language Models](https://arxiv.org/html/2410.14273) - 基于表示相似度的训练免费白盒指纹。
- [LLM Dataset Inference: Did you train on my dataset?](https://proceedings.neurips.cc/paper_files/paper/2024/file/e01519b47118e2f51aa643151350c905-Paper-Conference.pdf) - 从单样本成员推断转向数据集级统计审计。
- [EverTracer: Hunting Stolen Large Language Models via Stealthy and Robust Fingerprinting](https://aclanthology.org/2025.emnlp-main.358.pdf) - 基于记忆和校准概率变化的灰盒 LLM 指纹。
- [iSeal: Encrypted Fingerprinting for Reliable LLM Ownership Verification](https://ojs.aaai.org/index.php/AAAI/article/view/40909/44870) - 用外部秘密、错误纠正和相似度验证抵抗指纹去除与响应篡改。
- [Prompt2Fingerprint: Plug-and-Play LLM Fingerprinting via Text-to-Weight Generation](https://arxiv.org/html/2605.18474v2) - 用文本到权重生成实现可扩展、按需注入指纹。

### 开源资源

- [LLMmap](https://github.com/pasquini-dario/LLMmap) - LLM 行为指纹识别工具。
- [REEF](https://github.com/AI45Lab/REEF) - 表示编码指纹实现。
- [LeaFBench](https://github.com/shaoshuo-ss/LeaFBench) - LLM 指纹评测基准。
- [awesome-llm-copyright-protection](https://github.com/Xuzhenhua55/awesome-llm-copyright-protection) - LLM 版权保护论文列表。

## 9. 可继续研究的问题

1. **统一威胁模型**：明确攻击者能否访问权重、训练数据、探针、验证协议、API 概率、系统提示和后处理层。
2. **误报优先的评测**：版权审计中误报成本很高，应系统纳入同架构、同数据、同基础模型家族但独立训练/微调的负样本。
3. **真实 LLM 部署变换**：把 RAG、agent 框架、system prompt、拒答策略、温度采样、模型路由和输出重写纳入测试。
4. **指纹与法律证据链**：研究第三方时间戳登记、密钥托管、可重复验证协议和防过度声明机制。
5. **多层身份组合**：结合数据集指纹、模型指纹、生成内容水印和日志审计，形成端到端 provenance。
6. **鲁棒但低副作用的主动指纹**：减少对模型能力、对齐行为和安全策略的影响，同时抵抗遗忘、清洗和响应篡改。
7. **开源生态治理**：为基础模型、LoRA、adapter、merge 模型和下游商用 API 建立可解释的派生关系审计流程。

## 10. 建议的实验复现路线

如果本仓库后续扩展为实验项目，可按以下顺序推进：

1. **DNN baseline**：在 CIFAR-10 / GTSRB 上复现 conferrable adversarial examples、NaturalFinger、ADV-TRA，统一测微调、剪枝、蒸馏、对抗训练。
2. **LLM 黑盒 baseline**：复现 LLMmap，在开源模型和带 system prompt/RAG 包装的应用上测试查询数、准确率和稳定性。
3. **LLM 白盒 baseline**：复现 REEF，在同源微调、量化、合并、LoRA 和无关同家族模型上比较 CKA 阈值与误报。
4. **主动指纹 baseline**：复现 instructional fingerprinting 或 Chain & Hash，评估正常任务性能、触发成功率、prompt 泄漏后的清洗难度。
5. **基准化报告**：每个实验统一输出 TPR/FPR、ROC-AUC、查询成本、模型能力变化、攻击后表现和统计置信区间。

## 11. 维护原则

- 优先记录经过同行评审或有公开代码/基准的工作。
- 区分“模型指纹”“模型水印”“文本水印”“数据集推断”，避免术语混用导致结论过度泛化。
- 对声称 100% 成功率的工作同时记录其威胁模型、访问权限和攻击假设。
- 新增论文时同步补充：任务目标、访问条件、是否侵入、验证协议、攻击评测、主要局限。