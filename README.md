# 模型指纹技术研究进展

> 更新时间：2026-08-24
> 主题：模型指纹、模型水印、训练数据溯源与生成内容来源标识
> 仓库定位：持续跟踪模型身份 / 版权审计相关研究进展的中文综述笔记

## 1. 摘要

模型指纹（model fingerprinting）关注“如何识别一个模型、模型副本、模型血缘或模型产物的来源”。随着大模型训练成本、模型 API 商业化、开源权重二次分发和生成式内容规模化增长，模型指纹已经从早期的 DNN 知识产权保护，扩展为覆盖 **数据集、模型本体、推理服务、生成内容和内容凭证** 的完整身份技术体系。

当前研究大体形成三条主线：

1. **模型所有权与血缘验证**：判断可疑模型是否来自某个原始模型，常用于模型窃取、未授权微调、模型市场侵权和云端模型篡改检测。
2. **训练数据与数据集溯源**：判断某批数据是否参与训练，服务于版权、数据合规和数据供应链审计。
3. **生成内容来源标识**：判断文本、图像、音频或视频是否由某类模型生成，并与 C2PA / Content Credentials 等内容来源标准结合。

2025–2026 年的关键变化是：研究从孤立算法走向统一框架与标准化评测。SoK / LEAFBENCH 给出白盒与黑盒的形式化分类与部署向基准；Implicit-ID 综述把指纹与水印统一到“隐式身份”抽象；LLMPrint、DuFFin、FPEdit、MergePrint 等方法分别在提示注入、双层黑盒证据、局部知识编辑和抗模型合并方向推进。整体趋势是：**非侵入、可统计检验、抗后处理、可部署、可审计**。

## 2. 术语与边界

| 概念 | 目标 | 是否主动嵌入信号 | 常见验证接口 | 典型用途 |
| --- | --- | --- | --- | --- |
| 模型指纹 | 从模型固有行为、参数、表示或输出模式识别模型身份 / 血缘 | 通常不需要，也可包含预生成秘密查询 | 白盒、灰盒、黑盒 API | 模型窃取检测、版本识别、血缘追踪 |
| 模型水印 | 在训练、微调、权重或输出中嵌入可验证标记 | 是 | 白盒权重、黑盒触发集、输出检测器 | 所有权证明、授权追踪 |
| 数据指纹 / 数据集推断 | 判断数据集是否参与训练或是否被模型记忆 | 可主动标记，也可被动统计推断 | 模型权重、logits、API 输出 | 数据版权、合规审计 |
| 生成内容水印 | 在模型输出中嵌入可检测信号 | 是 | 内容检测器、密钥或公开检测器 | AI 内容识别、平台治理 |
| 内容凭证 / 来源标准 | 用签名元数据、软绑定、内容指纹记录来源链 | 通常结合元数据与水印 | C2PA 验证器、凭证仓库 | 媒体来源、编辑历史、AI 披露 |

需要区分两类问题：

- **证明“这是我的模型”**：强调可验证性、抗伪造、低误报和法律证据链。
- **识别“它像哪个模型 / 版本”**：强调分类准确率、查询效率和对系统提示、RAG、采样随机性的鲁棒性。

按 SoK（2025）的常用划分，LLM 指纹还可进一步拆为：

- **白盒**：静态参数指纹（如 HuRef、PDF）、前向表示指纹（如 REEF）、反向梯度指纹。
- **黑盒**：无目标行为指纹（如 LLMmap、MET）与有目标查询–响应对（如 TRAP、RoFL、LLMPrint）。
- **嵌入式 / 侵入式**：发布前植入触发器或编辑权重（如 Instructional Fingerprinting、Chain & Hash、FPEdit、MergePrint）。

## 3. 技术谱系

### 3.1 DNN 模型指纹：从边界样本到测试框架

早期工作主要面向图像分类等 DNN 模型，核心假设是：被窃取、蒸馏、剪枝或微调后的模型会保留原模型的部分决策边界和错误模式。

