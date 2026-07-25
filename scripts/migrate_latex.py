from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "content" / "parts"
sys.path.insert(0, str(ROOT))

from src.math_markup import audit_text, auto_markup_text

MANUAL_OVERRIDES = {
    "A. 2xeˣ": r"A. $2xe^{x}$",
    "C(t)={6, 0<t≤2；6+3(t-2)=3t, 2<t≤5}。定义域为 (0,5]，值域为 [6,15]；函数单调不减，且 6≤C(t)≤15。": (
        r"$C(t)=\begin{cases}"
        r"6,&0<t\le 2,\\"
        r"3t,&2<t\le 5."
        r"\end{cases}$"
        r"定义域为 $(0,5]$，值域为 $[6,15]$；函数单调不减，且 "
        r"$6\le C(t)\le 15$。"
    ),
    "C(t)={6 for 0<t≤2; 6+3(t-2)=3t for 2<t≤5}. The domain is (0,5], the range is [6,15], C is nondecreasing, and 6≤C(t)≤15.": (
        r"$C(t)=\begin{cases}"
        r"6,&0<t\le 2,\\"
        r"3t,&2<t\le 5."
        r"\end{cases}$ "
        r"The domain is $(0,5]$, the range is $[6,15]$, $C$ is "
        r"nondecreasing, and $6\le C(t)\le 15$."
    ),
    "设 f(x)={2x+a，当 x<1；x²+1，当 x>1}。要使 lim(x→1)f(x) 存在，应有 a=______，此时极限为______。": (
        r"设 $f(x)=\begin{cases}"
        r"2x+a,&x<1,\\"
        r"x^{2}+1,&x>1."
        r"\end{cases}$ "
        r"要使 $\lim_{x\to 1}f(x)$ 存在，应有 "
        r"$a=\underline{\qquad}$，此时极限为 $\underline{\qquad}$。"
    ),
    "Let f(x)={2x+a for x<1; x²+1 for x>1}. For lim(x→1)f(x) to exist, a must equal ______, and the limit is then ______.": (
        r"Let $f(x)=\begin{cases}"
        r"2x+a,&x<1,\\"
        r"x^{2}+1,&x>1."
        r"\end{cases}$ "
        r"For $\lim_{x\to 1}f(x)$ to exist, $a$ must equal "
        r"$\underline{\qquad}$, and the limit is then $\underline{\qquad}$."
    ),
    "双侧极限存在等价于“左极限=右极限=同一有限值”。": (
        r"双侧极限存在等价于“$\text{左极限}=\text{右极限}=\text{同一有限值}$”。"
    ),
    "分段函数连接点的极限参数由“左极限=右极限”确定，与点值无关。": (
        r"分段函数连接点的极限参数由“$\text{左极限}=\text{右极限}$”确定，与点值无关。"
    ),
    "C 正确：体积的量纲为长度³，除以时间后得到长度³/时间。": (
        r"C 正确：体积的量纲为$\text{长度}^{3}$，除以时间后得到"
        r"$\frac{\text{长度}^{3}}{\text{时间}}$。"
    ),
    "C. 体积变化率 $dV/dt$ 的单位应是长度$^{3}/$时间": (
        r"C. 体积变化率 $\frac{dV}{dt}$ 的单位应是"
        r"$\frac{\text{长度}^{3}}{\text{时间}}$"
    ),
    "C. 体积变化率 dV/dt 的单位应是长度³/时间": (
        r"C. 体积变化率 $\frac{dV}{dt}$ 的单位应是"
        r"$\frac{\text{长度}^{3}}{\text{时间}}$"
    ),
    "C. The unit of $dV/dt$ is length$^{3}/$time": (
        r"C. The unit of $\frac{dV}{dt}$ is "
        r"$\frac{\mathrm{length}^{3}}{\mathrm{time}}$"
    ),
    "C. The unit of dV/dt is length³/time": (
        r"C. The unit of $\frac{dV}{dt}$ is "
        r"$\frac{\mathrm{length}^{3}}{\mathrm{time}}$"
    ),
    "C is correct because volume has dimension length$^{3}$, so its rate has dimension length$^{3}/$time.": (
        r"C is correct because volume has dimension $\mathrm{length}^{3}$, "
        r"so its rate has dimension $\frac{\mathrm{length}^{3}}{\mathrm{time}}$."
    ),
    "C is correct because volume has dimension length³, so its rate has dimension length³/time.": (
        r"C is correct because volume has dimension $\mathrm{length}^{3}$, "
        r"so its rate has dimension $\frac{\mathrm{length}^{3}}{\mathrm{time}}$."
    ),
    "|dA|≈0.4π cm²；|dA|/A≈0.004=0.4%。": (
        r"$|dA|\approx 0.4\pi\ \mathrm{cm}^{2}$；"
        r"$\frac{|dA|}{A}\approx 0.004=0.4\%$。"
    ),
    "若 α>1，则 |sgn(h)|h|^{α-1}|=|h|^{α-1}→0，所以双侧极限存在且 f′_α(0)=0。": (
        r"若 $\alpha>1$，则 "
        r"$\left|\operatorname{sgn}(h)\,|h|^{\alpha-1}\right|"
        r"=|h|^{\alpha-1}\to 0$，所以双侧极限存在且 "
        r"$f'_{\alpha}(0)=0$。"
    ),
    "设 f(x)={x², x≤1; ax+b, x>1}。求 a,b，使 f 在 x=1 处可导，并求 f′(1)。": (
        r"设 $f(x)=\begin{cases}"
        r"x^{2},&x\le 1,\\"
        r"ax+b,&x>1."
        r"\end{cases}$ "
        r"求 $a,b$，使 $f$ 在 $x=1$ 处可导，并求 $f'(1)$。"
    ),
    "Let f(x)={x², x≤1; ax+b, x>1}. Find a,b so that f is differentiable at x=1, and find f′(1).": (
        r"Let $f(x)=\begin{cases}"
        r"x^{2},&x\le 1,\\"
        r"ax+b,&x>1."
        r"\end{cases}$ "
        r"Find $a,b$ so that $f$ is differentiable at $x=1$, and find $f'(1)$."
    ),
    "设 f(x)={x²sin(1/x), x≠0; 0, x=0}。判断 f 在 0 处是否可导，并求完整的导函数 f′(x)。": (
        r"设 $f(x)=\begin{cases}"
        r"x^{2}\sin\!\left(\frac{1}{x}\right),&x\ne 0,\\"
        r"0,&x=0."
        r"\end{cases}$ "
        r"判断 $f$ 在 0 处是否可导，并求完整的导函数 $f'(x)$。"
    ),
    "Let f(x)={x²sin(1/x), x≠0; 0, x=0}. Decide whether f is differentiable at 0, and find the complete derivative f′(x).": (
        r"Let $f(x)=\begin{cases}"
        r"x^{2}\sin\!\left(\frac{1}{x}\right),&x\ne 0,\\"
        r"0,&x=0."
        r"\end{cases}$ "
        r"Decide whether $f$ is differentiable at 0, and find the complete derivative $f'(x)$."
    ),
    "设 f(x)={x²sin(1/x²), x≠0; 0, x=0}。(1) 证明 f 在 0 连续；(2) 证明 f 在 0 可导并写出原点切线；(3) 求 x≠0 时的 f′(x)；(4) 构造 x_n→0⁺，说明 f′(x) 在 0 不连续。": (
        r"设 $f(x)=\begin{cases}"
        r"x^{2}\sin\!\left(\frac{1}{x^{2}}\right),&x\ne 0,\\"
        r"0,&x=0."
        r"\end{cases}$ "
        r"(1) 证明 $f$ 在 0 连续；(2) 证明 $f$ 在 0 可导并写出原点切线；"
        r"(3) 求 $x\ne 0$ 时的 $f'(x)$；(4) 构造 $x_n\to 0^{+}$，"
        r"说明 $f'(x)$ 在 0 不连续。"
    ),
    "Let f(x)={x²sin(1/x²), x≠0; 0, x=0}. (1) Prove continuity at 0. (2) Prove differentiability at 0 and write the tangent there. (3) Find f′(x) for x≠0. (4) Construct x_n→0⁺ showing that f′ is not continuous at 0.": (
        r"Let $f(x)=\begin{cases}"
        r"x^{2}\sin\!\left(\frac{1}{x^{2}}\right),&x\ne 0,\\"
        r"0,&x=0."
        r"\end{cases}$ "
        r"(1) Prove continuity at 0. (2) Prove differentiability at 0 and write "
        r"the tangent there. (3) Find $f'(x)$ for $x\ne 0$. "
        r"(4) Construct $x_n\to 0^{+}$ showing that $f'$ is not continuous at 0."
    ),
    "设 α,β>0，且 f_{α,β}(x)={|x|^α sin(1/|x|^β), x≠0; 0, x=0}。(1) 证明 f_{α,β} 在 0 连续；(2) 完整判定它在 0 可导的充要条件；(3) 在可导情形下，完整判定 f′_{α,β} 在 0 连续的充要条件。": (
        r"设 $\alpha,\beta>0$，且 "
        r"$f_{\alpha,\beta}(x)=\begin{cases}"
        r"|x|^{\alpha}\sin\!\left(\frac{1}{|x|^{\beta}}\right),&x\ne 0,\\"
        r"0,&x=0."
        r"\end{cases}$ "
        r"(1) 证明 $f_{\alpha,\beta}$ 在 0 连续；"
        r"(2) 完整判定它在 0 可导的充要条件；"
        r"(3) 在可导情形下，完整判定 $f'_{\alpha,\beta}$ 在 0 连续的充要条件。"
    ),
    "Let α,β>0 and f_{α,β}(x)={|x|^α sin(1/|x|^β), x≠0; 0, x=0}. (1) Prove that f_{α,β} is continuous at 0. (2) Completely classify differentiability at 0. (3) When it is differentiable, completely classify continuity of f′_{α,β} at 0.": (
        r"Let $\alpha,\beta>0$ and "
        r"$f_{\alpha,\beta}(x)=\begin{cases}"
        r"|x|^{\alpha}\sin\!\left(\frac{1}{|x|^{\beta}}\right),&x\ne 0,\\"
        r"0,&x=0."
        r"\end{cases}$ "
        r"(1) Prove that $f_{\alpha,\beta}$ is continuous at 0. "
        r"(2) Completely classify differentiability at 0. "
        r"(3) When it is differentiable, completely classify continuity of "
        r"$f'_{\alpha,\beta}$ at 0."
    ),
    "设 f(x)={ax+b，x<1；x²+1，x≥1}。要使 f 在 x=1 处可导，应有 a=________，b=________。": (
        r"设 $f(x)=\begin{cases}"
        r"ax+b,&x<1,\\"
        r"x^{2}+1,&x\ge 1."
        r"\end{cases}$ "
        r"要使 $f$ 在 $x=1$ 处可导，应有 "
        r"$a=\underline{\qquad}$，$b=\underline{\qquad}$。"
    ),
    "Let f(x)={ax+b for x<1; x²+1 for x≥1}. For f to be differentiable at x=1, a=________ and b=________.": (
        r"Let $f(x)=\begin{cases}"
        r"ax+b,&x<1,\\"
        r"x^{2}+1,&x\ge 1."
        r"\end{cases}$ "
        r"For $f$ to be differentiable at $x=1$, "
        r"$a=\underline{\qquad}$ and $b=\underline{\qquad}$."
    ),
    "设 f(x)={x²+ax+b，x<1；c ln x+2，x≥1}。求所有使 f 在 x=1 处可导的实参数三元组 (a,b,c)，并写出此时 f′(1)。": (
        r"设 $f(x)=\begin{cases}"
        r"x^{2}+ax+b,&x<1,\\"
        r"c\ln x+2,&x\ge 1."
        r"\end{cases}$ "
        r"求所有使 $f$ 在 $x=1$ 处可导的实参数三元组 $(a,b,c)$，"
        r"并写出此时 $f'(1)$。"
    ),
    "Let f(x)={x²+ax+b for x<1; c ln x+2 for x≥1}. Find all real triples (a,b,c) for which f is differentiable at x=1, and give f′(1).": (
        r"Let $f(x)=\begin{cases}"
        r"x^{2}+ax+b,&x<1,\\"
        r"c\ln x+2,&x\ge 1."
        r"\end{cases}$ "
        r"Find all real triples $(a,b,c)$ for which $f$ is differentiable at "
        r"$x=1$, and give $f'(1)$."
    ),
    "在 r=10 cm 且 |dr|≤0.02 cm 时，|dA|≈2π·10·0.02=0.4π cm²。": (
        r"在 $r=10\ \mathrm{cm}$ 且 $|dr|\le 0.02\ \mathrm{cm}$ 时，"
        r"$|dA|\approx 2\pi\cdot 10\cdot 0.02=0.4\pi\ \mathrm{cm}^{2}$。"
    ),
    "量纲 2πrdr 为 cm²；相对误差无单位。半径相对误差为 0.2%，面积约为其 2 倍，即 0.4%。": (
        r"量纲 $2\pi r\,dr$ 为 $\mathrm{cm}^{2}$；相对误差无单位。"
        r"半径相对误差为 $0.2\%$，面积约为其 2 倍，即 $0.4\%$。"
    ),
    "At r=10 cm with |dr|≤0.02 cm, |dA|≈2π·10·0.02=0.4π cm².": (
        r"At $r=10\ \mathrm{cm}$ with $|dr|\le 0.02\ \mathrm{cm}$, "
        r"$|dA|\approx 2\pi\cdot 10\cdot 0.02=0.4\pi\ \mathrm{cm}^{2}$."
    ),
    "Using cm instead of cm²": r"using $\mathrm{cm}$ instead of $\mathrm{cm}^{2}$",
}

