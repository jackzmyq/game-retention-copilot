"""Local analyst workbench. Run: python -m streamlit run app.py"""
import json
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from src.config import ROOT, RAW, DB, REPORTS, SOURCE_URL, settings
from src.statistics import required_n
from src.reporting import load_analysis, decision_report
from src.queries import run_query, schema_description, QueryRejected
from src.copilot import offline_demo, run_agent, AgentError
from src.decision import impact_scenario, harm_lens, allocation_check, return_patterns, scenario_markdown
from src.ui import css, banner, note
from src.provenance import EvidenceError
from src.guide import scope_rows,guide_markdown


def navigate(target):
    st.session_state["workspace"]=target

st.set_page_config(page_title="Game Retention Lab",page_icon="◈",layout="wide")
st.markdown(css(),unsafe_allow_html=True)

if not (DB.exists() and (REPORTS/"analysis.json").exists()):
    st.error("请先运行 setup.ps1 或 python scripts/build_pipeline.py。 / Run setup first.")
    st.stop()

with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-mark">R</div><div><div class="brand-name">Retention Lab</div><div class="brand-sub">GAME ANALYTICS WORKSPACE</div></div></div>',unsafe_allow_html=True)
    language=st.selectbox("Language / 语言",["中文","English"],label_visibility="collapsed")
    en=language=="English"
    lang="en" if en else "zh"
    tr=lambda zh,english:english if en else zh
    st.caption(tr("游戏留存实验与 AI 运营助手","Game experiments & operations copilot"))
    page=st.radio(tr("工作区","Workspace"),[
        tr("作品导览","Project guide"),tr("实验决策","Experiment decision"),tr("决策沙盘","Decision lab"),tr("行为与质量","Behavior & quality"),
        tr("AI 分析助手","AI copilot"),tr("指标与项目说明","Definitions & scope")],key="workspace")
    st.divider()
    st.markdown('<div class="source-status"><span class="status-dot"></span>'+tr("本地数据已就绪","LOCAL DATA READY")+'<br>Cookie Cats · 90,189 '+tr("名玩家","players")+'</div>',unsafe_allow_html=True)
    st.caption(tr("历史静态样本，不是实时监控或米哈游内部数据。","Historical static sample; not live monitoring or miHoYo telemetry."))
    st.link_button(tr("原始数据地址","Publisher data"),SOURCE_URL)

try:
    a=load_analysis()
except EvidenceError:
    st.error(tr("当前数据库与报告不完整或版本不一致，请运行 setup.ps1 重建后再查看。","Database and report are incomplete or from different builds. Run setup.ps1 before continuing."))
    st.stop()
c,t=a["arms"]
d1,d7=a["tests"]
COLORS={"gate_30":"#087F8C","gate_40":"#DA8B52"}


def chart_style(fig,height=340):
    fig.update_layout(height=height,margin=dict(l=15,r=20,t=27,b=40),
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, Microsoft YaHei, sans-serif",color="#62748a",size=12),
        legend=dict(orientation="h",y=-.18,x=0,font=dict(size=11)),hoverlabel=dict(bgcolor="white"),
        bargap=.35,bargroupgap=.08)
    fig.update_xaxes(gridcolor="#e5ebf3",zerolinecolor="#aab8c8")
    fig.update_yaxes(gridcolor="#e5ebf3",zerolinecolor="#aab8c8")
    return fig


def show_trace(result,prefix="trace"):
    for i,step in enumerate(result["trace"],1):
        with st.container():
            st.markdown(f"**{i:02d} · `{step['tool']}`**")
            args=step.get("arguments",{})
            if "sql" in args:
                st.code(args["sql"],language="sql")
            out=step["result"]
            if isinstance(out,dict) and "rows" in out:
                st.dataframe(pd.DataFrame(out["rows"]),hide_index=True,width="stretch",key=f"{prefix}_{i}")
                st.caption(f"{out['row_count']} rows · {out['elapsed_ms']} ms · truncated={out['truncated']}")
            else:
                st.json(out,expanded=False)