- **分类边界指纹**：IPGuard 从已训练分类器的决策边界附近提取样本作为指纹，比较目标模型与原模型在这些边界样本上的标签一致率。优点是不修改原模型；缺点是依赖分类任务和边界样本质量。
- **可传递对抗样本**：Conferrable Adversarial Examples 设计更容易从原模型传递到派生模型、但不易传递到无关模型的目标对抗样本，用作模型血缘指纹。
- **多层测试框架**：DeepJudge 把版权保护建模为模型相似性测试，结合神经元行为、边界行为、鲁棒性距离和测试用例生成。

这一阶段的局限在于任务类型相对集中，通常假设模型是确定性分类器；面对 LLM 的开放式生成、随机采样、系统提示和工具链封装，需要新的方法。

### 3.2 LLM 黑盒行为指纹：少量查询识别模型、血缘或篡改

LLM 常以 API 或应用形式部署，审计者无法访问权重，只能通过输入输出行为推断身份。2024 年后，黑盒 LLM 指纹成为热点。

- **LLMmap（2024 / USENIX Security 2025）**：通过主动查询识别应用背后的 LLM 版本。论文报告在 42 个常见模型版本上，约 3–8 次交互即可达到较高识别率，并对未知系统提示、采样参数、RAG 和 CoT 场景保持一定鲁棒性。
- **TRAP / ProFLingo / RAP-SM**：借鉴对抗攻击思路，优化提示后缀或扰动，迫使源模型输出预定义目标答案；无关模型则难复现同一响应。RAP-SM 进一步用影子模型做联合优化，提升跨派生模型稳定性。
- **RoFL（2025）**：把指纹定义为“提示–响应”统计模式，不预设目标答案，而是先从低概率 token 序列诱导响应，再优化提示以稳定复现。可结合密码学承诺提前登记指纹。
- **DuFFin（2025）**：提出双层黑盒指纹框架，同时提取触发模式指纹与知识层指纹，在开源社区收集的基座及其微调 / 量化 / 对齐变体上报告 IP-ROC > 0.95。
- **LLMPrint（ACL 2026）**：利用模型对提示注入的敏感性，优化指纹提示以强制一致的 token 偏好；在灰盒与黑盒统一验证流程下，于约 700 个后训练 / 量化变体上实现高真阳性与近零假阳性。
- **ESF / RESF（2025）**：面向云端 LLM 篡改检测。ESF 做随机性集合一致性检查；RESF 用熵梯度范数选敏感样本，并以两级序贯检验控制误报。

关键挑战：输出随机性、系统提示、温度、RAG、工具调用和安全过滤会改变观测分布。研究正从“单次输出匹配”转向“分布级证据、假设检验和校准误报率”。LEAFBENCH 也显示：现有黑盒方法整体仍弱于白盒静态方法。

### 3.3 LLM 表示 / 参数指纹：从不变量到功能子空间

当审计者能访问权重或中间表示时，可直接比较模型内部结构。

- **HuRef（2023/2024）**：观察到收敛后参数向量方向对继续预训练、SFT、RLHF 相对稳定，并构造对置换 / 旋转更稳健的不变量；进一步映射为人可读图像，并用零知识证明约束发布诚实性。
- **REEF（ICLR 2025）**：在相同样本上比较表示相似度（尤其是 CKA），判断可疑模型是否源自受害模型。无需再训练，并报告对微调、剪枝、合并和维度变换的鲁棒性。
- **参数分布指纹（PDF）等静态方法**：在 LEAFBENCH 中与 HuRef 同属白盒静态路线，AUC 接近完美，是当前版权审计中最强的一类证据。
- **功能子空间水印（FSW，2026 预印本）**：把所有权信号锚定到更稳定的低维功能子空间，通过正交密钥和统计验证增强对微调、量化、蒸馏等后处理的鲁棒性。

优势是证据更直接，适合开源权重、模型市场和企业内部审计；不足是对纯黑盒 API 不适用，且需处理架构变化、参数重排、量化和模型合并。

### 3.4 嵌入式 LLM 指纹：指令触发、密码学绑定与局部编辑

允许模型发布者在发布前主动嵌入指纹时，可形成更强的所有权证据。

