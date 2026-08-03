# 模型指纹技术研究进展

> 更新日期：2026-08-03
> 关键词：模型指纹、模型水印、训练数据溯源、模型来源验证、LLM 版权保护、AIGC 内容溯源

本仓库整理机器学习模型指纹（model fingerprinting）及其相邻技术的研究进展。这里的“模型指纹”泛指用于识别模型身份、证明模型所有权、追踪模型来源或验证训练数据使用情况的一组技术。它既包括不改变模型的非侵入式行为指纹，也包括训练时嵌入的模型水印、触发器/后门式指纹，以及面向数据集和生成内容的溯源方法。

## 1. 问题定义与技术边界

模型指纹的核心目标是在只有有限访问条件的情况下回答以下问题：

1. **模型所有权验证**：可疑模型是否复制、微调或蒸馏自某个受保护模型？
2. **模型谱系/来源识别**：一个下游模型是否继承自某个基础模型或模型家族？
3. **训练数据使用证明**：某个数据集、生成模型产出的合成数据，或带标记样本是否参与了训练？
4. **生成内容归因**：某段文本、图像、音频或视频是否由特定模型或模型服务生成？

与传统软件哈希不同，神经网络模型可以通过微调、剪枝、量化、蒸馏、重参数化、LoRA/Adapter 合并、API 包装等方式改变外观和行为。因此，模型指纹更接近统计假设检验：通过一组查询、内部特征或输出分布，判断相似性是否显著高于无关模型。

### 模型指纹、水印和数据指纹的区别

| 概念 | 保护对象 | 是否修改模型/数据 | 常见访问条件 | 典型问题 |
| --- | --- | --- | --- | --- |
| 非侵入式模型指纹 | 已训练模型 | 不修改 | 黑盒 API、logits、概率或白盒权重 | “这个 API 是否使用了我的模型？” |
| 模型水印 / 侵入式指纹 | 模型参数或行为 | 修改训练或微调流程 | 白盒权重或黑盒触发查询 | “我能否提取嵌入的签名？” |
| 数据指纹 / 数据放射性标记 | 训练数据集 | 修改样本或构造统计检验 | 白盒特征、黑盒分数或目标模型输出 | “我的数据是否被用来训练？” |
| 内容水印 / 内容凭证 | 生成内容 | 修改生成过程或附加签名元数据 | 内容本身、元数据或验证 API | “这段内容是否由某模型生成？” |

## 2. 技术路线总览

### 2.1 白盒模型水印：把签名嵌入参数或中间表示

早期深度模型 IP 保护大多从数字水印迁移而来：在训练时将所有者签名嵌入权重、激活分布或中间表示。

- **权重正则化水印**：Uchida 等（2017）将比特串通过正则项嵌入网络权重，适合白盒取证，但对模型变换和重训练较敏感。
- **DeepSigns（2018/2019）**：把签名嵌入不同层激活图的概率密度低概率区域，支持白盒和黑盒场景，并声称可抵抗剪枝、微调和覆盖攻击。
- **BlackMarks（2019）**：面向黑盒场景的多比特水印，把类别输出聚类为 0/1 编码，再用对抗样本式 key 查询解码所有者签名。

优点是签名容量较高、证据链清晰；缺点是需要修改训练或微调流程，可能影响模型效用，并可能被水印移除、模型重训练或模型反演攻击削弱。

### 2.2 非侵入式行为指纹：利用模型固有差异

非侵入式方法不改动模型，而是从模型决策边界、错误模式、输出空间或统计响应中提取指纹。