if page in ["作品导览","Project guide"]:
    st.markdown('<div class="page-meta">YANQING MA / PROJECT GUIDE / GAME OPERATIONS ANALYTICS</div>',unsafe_allow_html=True)
    st.title(tr("用证据，回答一次游戏上线决策","One game decision, backed by evidence"))
    st.caption(tr("游戏留存实验分析与 AI 运营助手 · 面向招聘浏览与业务演示","Game Retention Experiment Analytics & AI Operations Copilot · reviewer orientation"))
    st.markdown(note(tr("这个项目研究：把游戏进度门槛从第 30 关后移至第 40 关，玩家是否更愿意回来？它把数据检查、实验评估、情景分析和报告交付连接在一起。",
        "The case asks whether moving a progression gate from level 30 to 40 improves return behavior. It connects data checks, experiment assessment, decision scenarios and report delivery.")),unsafe_allow_html=True)
    with st.container(border=True):
        st.subheader(tr("先看结论，再看判断依据","The finding and the judgment"))
        st.write(tr(f"在 {a['rows']:,} 名玩家的公开样本中，实验组 D7 留存比对照组低约 {abs(d7['delta'])*100:.2f} 个百分点。建议暂缓全量上线，先核查分流与数据完整性。",
            f"Across {a['rows']:,} publicly released players, treatment D7 retention is about {abs(d7['delta'])*100:.2f} pp below control. The recommendation is to pause rollout and audit allocation and outcome integrity."))
        st.caption(tr("D7：安装后第七天是否返回。50:50 是未核实的分流假设；观察差异不直接证明机制原因。",
            "D7: return seven days after installation. A 50:50 split is unverified; the difference does not identify its mechanism."))
        st.button(tr("查看实验决策与区间","View experiment evidence"),type="primary",on_click=navigate,args=(tr("实验决策","Experiment decision"),),key="guide_decision")
    route,fit=st.columns([1.15,1])
    with route,st.container(border=True):
        st.subheader(tr("三分钟体验路线","A three-minute review"))
        st.markdown(tr("**① 实验决策** · 看结论、分母与不确定性。\n\n**② 决策沙盘** · 改变规模或容忍边界，理解业务含义。\n\n**③ 行为与质量** · 看极端值与回访组合，核对解释是否可靠。\n\n**④ AI 助手** · 用离线示例查证据，无需 Key。",
            "**① Experiment decision** · finding, denominators and uncertainty.\n\n**② Decision lab** · scale and tolerance assumptions.\n\n**③ Behavior & quality** · outliers and return combinations.\n\n**④ AI copilot** · evidence queries in offline mode, no key needed."))
        st.button(tr("打开决策沙盘","Open decision lab"),on_click=navigate,args=(tr("决策沙盘","Decision lab"),),key="guide_lab")
        st.button(tr("体验离线分析助手","Try offline copilot"),on_click=navigate,args=(tr("AI 分析助手","AI copilot"),),key="guide_copilot")
    with fit,st.container(border=True):
        st.subheader(tr("这份作品展示什么","What the work demonstrates"))
        st.markdown(tr("- SQL/Python 指标构建与实验分析\n- 数据质量复核与运营判断\n- 可交互、可复核的分析交付\n- 中英文沟通与国际化迁移设计\n- 已实现的 LLM 工具接口与边界控制",
            "- SQL/Python metrics and experiment analysis\n- Data integrity and operational judgment\n- Interactive, inspectable analytical delivery\n- Bilingual communication and international measurement design\n- Implemented bounded LLM tool interface"))
        st.caption(tr("个人作品，使用 AI 编程辅助；真实模型调用验收尚待完成。",
            "Independent portfolio project with AI coding assistance; live model acceptance remains pending."))
    with st.expander(tr("适用到哪里？哪些功能没有实现？","Where does it apply, and what is outside scope?")):
        st.dataframe(pd.DataFrame(scope_rows(lang),columns=[tr("分类","Classification"),tr("场景","Scenario"),tr("当前支持","Current support")]),hide_index=True,width="stretch")
        st.write(tr("当前程序只适配这份固定、已审核的数据，不支持任意 CSV 上传。新手引导、版本或地区实验是方法迁移方向，接入新数据后才能开展对应分析。",
            "The app currently supports this fixed reviewed dataset, not arbitrary CSV uploads. Onboarding, version or regional experiments require new data and validation."))
    with st.expander(tr("使用方式与常见问题","Access and frequently asked questions")):
        st.markdown(tr("**需要安装或登录吗？** 已运行的交互版无需登录；离线规则、图表和报告无需 API Key。\n\n**HR 能直接打开当前网址吗？** 不能。127.0.0.1 仅指向当前电脑；远程交互需要另行部署地址。免安装介绍文件则可直接打开。\n\n**能上传自己的游戏数据吗？** 当前不能；需要适配数据契约与指标。\n\n**分析是否代表米哈游玩家？** 不代表；这是 Cookie Cats 历史公开实验。",
            "**Install or sign in?** The running app needs no sign-in. Offline rules, charts and reports need no API key.\n\n**Can an external reviewer use localhost?** No. It refers to the current machine. Remote interaction needs a separately hosted URL; the static introduction opens directly.\n\n**Upload another game's data?** Not currently; schema and metrics need adaptation.\n\n**miHoYo player evidence?** No; this is a historical public Cookie Cats experiment."))
    st.download_button(tr("下载作品介绍与使用说明","Download project introduction"),guide_markdown(a,lang),file_name=f"project_guide_{lang}.md",mime="text/markdown")