QUESTION_FIELD_OVERRIDES: dict[str, dict[str, str]] = {
    "Q033": {
        "en.choices[1]": (
            r"B. $(\frac{f}{g})'=\frac{f'g-fg'}{g^{2}}$ for $(g\ne 0)$"
        ),
    },
    "Q038": {
        "zh.solution.analysis": (
            r"共有 $\ln(\,\cdot\,)$、$1+(\,\cdot\,)^{2}$、"
            r"$\sin(\,\cdot\,)$、$3x$ 四层。求导时从最外层向内层"
            r"依次乘入导数因子。"
        ),
    },
    "Q063": {
        "zh.answer": (
            r"(1) $(-1+h^{2})\,\mathrm{m}\,\mathrm{s}^{-1}$；"
            r"(2) $v(1)=-1\,\mathrm{m}\,\mathrm{s}^{-1}$；"
            r"(3) $s=-(t-1)$；(4) 此刻沿负方向运动"
        ),
        "zh.solution.steps[1]": (
            r"区间 $[1,1+h]$ 的平均速度为 "
            r"$\frac{s(1+h)-s(1)}{h}=\frac{-h+h^{3}}{h}"
            r"=(-1+h^{2})\,\mathrm{m}\,\mathrm{s}^{-1}$。"
        ),
        "zh.solution.steps[2]": (
            r"令 $h\to 0$，得到瞬时速度 "
            r"$v(1)=\lim_{h\to 0}(-1+h^{2})"
            r"=-1\,\mathrm{m}\,\mathrm{s}^{-1}$。"
        ),
        "zh.solution.extension": (
            r"比较 $h=0.1$ 与 $h=-0.1$ 的平均速度，二者均为 "
            r"$-0.99\,\mathrm{m}\,\mathrm{s}^{-1}$，体现其对瞬时速度的逼近。"
        ),
        "en.answer": (
            r"(1) $(-1+h^{2})\,\mathrm{m}\,\mathrm{s}^{-1}$; "
            r"(2) $v(1)=-1\,\mathrm{m}\,\mathrm{s}^{-1}$; "
            r"(3) $s=-(t-1)$; (4) the particle is moving in the negative "
            r"direction at that instant"
        ),
        "en.solution.steps[1]": (
            r"The average velocity on $[1,1+h]$ is "
            r"$\frac{s(1+h)-s(1)}{h}=\frac{-h+h^{3}}{h}"
            r"=(-1+h^{2})\,\mathrm{m}\,\mathrm{s}^{-1}$."
        ),
        "en.solution.steps[2]": (
            r"Let $h\to 0$ to obtain the instantaneous velocity "
            r"$v(1)=\lim_{h\to 0}(-1+h^{2})"
            r"=-1\,\mathrm{m}\,\mathrm{s}^{-1}$."
        ),
        "en.solution.extension": (
            r"For $h=0.1$ and $h=-0.1$, the average velocity is "
            r"$-0.99\,\mathrm{m}\,\mathrm{s}^{-1}$ in both cases, "
            r"illustrating approximation to the instantaneous value."
        ),
    },
    "Q066": {
        "zh.prompt": (
            r"求 $y=\arctan\!\left(e^{\sin(x^{2})}\right)$ 的导数，"
            r"并用分层变量说明每个因子的来源。"
        ),
        "zh.answer": (
            r"$y'=\frac{2x e^{\sin(x^{2})}\cos(x^{2})}"
            r"{1+e^{2\sin(x^{2})}}$。"
        ),
        "zh.solution.steps[0]": (
            r"设 $u=e^{\sin(x^{2})}$，则 $y=\arctan u$，故 "
            r"$\frac{dy}{du}=\frac{1}{1+u^{2}}$。"
        ),
        "en.prompt": (
            r"Differentiate $y=\arctan\!\left(e^{\sin(x^{2})}\right)$, "
            r"using layer variables to explain the source of every factor."
        ),
        "en.answer": (
            r"$y'=\frac{2x e^{\sin(x^{2})}\cos(x^{2})}"
            r"{1+e^{2\sin(x^{2})}}$."
        ),
        "en.solution.steps[0]": (
            r"Let $u=e^{\sin(x^{2})}$, so $y=\arctan u$ and "
            r"$\frac{dy}{du}=\frac{1}{1+u^{2}}$."
        ),
    },
    "Q072": {
        "zh.answer": (
            r"$y^{(n)}=x^{2}\sin\!\left(x+\frac{n\pi}{2}\right)"
            r"+2nx\sin\!\left(x+\frac{(n-1)\pi}{2}\right)"
            r"+n(n-1)\sin\!\left(x+\frac{(n-2)\pi}{2}\right)$。"
        ),
        "zh.solution.steps[3]": (
            r"三项分别为 $x^{2}\sin\!\left(x+\frac{n\pi}{2}\right)$、"
            r"$2nx\sin\!\left(x+\frac{(n-1)\pi}{2}\right)$、"
            r"$\binom{n}{2}\,2\sin\!\left(x+\frac{(n-2)\pi}{2}\right)$。"
        ),
        "zh.solution.extension": (
            r"把 $x^{2}$ 换成 $x^{m}$，公式将保留 "
            r"$k=0,1,\ldots,m$ 共 $m+1$ 项。"
        ),
        "en.answer": (
            r"$y^{(n)}=x^{2}\sin\!\left(x+\frac{n\pi}{2}\right)"
            r"+2nx\sin\!\left(x+\frac{(n-1)\pi}{2}\right)"
            r"+n(n-1)\sin\!\left(x+\frac{(n-2)\pi}{2}\right)$."
        ),
        "en.solution.steps[3]": (
            r"The three terms are "
            r"$x^{2}\sin\!\left(x+\frac{n\pi}{2}\right)$, "
            r"$2nx\sin\!\left(x+\frac{(n-1)\pi}{2}\right)$, and "
            r"$\binom{n}{2}\,2\sin\!\left(x+\frac{(n-2)\pi}{2}\right)$."
        ),
        "en.solution.extension": (
            r"Replacing $x^{2}$ by $x^{m}$ leaves "
            r"$k=0,1,\ldots,m$, for a total of $m+1$ terms."
        ),
    },
    "Q075": {
        "zh.solution.steps[2]": (
            r"对 $t$ 求导，"
            r"$\frac{d}{dt}\!\left(\frac{dy}{dx}\right)=\frac{3}{2}$。"
        ),
        "zh.solution.steps[3]": (
            r"使用 $\frac{d^{2}y}{dx^{2}}="
            r"\frac{\frac{d}{dt}\left(\frac{dy}{dx}\right)}{\frac{dx}{dt}}$，"
            r"得到 $\frac{d^{2}y}{dx^{2}}=\frac{\frac{3}{2}}{2t}"
            r"=\frac{3}{4t}$。"
        ),
        "en.solution.steps[2]": (
            r"Differentiate with respect to $t$: "
            r"$\frac{d}{dt}\!\left(\frac{dy}{dx}\right)=\frac{3}{2}$."
        ),
        "en.solution.steps[3]": (
            r"Use $\frac{d^{2}y}{dx^{2}}="
            r"\frac{\frac{d}{dt}\left(\frac{dy}{dx}\right)}{\frac{dx}{dt}}"
            r"=\frac{\frac{3}{2}}{2t}=\frac{3}{4t}$."
        ),
    },
    "Q077": {
        "zh.prompt": (
            r"倒置圆锥形容器中水面形成相似圆锥，始终满足 $h=3r$，"
            r"其中 $h,r$ 的单位为 $\mathrm{cm}$。水深以 "
            r"$\frac{dh}{dt}=6\,\mathrm{cm}\,\mathrm{min}^{-1}$ 增加。"
            r"当 $h=6\,\mathrm{cm}$ 时，求 $\frac{dr}{dt}$ 与 "
            r"$\frac{dV}{dt}$。"
        ),
        "zh.answer": (
            r"$\frac{dr}{dt}=2\,\mathrm{cm}\,\mathrm{min}^{-1}$；"
            r"$\frac{dV}{dt}=24\pi\,\mathrm{cm}^{3}\,\mathrm{min}^{-1}$。"
        ),
        "zh.solution.steps[0]": (
            r"由 $h=3r$，得 $r=\frac{h}{3}$；对时间求导得 "
            r"$\frac{dr}{dt}=\frac{1}{3}\frac{dh}{dt}"
            r"=2\,\mathrm{cm}\,\mathrm{min}^{-1}$。"
        ),
        "zh.solution.steps[1]": (
            r"当 $h=6\,\mathrm{cm}$ 时，$r=\frac{6}{3}"
            r"=2\,\mathrm{cm}$。"
        ),
        "zh.solution.steps[4]": (
            r"代入 $h=6$ 与 $\frac{dh}{dt}=6$，得到 "
            r"$\frac{dV}{dt}=\left(\frac{\pi\cdot36}{9}\right)\!6"
            r"=24\pi\,\mathrm{cm}^{3}\,\mathrm{min}^{-1}$。"
        ),
        "zh.solution.pitfalls[3]": (
            r"把体积率单位误写成 $\mathrm{cm}\,\mathrm{min}^{-1}$"
        ),
        "zh.solution.verification": (
            r"直接对 $V=\frac{1}{3}\pi r^{2}h$ 求导并代入 "
            r"$r=2,h=6,r'=2,h'=6$，也得到 "
            r"$\frac{\pi}{3}(2r h\,r'+r^{2}h')=24\pi$。"
        ),
        "en.prompt": (
            r"Water in an inverted conical tank forms similar cones satisfying "
            r"$h=3r$, with $h,r$ measured in $\mathrm{cm}$. The depth "
            r"increases at $\frac{dh}{dt}=6\,\mathrm{cm}\,\mathrm{min}^{-1}$. "
            r"When $h=6\,\mathrm{cm}$, find $\frac{dr}{dt}$ and "
            r"$\frac{dV}{dt}$."
        ),
        "en.answer": (
            r"$\frac{dr}{dt}=2\,\mathrm{cm}\,\mathrm{min}^{-1}$; "
            r"$\frac{dV}{dt}=24\pi\,\mathrm{cm}^{3}\,\mathrm{min}^{-1}$."
        ),
        "en.solution.steps[0]": (
            r"From $h=3r$, $r=\frac{h}{3}$. Differentiate to get "
            r"$\frac{dr}{dt}=\frac{1}{3}\frac{dh}{dt}"
            r"=2\,\mathrm{cm}\,\mathrm{min}^{-1}$."
        ),
        "en.solution.steps[1]": (
            r"When $h=6\,\mathrm{cm}$, $r=\frac{6}{3}=2\,\mathrm{cm}$."
        ),
        "en.solution.steps[4]": (
            r"With $h=6$ and $\frac{dh}{dt}=6$, "
            r"$\frac{dV}{dt}=\left(\frac{\pi\cdot36}{9}\right)\!6"
            r"=24\pi\,\mathrm{cm}^{3}\,\mathrm{min}^{-1}$."
        ),
        "en.solution.pitfalls[3]": (
            r"Using $\mathrm{cm}\,\mathrm{min}^{-1}$ for a volume rate"
        ),
    },
    "Q078": {
        "zh.prompt": (
            r"一架 $10\,\mathrm{m}$ 长的梯子靠墙，底端以 "
            r"$\frac{dx}{dt}=0.6\,\mathrm{m}\,\mathrm{s}^{-1}$ "
            r"沿地面远离墙移动。设底端离墙为 $x$、顶端高度为 $y$、"
            r"梯子与地面夹角为 $\theta$。当 $x=6\,\mathrm{m}$ 时，"
            r"求 $\frac{dy}{dt}$ 与 $\frac{d\theta}{dt}$。"
        ),
        "zh.answer": (
            r"$\frac{dy}{dt}=-0.45\,\mathrm{m}\,\mathrm{s}^{-1}$；"
            r"$\frac{d\theta}{dt}=-0.075\,\mathrm{rad}\,\mathrm{s}^{-1}$。"
        ),
        "zh.solution.steps[0]": (
            r"当 $x=6$ 时，由 $x^{2}+y^{2}=100$ 得 "
            r"$y=\sqrt{100-36}=8\,\mathrm{m}$。"
        ),
        "zh.solution.steps[2]": (
            r"代入 $x=6$、$y=8$、$\frac{dx}{dt}=0.6$，得 "
            r"$\frac{dy}{dt}=-\frac{6}{8}(0.6)"
            r"=-0.45\,\mathrm{m}\,\mathrm{s}^{-1}$。"
        ),
        "zh.solution.steps[4]": (
            r"此时 $\sin\theta=\frac{y}{10}=0.8$，所以 "
            r"$\frac{d\theta}{dt}=\frac{0.6}{-10(0.8)}"
            r"=-0.075\,\mathrm{rad}\,\mathrm{s}^{-1}$。"
        ),
        "zh.solution.pitfalls[2]": (
            r"角速度单位漏写 $\mathrm{rad}\,\mathrm{s}^{-1}$"
        ),
        "zh.solution.verification": (
            r"也可用 $y=10\sin\theta$ 求导："
            r"$\frac{dy}{dt}=10\cos\theta\cdot\theta'"
            r"=10(0.6)(-0.075)=-0.45\,\mathrm{m}\,\mathrm{s}^{-1}$，"
            r"与前式一致。"
        ),
        "en.prompt": (
            r"A $10\,\mathrm{m}$ ladder leans against a wall. Its foot moves "
            r"away from the wall at "
            r"$\frac{dx}{dt}=0.6\,\mathrm{m}\,\mathrm{s}^{-1}$. Let $x$ "
            r"be the foot's distance from the wall, $y$ the top height, and "
            r"$\theta$ the angle with the ground. When $x=6\,\mathrm{m}$, "
            r"find $\frac{dy}{dt}$ and $\frac{d\theta}{dt}$."
        ),
        "en.answer": (
            r"$\frac{dy}{dt}=-0.45\,\mathrm{m}\,\mathrm{s}^{-1}$; "
            r"$\frac{d\theta}{dt}=-0.075\,\mathrm{rad}\,\mathrm{s}^{-1}$."
        ),
        "en.solution.steps[0]": (
            r"When $x=6$, $x^{2}+y^{2}=100$ gives "
            r"$y=\sqrt{100-36}=8\,\mathrm{m}$."
        ),
        "en.solution.steps[2]": (
            r"Substitute $x=6$, $y=8$, and $\frac{dx}{dt}=0.6$ to get "
            r"$\frac{dy}{dt}=-\frac{6}{8}(0.6)"
            r"=-0.45\,\mathrm{m}\,\mathrm{s}^{-1}$."
        ),
        "en.solution.steps[4]": (
            r"Since $\sin\theta=\frac{y}{10}=0.8$, "
            r"$\frac{d\theta}{dt}=\frac{0.6}{-10(0.8)}"
            r"=-0.075\,\mathrm{rad}\,\mathrm{s}^{-1}$."
        ),
        "en.solution.pitfalls[2]": (
            r"Omitting the angular unit $\mathrm{rad}\,\mathrm{s}^{-1}$"
        ),
        "en.solution.verification": (
            r"Using $y=10\sin\theta$ gives "
            r"$\frac{dy}{dt}=10\cos\theta\cdot\theta'"
            r"=10(0.6)(-0.075)=-0.45\,\mathrm{m}\,\mathrm{s}^{-1}$, "
            r"confirming the result."
        ),
    },
    "Q080": {
        "zh.prompt": (
            r"圆的半径测得 $r=10\,\mathrm{cm}$，可能的绝对测量误差满足 "
            r"$|dr|\le 0.02\,\mathrm{cm}$。用微分估计面积 "
            r"$A=\pi r^{2}$ 的最大绝对误差与最大相对误差。"
        ),
        "zh.solution.analysis": (
            r"面积微分 $dA=2\pi r\,dr$。取绝对值并使用给定的最大 "
            r"$|dr|$，再除以 $A$ 得相对误差。"
        ),
        "zh.solution.steps[0]": (
            r"面积函数为 $A=\pi r^{2}$，因此 $dA=2\pi r\,dr$。"
        ),
        "zh.solution.steps[2]": (
            r"相对微分为 "
            r"$\frac{dA}{A}=\frac{2\pi r\,dr}{\pi r^{2}}"
            r"=\frac{2\,dr}{r}$。"
        ),
        "en.prompt": (
            r"A circle's radius is measured as $r=10\,\mathrm{cm}$ with "
            r"possible absolute measurement error "
            r"$|dr|\le 0.02\,\mathrm{cm}$. Use differentials to estimate "
            r"the maximum absolute and relative errors in $A=\pi r^{2}$."
        ),
        "en.answer": (
            r"$|dA|\approx 0.4\pi\,\mathrm{cm}^{2}$; "
            r"$\frac{|dA|}{A}\approx 0.004=0.4\%$."
        ),
        "en.solution.analysis": (
            r"Use $dA=2\pi r\,dr$. Take absolute values with the maximum "
            r"$|dr|$, then divide by $A$ for the relative error."
        ),
        "en.solution.steps[0]": (
            r"For $A=\pi r^{2}$, the differential is $dA=2\pi r\,dr$."
        ),
        "en.solution.steps[2]": (
            r"The relative differential is "
            r"$\frac{dA}{A}=\frac{2\pi r\,dr}{\pi r^{2}}"
            r"=\frac{2\,dr}{r}$."
        ),
        "en.solution.steps[4]": r"As a percentage, $0.004=0.4\%$.",
        "en.solution.verification": (
            r"The dimension of $2\pi r\,dr$ is $\mathrm{cm}^{2}$, while "
            r"relative error is dimensionless. A $0.2\%$ radius error "
            r"produces approximately a $0.4\%$ area error."
        ),
    },
    "Q083": {
        "en.prompt": (
            r"Decide whether the following statement is true and prove it: "
            r"for $\alpha>0$, $f_{\alpha}(x)=|x|^{\alpha}$ is differentiable "
            r"at $x=0$ if and only if $\alpha>1$; when differentiable, "
            r"$f'_{\alpha}(0)=0$."
        ),
    },
    "Q088": {
        "zh.solution.steps[3]": (
            r"将第一组求和改指标 $j=k+1$，它覆盖 "
            r"$j=1,\ldots,n+1$；第二组覆盖 $j=0,\ldots,n$。"
        ),
        "en.solution.steps[3]": (
            r"Reindex the first sum with $j=k+1$, which covers "
            r"$j=1,\ldots,n+1$; the second covers $j=0,\ldots,n$."
        ),
    },
    "Q091": {
        "zh.answer": (
            r"由 $\frac{dy}{dx}=\frac{y'(t)}{x'(t)}$，再用 "
            r"$\frac{d}{dx}=\frac{1}{x'(t)}\frac{d}{dt}$ 与商法则"
            r"即可得到公式。"
        ),
        "zh.solution.steps[2]": (
            r"令 $H(t)=\frac{y'(t)}{x'(t)}$，则 "
            r"$\frac{d^{2}y}{dx^{2}}="
            r"\frac{1}{x'}\frac{d}{dt}\!\left(\frac{y'}{x'}\right)$。"
        ),
        "zh.solution.steps[3]": (
            r"由商法则，"
            r"$\frac{d}{dt}\!\left(\frac{y'}{x'}\right)"
            r"=\frac{y''x'-y'x''}{(x')^{2}}$。"
        ),
        "en.answer": (
            r"Start from $\frac{dy}{dx}=\frac{y'(t)}{x'(t)}$, then use "
            r"$\frac{d}{dx}=\frac{1}{x'(t)}\frac{d}{dt}$ and the quotient rule."
        ),
        "en.solution.steps[2]": (
            r"With $H(t)=\frac{y'(t)}{x'(t)}$, "
            r"$\frac{d^{2}y}{dx^{2}}="
            r"\frac{1}{x'}\frac{d}{dt}\!\left(\frac{y'}{x'}\right)$."
        ),
        "en.solution.steps[3]": (
            r"The quotient rule gives "
            r"$\frac{d}{dt}\!\left(\frac{y'}{x'}\right)"
            r"=\frac{y''x'-y'x''}{(x')^{2}}$."
        ),
    },
    "Q092": {
        "zh.prompt": (
            r"倒置圆锥容器高 $9\,\mathrm{m}$、口半径 $3\,\mathrm{m}$。"
            r"水深 $h$ 以 $0.2\,\mathrm{m}\,\mathrm{min}^{-1}$ 上升；"
            r"当 $h=3\,\mathrm{m}$ 时求水体积变化率。某同学把水体半径"
            r"直接取为容器口半径 $3\,\mathrm{m}$，写 "
            r"$V=\frac{1}{3}\pi\cdot3^{2}h$，得到 "
            r"$\frac{dV}{dt}=0.6\pi\,\mathrm{m}^{3}\,\mathrm{min}^{-1}$。"
            r"指出错误并给出正确结果。"
        ),
        "zh.answer": (
            r"水面半径随 $h$ 变化，不能固定为 $3\,\mathrm{m}$。由 "
            r"$\frac{r}{h}=\frac{1}{3}$，$V=\frac{\pi h^{3}}{27}$，"
            r"故在 $h=3\,\mathrm{m}$ 时 "
            r"$\frac{dV}{dt}=0.2\pi\,\mathrm{m}^{3}\,\mathrm{min}^{-1}$。"
        ),
        "zh.solution.steps[1]": (
            r"因此当前水面半径 $r=\frac{h}{3}$，而不是始终等于 "
            r"$3\,\mathrm{m}$。"
        ),
        "zh.solution.steps[4]": (
            r"代入 $h=3\,\mathrm{m}$ 与 "
            r"$\frac{dh}{dt}=0.2\,\mathrm{m}\,\mathrm{min}^{-1}$，得 "
            r"$\frac{dV}{dt}=\left(\frac{\pi\cdot9}{9}\right)\!0.2"
            r"=0.2\pi\,\mathrm{m}^{3}\,\mathrm{min}^{-1}$。"
        ),
        "zh.solution.pitfalls[3]": (
            r"未检查 $\mathrm{m}^{3}\,\mathrm{min}^{-1}$ 量纲"
        ),
        "zh.solution.verification": (
            r"当 $h=3\,\mathrm{m}$ 时正确水面半径为 $1\,\mathrm{m}$；"
            r"直接用多变量公式 "
            r"$\frac{dV}{dt}=\frac{\pi}{3}(2r h\,r'+r^{2}h')$，其中 "
            r"$r'=\frac{h'}{3}$，也得到 $0.2\pi$。"
        ),
        "en.prompt": (
            r"An inverted conical tank is $9\,\mathrm{m}$ high with rim radius "
            r"$3\,\mathrm{m}$. The water depth rises at "
            r"$0.2\,\mathrm{m}\,\mathrm{min}^{-1}$. Find the volume rate when "
            r"$h=3\,\mathrm{m}$. A student fixes the water radius at "
            r"$3\,\mathrm{m}$, writes $V=\frac{1}{3}\pi\cdot3^{2}h$, and "
            r"obtains $\frac{dV}{dt}=0.6\pi\,\mathrm{m}^{3}\,\mathrm{min}^{-1}$. "
            r"Diagnose the error and give the correct result."
        ),
        "en.answer": (
            r"The water-surface radius changes with $h$ and cannot be fixed at "
            r"$3\,\mathrm{m}$. Since $\frac{r}{h}=\frac{1}{3}$ and "
            r"$V=\frac{\pi h^{3}}{27}$, at $h=3\,\mathrm{m}$ we have "
            r"$\frac{dV}{dt}=0.2\pi\,\mathrm{m}^{3}\,\mathrm{min}^{-1}$."
        ),
        "en.solution.steps[1]": (
            r"Thus the current water radius is $r=\frac{h}{3}$, not always "
            r"$3\,\mathrm{m}$."
        ),
        "en.solution.steps[4]": (
            r"At $h=3\,\mathrm{m}$ and "
            r"$\frac{dh}{dt}=0.2\,\mathrm{m}\,\mathrm{min}^{-1}$, "
            r"$\frac{dV}{dt}=\left(\frac{\pi\cdot9}{9}\right)\!0.2"
            r"=0.2\pi\,\mathrm{m}^{3}\,\mathrm{min}^{-1}$."
        ),
        "en.solution.pitfalls[3]": (
            r"Failing to check the dimension "
            r"$\mathrm{m}^{3}\,\mathrm{min}^{-1}$"
        ),
        "en.solution.verification": (
            r"At $h=3\,\mathrm{m}$, $r=1\,\mathrm{m}$. Direct differentiation "
            r"of $V=\frac{\pi}{3}r^{2}h$ with $r'=\frac{h'}{3}$ also gives "
            r"$0.2\pi$."
        ),
    },
    "Q095": {
        "zh.solution.steps[4]": (
            r"因为 $2025\equiv 1\pmod{8}$，"
            r"$\cos\!\left(\frac{2025\pi}{4}\right)"
            r"=\cos\!\left(\frac{\pi}{4}\right)=\frac{\sqrt{2}}{2}$。"
        ),
        "en.solution.steps[4]": (
            r"Since $2025\equiv 1\pmod{8}$, "
            r"$\cos\!\left(\frac{2025\pi}{4}\right)"
            r"=\cos\!\left(\frac{\pi}{4}\right)=\frac{\sqrt{2}}{2}$."
        ),
    },
    "Q097": {
        "zh.answer": (
            r"(1) 对所有 $\alpha,\beta>0$ 均连续；"
            r"(2) 在 0 可导当且仅当 $\alpha>1$，且 $f'(0)=0$；"
            r"(3) $f'$ 在 0 连续当且仅当 $\alpha>\beta+1$。"
        ),
        "en.answer": (
            r"(1) Continuous for all $\alpha,\beta>0$; "
            r"(2) differentiable at 0 exactly when $\alpha>1$, with "
            r"$f'(0)=0$; (3) $f'$ is continuous at 0 exactly when "
            r"$\alpha>\beta+1$."
        ),
    },
    "Q099": {
        "zh.prompt": (
            r"设 $\varphi$、$\psi$ 二阶可导，$y=y(x)$ 满足 "
            r"$\varphi(x)+\psi(y)=C$，且 $\psi'(y)\ne 0$。证明 "
            r"$y''=-\frac{\varphi''(x)}{\psi'(y)}"
            r"-\allowbreak\frac{[\varphi'(x)]^{2}\psi''(y)}"
            r"{[\psi'(y)]^{3}}$。"
            r"全程只用第二章求导法则。"
        ),
        "en.prompt": (
            r"Let $\varphi$ and $\psi$ be twice differentiable, with "
            r"$y=y(x)$ satisfying $\varphi(x)+\psi(y)=C$ and "
            r"$\psi'(y)\ne 0$. Prove "
            r"$y''=-\frac{\varphi''(x)}{\psi'(y)}"
            r"-\allowbreak\frac{[\varphi'(x)]^{2}\psi''(y)}"
            r"{[\psi'(y)]^{3}}$ using only "
            r"the differentiation rules of this chapter."
        ),
        "zh.solution.steps[5]": (
            r"代入 $(y')^{2}=\frac{[\varphi'(x)]^{2}}{[\psi'(y)]^{2}}$，"
            r"并拆分两项，即得题设公式。"
        ),
        "en.solution.steps[5]": (
            r"Substitute $(y')^{2}=\frac{[\varphi'(x)]^{2}}"
            r"{[\psi'(y)]^{2}}$ and separate the two terms to obtain "
            r"the stated formula."
        ),
    },
    "Q100": {
        "zh.prompt": (
            r"设 $u=u(x)$、$v=v(x)$ 在 $x_{0}$ 可微。仅用增量分解证明"
            r"乘积 $uv$ 在 $x_{0}$ 可微，且 $d(uv)=v\,du+u\,dv$。"
            r"不得引用中值定理或更后章节工具。"
        ),
        "zh.solution.steps[4]": (
            r"因此 $\Delta(uv)=[vu'(x_{0})+uv'(x_{0})]\Delta x"
            r"+o(\Delta x)$，这证明 $uv$ 在 $x_{0}$ 可微。"
        ),
        "zh.solution.steps[5]": (
            r"其线性主部定义为 "
            r"$d(uv)=[vu'+uv']\,dx=v(u'\,dx)+u(v'\,dx)=v\,du+u\,dv$。"
        ),
        "en.prompt": (
            r"Let $u=u(x)$ and $v=v(x)$ be differentiable at $x_{0}$. "
            r"Using only increment decompositions, prove that $uv$ is "
            r"differentiable at $x_{0}$ and "
            r"$d(uv)=v\,du+u\,dv$. Do not cite the mean value theorem or "
            r"later-chapter tools."
        ),
        "en.solution.steps[4]": (
            r"Thus $\Delta(uv)=[vu'(x_{0})+uv'(x_{0})]\Delta x"
            r"+o(\Delta x)$, proving $uv$ differentiable at $x_{0}$."
        ),
        "en.solution.steps[5]": (
            r"Its linear principal part is "
            r"$d(uv)=[vu'+uv']\,dx=v(u'\,dx)+u(v'\,dx)=v\,du+u\,dv$."
        ),
    },
}

