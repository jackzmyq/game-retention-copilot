"""Exploratory decision lenses. Scenarios never overwrite experimental evidence."""
from math import isfinite
from scipy.stats import chi2


def impact_scenario(effect, eligible_players):
    if type(eligible_players) is not int or eligible_players <= 0:
        raise ValueError("Eligible population must be a positive integer")
    return {"population":int(eligible_players),
            "retained_difference":effect["delta"]*eligible_players,
            "ci_low":effect["ci_low"]*eligible_players,
            "ci_high":effect["ci_high"]*eligible_players,
            "kind":"conditional scenario, not observed impact or forecast"}


def harm_lens(effect, acceptable_decline_pp):
    """Descriptive interval comparison, NOT a preregistered non-inferiority test."""
    if not isfinite(acceptable_decline_pp) or acceptable_decline_pp <= 0:
        raise ValueError("Tolerance must be a positive number of percentage points")
    boundary=-acceptable_decline_pp/100
    if effect["ci_high"] < boundary:
        state="beyond_tolerance"
    elif effect["ci_low"] >= boundary:
        state="within_tolerance"
    else:
        state="overlaps_tolerance"
    return {"state":state,"boundary":boundary,"retrospective":True,
            "integrity_audit_required":True}


def allocation_check(control_n,treatment_n,expected_control_share=.5):
    if not 0 < expected_control_share < 1:
        raise ValueError("Expected allocation must lie strictly between 0 and 1")
    total=control_n+treatment_n
    expected_c=total*expected_control_share
    expected_t=total-expected_c
    value=(control_n-expected_c)**2/expected_c+(treatment_n-expected_t)**2/expected_t
    return {"expected_control_share":expected_control_share,"p_value":float(chi2.sf(value,1)),
            "expected_control_n":expected_c,"expected_treatment_n":expected_t,
            "assumption_verified":False}


def return_patterns(analysis):
    denominators={r["version"]:r["players"] for r in analysis["arms"]}
    return [{**r,"pattern":f"{r['returned_d1']}{r['returned_d7']}",
             "share":r["players"]/denominators[r["version"]]}
            for r in analysis["transitions"]]


def scenario_markdown(effect,population,tolerance,language="zh"):
    impact=impact_scenario(effect,population)
    lens=harm_lens(effect,tolerance)
    labels={"en":{"beyond_tolerance":"Entire interval beyond the tolerated decline", "within_tolerance":"Interval within the chosen tolerance; audit still required", "overlaps_tolerance":"Interval crosses the tolerance boundary"},
            "zh":{"beyond_tolerance":"整个区间都超出容忍边界", "within_tolerance":"区间位于容忍范围内，但仍需完整性复核", "overlaps_tolerance":"区间跨越容忍边界"}}
    if language=="en":
        return (f"# D7 decision scenario\n\nAssumed future eligible population: {population:,}. "
                f"If the observed effect transported unchanged, retained-player difference = {impact['retained_difference']:+,.0f}; "
                f"transformed pointwise 95% interval [{impact['ci_low']:+,.0f}, {impact['ci_high']:+,.0f}].\n\n"
                f"Observed treatment-control difference: {effect['delta']*100:+.3f} pp, 95% CI [{effect['ci_low']*100:+.3f}, {effect['ci_high']*100:+.3f}] pp.\n\n"
                f"Retrospectively chosen acceptable decline: {tolerance:.2f} pp. {labels['en'][lens['state']]}.\n\n"
                "This is a conditional scale scenario, not measured business loss, a forecast, or a formal non-inferiority test. "
                "The historical uncertainty interval excludes transport uncertainty. Allocation and outcome integrity still require audit.")
    return (f"# D7 业务决策情景\n\n假设未来符合条件的玩家为 {population:,} 人，且观察差异可原样迁移："
            f"D7 返回人数差约 {impact['retained_difference']:+,.0f} 人；由单指标 95% 区间换算的范围"
            f"为 [{impact['ci_low']:+,.0f}, {impact['ci_high']:+,.0f}] 人。\n\n"
            f"原样本的实验组减对照组差异为 {effect['delta']*100:+.3f} 个百分点，95% 区间 [{effect['ci_low']*100:+.3f}, {effect['ci_high']*100:+.3f}] 个百分点。\n\n"
            f"事后设定的可接受绝对下降为 {tolerance:.2f} 个百分点：{labels['zh'][lens['state']]}。\n\n"
            "这是带假设的规模换算，不是实测业务损失、预测或正式非劣效检验；区间不包含跨时期迁移的不确定性。"
            "分流和结果完整性仍需复核，调整阈值不能消除数据缺口。")