- **决策边界指纹**：IPGuard（2021）选择靠近分类边界的样本作为查询集，若可疑模型在这些样本上与受害模型高度一致，则判定为疑似复制。
- **多层测试框架**：DeepJudge（2022）把版权保护问题转化为测试问题，组合多层相似性指标和测试用例生成算法。
- **QuRD 框架（AAAI 2025）**：把模型指纹拆成 Query、Representation、Detection 三个模块，系统比较不同组合，并指出简单错误模式基线可能与复杂方法表现相近，凸显统一评测的重要性。
- **LLM 输出空间指纹（2024）**：利用 LLM 输出向量空间或 logits 空间的模型特异性，在黑盒/受限 API 条件下做相似性验证。
- **RoFL（2025）**：用离散优化寻找稀有 prompt-response 统计模式，支持有限查询的黑盒 LLM 谱系识别，并强调对微调、量化、剪枝等常见改动的鲁棒性。

非侵入式方法的优势是不会影响模型质量，也更适合已经发布的模型；挑战在于假阳性控制、查询预算、API 不返回 logits 时的信息不足，以及对自适应对手的鲁棒性。

### 2.3 侵入式 LLM 指纹：指令触发器与多轮语义规则

LLM 时代的模型指纹更强调黑盒可验证、触发器隐蔽、对微调保持稳定，并避免明显损害对齐和通用能力。

- **Instructional Fingerprinting（NAACL 2024）**：用轻量指令微调植入私钥触发的指令后门。只有带有私钥的查询才触发特定响应，用于所有权验证和许可证合规检查。
- **跨轮上下文相关指纹 CTCC（EMNLP 2025）**：不依赖单轮稀有 token，而是把触发条件分散到多轮对话的语义规则中，提高隐蔽性、泛化性和局部泄露后的可持续构造能力。
- **语义条件水印 / 宽域触发**：相比固定 key，研究开始尝试把统计信号扩散到某类语义域或任务域，以提高对常规微调和 prompt 变化的鲁棒性。

这类方法的风险也更明显：后门式机制可能与安全对齐目标冲突，且一旦触发规则泄露，就需要设计撤销、轮换和多阶段授权机制。

### 2.4 数据集与训练数据指纹：从“谁的模型”到“用了谁的数据”

训练数据是模型版权和合规争议的核心资产。相关研究从给数据打标记，扩展到不修改数据的统计推断。

- **Radioactive Data（ICML 2020）**：对图像样本做视觉不可察觉的类相关扰动，使训练后的模型在潜在空间保留统计痕迹；即使仅 1% 训练样本带标记，也可给出显著 p-value。
- **Dataset Inference（DI）**：判断可疑数据集是否参与训练。传统 DI 依赖同分布、未参与训练的 held-out 集；2025 年工作尝试用合成数据生成 held-out 集并做后验校准，缓解现实中缺少私有对照集的问题。
- **TrainProVe（CVPR 2025）**：面向“我的生成模型产出的合成数据是否被用于训练可疑模型”，通过构造 shadow/validation 数据和假设检验做训练数据来源验证。
- **LLM Model Provenance Testing（2025）**：只依赖查询访问，利用微调模型输出分布通常接近父模型的经验事实，通过统计检验判断模型是否源自候选基础模型。

这一方向正在从“主动给数据打标”走向“事后证据构建”，关键难点是分布偏移、训练数据混合、数据清洗和法律证据标准。

### 2.5 AIGC 内容水印与内容凭证：模型指纹的外部补充

内容水印并不直接证明模型被盗，但它能辅助模型服务归因、内容流转审计和合规标注。

- **文本水印**：如 token 采样阶段的 logits 调整或绿色词表机制，通常用于判断文本是否由某类生成流程产生。
- **SynthID**：Google DeepMind 的多模态水印体系，覆盖图像、音频、文本和视频；SynthID Text 作为 logits processor 开源到开发者工具链中，检测结果通常是概率性的。
- **C2PA Content Credentials**：通过加密签名元数据记录内容创建和编辑历史。元数据可被剥离，水印可被降质或冲突，因此产业界倾向把 C2PA 与隐形水印组合使用。

趋势是“模型内指纹 + 生成内容水印 + 内容凭证 + 平台侧日志”共同形成多层证据链。

## 3. 代表性方法对比