elif page in ["实验决策","Experiment decision"]:
    st.markdown('<div class="page-meta">EXPERIMENT 01 / COOKIE CATS / RETENTION</div>',unsafe_allow_html=True)
    st.title(tr("游戏节奏调整，是否值得上线？","Should a later gate ship?"))
    st.caption(tr("进度门槛：第 30 关 → 第 40 关 · 全体入组玩家 · 历史公开实验","Progression gate: level 30 → level 40 · all assigned players · public historical experiment"))
    st.markdown(banner(tr("暂缓上线","HOLD ROLLOUT"),
        tr("D7 留存降低，先完成实验完整性复核","Lower D7 retention; verify experiment integrity first"),
        tr("差异 −0.820pp，95% 区间 [−1.328, −0.312]pp；50:50 分流假设下触发复核。",
           "Difference −0.820pp, 95% CI [−1.328, −0.312]pp; allocation audit flagged under a 50:50 assumption.")),unsafe_allow_html=True)
    with st.container(key="headline_metrics"):
        cols=st.columns(4)
        cols[0].metric(tr("实验玩家","Assigned players"),f"{a['rows']:,}")
        cols[1].metric("gate_30 · D7",f"{c['d7_rate']:.2%}")
        cols[2].metric("gate_40 · D7",f"{t['d7_rate']:.2%}")
        cols[3].metric(tr("D7 差异（百分点）","D7 difference (pp)"),f"{d7['delta']*100:+.3f}")
    st.write("")
    left,right=st.columns([1.05,1])
    with left, st.container(border=True,key="retention_chart"):
        st.subheader(tr("两组留存率","Retention by experiment arm"))
        fig=go.Figure()
        for row in a["arms"]:
            values=[row["d1_rate"]*100,row["d7_rate"]*100]
            fig.add_trace(go.Bar(name=row["version"],x=["D1","D7"],y=values,
                text=[f"{v:.2f}%" for v in values],textposition="outside",marker_color=COLORS[row["version"]],
                error_y=dict(type="data",array=[(row[f"d{k}_ci_high"]-row[f"d{k}_rate"])*100 for k in [1,7]],
                             arrayminus=[(row[f"d{k}_rate"]-row[f"d{k}_ci_low"])*100 for k in [1,7]]),
                hovertemplate="%{x}: %{y:.2f}%<extra>%{fullData.name}</extra>"))
        fig.update_layout(barmode="group")
        fig.update_yaxes(range=[0,55],ticksuffix="%")
        st.plotly_chart(chart_style(fig),width="stretch",key="rates")
        st.caption(tr("分母为各组全部玩家；误差线为 Wilson 95% 区间。","Denominator: all assigned players per arm. Error bars: Wilson 95% CI."))
    with right, st.container(border=True,key="effect_chart"):
        st.subheader(tr("效果与不确定性","Effect and uncertainty"))
        fig=go.Figure(go.Scatter(x=[r["delta"]*100 for r in a["tests"]],y=[r["metric"] for r in a["tests"]],
            mode="markers+text",text=[f"{r['delta']*100:+.3f} pp" for r in a["tests"]],textposition="top center",
            marker=dict(size=13,color=["#62748A","#087F8C"]),
            error_x=dict(type="data",array=[(r["ci_high"]-r["delta"])*100 for r in a["tests"]],
                         arrayminus=[(r["delta"]-r["ci_low"])*100 for r in a["tests"]]),
            hovertemplate="%{y}: %{x:.3f} pp<extra></extra>"))
        fig.add_vline(x=0,line_dash="dash",line_color="#98a6b8")
        fig.update_xaxes(title=tr("gate_40 − gate_30（百分点）","gate_40 − gate_30 (percentage points)"),range=[-1.65,.4])
        fig.update_yaxes(range=[-.55,1.55])
        st.plotly_chart(chart_style(fig),width="stretch",key="effects")
        st.caption(tr("单指标 95% Newcombe 区间；双侧检验，D1/D7 使用 Holm 校正。","Pointwise 95% Newcombe CIs; two-sided tests with Holm correction across D1/D7."))
    info,action=st.columns([1.05,1])
    with info:
        st.warning(tr(f"分流待核验：假设 50:50 时 SRM p={a['srm']['p_value']:.4f}，低于筛查阈值 0.01；真实预期比例未提供。",
                      f"Allocation needs verification: assuming 50:50, SRM p={a['srm']['p_value']:.4f} < screening threshold 0.01. Intended allocation is unavailable."))
    with action:
        st.info(tr("下一步：核对预期分流、结果覆盖与门槛曝光；若核验通过，再确认效果和复测计划。",
                   "Next: verify intended allocation, outcome coverage and gate exposure; then reassess the effect and retest plan."))
    per10k=impact_scenario(d7,10000)
    st.markdown(note(tr(
        f"规模解读：若同样差异适用于每 1 万名新玩家，D7 返回人数差约为 {per10k['retained_difference']:.0f} 人，区间换算约 [{per10k['ci_low']:.0f}, {per10k['ci_high']:.0f}] 人。这是假设换算，进一步情景分析见「决策沙盘」。",
        f"Scale lens: for 10,000 comparable new players, the estimated D7 return difference is {per10k['retained_difference']:.0f}, with transformed interval [{per10k['ci_low']:.0f}, {per10k['ci_high']:.0f}]. Conditional scenario only; explore assumptions in Decision lab.")),unsafe_allow_html=True)
    with st.expander(tr("查看分子、分母和检验结果","Inspect counts and test results")):
        st.dataframe(pd.DataFrame(a["arms"])[["version","players","retained_d1","retained_d7","d1_rate","d7_rate"]],hide_index=True,width="stretch")
        st.dataframe(pd.DataFrame(a["tests"]),hide_index=True,width="stretch")
        st.caption(tr("D1 未显著不等于等效；D7 为本项目事后选定的主指标。","A nonsignificant D1 test is not evidence of equivalence. D7 was chosen retrospectively for this project."))
    st.download_button(tr("下载中文决策简报","Download decision brief"),decision_report(a,lang),file_name=f"decision_brief_{lang}.md",mime="text/markdown")

