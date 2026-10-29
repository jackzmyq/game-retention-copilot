(function(){
'use strict';
const D=window.RETENTION_EVIDENCE,C=window.RetentionCore;
const root=document.getElementById('content');
if(!D||!C){root.innerHTML='<h1>证据未就绪 / Evidence unavailable</h1><p>请运行 python scripts/build_web.py 后再打开。</p>';return;}
const A=D.analysis,control=A.arms[0],treatment=A.arms[1],d7=A.tests.find(x=>x.metric==='D7');
const state={page:['guide','experiment','lab','quality','copilot','scope'].includes(location.hash.slice(1))?location.hash.slice(1):'guide',lang:'zh',population:100000,tolerance:.5,allocation:50,mde:1,arm:'All',chat:{zh:[],en:[]}};
const E=C.escape,T=(zh,en)=>state.lang==='en'?en:zh;
const number=n=>Number(n).toLocaleString('en-US',{maximumFractionDigits:0});
const percent=n=>(n*100).toFixed(2)+'%';
const signed=(n,d=3)=>(n>=0?'+':'')+n.toFixed(d);
const pp=n=>signed(n*100)+' pp';
const metric=(label,value)=>`<div class="metric"><div class="label">${E(label)}</div><div class="value">${E(value)}</div></div>`;
const note=(text,warning=false)=>`<div class="note ${warning?'warning':''}">${E(text)}</div>`;
const panel=(title,body)=>`<section class="panel"><h2>${E(title)}</h2>${body}</section>`;
const table=(headers,rows)=>`<div class="table-scroll"><table><thead><tr>${headers.map(x=>`<th>${E(x)}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr>${r.map(x=>`<td>${E(x)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
const heading=(meta,title,sub)=>`<div class="eyebrow">${E(meta)}</div><h1>${E(title)}</h1><p class="subtitle">${E(sub)}</p>`;
const goButton=(page,label)=>`<button class="button secondary" data-page="${page}">${E(label)}</button>`;
const reportLinks=()=>`<div class="buttons"><a class="button" download href="assets/project_brief.pdf">${T('下载两页作品 PDF','Download project PDF')}</a><a class="button secondary" download href="assets/decision_brief_${state.lang}.md">${T('下载决策简报','Download decision brief')}</a></div>`;
const legend=()=>'<div class="legend"><span><i class="dot" style="background:#087f86"></i>gate_30</span><span><i class="dot" style="background:#d58d55"></i>gate_40</span></div>';
function svg(contents,label,height=260){return `<div class="chart"><svg viewBox="0 0 680 ${height}" role="img" aria-label="${E(label)}">${contents}</svg></div>`;}
function rateChart(){
  const y=n=>210-n*310;let s='';
  for(let v=0;v<=.5;v+=.1){const yy=y(v);s+=`<line x1="55" y1="${yy}" x2="650" y2="${yy}" stroke="#e6edf4"/><text x="43" y="${yy+4}" text-anchor="end" class="chart-label">${(v*100).toFixed(0)}%</text>`;}
  [1,7].forEach((day,i)=>{
    const center=210+i*275;
    A.arms.forEach((r,j)=>{
      const value=r[`d${day}_rate`],x=center-77+j*83,color=j?'#d58d55':'#087f86',lo=r[`d${day}_ci_low`],hi=r[`d${day}_ci_high`];
      s+=`<rect x="${x}" y="${y(value)}" width="70" height="${210-y(value)}" fill="${color}"/><line x1="${x+35}" y1="${y(lo)}" x2="${x+35}" y2="${y(hi)}" stroke="#405970"/><text x="${x+35}" y="${y(hi)-12}" text-anchor="middle" class="chart-value">${percent(value)}</text>`;
    });s+=`<text x="${center}" y="236" text-anchor="middle" class="chart-label">D${day}</text>`;
  });return svg(s,T('各组 D1/D7 留存及 Wilson 区间','D1/D7 retention and Wilson intervals'))+legend();
}
function effectChart(tolerance){
  const x=v=>60+(v+1.65)/2.05*585;let s='';
  if(tolerance!==undefined)s+=`<rect x="60" y="30" width="${x(-tolerance)-60}" height="155" fill="#fcf0e9"/><line x1="${x(-tolerance)}" y1="30" x2="${x(-tolerance)}" y2="190" stroke="#cc946b" stroke-dasharray="5 4"/><text x="${x(-tolerance)}" y="19" text-anchor="middle" class="chart-label">${T('容忍边界','Tolerance')}</text>`;
  s+=`<line x1="${x(0)}" y1="30" x2="${x(0)}" y2="190" stroke="#8f9eae" stroke-dasharray="5 4"/>`;
  const rows=tolerance===undefined?A.tests:[d7];
  rows.forEach((r,i)=>{const y=rows.length===1?108:75+i*85;s+=`<text x="38" y="${y+4}" text-anchor="end" class="chart-label">${r.metric}</text><line x1="${x(r.ci_low*100)}" y1="${y}" x2="${x(r.ci_high*100)}" y2="${y}" stroke="#496278" stroke-width="2"/><circle cx="${x(r.delta*100)}" cy="${y}" r="6" fill="#087f86"/><text x="${x(r.delta*100)}" y="${y-15}" text-anchor="middle" class="chart-value">${pp(r.delta)}</text>`;});
  [-1.5,-1,-.5,0].forEach(v=>{s+=`<text x="${x(v)}" y="214" text-anchor="middle" class="chart-label">${v}</text>`;});
  s+=`<text x="350" y="244" text-anchor="middle" class="chart-label">${T('gate_40 − gate_30（百分点）','gate_40 − gate_30 (percentage points)')}</text>`;
  return svg(s,T('留存差异与单指标 95% 区间','Retention difference and pointwise 95% interval'));
}
function evidenceDetails(names){return `<details><summary>${T('展开已执行 SQL 与聚合证据','Inspect executed SQL and aggregate evidence')}</summary>${names.map(name=>{const r=D.evidence[name];return `<h3>${E(name)}</h3><pre>${E(r.sql)}</pre>${table(r.columns,r.rows.map(row=>r.columns.map(c=>typeof row[c]==='number'&&!Number.isInteger(row[c])?row[c].toFixed(6):row[c])))}`;}).join('')}<p class="muted">${T('SQL 已在 Python 构建时执行；本网页展示保存的结果，不运行任意 SQL。','SQL executed during the Python build. This page displays saved results, not arbitrary live SQL.')}<br>Build: ${E(A.build_id)}</p></details>`;}
function guide(){return heading('YANQING MA / PUBLIC VISITOR EDITION',T('用证据，评估一次产品改动','A product decision, backed by evidence'),T('无需登录 · 无需 Key · 浏览器内交互','No login · no API key · browser-local interactions'))+
  note(T('公开历史实验案例：进度门槛从第 30 关移到第 40 关，玩家是否更愿意回来？','Historical public experiment: does moving a progression gate from level 30 to 40 improve return behavior?'))+
  `<div class="grid three">${metric(T('公开实验玩家','Assigned players'),number(A.rows))}${metric('gate_30 · D7',percent(control.d7_rate))}${metric('gate_40 · D7',percent(treatment.d7_rate))}</div>`+
  `<div class="decision"><span class="badge">${T('暂缓上线','HOLD ROLLOUT')}</span><div><b>${T('D7 留存更低，先核查实验完整性','Lower D7 retention; audit experiment integrity first')}</b><p class="muted">${T('差异 −0.820 个百分点；50:50 分流假设未核实，比例检查触发复核。','Difference −0.820 pp; the unverified 50:50 allocation assumption triggers an integrity screen.')}</p></div></div>`+
  `<div class="grid two">${panel(T('三分钟体验路线','A three-minute review'),`<ol><li>${T('查看实验结论、分母与区间。','Inspect the finding, denominators and intervals.')}</li><li>${T('调整沙盘规模和容忍边界。','Change population and tolerance assumptions.')}</li><li>${T('看极端值，再用离线规则问一个问题。','Inspect outliers, then try an offline question.')}</li></ol><div class="buttons">${goButton('experiment',T('查看实验决策','View experiment'))}${goButton('lab',T('操作决策沙盘','Explore scenarios'))}${goButton('copilot',T('体验离线助手','Try offline copilot'))}</div>`)}${panel(T('作品展示的能力','What this demonstrates'),`<ul><li>SQL / Python ${T('指标构建与实验评估','metrics and experiment assessment')}</li><li>${T('质量复核、业务判断与证据追溯','Integrity checks, business judgment and traceable evidence')}</li><li>${T('双语汇报与交互交付','Bilingual communication and interactive delivery')}</li><li>${T('源码保留可选 LLM 接口，真实调用待验收','Optional LLM interface in source; live acceptance pending')}</li></ul>`)}</div>`+
  reportLinks()+note(T('访客版不调用大模型、不收集密钥、不保存聊天到服务器。Python 完整版与受限 SQL 工具保留在源码中。','The visitor edition makes no LLM calls, collects no keys and sends no chat to a server. The full Python app and restricted SQL tools remain in source.'));
}
function experiment(){return heading('EXPERIMENT 01 / RETENTION',T('游戏节奏调整，是否值得上线？','Should a later gate ship?'),T('全体入组玩家 · gate_30 对照 → gate_40 实验','All assigned players · gate_30 control → gate_40 treatment'))+
  `<div class="grid four">${metric(T('实验玩家','Assigned players'),number(A.rows))}${metric('gate_30 · D7',percent(control.d7_rate))}${metric('gate_40 · D7',percent(treatment.d7_rate))}${metric(T('D7 差异（百分点）','D7 difference (pp)'),signed(d7.delta*100))}</div>`+
  `<div class="grid two">${panel(T('两组留存率','Retention by arm'),rateChart()+`<p class="muted">${T('各组全部玩家为分母；误差线为 Wilson 95% 区间。','All players per arm in denominator; Wilson 95% intervals.')}</p>`)}${panel(T('效果与不确定性','Effect and uncertainty'),effectChart()+`<p class="muted">${T('单指标 Newcombe 95% 区间；D1/D7 的 p 值做 Holm 校正。','Pointwise Newcombe 95% intervals; Holm correction over D1/D7 p-values.')}</p>`)}</div>`+
  note(T(`50:50 假设下 SRM p=${A.srm.p_value.toFixed(5)}，低于 .01 筛查阈值。预期分流比例尚未核实，建议先核查。`,`Under an unverified 50:50 split, SRM p=${A.srm.p_value.toFixed(5)} < .01. Verify intended allocation before causal interpretation.`),true)+
  note(T('D7 为本作品事后选定的主指标，并非已核验的预注册。D1 未显著不代表等效。','D7 was selected retrospectively for this work, not verified preregistration. Nonsignificant D1 does not establish equivalence.'))+
  evidenceDetails(['arms','tests'])+reportLinks();}
function lab(){return heading('DECISION LAB / ASSUMPTIONS',T('从统计结果，走到业务决策','From an estimate to a decision'),T('调整假设，不改动历史证据；不自动批准上线。','Change assumptions, not evidence; no automatic rollout approval.'))+
  `<div class="grid two">${panel(T('设定决策场景','Scenario assumptions'),`<label class="control">${T('假设未来符合条件的玩家数','Hypothetical eligible players')}<select id="population">${[1000,10000,50000,100000,500000,1000000].map(n=>`<option value="${n}" ${n===state.population?'selected':''}>${number(n)}</option>`).join('')}</select></label><label class="control" for="tolerance">${T('可接受 D7 绝对下降（百分点）','Acceptable D7 decline (pp)')} <output id="tolerance-value">${state.tolerance.toFixed(1)}</output><input id="tolerance" type="range" min="0.1" max="1.5" step="0.1" value="${state.tolerance}"></label><p class="muted">${T('事后演示边界，不是预注册的非劣效检验。','Retrospective lens, not a preregistered non-inferiority test.')}</p>`)}<section class="panel" id="scenario-results"></section></div>`+
  panel(T('分流假设敏感性','Allocation-assumption sensitivity'),note(T('预期比例应来自实验配置，不能按观察人数反推来让检查通过。这里仅展示假设变化。','The intended ratio must come from configuration, not be fitted to observed counts to pass a check. Sensitivity only.'))+`<label class="control" for="allocation">${T('假设对照组应占（%）','Assumed intended control share (%)')} <output id="allocation-value">${state.allocation.toFixed(1)}%</output><input id="allocation" type="range" min="49" max="51" step="0.1" value="${state.allocation}"></label><div id="allocation-results"></div>`)+
  `<div class="grid two">${panel(T('复测样本量规划','Plan the next experiment'),`<label class="control" for="mde">${T('检测绝对下降（百分点）','Detectable decline (pp)')} <output id="mde-value">${state.mde.toFixed(1)}</output><input id="mde" type="range" min="0.5" max="2" step="0.1" value="${state.mde}"></label><div id="planning-result"></div><p class="muted">${T('基线 19.02%，等比例分组、80% 功效、双侧 alpha=.05，固定样本正态近似。','Baseline 19.02%, equal allocation, 80% power, two-sided alpha=.05; fixed-sample normal approximation.')}</p>`)}${panel(T('复测前的证据清单','Before retesting'),`<ul><li>${T('核对预期分流、入组和排除规则。','Verify allocation, eligibility and exclusions.')}</li><li>${T('补齐曝光、观察期和结果覆盖日志。','Obtain exposure and mature-outcome coverage logs.')}</li><li>${T('预先定义主指标、护栏和停止规则。','Prespecify primary metric, guardrails and stopping rule.')}</li><li>${T('地区实验需时区、分层与多重比较设计。','Regional experiments need timezone, stratification and multiplicity design.')}</li></ul>`)}</div>`;}
function updateScenario(){
  const result=C.impact(d7,state.population),lens=C.tolerance(d7,state.tolerance);
  const labels={beyond_tolerance:T('整个区间都超出容忍边界。','The entire interval exceeds the tolerated decline.'),within_tolerance:T('区间位于容忍范围内；仍不等于正式非劣效或可直接上线。','The interval lies within the chosen tolerance; this is not formal non-inferiority or rollout approval.'),overlaps_tolerance:T('区间跨越容忍边界，不能排除更大的损害。','The interval crosses the tolerance boundary; larger harm remains possible.')};
  document.getElementById('scenario-results').innerHTML=`<h2>${T('同样差异，在这个规模的含义','The same difference at this scale')}</h2><div class="grid two">${metric(T('D7 返回人数差（情景）','D7 returns difference (scenario)'),number(result.estimate))}${metric(T('区间换算（人）','Transformed interval'),number(result.low)+' ~ '+number(result.high))}</div>${effectChart(state.tolerance)}${note(labels[lens])}<p class="muted">${T('假设差异可原样迁移。区间只反映历史抽样不确定性，不含未来迁移风险；不是实测损失或预测。','Assumes transport of the same effect. Historical sampling uncertainty only, excluding transport risk; not observed loss or a forecast.')}</p><button class="button" data-export="scenario">${T('下载当前情景','Download this scenario')}</button>`;
}
function updateAllocation(){const r=D.allocation_grid[state.allocation.toFixed(1)];document.getElementById('allocation-results').innerHTML=`<div class="grid three">${metric(T('观察对照占比','Observed control share'),percent(control.players/A.rows))}${metric(T('该假设下 p 值','Conditional p-value'),r.p_value.toFixed(5))}${metric(T('筛查阈值 .01','Screen at .01'),r.p_value<.01?T('需复核','FLAG'):T('未触发','NO FLAG'))}</div>`;}
function updatePlanning(){document.getElementById('planning-result').innerHTML=metric(T('每组所需玩家（近似）','Approximate players per arm'),number(D.planning_grid[state.mde.toFixed(1)]));}
function quality(){
  const full=A.sensitivity.filter(r=>r.sample==='All players'),trim=A.sensitivity.filter(r=>r.sample!=='All players');
  const before=full[0].mean_rounds-full[1].mean_rounds,after=trim[0].mean_rounds-trim[1].mean_rounds;
  return heading('BEHAVIOR / INTEGRITY',T('行为、极端值与解释边界','Behavior, outliers and interpretation'),T('观察关联不等于因果，回访组合不是顺序漏斗。','Association is not causation; return combinations are not a sequential funnel.'))+
    note(T('累计局数的源说明存在 7/14 天窗口冲突，且发生在分流后，不用于早期流失预测。','Source descriptions conflict on a 7/14-day rounds horizon. Rounds are post-treatment, not prospective early-churn features.'),true)+
    panel(T('累计局数与 D7：探索性分组','Recorded rounds and D7: descriptive bands'),`<label class="control" for="arm-filter">${T('行为表筛选（不改变主实验总体）','Behavior-table filter (main population unchanged)')}<select id="arm-filter">${['All','gate_30','gate_40'].map(v=>`<option ${state.arm===v?'selected':''}>${v}</option>`).join('')}</select></label><div id="band-table"></div><div class="buttons"><button class="button secondary" data-export="bands">${T('导出当前行为表','Export current behavior table')}</button></div><p class="muted">${T('分组基于记录期累计局数，不能解释曝光或机制。','Post-treatment rounds do not establish exposure or mechanism.')}</p>`)+
    `<div class="grid two">${panel(T('极端值敏感性','Extreme-record sensitivity'),note(T(`平均局数差（对照减实验）由 ${before.toFixed(3)} 局变为排除最大值后的 ${after.toFixed(3)} 局，而 D7 差异仍约 −0.82pp。`,`Mean-round gap (control minus treatment): ${before.toFixed(3)} rounds versus ${after.toFixed(3)} after excluding the maximum; D7 difference remains about −0.82pp.`))+table([T('样本','Sample'),'arm',T('人数','n'),T('平均局数','Mean rounds'),T('中位数','Median')],A.sensitivity.map(r=>[r.sample==='All players'?T('全部保留','All players'):T('排除最大值（仅敏感性）','Exclude maximum (sensitivity)'),r.version,number(r.players),r.mean_rounds.toFixed(2),r.median_rounds]))) }${panel(T('D1 / D7 四种回访组合','Four D1/D7 return combinations'),table(['arm','D1','D7',T('人数','Players'),T('组内占比','Arm share')],A.transitions.map(r=>[r.version,r.returned_d1,r.returned_d7,number(r.players),percent(r.players/(r.version==='gate_30'?control.players:treatment.players))]))+`<p class="muted">${T('两天均未返回不等于期间从未登录；仅 D7 返回不证明活动召回。','Neither-day return does not mean no activity between days; D7-only is not evidence of campaign reactivation.')}</p>`)}</div>`+evidenceDetails(['quality']);
}
function selectedBands(){return A.round_bands.filter(r=>state.arm==='All'||r.version===state.arm).sort((a,b)=>a.version.localeCompare(b.version)||parseInt(a.round_band,10)-parseInt(b.round_band,10));}
function updateBands(){document.getElementById('band-table').innerHTML=table(['arm',T('累计局数','Rounds'),T('人数','Players'),'D7',T('组内占比','Arm share')],selectedBands().map(r=>[r.version,r.round_band,number(r.players),percent(r.d7_rate),percent(r.players/(r.version==='gate_30'?control.players:treatment.players))]));}
function answer(question){
  const kind=C.intent(question);let body='',names=[];
  if(kind==='decision'||kind==='report'){
    names=['arms','tests'];body=`<p><b>${T('建议：暂缓全量上线 gate_40，先核查实验完整性。','Recommendation: pause rollout of gate_40 and audit integrity first.')}</b></p><ul><li>D7: ${percent(control.d7_rate)} → ${percent(treatment.d7_rate)}; ${pp(d7.delta)}, 95% CI [${pp(d7.ci_low)}, ${pp(d7.ci_high)}].</li><li>${T('Holm 校正 p 值','Holm-adjusted p-value')}: ${d7.holm_p.toFixed(5)}.</li><li>${T('假设 50:50 分流时 SRM 触发复核；真实预期比例未提供。','A 50:50 assumption flags an allocation audit; intended allocation is unknown.')}</li><li>${T('机制、地区与收入影响无法由当前数据确定。','Mechanism, regional and revenue effects are unidentified.')}</li></ul>${kind==='report'?reportLinks():''}`;
  }else if(kind==='unavailable'){
    names=['capabilities'];body=note(T('当前数据无法回答：没有地区、渠道、日历时间或付费字段，不能编造欧洲上周活跃下降的原因。需要相应事件、地区与时间口径。','The data cannot answer this: region, channel, calendar timestamps and payment events are absent. Do not invent a cause for European DAU decline; appropriate events and definitions are required.'),true);
  }else if(kind==='prediction'){
    names=['definitions','tests'];body=`<p>${T('当前只能观察留存差异，不能确认机制原因。累计局数发生在分流后，与 D7 结果期重叠，且源窗口说明不一致；用它预测 D7 会有泄漏风险。需更早的观察窗口、后续完整标签与时间划分验证。','The sample identifies an observed difference, not its mechanism. Recorded rounds are post-treatment, overlap D7 and have conflicting horizon descriptions; using them prospectively risks leakage. Earlier observation windows, later labels and time-based validation are needed.')}</p>`;
  }else if(kind==='quality'){
    names=['quality'];body=`<p>${T('主分析保留 49,854 局极端记录，排除仅作敏感性复核。平均局数差对它敏感，但 D7 差异约 −0.82pp，结论不靠删除该记录得到。','The main analysis retains the 49,854-round record; exclusion is sensitivity-only. Mean rounds are sensitive to it, while the D7 difference stays near −0.82pp.')}</p>`;
  }else body=note(T('离线规则只能识别列出的意图。请尝试：是否上线、为什么不能预测流失、数据质量、地区 DAU 或生成报告。这里没有通用大模型理解。','Offline rules only recognize the listed intents. Try rollout, prediction limits, data quality, regional DAU or report generation. This is not general LLM understanding.'));
  return {question,kind,body,names};
}
function copilot(){const chats=state.chat[state.lang];return heading('OFFLINE RULES / TRACEABLE EVIDENCE',T('提一个问题，展开它的证据','Ask a question, inspect the evidence'),T('固定规则 · 无模型调用 · 不收集密钥 · 会话仅在当前页面内存','Fixed rules · no model call · no keys · page-memory conversation only'))+
  note(T('网页展示 Python 构建时执行的 SQL 结果，不执行任意 SQL，也不把输入发往模型或聊天服务。','This page displays SQL results executed at build time. No arbitrary live SQL, model calls or chat-service transmission.'))+
  `<div class="preset">${[T('是否应该上线 gate_40？','Should we roll out gate_40?'),T('为什么不能预测早期流失？','Why can this not predict early churn?'),T('为什么欧洲上周 DAU 下降？','Why did European DAU decline last week?'),T('生成运营报告','Generate a decision report')].map(q=>`<button data-question="${E(q)}">${E(q)}</button>`).join('')}</div><div id="messages" aria-live="polite">${chats.map(r=>`<div class="message user">${E(r.question)}</div><article class="message"><span class="pill">${T('离线规则','Offline rules')}</span><h3>${T('回答与边界','Answer and limits')}</h3>${r.body}${r.names.length?evidenceDetails(r.names):''}</article>`).join('')}</div><form class="chat-form" id="chat-form"><label class="sr-only" for="question">${T('分析问题','Analysis question')}</label><textarea id="question" maxlength="3000" rows="2" placeholder="${T('例如：是否应该上线 gate_40？','For example: should we roll out gate_40?')}"></textarea><button class="primary" type="submit">${T('执行规则','Run rules')}</button></form>${chats.length?`<button class="button secondary" id="clear-chat">${T('清空当前会话','Clear conversation')}</button>`:''}`;}
function scope(){return heading('SCOPE / STATUS / REPRODUCIBILITY',T('适用范围与完成状态','Scope, status and reproducibility'),T('已实现的案例、可迁移方法与未实现功能分别说明。','Distinguishing implemented cases, transferable methods and unimplemented features.'))+
  panel(T('当前可以体验','Available now'),`<div class="grid three">${metric(T('访客访问','Visitor access'),T('无需登录','No sign-in'))}${metric(T('模型凭据','Model key'),T('不需要','Not needed'))}${metric(T('数据范围','Evidence scope'),T('聚合结果','Aggregates'))}</div>`)+
  table([T('分类','Category'),T('范围','Scope'),T('状态','Status')],[
    [T('当前案例','Current case'),'Cookie Cats gate_30 / gate_40',T('固定数据已适配，不支持任意 CSV 上传','Fixed reviewed dataset; no arbitrary CSV upload')],
    [T('可迁移方法','Transferable method'),T('新手引导、功能改动、用户运营实验','Onboarding, feature changes and engagement experiments'),T('需要新数据、指标定义与验证','Requires new data, definitions and validation')],
    [T('国际化','International'),T('双语汇报、地区实验设计','Bilingual reporting and regional design'),T('双语已实现；真实地区效果未实现','Bilingual implemented; regional measurement absent')],
    [T('源码中的 AI','AI in source'),T('DeepSeek 工具接口','DeepSeek tool interface'),T('可选接口已实现；真实调用待验收，访客版不启用','Optional interface implemented; live acceptance pending; disabled in visitor edition')],
    [T('当前不支持','Not supported'),T('实时监控、投放 ROI、付费归因、自动干预','Live monitoring, acquisition ROI, payment attribution, intervention'),T('当前无对应数据与接入','Required evidence and integration absent')]
  ])+note(T('公开历史实验，使用公开历史样本，不代表实时生产数据。开发使用 AI 编程辅助。','Historical public experiment, based on public historical data, not a live production feed. Developed with AI coding assistance.'))+
  `<details><summary>${T('来源与统计说明','Source and statistical notes')}</summary><p><a href="https://assets.datacamp.com/production/project_184/datasets/cookie_cats.csv" target="_blank" rel="noopener">DataCamp source CSV ↗</a></p><p>${T('D7 事后选定，区间为逐项区间；没有地区、逐日时间、付费或门槛曝光。原始文件不随网页发布。','D7 chosen retrospectively; pointwise intervals. No region, calendar timestamps, payments or gate exposure. Raw players are not published with this page.')}</p><pre>SHA-256: ${E(A.source_sha256)}\nBuild: ${E(A.build_id)}</pre></details>`+reportLinks();}
function download(text,name,type='text/plain;charset=utf-8'){const url=URL.createObjectURL(new Blob([text],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function exportScenario(){const r=C.impact(d7,state.population),lens=C.tolerance(d7,state.tolerance);const text=T(`# D7 决策情景\n\n假设未来总体：${number(state.population)} 人；可接受绝对下降：${state.tolerance.toFixed(1)} 个百分点。\n\nD7 返回人数差约 ${number(r.estimate)}，区间换算 [${number(r.low)}, ${number(r.high)}]。\n\n原样本差异 ${pp(d7.delta)}。判断：${C.lensLabel(lens,state.lang)}。\n\n这是条件规模换算，不是实测损失、预测或正式非劣效检验；不包含未来迁移风险。分流完整性仍需核验。`, `# D7 decision scenario\n\nHypothetical population: ${number(state.population)}; acceptable decline: ${state.tolerance.toFixed(1)} pp.\n\nReturns difference ${number(r.estimate)}, transformed interval [${number(r.low)}, ${number(r.high)}].\n\nObserved effect ${pp(d7.delta)}. Interval interpretation: ${C.lensLabel(lens,state.lang)}.\n\nConditional scale scenario, not observed loss, forecast or formal non-inferiority. Transport uncertainty excluded; integrity audit required.`);download(text+`\n\nSource SHA-256: ${A.source_sha256}\nBuild: ${A.build_id}\n`,`decision_scenario_${state.population}_${state.tolerance.toFixed(1)}pp_${state.lang}.md`);}
function exportBands(){const rows=selectedBands();const text=['version,round_band,players,retained_d7,d7_rate,share',...rows.map(r=>[r.version,r.round_band,r.players,r.retained_d7,r.d7_rate,r.players/(r.version==='gate_30'?control.players:treatment.players)].join(','))].join('\n');download(text,`round_bands_${state.arm}.csv`,'text/csv;charset=utf-8');}
function go(page){state.page=page;location.hash=page;render();window.scrollTo(0,0);document.getElementById('main').focus({preventScroll:true});}
function ask(q){if(!q.trim())return;state.chat[state.lang].push(answer(q.trim().slice(0,3000)));if(state.chat[state.lang].length>12)state.chat[state.lang].shift();render();}
function render(){
  document.documentElement.lang=state.lang==='zh'?'zh-CN':'en';
  const names={guide:T('作品导览','Project guide'),experiment:T('实验决策','Experiment decision'),lab:T('决策沙盘','Decision lab'),quality:T('行为与质量','Behavior & quality'),copilot:T('离线运营助手','Offline copilot'),scope:T('范围与状态','Scope & status')};
  document.getElementById('navigation').innerHTML=Object.entries(names).map(([k,v])=>`<button data-page="${k}" class="${state.page===k?'active':''}" ${state.page===k?'aria-current="page"':''}>${E(v)}</button>`).join('');
  document.getElementById('ready-label').textContent=T('访客版 · 无需 Key','VISITOR EDITION · NO KEY');
  document.getElementById('sidebar-caption').textContent=T('游戏留存实验与运营分析','Game experiments & operations analytics');
  document.getElementById('sidebar-note').textContent=T('仅使用公开历史实验的聚合证据，不含原始玩家记录。','Historical public aggregate evidence only; no raw player records.');
  document.getElementById('footer').textContent=T('马延青 · 个人作品 · 历史公开实验 · 无模型调用 · 建议待业务复核','Yanqing Ma · independent project · historical public experiment · no model calls · analyst review required');
  root.innerHTML=({guide,experiment,lab,quality,copilot,scope})[state.page]();
  if(state.page==='lab'){
    updateScenario();updateAllocation();updatePlanning();
    document.getElementById('population').addEventListener('change',e=>{state.population=Number(e.target.value);updateScenario();});
    for(const id of ['tolerance','allocation','mde'])document.getElementById(id).addEventListener('input',e=>{state[id]=Number(e.target.value);document.getElementById(id+'-value').textContent=state[id].toFixed(1)+(id==='allocation'?'%':'');({tolerance:updateScenario,allocation:updateAllocation,mde:updatePlanning})[id]();});
  }
  if(state.page==='quality'){updateBands();document.getElementById('arm-filter').addEventListener('change',e=>{state.arm=e.target.value;updateBands();});}
  if(state.page==='copilot'){
    document.getElementById('chat-form').addEventListener('submit',e=>{e.preventDefault();ask(document.getElementById('question').value);});
    document.getElementById('clear-chat')?.addEventListener('click',()=>{state.chat[state.lang]=[];render();});
  }
}
document.addEventListener('click',e=>{const target=e.target.closest('[data-page],[data-question],[data-export]');if(!target)return;if(target.dataset.page)go(target.dataset.page);else if(target.dataset.question)ask(target.dataset.question);else if(target.dataset.export==='scenario')exportScenario();else if(target.dataset.export==='bands')exportBands();});
document.getElementById('language').addEventListener('change',e=>{state.lang=e.target.value;render();});
window.addEventListener('hashchange',()=>{const page=location.hash.slice(1);if(['guide','experiment','lab','quality','copilot','scope'].includes(page)&&state.page!==page){state.page=page;render();}});
render();
})();
