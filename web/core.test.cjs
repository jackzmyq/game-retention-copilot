const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const test=require('node:test');
const core=require('./core.js');
const sandbox={window:{}};
vm.runInNewContext(fs.readFileSync(__dirname+'/assets/evidence.js','utf8'),sandbox);
const data=sandbox.window.RETENTION_EVIDENCE;
const a=data.analysis,effect=a.tests.find(r=>r.metric==='D7');
test('export contains aggregate evidence only',()=>{
 assert.equal(a.rows,90189);assert.equal(data.raw_players_included,false);
 const walk=x=>{if(Array.isArray(x))x.forEach(walk);else if(x&&typeof x==='object'){assert.equal(Object.hasOwn(x,'userid'),false);assert.equal(Object.hasOwn(x,'api_key'),false);Object.values(x).forEach(walk);}};walk(data);
});
test('scenario scales the same estimate and ordered interval',()=>{
 const r=core.impact(effect,100000);assert.ok(Math.abs(r.estimate+820.1298315205913)<1e-8);assert.ok(r.low<r.estimate&&r.estimate<r.high&&r.high<0);
 assert.throws(()=>core.impact(effect,-1));
});
test('tolerance lens changes without changing evidence',()=>{
 assert.equal(core.tolerance(effect,.1),'beyond_tolerance');assert.equal(core.tolerance(effect,.5),'overlaps_tolerance');assert.equal(core.tolerance(effect,1.5),'within_tolerance');assert.equal(effect.delta,a.tests.find(r=>r.metric==='D7').delta);
});
test('offline rules refuse unsupported metrics and unknown questions',()=>{
 assert.equal(core.intent('为什么欧洲上周 DAU 下降？'),'unavailable');assert.equal(core.intent('是否应该上线 gate_40？'),'decision');assert.equal(core.intent('预测早期流失'),'prediction');assert.equal(core.intent('hello'),'unknown');
});
test('question text is escaped',()=>{assert.equal(core.escape('<img src=x onerror="alert(1)">'),'&lt;img src=x onerror=&quot;alert(1)&quot;&gt;');});
test('planning and allocation grids retain Python calculations',()=>{assert.equal(data.planning_grid['1.0'],23688);assert.ok(Math.abs(data.allocation_grid['50.0'].p_value-a.srm.p_value)<1e-12);assert.equal(Object.keys(data.planning_grid).length,16);assert.equal(Object.keys(data.allocation_grid).length,21);});
test('public app has no API credential form or chat persistence',()=>{
 const js=fs.readFileSync(__dirname+'/app.js','utf8');assert.equal(/localStorage|sessionStorage|document\.cookie|fetch\(|XMLHttpRequest|api\.deepseek\.com/.test(js),false);
 const html=fs.readFileSync(__dirname+'/index.html','utf8');assert.equal(/type=["']password/.test(html),false);assert.equal(/https:\/\/.*\.js["']/.test(html),false);
});
