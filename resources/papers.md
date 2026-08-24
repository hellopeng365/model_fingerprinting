# 模型指纹相关研究索引

> 配套 [`README.md`](../README.md) 的文献与资源清单
> 更新时间：2026-08-24

## 1. 综述 / SoK / Benchmark

| 标题 | 年份 | 链接 | 备注 |
| --- | --- | --- | --- |
| SoK: Large Language Model Copyright Auditing via Fingerprinting | 2025 | https://arxiv.org/abs/2508.19843 | 提出 LEAFBENCH；统一白盒 / 黑盒分类 |
| LEAFBENCH 代码仓库 | 2025 | https://github.com/shaoshuo-ss/LeaFBench | 149 个模型实例、13 类后处理 |
| Copyright Protection for Large Language Models: A Survey | 2025 | https://arxiv.org/abs/2508.11548 | 水印 + 指纹方法、挑战与趋势 |
| Implicit Identity Technologies for LLMs | 2026 | https://arxiv.org/abs/2605.29245 | Implicit-ID 统一抽象；生命周期分类 |

## 2. DNN 时代的模型指纹

| 标题 | 年份 | 链接 | 类型 |
| --- | --- | --- | --- |
| IPGuard | 2021 | https://doi.org/10.1145/3433210.3437526 | 决策边界指纹 |
| Conferrable Adversarial Examples | 2021 | https://arxiv.org/abs/1912.00888 | 可传递对抗样本 |
| Copy, Right? / DeepJudge | 2022–2023 | https://arxiv.org/abs/2112.05588 | 测试框架 |

## 3. LLM 白盒 / 表示 / 参数指纹

| 标题 | 年份 | 链接 | 类型 |
| --- | --- | --- | --- |
| HuRef | 2023–2024 | https://arxiv.org/abs/2312.04828 | 参数方向不变量、人可读指纹 |
| REEF | 2025 | https://arxiv.org/abs/2410.14273 | CKA 表示相似度 |

## 4. LLM 黑盒行为指纹

| 标题 | 年份 | 链接 | 类型 |
| --- | --- | --- | --- |
| LLMmap | 2024–2025 | https://arxiv.org/abs/2407.15847 | 主动查询版本识别 |
| DuFFin | 2025 | https://arxiv.org/abs/2505.16530 | 触发模式 + 知识层双证据 |
| RoFL | 2025 | https://arxiv.org/abs/2505.12682 | 鲁棒提示–响应统计指纹 |
| LLMPrint | 2026 | https://aclanthology.org/2026.acl-long.541/ | 提示注入诱导稳定 token 偏好 |
| LLMPrint 代码 | 2026 | https://github.com/hifi-hyp/ACL-LLMPrint | 灰盒 / 黑盒验证实现 |

## 5. 嵌入式 / 编辑式 / 抗合并指纹

| 标题 | 年份 | 链接 | 类型 |
| --- | --- | --- | --- |
| Instructional Fingerprinting | 2024 | https://aclanthology.org/2024.naacl-long.180/ | 指令微调触发器 |
| Chain & Hash | 2024 | https://arxiv.org/abs/2407.10887 | 密码学绑定问答对 |
| MergePrint | 2025 | https://aclanthology.org/2025.acl-long.342/ | 抗模型合并 |
| FPEdit | 2025 | https://arxiv.org/abs/2508.02092 | 局部知识编辑植入 |
| Scalable Fingerprinting | 2025 | https://proceedings.neurips.cc/paper_files/paper/2025/file/b5ee4715ef8e96176ef3ccbe229b6ab9-Paper-Conference.pdf | 大规模多指纹 |

## 6. 训练数据溯源

| 标题 | 年份 | 链接 | 类型 |
| --- | --- | --- | --- |
| Radioactive Data | 2020 | https://arxiv.org/abs/2002.00937 | 放射性数据标记 |
| Dataset Inference | 2021 | https://arxiv.org/abs/2104.10706 | 集合级训练数据推断 |
| LLM Dataset Inference | 2024 | https://arxiv.org/abs/2406.06443 | LLM 数据集级推断 |

## 7. 生成内容水印与来源标准

| 标题 | 年份 | 链接 | 类型 |
| --- | --- | --- | --- |
| A Watermark for Large Language Models | 2023 | https://arxiv.org/abs/2301.10226 | 文本绿名单水印 |
| Tree-Ring Watermarks | 2023 | https://arxiv.org/abs/2305.20030 | 扩散图像指纹 |
| SynthID-Text | 2024 | https://doi.org/10.1038/s41586-024-08025-4 | 生产级文本水印 |
| SynthID Text 实现 | 2024 | https://github.com/google-deepmind/synthid-text | 参考实现 |
| C2PA Specification | — | https://spec.c2pa.org/specifications/specifications/2.4/specs/C2PA_Specification.html | 内容凭证标准 |

## 8. 维护约定

- 新增论文时优先补：访问假设（白盒 / 灰盒 / 黑盒）、是否侵入、代码链接、主要威胁模型。
- README 保持叙事综述；本文件保持表格化索引，避免两边大段重复。
- 每周例行更新时，至少检查：ACL / NeurIPS / ICLR / USENIX / arXiv 上的 `LLM fingerprinting`、`model watermarking`、`dataset inference` 新结果。
