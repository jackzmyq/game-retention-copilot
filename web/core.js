(function(root){
  'use strict';
  const C={};
  C.impact=(effect,population)=>{
    if(!Number.isInteger(population)||population<1000||population>1000000)throw Error('Invalid population');
    return {population,estimate:effect.delta*population,low:effect.ci_low*population,high:effect.ci_high*population};
  };
  C.tolerance=(effect,pp)=>{
    if(!Number.isFinite(pp)||pp<.1||pp>1.5)throw Error('Invalid tolerance');
    const boundary=-pp/100;
    return effect.ci_high<boundary?'beyond_tolerance':effect.ci_low>=boundary?'within_tolerance':'overlaps_tolerance';
  };
  C.lensLabel=(state,lang='zh')=>({zh:{beyond_tolerance:'整个区间超出容忍边界',within_tolerance:'区间位于容忍范围内，仍需复核',overlaps_tolerance:'区间跨越容忍边界'},en:{beyond_tolerance:'Entire interval beyond tolerance',within_tolerance:'Interval within tolerance; audit still required',overlaps_tolerance:'Interval crosses tolerance'}}[lang][state]);
  C.intent=question=>{
    const q=String(question).toLowerCase();
    if(/欧洲|地区|国家|渠道|dau|收入|付费|上周|每日|region|country|europe|revenue|last week|channel/.test(q))return 'unavailable';
    if(/预测|模型|因果|原因|predict|cause|why|为什么/.test(q))return 'prediction';
    if(/质量|异常值|极端|quality|outlier/.test(q))return 'quality';
    if(/报告|简报|report|brief/.test(q))return 'report';
    if(/上线|留存|gate|retention|rollout|ship/.test(q))return 'decision';
    return 'unknown';
  };
  C.escape=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  if(typeof module!=='undefined'&&module.exports)module.exports=C;else root.RetentionCore=C;
})(typeof window!=='undefined'?window:globalThis);