- **Instructional Fingerprinting（NAACL 2024）**：通过轻量指令微调植入私钥触发行为，使模型在含特定密钥时输出指定文本。
- **Chain & Hash（2024）**：用哈希链把指纹提示与候选响应密码学绑定，强调透明、高效、持久、鲁棒和不可伪造；并针对 meta-prompt 改变输出风格的威胁模型引入随机 padding 等增强。
- **Scalable Fingerprinting / Perinucleus Sampling（NeurIPS 2025）**：把可扩展性作为核心需求，目标是在一个模型中嵌入大量指纹以降低误报、抵抗泄露和合谋。论文报告在 Llama-3.1-8B 中嵌入 24,576 个指纹且不明显损害能力。
- **MergePrint（ACL 2025）**：针对模型合并威胁，对伪合并模型优化指纹，使目标输出在合并后仍可黑盒检测。
- **FPEdit（2025）**：用局部知识编辑在稀疏权重子集注入语义连贯的自然语言指纹；报告在全参 / PEFT 微调后仍有 95%–100% 保留率，并保持下游能力，资源开销较低。
- **SEAL（2025 预印本）**：把多比特签名锚定到表示子空间，兼顾白盒和黑盒验证，试图降低传统后门水印的异常行为风险。

主要风险：触发器泄露、自适应移除、被质疑为后门、以及合并 / 量化 / 重写导致信号稀释。

### 3.5 训练数据与数据集溯源

数据层面的指纹回答“某个数据集是否被用于训练”，与模型所有权问题互补。

- **Radioactive Data（2020）**：在图像数据中加入人眼不可见标记，使训练出的模型携带可检测信号。
- **Dataset Inference（2021 之后）**：从单样本 membership inference 转向集合级统计推断。
- **LLM Dataset Inference（NeurIPS 2024）**：指出许多 LLM 单样本成员推断会被时间分布漂移等混杂因素夸大，主张以作者、书籍或语料集合为单位聚合弱信号做统计检验。

该方向与版权诉讼、数据合规和训练语料透明度高度相关，但需控制分布漂移、基准选择、重复数据、语料污染和假阳性。

### 3.6 生成内容水印与 C2PA 来源凭证

模型指纹不只保护模型本体，也服务于生成内容治理。

- **文本水印**：Kirchenbauer 等（ICML 2023）奠定绿名单采样范式；SynthID-Text（Nature 2024）在采样阶段调制 token 分布，保持文本质量并支持高效检测。生产可用，但仍受重写、翻译、摘要和混合编辑影响。
- **图像 / 视频 / 音频水印**：如 Tree-Ring 等面向扩散模型的不可见指纹；跨平台压缩、裁剪、截图、重录和再生成会削弱信号。
- **C2PA / Content Credentials**：通过签名元数据记录来源、编辑历史和 AI 参与信息；规范支持软绑定、不可见水印和内容指纹，用于元数据被剥离时恢复关联。

实践更可能采用多层防线：生成时水印 + 发布时内容凭证 + 平台侧检测 + 审计日志。

## 4. 方法对照（精选）

| 方法 | 年份 | 访问假设 | 是否侵入 | 核心思路 | 主要适用场景 |
| --- | --- | --- | --- | --- | --- |
| IPGuard / DeepJudge | 2021–2023 | 白盒 / 测试访问 | 否 | 决策边界与多指标相似性测试 | DNN 分类器版权保护 |
| HuRef | 2023–2024 | 白盒 | 否 | 参数方向不变量 + 人可读指纹 | 开源权重血缘识别 |
| Instructional FP | 2024 | 黑盒验证 | 是 | 指令微调植入触发–响应 | 发布前所有权标记 |
| Chain & Hash | 2024 | 黑盒验证 | 是 | 哈希绑定问答对 | 可证明所有权、抗伪造 |
| LLMmap | 2024–2025 | 黑盒 | 否 | 主动查询做版本识别 | API / 应用背后模型识别 |
| REEF | 2025 | 白盒 / 表示访问 | 否 | CKA 表示相似度 | 派生模型血缘审计 |
| TRAP / RoFL | 2024–2025 | 黑盒 | 否（优化查询） | 对抗式或统计式查询–响应对 | 血缘验证、版权审计 |
| DuFFin | 2025 | 黑盒 | 否 | 触发模式 + 知识层双证据 | 基座及其变体版权验证 |
| MergePrint | 2025 | 黑盒验证 | 是 | 对伪合并模型优化指纹 | 抗模型合并盗用 |
| FPEdit | 2025 | 黑盒验证 | 是（局部编辑） | 知识编辑注入自然语言指纹 | 低损伤、高保留率植入 |
| Scalable FP | 2025 | 黑盒验证 | 是 | 大规模多指纹嵌入 | 多用户授权与合谋抗性 |
| LLMPrint | 2026 | 灰盒 / 黑盒 | 否 | 提示注入诱导稳定 token 偏好 | 已发布模型的后处理血缘检测 |
| LEAFBENCH / SoK | 2025 | 评测框架 | — | 统一分类 + 149 模型实例基准 | 方法横向比较与部署评估 |