elif page in ["决策沙盘","Decision lab"]:
    st.markdown('<div class="page-meta">DECISION LAB / IMPACT · TOLERANCE · INTEGRITY</div>',unsafe_allow_html=True)
    st.title(tr("从统计结果，走到业务决策","From an effect estimate to a decision"))
    st.caption(tr("调整假设，查看结论如何变化；不改动历史样本，也不自动批准上线。","Change assumptions, not historical evidence. No automatic rollout approval."))
    impact_tab,integrity_tab,planning_tab=st.tabs([tr("业务影响与容忍边界","Impact & tolerance"),tr("分流假设复核","Allocation assumptions"),tr("复测设计","Retest design")])
    with impact_tab:
        controls,display=st.columns([.85,1.65],gap="large")
        with controls,st.container(border=True):
            st.subheader(tr("设定决策场景","Scenario assumptions"))
            population=st.select_slider(tr("假设未来符合条件的玩家数","Hypothetical future eligible players"),options=[1000,10000,50000,100000,500000,1000000],value=100000,format_func=lambda x:f"{x:,}")
            tolerance=st.slider(tr("可接受的 D7 绝对下降（百分点）","Acceptable D7 decline (pp)"),.1,1.5,.5,.1)
            st.caption(tr("该边界为事后决策演示；不是已批准的业务目标或预注册的非劣效界限。","Retrospective decision lens, not an approved business target or preregistered non-inferiority margin."))
        with display,st.container(border=True):
            impact=impact_scenario(d7,population)
            lens=harm_lens(d7,tolerance)
            st.subheader(tr("同样差异，在这个规模意味着什么？","What would the same difference mean at this scale?"))
            q1,q2=st.columns(2)
            q1.metric(tr("D7 返回人数差（情景）","D7 returns difference (scenario)"),f"{impact['retained_difference']:+,.0f}")
            q2.metric(tr("区间换算（人）","Transformed interval (players)"),f"{impact['ci_low']:+,.0f} ~ {impact['ci_high']:+,.0f}")
            fig=go.Figure(go.Scatter(x=[d7["delta"]*100],y=["D7"],mode="markers+text",marker=dict(color=COLORS["gate_30"],size=13),
                text=[f"{d7['delta']*100:+.3f} pp"],textposition="top center",error_x=dict(type="data",array=[(d7["ci_high"]-d7["delta"])*100],arrayminus=[(d7["delta"]-d7["ci_low"])*100])))
            fig.add_vrect(x0=-1.65,x1=-tolerance,fillcolor="#fbede7",opacity=.75,line_width=0,layer="below")
            fig.add_vline(x=-tolerance,line_color="#cb8d63",line_dash="dash",annotation_text=tr("容忍边界","Tolerance"))
            fig.add_vline(x=0,line_color="#8da2b8",line_dash="dot")
            fig.update_xaxes(range=[-1.65,.35],title=tr("gate_40 − gate_30（百分点）","gate_40 − gate_30 (pp)"))
            fig.update_yaxes(range=[-.7,.9])
            st.plotly_chart(chart_style(fig,230),width="stretch",config={"displayModeBar":False},key="tolerance_interval")
            labels={"overlaps_tolerance":tr("区间跨越容忍边界，尚不能排除超出容忍范围的损害。","The interval crosses the tolerance boundary; larger-than-tolerated harm remains possible."),
                    "beyond_tolerance":tr("整个区间都落在容忍边界之外，提示需重视的留存损害。","The entire interval lies beyond the tolerated decline."),
                    "within_tolerance":tr("当前区间位于容忍范围内；仍不代表正式非劣效成立或可直接上线。","The interval is within the chosen tolerance; this is not a formal non-inferiority finding or rollout approval.")}
            st.markdown(note(labels[lens["state"]]),unsafe_allow_html=True)
        st.caption(tr("人数换算假设差异可迁移至未来总体；区间仅继承本次样本的统计不确定性，不包含跨时期、地区或产品迁移的不确定性。",
                       "The scenario assumes transport to the future population. The interval reflects historical sampling uncertainty only, excluding transport across periods, markets or products."))
        st.download_button(tr("导出当前决策情景","Export this scenario"),scenario_markdown(d7,population,tolerance,lang),file_name=f"decision_scenario_{population}_{tolerance:.1f}pp_{lang}.md",mime="text/markdown")
    with integrity_tab:
        with st.container(border=True):
            st.subheader(tr("同一批人数，不同预期分流假设","Same counts, different intended-allocation assumptions"))
            st.markdown(note(tr("预期比例必须来自实验配置，不能按观察人数反推来让检查通过。下面只展示假设敏感性，默认分析仍保留未核实的 50:50 假设。",
                                "The intended ratio must come from assignment configuration, not be fitted to observed counts. This is sensitivity analysis only; the main report retains the unverified 50:50 assumption.")),unsafe_allow_html=True)
            share=st.slider(tr("假设对照组应占（%）","Assumed intended control share (%)"),49.,51.,50.,.1)
            check=allocation_check(c["players"],t["players"],share/100)
            x1,x2,x3=st.columns(3)
            x1.metric(tr("观察到的对照占比","Observed control share"),f"{c['players']/a['rows']:.3%}")
            x2.metric(tr("该假设下 SRM p 值","Conditional SRM p-value"),f"{check['p_value']:.5f}")
            x3.metric(tr("筛查结果（阈值 .01）","Screen (threshold .01)"),tr("需复核","FLAG") if check["p_value"]<.01 else tr("未触发","NO FLAG"))
            allocation=pd.DataFrame({"arm":["gate_30","gate_40"],"observed":[c["players"],t["players"]],"expected":[check["expected_control_n"],check["expected_treatment_n"]]})
            fig=go.Figure()
            fig.add_bar(name=tr("观察人数","Observed"),x=allocation.arm,y=allocation.observed,marker_color="#087f8c")
            fig.add_bar(name=tr("假设预期人数","Assumed expected"),x=allocation.arm,y=allocation.expected,marker_color="#c7d4e4")
            fig.update_layout(barmode="group")
            fig.update_yaxes(rangemode="tozero")
            st.plotly_chart(chart_style(fig,280),width="stretch",config={"displayModeBar":False},key="allocation_scenario")
    with planning_tab:
        plan,scope=st.columns([1.1,1])
        with plan,st.container(border=True):
            st.subheader(tr("为下一次实验预先设定样本量","Plan sample size before the next experiment"))
            mde=st.slider(tr("希望检测的 D7 绝对下降（百分点）","D7 decline to detect (pp)"),.5,2.,1.,.1)
            n=required_n(c["d7_rate"],mde/100)
            st.metric(tr("每组所需玩家（近似）","Required players per arm (approx.)"),f"{n:,}")
            grid=[.5,.75,1.,1.25,1.5,2.]
            fig=go.Figure(go.Scatter(x=grid,y=[required_n(c["d7_rate"],m/100) for m in grid],mode="lines+markers",line_color="#087f8c"))
            fig.update_xaxes(title=tr("可检测绝对下降（百分点）","Detectable absolute decline (pp)"))
            fig.update_yaxes(title=tr("每组人数","Players per arm"),rangemode="tozero")
            st.plotly_chart(chart_style(fig,260),width="stretch",config={"displayModeBar":False},key="power_plan")
            st.caption(tr("基线 19.02%、等比例分组、80% 功效、双侧 alpha=.05、固定样本正态近似；不计算事后功效。","Baseline 19.02%, equal allocation, 80% power, two-sided alpha=.05; fixed-sample normal approximation, not post-hoc power."))
        with scope,st.container(border=True):
            st.subheader(tr("复测前先补齐的证据","Evidence needed before retesting"))
            st.markdown(tr("1. **实验配置**：预期分流、入组与排除规则。\n2. **日志完整性**：分流、曝光、去重、结果成熟度。\n3. **事前指标**：主指标、可接受损害、停止规则。\n4. **业务护栏**：付费、新手体验和性能数据。\n5. **国际化**：地区分层、当地日界与多重比较。",
                "1. **Assignment:** intended ratio and eligibility.\n2. **Integrity:** exposure, deduplication and mature outcomes.\n3. **Prespecification:** primary metric, acceptable harm and stopping rule.\n4. **Guardrails:** payments, onboarding and performance.\n5. **International:** region stratification, local-day rules and multiplicity."))
            st.caption(tr("仅有 D1 与 D7 不能识别随时间衰减的新鲜感效应；需要按暴露时长记录的纵向数据。","D1 and D7 alone cannot identify a novelty effect over exposure duration; longitudinal evidence is needed."))

