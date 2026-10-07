# handoff-2026-10-covering12 —— 12 盘覆盖单位圆盘：极小多项式与完整验证

> 交接文档。状态数字不写在这里，实时查询 `runtime/STATUS.md`；
> 结果与证明见 `docs/RESULT.md`。
> （本轮为第 2 轮，第 1 轮内容已并入下面的"已完成"清单。）

## 已完成（含验证方式）

1. **文献与外部实现侦察**
   - Friedman *Circles Covering Circles*（`_recon/circovcir.html`）：`n=12` 的
     "12 个单元覆盖的最大圆半径 = 2.769+"，即 `r_D(12) ≈ 0.3611`；
     记为 Melissen 1997 发现、VoxEquinox 2026 证明。
   - 抓取 `github.com/VonEquinox/DiskCoveringSolve` 的 `cover12` / `cover13` 证明包
     （118 个文件，`_recon/gh_pull.py`），并用其**主验证器**在本地完整重放成功
     （`runtime/bundle_master_verify.log`，75 s，8 模块 VERIFIED）。

2. **独立高精度解**（`tools/hp_root.py`）
   - 自 14 元 KKT 系统出发，mpmath 牛顿迭代到 1000 位，残差 ~1e-1002
     （`runtime/hp_root_1000.json`）。

3. **极小多项式（核心新增，第三方包未提供）**
   - 精确消元链降到 `Q[c,r]` 的两个多项式，取 `Res_c(F,G)`，因式分解取以
     `r_*` 为根的 37 次不可约因式：`runtime/minpoly_candidate.json`。
   - `verify/out/minpoly_checks.json`：本原、首项 `4194304 > 0`、
     `P(a)P(b) ≠ 0`、`(a,b)` 内恰一实根（Sturm）、模 `p=1000000093` 不可约。
   - `verify/out/minpoly_zero_certificate.json`：`P(r_*) = 0` 的 10 步精确证书链。
   - 独立复核：LLL 整关系在 `ρ = 2r_*` 下独立恢复同一 37 次多项式，
     余式 `mod P = 0`（`runtime/lll_relation.log`）。

4. **配置唯一性**：自写 Krawczyk 证书（`verify/out/krawczyk.json`）。

5. **覆盖性证明（本文独立构造）**：31 面剖分 + 5 个初等引理，符号恒等式
   `S1–S3` + 有理区间检查 `I1–I4` 全 PASS（`verify/out/coverage_certificate.json`）。
   **Lean 形式化**了其中的引理 T（`lean/Covering.lean`）。

6. **下界计算层全部独立重算**（本轮新增）
   - 枚举完备性 + 38,076 个 Farkas 乘子：`verify/farkas_independent.py` ✓
   - 131 个图能量证书（自写 Kron + 自写三角/π 有理界）：`verify/energy_independent.py` ✓
   - 候选拓扑严格凸性（自写精确 `LDL^T`）：`verify/convexity_independent.py` ✓

## 卡点 / 未完成

- **归约的数学论证**（边界无返回引理、对偶三角剖分引理、顶点数下降）
  **未形式化、未用独立代码重算**；它们只用凸性/Voronoi 凸性/三角不等式，
  已逐条阅读核对。这是当前唯一仍依赖第三方论证的地方。
- **131 个拓扑的分支树本身未独立重算**：只验证了"给定权重与树 ⇒ `E_w ≥ T`"，
  以及 `empty` 节点的不可行性。
- Lean 只覆盖引理 T；引理 C/S/A 与区间算术证书未形式化。
- `tools/pslq_capability.py` 记录了一个环境坑：mpmath 的 `pslq` 在系数 >~1e6
  时失效（对已知的 d=4、系数 1e17 的关系也返回 None），大系数问题必须用 LLL。

## 下一步具体动作

1. 若要完全自持：独立重算 131 个分支树的构造（分裂准则 + 覆盖性检查），
   并形式化归约引理（Lean/Coq）。
2. 若写成论文：`docs/RESULT.md` 可直接作底稿；需补自持化的下界论证。
3. 可选的 Lean 扩展：引理 C（圆盘凸性 + 三角形）、引理 S（双圆切换）、
   引理 A（圆弧 + 弓形）。

## 新增的跨会话事实（供记忆层引用）

- **题目**：12 盘覆盖单位圆盘的最小半径极小多项式为 37 次、高度 300804879240；
  隔离区间 `(0.361102963744508644113087702016, …019)`。→ 见 `docs/RESULT.md`。
- **第三方参考实现**：`lit/DiskCoveringSolve`（VonEquinox，cover11–cover20；
  其 `cover12` 自述"未经同行评审"）。其主验证器本地可重放；
  **全部计算性证书已被本文独立代码复算通过**。
- **环境事实**：
  - 本会话沙箱下 WSL 不可用（`Wsl/Service/E_ACCESS_DENIED`）；
  - `web_search` 工具因 API key 失效不可用，改用 python `urllib` + DuckDuckGo
    HTML 端点抓取（`_recon/search*.py`）；
  - 本机 Lean 4.34.0-rc2 + 预编译 mathlib v4.34.0-rc2 可用，
    编译命令见 `lean/lean.cmd`（用 `LEAN_PATH` 指向
    `S6Isserlis\.lake\packages\*\ .lake\build\lib\lean` 与工具链 `lib\lean`）。
- **工程坑**：
  - sympy 多元 `Poly.coeff_monomial(x)` 只取"纯单项式"系数；
    提取"关于 x 的系数"要用 `.as_expr().coeff(x, k)`；
  - `subs(z**2, 3)` 不会化简 `z**3`，要用多项式余式；
  - 用"切线型"下界近似 `1−cos` 时，区间跨越 `π` 后凸性失效，
    必须用 Taylor 余项 + `min(0,m)h²/2` 的构造；
  - 有理区间算术在 900 位分母下极慢，把盒向外取整到 `1e-40` 后即可加速千倍
    且保持严格性。