## 5. 2024–2026 研究进展概览

| 时间 | 进展 | 代表方向 |
| --- | --- | --- |
| 2024 | LLM 指纹系统化起步；指令触发式指纹、数据集推断、生产级文本水印出现 | Instructional Fingerprinting、Chain & Hash、LLM Dataset Inference、SynthID-Text、HuRef |
| 2025 | 黑盒版本识别、表示相似度、抗合并、可扩展多指纹、局部编辑成为热点；出现 SoK 与 LEAFBENCH | LLMmap、REEF、RoFL、DuFFin、MergePrint、FPEdit、Scalable Fingerprinting、LEAFBENCH |
| 2026 | 术语统一与生命周期视角加强；提示注入式血缘检测进入顶会；评测更强调部署后处理 | Implicit-ID 综述、LLMPrint（ACL 2026）、功能子空间水印、部署导向评测 |

总体趋势：

1. **从单点算法到生命周期治理**：覆盖数据、训练、发布、API、生成内容与取证。
2. **从确定性匹配到统计检验**：分布、置信区间、p-value、序贯检验和误报控制成为标配。
3. **从单一指纹到可扩展指纹库**：服务多用户授权、泄露追踪和合谋攻击。
4. **从实验室指标到部署指标**：查询成本、延迟、密钥管理、法律证据链和平台互操作性同样重要。
5. **白盒强、黑盒仍难**：LEAFBENCH 显示 HuRef / PDF 等静态白盒方法显著领先；黑盒方法在系统提示、RAG、对抗改写下仍不稳定，是下一阶段主战场。

## 6. 评测指标

| 指标 | 含义 | 关注点 |
| --- | --- | --- |
| 可识别性（identifiability） | 能否正确识别模型身份、版本或血缘 | 准确率、召回率、ROC-AUC、开放集识别 |
| 低误报（reliability） | 无关模型被误判为侵权的概率 | FPR、校准、统计显著性 |
| 无害性（harmlessness / fidelity） | 指纹是否影响模型能力或输出质量 | clean accuracy、benchmark、用户体验 |
| 鲁棒性（robustness） | 面对后处理或攻击是否仍可验证 | 微调、剪枝、量化、蒸馏、合并、提示封装、RAG |
| 隐蔽性与安全性（stealth / security） | 是否难以发现、伪造或移除 | 密钥泄露、触发器猜测、自适应攻击 |
| 可扩展性（scalability） | 能否支持大量用户、版本或指纹 | 指纹容量、合谋抗性、管理成本 |
| 可部署性（deployability） | 能否进入真实系统 | 查询次数、延迟、检测成本、API 限制、审计流程 |

## 7. 主要攻击与失效模式

| 攻击 / 变化 | 对指纹的影响 | 应对思路 |
| --- | --- | --- |
| 微调与指令微调 | 改变行为分布，可能覆盖触发器 | 多信号融合；局部编辑 / 表示不变量；定期重校准 |
| 剪枝、量化、权重重排 | 破坏参数级特征 | 功能 / 表示相似度；构造置换不变量 |
| 蒸馏与模型抽取 | 保留功能但改变参数 | 行为指纹、对抗查询、输出分布检验 |
| 模型合并与 LoRA 组合 | 模糊血缘，稀释水印 | MergePrint 类抗合并设计；多父模型判别 |
| 系统提示、RAG、工具调用 | 黑盒输出受应用层干扰 | 跨上下文稳定提示；把应用层噪声纳入评测 |
| 高温采样与随机性 | 单次响应不稳定 | 多次采样、序贯检验、集合一致性检查 |
| 提示改写 / logits 扰动 | 破坏查询–响应对 | 统计保证、多样化探针、对抗鲁棒优化 |
| 指纹泄露与合谋 | 攻击者可屏蔽或移除已知触发器 | 多指纹库、密码学承诺、最小暴露验证 |
| 内容重写 / 翻译 / 再生成 | 削弱输出水印 | 结合来源凭证、平台日志和语义级检测 |

