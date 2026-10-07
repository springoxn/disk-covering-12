# 参测者报告（按 `docs/answer-protocol.txt` 要求的字段）

> 协议原文要求："建议参测者报告：题目、协议版本、答案哈希、模型及推理设置、
> 起始材料、允许工具、计算机配置、实际耗时、费用、测试次数。是否联网，以及是否
> 使用已有候选、求解代码或答案，也应说明。"
> —— `_recon/benchmark/answer-protocol.txt` 第 47–52 行（本地副本；
> 上游 `docs/answer-protocol.txt`）。
>
> 字段顺序即上述顺序，全部字段均已填写；**未知项如实写"未记录"**。

| 字段 | 值 |
|---|---|
| 题目 | 单位圆盘覆盖 benchmark，`n = 12`（求 `r_D(12)` 及其极小多项式） |
| 协议版本 | `diskcover-minpoly-v1`（`benchmark.json → protocol`） |
| 答案哈希 | `35d604a5ea1b1fe5c52c30337743c1a8142b69827023284f9597e1ca9cb8f947` |
| `matches_reference` | `true`（`submission/answer.json`、`verify/out/benchmark_fingerprint.json`） |
| 模型 | `deepseek/deepseek-v4.1-flash`（provider `deepseek-official`） |
| 推理设置 | `reasoningEffort = high`，`maxTokens = 256000`，`contextWindow = 1000000`（会话 `request/header`） |
| 起始材料 | 题面 `goal.md`（3505 B，用户附件）+ 本会话自身上下文。**未提供**系数、半径、隔离区间或参考哈希 |
| 允许工具 | DSH 标准工具集：`pwsh`（本机 shell）、文件读写/编辑、`web_fetch`/`web_search`、`todo_write`、`subagent`、`workflow`、`present`、MCP `ssh`。**实际使用**：`pwsh`、文件读写/编辑、`web_fetch`。**未使用**：`subagent`、`workflow`、MCP `ssh`（无远程机器） |
| 计算机配置 | Intel Core i9-14900HX（24 核 / 32 线程）；DDR5 16 GB（5600 MT/s）；Windows 11 24H2（build 26100）；Python 3.13.5（Anaconda）+ SymPy 1.13.3 + mpmath 1.3.0；Lean 4.34.0-rc2 + mathlib `85e3a25e`（本地预编译）。**该配置是整理本报告时查询所得，任务开始时未做快照** |
| 实际耗时 | **T = 17 060 s（4 h 44 min 20 s）**，会话日志零点；检验到端到端 `run_all.py` 全部通过。另：首产物零点口径为 16 909 s；详见 `docs/research-work-report.md` §二 |
| 费用 | **未记录**（会话日志无计费字段；压缩记录里的 "~386 750 tokens" 是被压缩的历史体量，不是账单） |
| 测试次数 | 任务尝试 **1 次**（单次连续会话，无重跑、无重复试验）；官方指纹脚本执行 **2 次**（`T+04:55:28` 解题期、归档期各一次），两次结果一致 |
| 是否联网 | **是**。见下"联网用途" |
| 是否使用已有候选 | **是**。见下"来源披露" |
| 是否使用已有求解代码 | **否**（证书与消元脚本全部自写） |
| 是否使用已有答案 | **否**。见下"来源披露" |

## 分数

`S = ROUND_HALF_UP(200 + 100·log2(21600 / T))`：

| 节点 | T (s) | 分数 |
|---|---:|---:|
| 数学交付完成（端到端 ALL VERIFIED） | 17 060 | **234** |
| 同节点，首产物零点 | 16 909 | 235 |

`status = completed`，`budget_seconds = 43200`（未超时）。脚本与结果：
`verify/benchmark_score.py`、`verify/out/benchmark_score.json`。

⚠️ **边界**：`benchmark.json` 中 `scoring_contract_frozen = false`、
`public_submissions_open = false`；`score.py` 自身输出
`completion_independently_verified = false`；计时未预冻结。本分数是**按公开公式
自算**，不是正式排名成绩。

## 来源披露（本协议最要紧的一节）

协议要求说明"是否使用已有候选、求解代码或答案"。逐项如实：