QUESTION_TEXT_REPLACEMENTS: dict[str, tuple[tuple[str, str], ...]] = {
    "Q027": (
        (r"\frac{3 m}{s}", r"3\,\mathrm{m}\,\mathrm{s}^{-1}"),
        (r"$s(2)=2 m$", r"$s(2)=2\,\mathrm{m}$"),
    ),
    "Q051": (
        (r"\frac{2 cm}{s}", r"2\,\mathrm{cm}\,\mathrm{s}^{-1}"),
        (r"5 cm", r"$5\,\mathrm{cm}$"),
        (
            r"$\frac{dV}{dt}=200\pi$ cm$\frac{^{3}}{s}$",
            r"$\frac{dV}{dt}=200\pi\,\mathrm{cm}^{3}\,\mathrm{s}^{-1}$",
        ),
        (
            r"$\frac{dV}{dt}=-200\pi$ cm$\frac{^{3}}{s}$",
            r"$\frac{dV}{dt}=-200\pi\,\mathrm{cm}^{3}\,\mathrm{s}^{-1}$",
        ),
        (
            r"量纲为 cm$\frac{^{2}\cdot cm}{s}=\frac{cm^{3}}{s}$",
            r"量纲为 $\mathrm{cm}^{2}\cdot\mathrm{cm}\,\mathrm{s}^{-1}"
            r"=\mathrm{cm}^{3}\,\mathrm{s}^{-1}$",
        ),
        (
            r"The dimension is cm$\frac{^{2}\cdot cm}{s}=\frac{cm^{3}}{s}$",
            r"The dimension is $\mathrm{cm}^{2}\cdot\mathrm{cm}\,\mathrm{s}^{-1}"
            r"=\mathrm{cm}^{3}\,\mathrm{s}^{-1}$",
        ),
    ),
    "Q059": ((r"\in R", r"\in \mathbb{R}"),),
}

