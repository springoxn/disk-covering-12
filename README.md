# ADB —— 12 个等圆盘覆盖单位圆盘（r_D(12)）

任务源：`goal.md`（见 `docs/goal.md`）。目标：求 `r_D(12)`，给出**极小多项式**（全部系数、
不可约性、有理隔离区间与唯一根）、精确配置、覆盖证明、全局最优性证明、完整可复现的
计算机辅助验证材料。

## 目录

| 目录 | 用途 |
|---|---|
| `docs/` | 问题原文、笔记、文献摘要 |
| `tools/` | 数值探索与代数识别脚本 |
| `verify/` | 精确验证脚本、证书、区间算术内核 |
| `proof_graph/` | 引理依赖图（状态层，实时查询） |
| `runtime/` | 运行日志（状态层） |
| `lit/` | 外部文献与参考实现（含 VonEquinox/DiskCoveringSolve 的 cover12 证明包）—— **未纳入 git**，见下 |
| `_recon/` | 侦察脚本与原始抓取（含官方 benchmark 的报告 Prompt 与计分脚本的本地副本） |

## 交付物

| 交付物 | 位置 |
|---|---|
| 结果与证明叙述 | `docs/RESULT.md` |
| 研究工作报告（按官方 Prompt 撰写） | `docs/research-work-report.md` |
| 参测者报告（按官方提交协议字段） | `docs/SUBMISSION.md` |
| 提交包（系数 / 半径 / 自检原文） | `submission/` |
| 机器可读最终答案 | `verify/out/FINAL_ANSWER.json` |
| 端到端复现 | `python verify/run_all.py`（14 步 / 8 证书） |
| 完整性清单（sha256） | `verify/SHA256SUMS` |
| Lean 形式化 | `lean/Covering.lean`（驱动 `lean/lean.cmd`） |
| 时间线取证 | `verify/session_timeline.py`、`verify/file_timeline.py` |

## 第三方材料

`lit/DiskCoveringSolve/`（`cover12/` 的归约论证与证书）**不在本仓库内**：该上游仓库
没有 LICENSE 文件，因此不随本交付再分发。重新获取：

```sh
git clone https://github.com/VonEquinox/DiskCoveringSolve lit/DiskCoveringSolve
```

本仓库对它的使用是**只读参照**；哪些结论依赖它、哪些已独立复核，见
`docs/RESULT.md` §4.3–§4.4 与 `docs/research-work-report.md` §5.4。

## 状态层入口

- 当前进展与验证证据：`runtime/STATUS.md`
- 交接：`handoff-*.md`