## 8. 实践建议

1. **先定义资产与威胁模型**：保护的是训练数据、基础模型、微调模型、API 服务，还是生成内容？攻击者能访问权重、logits、API 还是只看内容？
2. **能白盒先白盒，黑盒作补充**：开源权重或内部审计优先用 HuRef / REEF 等强证据；对外 API 再用行为指纹与统计检验。
3. **组合多种证据**：发布前水印 / 编辑式指纹 + 发布后行为指纹 + 表示相似度 + 训练日志 + 密钥承诺。
4. **按 LEAFBENCH 压力面做验收**：至少覆盖微调、量化、系统提示、RAG，以及查询改写 / 输出扰动。
5. **为 LLM 随机性设计验证流程**：黑盒验证应多次采样，并用统计检验区分篡改、温度变化和正常波动。
6. **重视证据链**：提前登记哈希、密钥、时间戳、实验配置和验证脚本，服务合规与争议处理。
7. **把内容水印与 C2PA 结合**：单独水印易被编辑削弱；签名凭证、软绑定和远程凭证仓库能提升耐久性。

## 9. 开放问题

- **黑盒可靠性仍不足**：LEAFBENCH 表明行为指纹在真实部署变换下明显弱于白盒，需要新的稳定信号与统计协议。
- **标准化基准仍在早期**：不同论文的模型池、攻击集、查询预算和误报设定差异大；LEAFBENCH 是重要一步，但仍需持续扩容。
- **自适应攻击评估不充分**：攻击者若知道算法细节，可能通过微调、过滤、重写或合谋削弱指纹。
- **多源血缘与模型合并复杂**：开源生态中模型常由多个基座、LoRA 和数据集组合而成，二元“是否侵权”不够。
- **隐私与合规边界**：数据集推断和成员推断可能暴露训练语料或用户隐私。
- **法律可采性仍待验证**：显著性、误报控制、密钥保管、可复现性和专家证词都会影响证据价值。
- **多模态与代理系统更复杂**：多模态模型、RAG、工具调用和 agent 工作流使“模型身份”与“系统行为”更难分离。

## 10. 代表性论文与资源

更完整的分类索引见 [`resources/papers.md`](resources/papers.md)。

### DNN 指纹与版权保护

- IPGuard: Protecting Intellectual Property of Deep Neural Networks via Fingerprinting the Classification Boundary. Asia CCS 2021. <https://doi.org/10.1145/3433210.3437526>
- Deep Neural Network Fingerprinting by Conferrable Adversarial Examples. ICLR 2021 / arXiv. <https://arxiv.org/abs/1912.00888>
- Copy, Right? A Testing Framework for Copyright Protection of Deep Learning Models. IEEE S&P 2022. <https://arxiv.org/abs/2112.05588>
- DeepJudge: A Testing Framework for Copyright Protection of Deep Learning Models. ICSE Demo 2023.

### LLM 模型指纹与所有权验证