COMMON_TEXT_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("$is:$", "is:"),
    ("$it:$", "it:"),
    ("$x-$", "$x$-"),
    ("$y-$", "$y$-"),
    ("$u-$", "$u$-"),
    ("$n-$", "$n$-"),
)


def _canonical_id(source_id: str) -> str:
    return {
        "A013": "Q027",
        "A019": "Q033",
        "A023": "Q063",
        "A026": "Q059",
        "A030": "Q083",
        "A034": "Q097",
        "B012": "Q038",
        "B021": "Q066",
        "B027": "Q072",
        "B030": "Q088",
        "B032": "Q095",
        "C012": "Q075",
        "C014": "Q051",
        "C015": "Q077",
        "C016": "Q078",
        "C018": "Q091",
        "C019": "Q092",
        "C020": "Q099",
        "C027": "Q080",
        "C032": "Q100",
    }.get(source_id, source_id)


def _set_field(payload: dict[str, Any], path: str, replacement: str) -> None:
    target: Any = payload
    parts = re.findall(r"[^.\[\]]+|\[\d+\]", path)
    keys: list[str | int] = []
    for part in parts:
        keys.append(int(part[1:-1]) if part.startswith("[") else part)
    for key in keys[:-1]:
        target = target[key]
    target[keys[-1]] = replacement


