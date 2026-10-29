import json
import sqlite3
import os
from pathlib import Path
from contextlib import closing
from src.config import REPORTS, DB
from src.provenance import EvidenceError


def load_analysis(reports=None,database=None):
    reports=Path(reports) if reports is not None else REPORTS
    database=Path(database) if database is not None else DB
    try:
        analysis=json.loads((reports/"analysis.json").read_text(encoding="utf-8"))
        if not isinstance(analysis,dict):
            raise EvidenceError("Analysis must be a report object. Rebuild before using this evidence.")
        with closing(sqlite3.connect(database.resolve().as_uri()+"?mode=ro",uri=True)) as con:
            row=con.execute("SELECT build_id,source_sha256 FROM build_metadata").fetchone()
        if row != (analysis.get("build_id"),analysis.get("source_sha256")):
            raise EvidenceError("Database and report are from different builds. Rebuild before using this evidence.")
        return analysis
    except (sqlite3.Error,OSError,json.JSONDecodeError) as exc:
        raise EvidenceError("Analysis is unavailable or incomplete. Run setup.ps1 to rebuild the local evidence.") from exc


def decision_report(a=None,language="zh"):
    a=a or load_analysis()
    c,t=a["arms"]
    d1,d7=a["tests"]
    srm=a["srm"]
    flag=srm["p_value"]<srm["threshold"]
    if language=="en":
        return f'''# Game retention experiment: decision brief

**Recommendation: pause a full rollout of gate_40; verify allocation and data integrity first.**

## Evidence
- Population: {a['rows']:,} players; gate_30 {c['players']:,}, gate_40 {t['players']:,}.
- D7 retention: {c['retained_d7']:,}/{c['players']:,} = {c['d7_rate']:.2%} vs {t['retained_d7']:,}/{t['players']:,} = {t['d7_rate']:.2%}.
- Treatment minus control: **{d7['delta']*100:+.3f} percentage points**; pointwise 95% Newcombe CI [{d7['ci_low']*100:+.3f}, {d7['ci_high']*100:+.3f}] pp; two-sided p={d7['p_value']:.5f}; Holm-adjusted p={d7['holm_p']:.5f} across D1/D7. Relative difference {d7['relative_change']:.2%}.
- D1 difference: {d1['delta']*100:+.3f} pp; CI [{d1['ci_low']*100:+.3f}, {d1['ci_high']*100:+.3f}] pp; Holm-adjusted p={d1['holm_p']:.5f}. No significant difference does not demonstrate equivalence.

## Integrity gate
Under an **assumed, unverified 50:50 allocation**, the sample-ratio-mismatch screening p-value is {srm['p_value']:.5f}; screening threshold 0.01; flag={'YES' if flag else 'NO'}. This does not prove a randomization failure. Obtain the intended ratio, assignment logs, eligibility rules and full outcome coverage before treating the estimate as causal.

## Decision and follow-up
The public sample supports a negative D7 difference. It does not identify whether pacing, difficulty or another mechanism explains it. Keep gate_30 as the provisional reference; audit assignment, deduplication, observation maturity, platform balance, and exposure. If integrity is confirmed, consider a new fixed-horizon experiment with prespecified D7 and guardrails. For illustration, a 1 pp absolute decline at baseline {c['d7_rate']:.2%}, 80% power, two-sided alpha 0.05 requires approximately **{a['planning']['players_per_arm']:,} players per arm** under an equal-allocation normal approximation. This is a planning scenario, not achieved power or observed lift.

## Scope
Historical Cookie Cats educational A/B release, not miHoYo telemetry. No raw timestamps, country, channel, payments or gate-exposure events. D7 is a source flag for return seven days after installation; it is not cumulative seven-day retention. The selected primary outcome and tests are retrospective, not verified preregistration. Teaching materials conflict on the rounds horizon (7 vs 14 days); the recorded aggregate is post-treatment, overlaps the outcome, and must not be used as a prospective churn predictor or a causal segment. The 49,854-round record is retained; the exclusion is sensitivity-only. Regional expansion requires new data and market-specific validation.
'''
    return f'''# 游戏留存实验：运营决策简报

**建议：暂缓全量上线 gate_40，先核查实验分流和数据完整性。**

## 主要证据
- 分析总体：{a['rows']:,} 名玩家；gate_30 为 {c['players']:,} 人，gate_40 为 {t['players']:,} 人。
- D7 留存：{c['retained_d7']:,}/{c['players']:,} = {c['d7_rate']:.2%}，对比 {t['retained_d7']:,}/{t['players']:,} = {t['d7_rate']:.2%}。
- gate_40 − gate_30：**{d7['delta']*100:+.3f} 个百分点**；单指标 95% Newcombe 置信区间 [{d7['ci_low']*100:+.3f}, {d7['ci_high']*100:+.3f}] 个百分点；双侧 p={d7['p_value']:.5f}；D1/D7 两项 Holm 校正后 p={d7['holm_p']:.5f}。相对变化为 {d7['relative_change']:.2%}，不能与百分点混用。
- D1 差异 {d1['delta']*100:+.3f} 个百分点，区间 [{d1['ci_low']*100:+.3f}, {d1['ci_high']*100:+.3f}]，Holm 校正后 p={d1['holm_p']:.5f}；未显著不代表两组等效。

## 实验可信度
在**假设但未核实的 50:50 分流比例**下，SRM 分组比例筛查 p={srm['p_value']:.5f}，项目设定的筛查阈值为 0.01，{'触发复核' if flag else '未触发复核'}。这不等于已经证明随机化失效。需核对预期比例、分流日志、入组规则和结果覆盖率，再决定能否作因果解释。

## 运营动作
当前样本显示 gate_40 的 D7 留存更低；不能据此断言是“难度提高”或“长草期”导致。以 gate_30 为暂时参照，优先核查分流、去重、观察窗口成熟度、平台平衡与门槛曝光。完整性确认后，再决定是否开展预先定义主指标和护栏的固定周期复测。若以基线 {c['d7_rate']:.2%}、检测绝对下降 1 个百分点、80% 检验功效、双侧 alpha=0.05 规划新实验，等比例分组的正态近似所需样本约为**每组 {a['planning']['players_per_arm']:,} 人**；这是规划场景，不是已实现的收益或事后功效。

## 分析边界
本项目使用 Cookie Cats 历史教学实验数据，不是米哈游内部数据。没有逐日时间戳、地区、渠道、付费或实际门槛曝光记录。D7 为安装后第七天返回的源数据标记，不是七日内累计返回；D1 与 D7 不是依次收窄的漏斗。本项目事后选择 D7 为主指标，并非已核验的实验预注册。累计局数在教学材料中存在 7 天 / 14 天窗口表述冲突，不能核定为早期特征；其发生在分流后且覆盖结果窗口，不能用于早期流失预测或按曝光用户划分因果效果。49,854 局极端记录在主分析中保留，删除仅作敏感性检查。结论不能直接外推到其他品类或地区。
'''


def write_reports():
    a=load_analysis()
    from src.decision import scenario_markdown
    from src.copilot import offline_demo
    for language in ["zh","en"]:
        atomic_text(REPORTS/f"decision_brief_{language}.md",decision_report(a,language))
        atomic_text(REPORTS/f"decision_scenario_{language}.md",scenario_markdown(a["tests"][1],100000,.5,language))
    for name,question in [("offline_demo_evidence","是否应该上线 gate_40？"),("unsupported_question_example","为什么欧洲上周 DAU 下降？")]:
        atomic_text(REPORTS/f"{name}.json",json.dumps(offline_demo(question),ensure_ascii=False,indent=2))


def atomic_text(path,text):
    pending=path.with_suffix(path.suffix+".pending")
    try:
        pending.write_text(text,encoding="utf-8")
        os.replace(pending,path)
    finally:
        pending.unlink(missing_ok=True)


if __name__=="__main__":
    write_reports()