elif page in ["行为与质量","Behavior & quality"]:
    st.title(tr("行为差异与数据可信度","Behavior and data integrity"))
    st.caption(tr("探索性视图；不改变全体入组玩家的主实验结论。","Exploratory view; the main experiment comparison remains all assigned players."))
    st.warning(tr("累计局数的源材料窗口存在 7 天 / 14 天表述冲突；仅作描述，不代表关卡、门槛曝光或可提前预测的特征。",
                  "Source materials conflict on the rounds window (7 vs 14 days). Descriptive only: rounds are not levels, gate exposure or prospective features."))
    arm=st.selectbox(tr("行为图分组范围","Arm scope for behavioral charts"),["All","gate_30","gate_40"])
    bands=pd.DataFrame(a["round_bands"])
    if arm!="All":
        bands=bands[bands.version==arm].copy()
    bands["share"]=bands.players/bands.groupby("version").players.transform("sum")*100
    order=["0","1-10","11-30","31-100","101-300","301+"]
    col1,col2=st.columns(2)
    with col1:
        st.subheader(tr("累计局数分布","Recorded rounds distribution"))
        fig=go.Figure()
        for version,g in bands.groupby("version"):
            g=g.set_index("round_band").reindex(order).reset_index()
            fig.add_bar(name=version,x=g.round_band,y=g.share,marker_color=COLORS[version],
                        text=[f"{x:.1f}%" for x in g.share],textposition="outside")
        fig.update_layout(barmode="group")
        fig.update_yaxes(title=tr("组内玩家占比","Share of players per arm"),ticksuffix="%",rangemode="tozero")
        st.plotly_chart(chart_style(fig),width="stretch",key="round_distribution")
    with col2:
        st.subheader(tr("局数与 D7 的观察关联","Observed rounds–D7 association"))
        fig=go.Figure()
        for version,g in bands.groupby("version"):
            g=g.set_index("round_band").reindex(order).reset_index()
            fig.add_scatter(name=version,x=g.round_band,y=g.d7_rate*100,mode="lines+markers",line_color=COLORS[version])
        fig.update_yaxes(range=[0,100],ticksuffix="%")
        st.plotly_chart(chart_style(fig),width="stretch",key="round_association")
        st.caption(tr("分组依据发生在分流后，且可能包含 D7 后行为。仅为相关性，不用于因果分群或流失预测。",
                       "Bands are defined after treatment and may include behavior after D7. Association only; not causal subgroup analysis or churn prediction."))
    st.subheader(tr("回访组合：D7 玩家从哪里来？","Return combinations: who returns on D7?"))
    with st.container(border=True):
        patterns=pd.DataFrame(return_patterns(a))
        names={"00":tr("D1、D7 均未返回","Neither D1 nor D7"),"10":tr("仅 D1 返回","D1 only"),
               "01":tr("仅 D7 返回","D7 only"),"11":tr("D1、D7 均返回","Both D1 and D7")}
        pattern_colors={"00":"#d8e1ed","10":"#849cba","01":"#d2a371","11":"#087f8c"}
        fig=go.Figure()
        for pattern in ["00","10","01","11"]:
            rows=patterns[patterns.pattern==pattern].sort_values("version")
            fig.add_bar(name=names[pattern],y=rows.version,x=rows.share*100,orientation="h",marker_color=pattern_colors[pattern],
                        text=[f"{v:.1%}" for v in rows.share],textposition="inside",customdata=rows.players,
                        hovertemplate="%{y}: %{x:.2f}% · n=%{customdata:,}<extra>%{fullData.name}</extra>")
        fig.update_layout(barmode="stack")
        fig.update_xaxes(range=[0,100],ticksuffix="%")
        st.plotly_chart(chart_style(fig,230),width="stretch",key="return_patterns",config={"displayModeBar":False})
        st.caption(tr("此图固定比较两组全部玩家，不受局数筛选影响。两天均未返回不等于期间从未登录；仅 D7 返回不等于由活动召回。组合是观察描述，不是归因。",
                       "Fixed all-player comparison, independent of the rounds filter. Neither-day return does not mean no activity between days; D7-only does not establish campaign reactivation. Descriptive, not attribution."))
    st.subheader(tr("极端记录敏感性","Extreme-record sensitivity"))
    sensitivity=pd.DataFrame(a["sensitivity"])
    full=sensitivity[sensitivity["sample"]=="All players"].set_index("version")
    trimmed=sensitivity[sensitivity["sample"]!="All players"].set_index("version")
    before=full.loc["gate_30","mean_rounds"]-full.loc["gate_40","mean_rounds"]
    after=trimmed.loc["gate_30","mean_rounds"]-trimmed.loc["gate_40","mean_rounds"]
    st.markdown(note(tr(f"均值差高度依赖极端记录：对照组减实验组的平均局数差，保留时为 {before:.3f} 局，排除最大值后约 {after:.3f} 局；D7 差异仍约 −0.82pp。不能用平均局数的原始差异单独解释留存变化。",
                       f"Mean-round gap (control minus treatment) is outlier-sensitive: {before:.3f} rounds with all records versus {after:.3f} excluding the maximum; D7 difference remains about −0.82pp. The raw mean gap alone cannot explain retention.")),unsafe_allow_html=True)
    st.dataframe(sensitivity,hide_index=True,width="stretch",column_config={"mean_rounds":st.column_config.NumberColumn(format="%.2f"),"median_rounds":st.column_config.NumberColumn(format="%.0f"),"d7_rate":st.column_config.NumberColumn(format="%.5f"),"d7_delta":st.column_config.NumberColumn(format="%.5f")})
    st.caption(tr("主分析保留 49,854 局记录；排除仅作敏感性检查，未修改原始数据。留存列单位为比例。该表固定显示全体样本，不受上方行为图筛选影响。",
                   "Main analysis retains the 49,854-round record; exclusion is sensitivity-only. Retention columns are fractions. This full-sample table is independent of the behavioral-chart filter."))
    q,tcol=st.columns([1.2,1])
    with q:
        st.subheader(tr("数据质量检查","Data quality checks"))
        st.dataframe(pd.DataFrame(a["quality"]),hide_index=True,width="stretch")
    with tcol:
        st.subheader(tr("D1 / D7 返回组合","D1 / D7 return combinations"))
        trans=pd.DataFrame(a["transitions"])
        st.dataframe(trans,hide_index=True,width="stretch")
        st.caption(tr("D7 返回但 D1 未返回是合法组合，因此不能画成顺序漏斗。","D7 return without D1 return is valid; these are not sequential funnel stages."))
    export=bands[["version","round_band","players","retained_d7","d7_rate","share"]]
    st.download_button(tr("导出当前行为图数据","Export current behavioral-chart data"),export.to_csv(index=False),file_name=f"round_bands_{arm}.csv",mime="text/csv")