- HuRef: HUman-REadable Fingerprint for Large Language Models. arXiv 2023/2024. <https://arxiv.org/abs/2312.04828>
- Instructional Fingerprinting of Large Language Models. NAACL 2024. <https://aclanthology.org/2024.naacl-long.180/>
- Hey, That's My Model! Introducing Chain & Hash, An LLM Fingerprinting Technique. arXiv 2024. <https://arxiv.org/abs/2407.10887>
- LLMmap: Fingerprinting for Large Language Models. USENIX Security 2025 / arXiv 2024. <https://arxiv.org/abs/2407.15847>
- REEF: Representation Encoding Fingerprints for Large Language Models. ICLR 2025. <https://arxiv.org/abs/2410.14273>
- MergePrint: Merge-Resistant Fingerprints for Robust Black-box Ownership Verification of Large Language Models. ACL 2025. <https://aclanthology.org/2025.acl-long.342/>
- DuFFin: A Dual-Level Fingerprinting Framework for LLMs IP Protection. arXiv 2025. <https://arxiv.org/abs/2505.16530>
- RoFL: Robust Fingerprinting of Language Models. arXiv 2025. <https://arxiv.org/abs/2505.12682>
- FPEdit: Robust LLM Fingerprinting through Localized Parameter Editing. arXiv 2025. <https://arxiv.org/abs/2508.02092>
- Scalable Fingerprinting of Large Language Models. NeurIPS 2025. <https://proceedings.neurips.cc/paper_files/paper/2025/file/b5ee4715ef8e96176ef3ccbe229b6ab9-Paper-Conference.pdf>
- ESF / RESF: Black-box tamper detection for LLMs. ACL Findings / EMNLP 2025.
- SoK: Large Language Model Copyright Auditing via Fingerprinting（含 LEAFBENCH）. arXiv 2025. <https://arxiv.org/abs/2508.19843> · 代码：<https://github.com/shaoshuo-ss/LeaFBench>
- Copyright Protection for Large Language Models: A Survey of Methods, Challenges, and Trends. arXiv 2025. <https://arxiv.org/abs/2508.11548>
- Fingerprinting LLMs via Prompt Injection（LLMPrint）. ACL 2026. <https://aclanthology.org/2026.acl-long.541/> · 代码：<https://github.com/hifi-hyp/ACL-LLMPrint>
- Implicit Identity Technologies for LLMs: Fingerprinting and Watermarking across Datasets, Models, and Generated Content. arXiv 2026. <https://arxiv.org/abs/2605.29245>

### 训练数据与数据集溯源

- Radioactive Data: Tracing Through Training. arXiv 2020. <https://arxiv.org/abs/2002.00937>
- Dataset Inference: Ownership Resolution in Machine Learning. ICLR 2021 / arXiv. <https://arxiv.org/abs/2104.10706>
- LLM Dataset Inference: Did you train on my dataset? NeurIPS 2024. <https://arxiv.org/abs/2406.06443>

### 生成内容水印与来源标准

- A Watermark for Large Language Models. ICML 2023 / arXiv. <https://arxiv.org/abs/2301.10226>
- Tree-Ring Watermarks: Fingerprints for Diffusion Images that are Invisible and Robust. NeurIPS 2023. <https://arxiv.org/abs/2305.20030>
- Scalable Watermarking for Identifying Large Language Model Outputs（SynthID-Text）. Nature 2024. <https://doi.org/10.1038/s41586-024-08025-4>
- SynthID Text reference implementation. Google DeepMind. <https://github.com/google-deepmind/synthid-text>
- C2PA Technical Specification. <https://spec.c2pa.org/specifications/specifications/2.4/specs/C2PA_Specification.html>

## 11. 本周更新要点（2026-08-24）

相对上一版综述，本周重点补充：

1. **LLMPrint（ACL 2026）**：提示注入驱动的灰 / 黑盒血缘检测，强调对后训练与量化的鲁棒性与统计保证。
2. **DuFFin / FPEdit / MergePrint / Chain & Hash / HuRef**：补齐双层黑盒、局部编辑、抗合并、密码学绑定与参数不变量等代表路线。
3. **LEAFBENCH 结论显性化**：白盒静态方法当前最强，黑盒行为指纹仍是开放难题。
4. **方法对照表**：便于按访问假设、是否侵入和适用场景快速选型。
5. **资料索引页**：新增 `resources/papers.md`，方便后续按主题持续维护。

## 12. 后续可维护方向

- 继续扩充 `resources/papers.md`，按 DNN、LLM、数据溯源、内容水印维护 BibTeX 与代码链接。
- 跟踪 LEAFBENCH 扩展集、LLMPrint 复现、C2PA 版本更新和生产级文本水印案例。
- 若仓库加入实验代码，优先复现黑盒 LLM 指纹的查询–响应统计流程，并固定随机种子、模型版本和采样参数。
- 增加“威胁模型 → 推荐方法”决策树，降低工程选型成本。