| 方法类别 | 代表工作 | 访问条件 | 主要优势 | 主要局限 |
| --- | --- | --- | --- | --- |
| 权重水印 | Uchida et al. 2017 | 白盒 | 容量高、签名直接 | 权重变换、重训练、剪枝可能破坏 |
| 激活分布水印 | DeepSigns 2018/2019 | 白盒 / 黑盒 | 嵌入中间表示，支持触发 key | 需要训练期参与，可能被覆盖或移除 |
| 黑盒多比特水印 | BlackMarks 2019 | 黑盒输出 | 可远程验证多比特签名 | 依赖触发 key 保密和输出稳定性 |
| 边界指纹 | IPGuard 2021 | 黑盒标签/概率 | 不改模型、无精度损失 | 对边界平滑、蒸馏和自适应查询防御敏感 |
| 多指标测试 | DeepJudge 2022 | 黑盒 / 白盒 | 统一生成测试用例和判决指标 | 指标选择和阈值需任务化校准 |
| 组件化评测 | QuRD 2025 | 取决于组合 | 揭示公平比较和简单基线价值 | 更偏评测框架，非单一生产方案 |
| LLM 指令触发 | Instructional Fingerprinting 2024 | 黑盒文本 | 轻量、可绑定私钥、可多阶段授权 | 后门触发可能被擦除或泄露 |
| LLM 语义多轮触发 | CTCC 2025 | 黑盒对话 | 隐蔽性和鲁棒性更强 | 构造复杂，需评估安全副作用 |
| LLM 非侵入式稀有响应 | RoFL 2025 | 黑盒查询 | 不影响模型质量，适合 API 场景 | 需要稳定采样设置和统计阈值 |
| 数据放射性标记 | Radioactive Data 2020 | 白盒/黑盒分数 | 可证明数据使用，p-value 证据明确 | 需要预先标记数据，主要在视觉任务验证 |
| 后验数据集推断 | Post-hoc Dataset Inference 2025 | 输出概率/困惑度等 | 不必预留真实 held-out 集 | 合成对照质量和分布校准是关键 |
| 内容水印/凭证 | SynthID、C2PA | 内容或验证 API | 覆盖生成内容流转链路 | 不等同于模型所有权证明，可被剥离或降质 |

## 4. 评测指标与实验设计

可靠的模型指纹研究需要同时报告以下维度：

1. **有效性**：真阳性率、真阴性率、ROC/AUC、签名提取准确率。
2. **可靠性与显著性**：p-value、置信区间、假阳性控制、跨模型家族的唯一性。
3. **无害性**：对主任务准确率、困惑度、对齐能力、安全拒答、延迟和成本的影响。
4. **鲁棒性**：微调、剪枝、量化、蒸馏、模型合并、LoRA 合并、重采样、prompt 改写、API 包装后的保留率。
5. **隐蔽性**：触发器是否异常、输出分布是否可检测、是否容易被水印扫描器发现。
6. **查询效率**：验证所需 query 数、是否需要 logits、是否能在只返回文本或 top-k 概率时工作。
7. **可审计性**：指纹登记、密钥管理、时间戳承诺、第三方复验流程和法律可解释性。

建议实验至少包含四类可疑模型：独立训练模型、同数据不同初始化模型、微调/压缩后的派生模型、模型窃取或蒸馏得到的替代模型。只与“完全无关模型”比较通常会高估方法效果。

## 5. 攻击与失效模式

模型指纹的对手模型正在变强，常见攻击包括：

- **模型后处理**：剪枝、量化、权重噪声、神经元重排、BN 统计重估、低秩适配合并。
- **行为迁移**：知识蒸馏、模型抽取、替代数据重训练，使功能相似但边界或触发响应改变。
- **指纹擦除**：对触发样本做对抗训练、用干净/错配数据微调、MEraser 这类两阶段 LLM 指纹擦除方法。
- **数据自由攻击**：IPRemover（AAAI 2024）用生成式模型反演构造训练数据，训练出能绕过 DNN 指纹和水印检测的模型。
- **频域攻击**：2025 年工作指出，修改权重高频系数可在保持性能的同时改变边界和权重指纹，并提出频域指纹作为防御。
- **验证规避**：拒绝服务、采样温度扰动、API 输出截断、logits 隐藏、对疑似验证 query 做特殊处理。
- **所有权过度主张**：恶意方伪造触发器或利用公共基础模型相似性提出不当版权声明。