elif page in ["AI 分析助手","AI copilot"]:
    st.markdown('<div class="page-meta">ANALYSIS COPILOT / QUESTION → EVIDENCE → REVIEW</div>',unsafe_allow_html=True)
    st.title(tr("让每个回答，都能追溯到证据","An answer you can trace to evidence"))
    st.caption(tr("会话式分析 · 聚合指标 · 每次回答保留执行记录","Conversational analysis · aggregate metrics · evidence attached to each answer"))
    mode=st.radio(tr("运行模式","Mode"),[tr("离线规则演示（不调用 LLM）","Offline rules demo (no LLM)"),tr("DeepSeek 实时 Agent","Live DeepSeek agent")],horizontal=True)
    live=mode in ["DeepSeek 实时 Agent","Live DeepSeek agent"]
    if live:
        st.caption(tr("模型仅接收问题、最近六条对话上下文、指标知识与聚合证据。密钥不写入轨迹；真实调用记录保存在本地。",
                       "Requests include the question, up to six prior messages, metric knowledge and aggregate evidence. Keys are excluded from traces; live runs are saved locally."))
        cfg=settings()
        api_key=st.text_input(tr("DeepSeek API Key（隐藏输入，不写文件）","DeepSeek API key (hidden; not saved)"),type="password",key="session_api_key")
        key=api_key or cfg.get("DEEPSEEK_API_KEY","")
        if not key:
            st.caption(tr("也可运行 configure_api.ps1 写入本地 .env；请不要把密钥发到聊天或提交 Git。",
                           "Alternatively run configure_api.ps1 to write local .env. Do not send keys in chat or commit them."))
        model=st.text_input(tr("模型名","Model"),value=cfg.get("DEEPSEEK_MODEL","deepseek-flash"))
    else:
        key=""
        model=""
        st.info(tr("此模式使用固定意图规则和真实 SQL 结果，便于无密钥演示；不代表已调用大模型。",
                   "This mode uses fixed intent rules and real SQL results for key-free demos; it is not an LLM response."))
    examples=[tr("是否应该上线 gate_40？请引用证据。","Should we roll out gate_40? Cite the evidence."),
              tr("为什么留存降低？能用累计局数预测早期流失吗？","Why is retention lower? Can recorded rounds predict early churn?"),
              tr("为什么上周欧洲地区 DAU 下降？","Why did European DAU decline last week?"),
              tr("请生成一份运营实验决策报告。","Generate an experiment decision report.")]
    chat_key=f"chat_{lang}_{'live' if live else 'offline'}"
    turns=st.session_state.setdefault(chat_key,[])
    question=None
    if not turns:
        st.subheader(tr("从一个业务问题开始","Start with a decision"))
        labels=[tr("评估是否上线","Evaluate rollout"),tr("检查流失预测边界","Check prediction limits"),tr("核查海外异常问题","Check regional coverage"),tr("生成运营简报","Draft decision brief")]
        for row in range(2):
            buttons=st.columns(2)
            for col in range(2):
                ix=row*2+col
                if buttons[col].button(labels[ix],key=f"ask_{ix}",width="stretch",disabled=live and not key):
                    question=examples[ix]
        st.caption(tr("离线模式仅识别预设意图，不具有通用多轮理解能力。实时模式会带入最近对话，并重新查询证据。",
                       "Offline mode recognizes fixed intents only. Live mode uses recent context and retrieves evidence again."))
    else:
        if st.button(tr("清空本模式会话","Clear this conversation"),key="clear_chat"):
            st.session_state[chat_key]=[]
            st.session_state.pop("agent_result",None)
            st.rerun()
    for turn_ix,result in enumerate(turns):
        with st.chat_message("user"):
            st.write(result["question"])
        with st.chat_message("assistant"):
            st.caption(f"{'DeepSeek' if result['mode']=='live_llm' else tr('离线规则','Offline rules')} · {len(result['trace'])} {tr('次工具执行','tool executions')} · {tr('待分析师复核','review required')}")
            if result.get("build_id")!=a["build_id"]:
                st.caption(tr("这条历史回答来自先前构建，请重新提问以使用当前证据。","This historical answer predates the current build. Ask again to use current evidence."))
            st.markdown(result["answer"])
            with st.expander(tr("查看本次执行证据","Inspect this answer's evidence")):
                show_trace(result,prefix=f"{chat_key}_{turn_ix}")
                st.json({k:result.get(k) for k in ["build_id","source_sha256"]},expanded=False)
                if result.get("usage"):
                    st.json(result["usage"],expanded=False)
                st.download_button(tr("下载回答与证据","Download answer and evidence"),json.dumps(result,ensure_ascii=False,indent=2),file_name=f"analysis_evidence_{turn_ix+1}.json",mime="application/json",key=f"export_{chat_key}_{turn_ix}")
    prompt=st.chat_input(tr("输入分析问题，例如：D7 差异是多少？","Ask a question, e.g. what is the D7 difference?"),max_chars=3000,disabled=live and not key,key=f"prompt_{chat_key}")
    question=prompt or question
    if question:
        with st.chat_message("user"):
            st.write(question)
        try:
            with st.status(tr("检索并执行分析工具…","Retrieving and executing evidence tools…"),expanded=True) as status:
                history=[]
                for previous in turns[-3:]:
                    history.extend([{"role":"user","content":previous["question"]},{"role":"assistant","content":previous["answer"]}])
                def progress(event):
                    if event["kind"]=="tool":
                        st.write(f"{event['tool']} · {'OK' if event['success'] else 'ERROR'}")
                    else:
                        status.update(label=tr(f"模型正在选择工具 · 第 {event['step']} 轮",f"Model choosing tools · round {event['step']}"))
                result=run_agent(question,key,model,lang,history=history,on_event=progress) if live else offline_demo(question,lang)
                if not live:
                    st.write(tr(f"已执行 {len(result['trace'])} 个本地证据工具；未调用大模型。",f"Executed {len(result['trace'])} local evidence tools; no LLM call."))
                status.update(label=tr("证据已返回，回答待复核","Evidence returned; answer ready for review"),state="complete",expanded=False)
            turns.append(result)
            st.session_state["agent_result"]=result
            st.rerun()
        except (AgentError,QueryRejected) as exc:
            st.error(str(exc))
    with st.expander(tr("SQL 工作台：仅允许聚合视图","SQL workbench: aggregate views only")):
        st.json(schema_description(),expanded=False)
        sql=st.text_area("SQL",value="SELECT version, players, d1_rate, d7_rate\nFROM v_arm_metrics ORDER BY version",height=110)
        if st.button(tr("执行只读 SQL","Run read-only SQL")):
            try:
                out=run_query(sql)
                st.dataframe(pd.DataFrame(out["rows"]),hide_index=True,width="stretch")
                st.caption(f"Rows: {out['row_count']} · {out['elapsed_ms']} ms · truncated={out['truncated']}")
            except QueryRejected as exc:
                st.error(str(exc))

