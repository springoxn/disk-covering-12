# 项目 AGENTS.md —— 用 12 个等圆盘覆盖单位圆盘

## 这是什么项目

求 `r_D(12)`（12 个等半径闭圆盘覆盖单位闭圆盘的最小半径），要求给出**极小多项式**
（全部系数 + 不可约性 + 有理隔离区间 + 唯一根证明）、精确配置、覆盖性证明、
全局最优性证明与可复现的计算机辅助验证材料。

## 交付纪律（本项目的具体化）

- 每个"已验证"的说法必须指向 `verify/out/*.json` 里的一个证书条目；
  没有证书就写"未验证"。
- `verify/` 下的判定**只用整数/有理数运算与有理区间算术**，不允许浮点参与判定。
- 浮点只用于**发现**（牛顿解、候选构型、因式筛选），发现结果必须再用
  精确/区间手段复核。
- 与第三方（`lit/DiskCoveringSolve`）的关系：**重放 + 独立复核**，不把
  第三方结论当作自己的证明；依赖项在 `docs/RESULT.md` §4.4 明列。

## 关键路径

| 事实 | 位置 |
|---|---|
| 结果与证明叙述 | `docs/RESULT.md` |
| 极小多项式候选 | `runtime/minpoly_candidate.json` |
| 1000 位根 | `runtime/hp_root_1000.json` |
| 证书链脚本 | `verify/minpoly_zero_cert.py` |
| 覆盖证明脚本 | `verify/coverage_cert.py` |
| 第三方证明包 | `lit/DiskCoveringSolve/cover12/` |
| 状态层 | `runtime/STATUS.md` |

## 环境

Windows 11 + Anaconda Python 3.13.5（sympy 1.13.3 / mpmath 1.3.0 / gmpy2 2.2.1）。
本地 Lean：`E:\study\AImath\.local-lean`（Lean 4.34.0-rc2，本会话**未**使用）。
WSL 在本会话沙箱下不可用（`Wsl/Service/E_ACCESS_DENIED`）。