def _replace_text(value: Any, replacements: tuple[tuple[str, str], ...]) -> Any:
    if isinstance(value, dict):
        return {key: _replace_text(item, replacements) for key, item in value.items()}
    if isinstance(value, list):
        return [_replace_text(item, replacements) for item in value]
    if not isinstance(value, str):
        return value
    for before, after in replacements:
        value = value.replace(before, after)
    return value


def _convert(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _convert(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_convert(item) for item in value]
    if not isinstance(value, str):
        return value
    if value in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[value]
    return auto_markup_text(value)


def _localized_payload(question: dict[str, Any]) -> dict[str, Any]:
    question = dict(question)
    canonical_id = _canonical_id(question["id"])
    question["zh"] = _convert(question["zh"])
    question["en"] = _convert(question["en"])
    question["tags"] = _convert(question["tags"])
    question = _replace_text(question, COMMON_TEXT_REPLACEMENTS)
    question = _replace_text(
        question, QUESTION_TEXT_REPLACEMENTS.get(canonical_id, ())
    )
    for path, replacement in QUESTION_FIELD_OVERRIDES.get(canonical_id, {}).items():
        _set_field(question, path, replacement)
    return question


def migrate(path: Path) -> list[dict[str, Any]]:
    items = json.loads(path.read_text(encoding="utf-8"))
    return [_localized_payload(item) for item in items]


def _audit(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            _audit(item, f"{path}.{key}", errors)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _audit(item, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        for message in audit_text(value):
            errors.append(f"{path}: {message}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="rewrite part files in place")
    args = parser.parse_args()

    errors: list[str] = []
    changed = 0
    for path in sorted(PARTS.glob("*.json")):
        before = json.loads(path.read_text(encoding="utf-8"))
        after = [_localized_payload(item) for item in before]
        changed += int(before != after)
        for item in after:
            _audit(item["zh"], f"{item['id']}.zh", errors)
            _audit(item["en"], f"{item['id']}.en", errors)
            _audit(item["tags"], f"{item['id']}.tags", errors)
        if args.write and before != after:
            path.write_text(
                json.dumps(after, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

    if errors:
        print("\n".join(errors))
        return 1
    mode = "rewritten" if args.write else "would change"
    print(f"LaTeX migration audit passed; {changed} part files {mode}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