else:
    st.title(tr("指标、证据与项目边界","Definitions, evidence and scope"))
    with st.container(border=True):
        st.subheader(tr("当前可用状态","Current readiness"))
        status1,status2,status3=st.columns(3)
        status1.metric(tr("来源快照","Source snapshot"),tr("已校验","Verified"))
        status2.metric(tr("数据库与报告","Database & report"),tr("版本一致","Matched build"))
        status3.metric(tr("模型连接","Model connection"),tr("可选增强","Optional"))
        st.caption(tr("统计、SQL、图表及报告可离线使用。真实模型能力需配置密钥后实测，不能由本地测试通过来替代。","Statistics, SQL, charts and reports work offline. Live model capability needs provider testing after key configuration; local tests are not a substitute."))
    st.subheader(tr("当前数据能回答什么","What this data supports"))
    st.dataframe(pd.DataFrame(run_query("SELECT * FROM v_capabilities")["rows"]),hide_index=True,width="stretch")
    st.subheader(tr("指标字典","Metric dictionary"))
    st.dataframe(pd.DataFrame(run_query("SELECT * FROM v_definitions")["rows"]),hide_index=True,width="stretch")
    st.subheader(tr("面向国际化运营的迁移设计","Extension to international operations"))
    st.markdown(tr("现有样本不含国家或语言，不能产出地区结论。迁移方案需要：匿名玩家 ID、事件 UTC 时间、玩家时区、地区与语言、平台、版本、实验分流与门槛曝光；再核对当地日界、完整观察期、地区分层随机化和多重比较。中英文简报共用一套计算结果。",
                   "The release has no country or language fields, so no regional finding is claimed. An extension needs pseudonymous player IDs, event UTC time, player timezone, country/locale, platform, version, assignment and gate-exposure events; then validate local-day boundaries, complete outcome windows, region-stratified randomization and multiplicity. Chinese and English briefs share the same computed evidence."))
    st.markdown(tr("**面向原神 / 星铁 / 绝区零的业务迁移：**可以把本例的“节奏门槛变更”转换为新手引导或内容解锁节奏实验；具体玩法假设需要新数据验证，不能把休闲消除游戏结论直接套用。",
                   "**Transfer to Genshin / Star Rail / ZZZ:** use the experiment framework for onboarding or content-unlock pacing, but validate new game-specific hypotheses and data. A casual-puzzle result does not establish an effect in another genre."))
    st.subheader(tr("数据来源与可复现性","Source and reproducibility"))
    st.markdown(f"[DataCamp dataset]({SOURCE_URL}) · [Historical teaching notebook](https://github.com/DataCamp-Data-Science-Projects/Project-Mobile-Games-AB-Testing-with-Cookie-Cats)")
    st.code(a["source_sha256"],language=None)
    st.caption(tr("原始 CSV 单独下载，不随仓库发布；未核验明确的再分发许可。累计局数窗口在教学材料中存在 7/14 天冲突。",
                   "Raw CSV is fetched separately and excluded from the repository; no explicit redistribution license was verified. Teaching materials conflict on the rounds horizon (7/14 days)."))
    with st.expander(tr("分析知识库与局限","Analysis knowledge and limitations")):
        st.markdown((ROOT/"docs/analysis_knowledge.md").read_text(encoding="utf-8"))
        st.json(a["limitations"])
    st.download_button(tr("下载英文决策简报","Download English decision brief"),decision_report(a,"en"),file_name="decision_brief_en.md",mime="text/markdown")

st.markdown('<div class="footer-note">'+tr("个人项目 · 历史公开实验 · 所有建议待业务复核 · SQL / Python / Streamlit","Independent project · historical public experiment · analyst review required · SQL / Python / Streamlit")+'</div>',unsafe_allow_html=True)