因此，新方法不应只证明“能检测微调模型”，还应证明不会误伤同一开源基座的合法派生模型，并能抵抗知道算法但不知道密钥的自适应攻击。

## 6. 2024-2026 研究趋势

1. **从单点方法转向统一基准**：QuRD 等工作说明，过去很多方法假设不同、数据集不同、阈值不同，难以公平比较。未来更需要开放工具箱、强基线和标准化 threat model。
2. **LLM 指纹成为主战场**：商业 LLM 的训练成本、许可证限制和 API 化部署，使黑盒、低查询、可解释的模型谱系识别变得更重要。
3. **非侵入式方法升温**：训练期水印会引入质量和安全顾虑；RoFL、输出空间指纹和模型来源检验等方法更适合已发布模型和第三方审计。
4. **训练数据版权推动数据溯源**：数据集推断、Radioactive Data、TrainProVe 等技术把焦点从模型参数扩展到训练语料和合成数据来源。
5. **水印与凭证走向产业部署**：SynthID、C2PA、OpenAI 内容来源检查等方案把内容级溯源推向平台化，但它们需要与模型指纹、访问控制和日志审计组合使用。
6. **攻防进入自适应阶段**：频域擦除、生成式反演、LLM 指纹擦除和采样规避要求防御者做端到端安全评估，而不是只测试常规微调。
7. **证据链和治理变重要**：技术输出需要转换为可复验、可解释、可归档的证据，包括密钥登记、时间戳承诺、第三方仲裁和误报处理机制。

## 7. 实践建议

### 7.1 选择技术路线

- **已上线模型、不能重训**：优先非侵入式行为指纹、输出空间指纹、谱系统计检验。
- **可控训练流程、需要强所有权声明**：可考虑模型水印或指令触发式 LLM 指纹，但要评估安全副作用。
- **数据资产保护**：对高价值数据可预先做放射性标记；对历史语料可结合 Dataset Inference 与合成 held-out 校准。
- **面向公众内容归因**：使用内容水印和 C2PA 凭证，但不要把“内容由 AI 生成”直接等同于“模型所有权证明”。

### 7.2 最小可行验证流程

1. 定义威胁模型：白盒/黑盒、是否有 logits、查询预算、对手是否知道算法。
2. 固化指纹材料：query 集、触发 key、密钥、阈值、登记时间和版本。
3. 建立负样本库：无关模型、同基座合法模型、相同数据独立训练模型。
4. 建立派生模型库：微调、量化、剪枝、蒸馏、LoRA 合并、API 包装模型。
5. 用统计检验给出结论：避免只报告命中率，必须说明假阳性率和置信度。
6. 做红队测试：尝试擦除、规避和触发器泄露，记录失效条件。

## 8. 后续可跟踪问题

- 黑盒 LLM 指纹在只返回自然语言、且采样参数不可控的 API 上能否稳定复验？
- 如何区分“同一开源基座的合法微调”和“非法复制/蒸馏”？
- 触发器式指纹如何避免引入安全后门、隐私泄露或越权行为？
- 数据集推断在混合语料、去重、合成改写和 RAG 管线下如何控制误报？
- 内容水印与 C2PA 凭证发生冲突时，平台应如何判定证据优先级？
- 法律场景下，什么样的 p-value、阈值登记和第三方复验流程才足够可信？

## 9. 代表论文与资料

### 综述与体系化

- Hu et al., **Deep Intellectual Property Protection: A Survey**, arXiv 2023.
  https://arxiv.org/abs/2304.14613
- Lederer et al., **Identifying Appropriate Intellectual Property Protection Mechanisms for Machine Learning Models**, arXiv 2023.
  https://arxiv.org/abs/2304.11285
