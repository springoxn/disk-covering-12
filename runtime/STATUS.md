# 项目状态（状态层，实时查询，勿抄入记忆）

最后更新：本轮会话（第 2 轮）。

## 阶段

| 阶段 | 状态 | 证据 |
|---|---|---|
| 0 侦察：文献 + 外部证明包 | 完成 | `_recon/`、`lit/DiskCoveringSolve/cover12`（GitHub VonEquinox） |
| 1 独立高精度解 KKT 系统 | 完成 | `runtime/hp_root.json`（250 位）、`runtime/hp_root_1000.json`（1000 位），残差 ~1e-1002 |
| 2 精确消元 → 极小多项式候选 | 完成 | `runtime/minpoly_candidate.json`（deg 37） |
| 3 根的唯一性（Krawczyk） | 完成 | `verify/out/krawczyk.json`：`K(X) ⊂ int(X)`，收缩范数 ≤ 8.37e-59 |
| 4 `P(r_*)=0` 证书链 | 完成 | `verify/out/minpoly_zero_certificate.json`（L1–L10 全 PASS） |
| 5 不可约性 / 隔离区间 / Sturm | 完成 | `verify/out/minpoly_checks.json` |
| 6 覆盖性证明（本文独立） | 完成 | `verify/out/coverage_certificate.json`（S1–S3 + I1–I4 全 PASS） |
| 7 全局最优性：重放第三方证书 | 完成 | `runtime/bundle_master_verify.log`（75 s，8 模块 VERIFIED） |
| 7b 独立复核 Farkas 第一层（38076 个） | 完成 | `verify/out/farkas_independent.json` |
| 7c 独立复核图能量第二层（131 个，含树结构完备性） | 完成 | `verify/out/energy_independent.json`（最小裕量 1.5666e-06） |
| 7d 独立复核候选凸性 | 完成 | `verify/out/convexity_independent.json`（最小 LDL 主元 0.01176782653397863） |
| 7e Brown 计数独立核对 | 完成 | `verify/brown_counts.py`：6 族全部相符 |
| 7f 归约数值阈值独立核验（T1–T6） | 完成 | `verify/out/thresholds_independent.json` |
| 8 整数关系（LLL）独立复核 deg 37 | 完成 | `runtime/lll_relation.log`：独立恢复同一 37 次多项式，余式 mod P = 0 |
| 9 Lean 形式化 | 完成（核心引理） | `lean/Covering.lean`（三角形覆盖引理 + 恒等式，mathlib v4.34.0-rc2，零错误零警告） |
| 10 端到端复现脚本 | 完成 | `verify/run_all.py` |
| 11 汇总交付 | 完成 | `docs/RESULT.md`、`verify/out/FINAL_ANSWER.json` |

## 关键数字（查询用，勿据此下结论）

- `r_* = 0.361102963744508644113087702017065180848530565591618515449660...`
- `P`：37 次，本原，首项 `4194304`，高度 `300804879240`
- 隔离区间 `(0.361102963744508644113087702016, 0.361102963744508644113087702019)`
- 覆盖：31 面剖分，非活动面最小 `r²` 裕量 `4.29112570161041e-05`
  （与第三方独立实现逐位一致）
- 能量层：131 拓扑 / 5291 节点 / 2711 叶，最小精确裕量 `1.5666e-06`
  （第三方 `1.5805e-06`）
- 凸性：最小 `LDL^T` 主元 `0.01176782653397863`（与第三方逐位相同）

## 未完成 / 依赖

- **归约的数学论证**（边界无返回引理 / 对偶三角剖分 / 顶点数下降）
  已逐条阅读核对，其**数值阈值 T1–T6 已独立核验**；
  但论证本身未形式化、分支树的构造未独立重造。
  **全部计算性证书（枚举完备性、Farkas 层、能量层、凸性）已独立重算通过**。
  详见 `docs/RESULT.md` §4.4。
- Lean 只覆盖引理 T；引理 C/S/A 与区间算术证书未形式化。