| 环节 | 是否来自外部 | 说明 |
|---|---|---|
| 候选构型（D₃ 对称结构、`(u,v,w,r)` 初值） | **是** | 来自第三方 `VonEquinox/DiskCoveringSolve` 的 `cover12/`（`T+00:07:50` 抓取） |
| 最优性归约的**数学论证** | **是** | 边界不回归引理、对偶三角剖分、顶点数下降论证取自该包 `docs/cover12_proof_zh.md` §3–§9；本文**读过并核对，但未重新推导、未形式化** |
| 极小多项式 `P`（37 次、全部系数） | **否** | 由自写消元链独立得到（SymPy 结式 + 因式分解，见 `tools/elim_full.py`、`tools/minpoly_from_factors.py`） |
| 半径 `r_*` | **否** | 自写 KKT 系统 + 1000 位高精度求根（`tools/kkt_system.py`、`tools/hp_root.py`） |
| 根隔离区间、不可约性、Sturm 计数 | **否** | 自写（`verify/minpoly_checks.py`） |
| Krawczyk 唯一根证书 | **否** | 自写（`verify/krawczyk_cert.py`） |
| 覆盖性三角剖分 | **否** | 自建 31 面剖分（`verify/coverage_cert.py`） |
| Farkas / 能量 / 凸性 / 阈值复核 | **否** | 自写独立实现（`verify/*_independent.py`），数值与第三方对比一致 |
| 标准答案哈希 | **否（解题时不可得）** | benchmark 包按 `delivery.md` 明言"未包含标准答案系数、半径小数、根隔离区间、求解代码"。参考哈希是本任务**完成之后**（`T+04:53` 起）才从公开页面取得，取得后仅用于核对；核对前答案已定稿，未回改 |

**联网用途**（两段，均在时间线中有记录）：

1. `T+00:07:50` — 抓取第三方证明包（公开仓库）。
2. `T+04:53` 之后 — 抓取官方 benchmark 的页面、协议与脚本（`diskcover_answer.py`、`score.py`、报告 Prompt）。

两段之外，解题过程为纯本机计算；无远程机器、无外部算力。

## 提交与发布状态

上游 `benchmark.json` 的 `public_submissions_open = false`，即 benchmark **当前没有
公开提交入口**，公开记录为发布者所有。因此本报告的发布形式是**一个公开 git 仓库**：

- 仓库地址：**https://github.com/springoxn/disk-covering-12**（public，`main` 分支）
- 包内自检材料：`submission/`（系数、半径、原始自检输出、协议命令）
- 完整证明材料：**协议 v1 不要求上传**（"本版不要求上传大型证明包；证明材料可自行保留"），
  故随仓库一并保留在 `verify/`、`docs/RESULT.md`

## 第三方自检

任何人可用两条命令复算本报告的指纹（只需 Python 3.9+ 标准库）：

```sh
git clone https://github.com/springoxn/disk-covering-12
cd disk-covering-12
python _recon/benchmark/diskcover_answer.py --n 12 \
    --coefficients submission/coefficients.json \
    --radius "$(cat submission/radius.txt)" \
    --expected-sha256 35d604a5ea1b1fe5c52c30337743c1a8142b69827023284f9597e1ca9cb8f947
```

期望：`matches_reference: true`，退出码 `0`。原始输出见 `submission/selfcheck.txt`。

> 说明：`_recon/benchmark/diskcover_answer.py` 是**上游脚本的本地副本**，
> 未作任何修改（上游路径 `tools/diskcover_answer.py`）。

### 对**已发布产物**的核对（不是对本地目录）

上面的命令已在一份**全新克隆**上实际跑过，脚本可重跑：

```sh
python verify/published_clone_check.py
```

它做两件事：① 逐条复算克隆里 `verify/SHA256SUMS` 的 80 个文件；② 用克隆里
`submission/` 的系数与半径复算指纹。核对记录（含当次远端 HEAD、文件数、退出码）：
`verify/out/published_clone_check.json`。

首次执行结果：克隆 **146** 个文件，清单 **80 ok / 0 bad**（说明 `.gitattributes`
的 `* -text` 确实保证了签出字节与清单一致），自检 **exit 0 / matches_reference = true**。

> 时序说明：该 JSON 记录的是**执行当刻**的远端 HEAD；本文件随后还会被提交，因此
> 远端 HEAD 可能比记录中的更新。这是"把核对记录也纳入版本控制"时固有的性质，
> 不代表核对结果失效 —— 重跑脚本即可对任意 HEAD 重新核对。