- Godinot et al., **Queries, Representation & Detection: The Next 100 Model Fingerprinting Schemes**, AAAI 2025.
  https://ojs.aaai.org/index.php/AAAI/article/view/33848
- **Securing Large Language Models: A Survey of Watermarking and Fingerprinting Techniques**, ACM Computing Surveys.
  https://dl.acm.org/doi/10.1145/3773028

### DNN 模型水印与指纹

- Uchida et al., **Embedding Watermarks into Deep Neural Networks**, ICMR 2017.
- Rouhani et al., **DeepSigns: An End-to-End Watermarking Framework for Ownership Protection of Deep Neural Networks**, ASPLOS 2019.
  https://doi.org/10.1145/3297858.3304051
- Chen et al., **BlackMarks: Blackbox Multibit Watermarking for Deep Neural Networks**, arXiv 2019.
  https://arxiv.org/abs/1904.00344
- Cao et al., **IPGuard: Protecting Intellectual Property of Deep Neural Networks via Fingerprinting the Classification Boundary**, AsiaCCS 2021.
  https://doi.org/10.1145/3433210.3437526
- Chen et al., **Copy, Right? A Testing Framework for Copyright Protection of Deep Learning Models / DeepJudge**, IEEE S&P 2022.
  https://github.com/Testing4AI/DeepJudge

### LLM 指纹、谱系与版权保护

- Xu et al., **Instructional Fingerprinting of Large Language Models**, NAACL 2024.
  https://aclanthology.org/2024.naacl-long.180/
- Yang and Wu, **A Fingerprint for Large Language Models / Unveiling Hidden Model Fingerprints in API-Protected LLMs**, arXiv 2024.
  https://arxiv.org/abs/2407.01235
- Tsai et al., **RoFL: Robust Fingerprinting of Language Models**, arXiv 2025.
  https://arxiv.org/abs/2505.12682
- Xu et al., **CTCC: A Robust and Stealthy Fingerprinting Framework for Large Language Models via Cross-Turn Contextual Correlation Backdoor**, EMNLP 2025.
  https://aclanthology.org/2025.emnlp-main.356/
- **Copyright Protection for Large Language Models: A Survey of Methods, Challenges, and Trends**, arXiv 2025.
  https://arxiv.org/abs/2508.11548

### 数据与内容溯源

- Sablayrolles et al., **Radioactive Data: Tracing Through Training**, ICML 2020.
  https://proceedings.mlr.press/v119/sablayrolles20a.html
- Zhao et al., **Unlocking Post-hoc Dataset Inference with Synthetic Data**, ICML 2025.
  https://proceedings.mlr.press/v267/zhao25q.html
- Xie et al., **Training Data Provenance Verification: Did Your Model Use Synthetic Data from My Generative Model for Training?**, CVPR 2025.
  https://openaccess.thecvf.com/content/CVPR2025/html/Xie_Training_Data_Provenance_Verification_Did_Your_Model_Use_Synthetic_Data_CVPR_2025_paper.html
- Google DeepMind, **SynthID**.
  https://deepmind.google/models/synthid/
- C2PA, **Content Credentials / Content Provenance and Authenticity**.
  https://c2pa.org/

### 攻击与防御

- Lukas et al., **SoK: How Robust is Image Classification Deep Neural Network Watermarking?**, IEEE S&P 2022.
- Camtepe, **IPRemover: A Generative Model Inversion Attack against Deep Neural Network Fingerprinting and Watermarking**, AAAI 2024.
  https://ojs.aaai.org/index.php/AAAI/article/view/28619
- Zhang et al., **Rethinking Removal Attack and Fingerprinting Defense for Model Intellectual Property Protection: A Frequency Perspective**, IJCAI 2025.
  https://doi.org/10.24963/ijcai.2025/71
- **MEraser: An Effective Fingerprint Erasure Approach for Large Language Models**, ACL 2025.
  https://aclanthology.org/2025.acl-long.1455/
