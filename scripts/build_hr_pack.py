"""Generate a no-install, no-key reviewer introduction from verified evidence."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from html import escape
import zipfile
from src.config import ROOT, REPORTS, SOURCE_URL
from src.reporting import load_analysis,decision_report,atomic_text
from src.guide import guide_markdown,scope_rows


def introduction_html(a):
    c,t=a["arms"]
    d7=next(r for r in a["tests"] if r["metric"]=="D7")
    scope="".join(f"<tr><th>{escape(x)}</th><td>{escape(y)}</td><td>{escape(z)}</td></tr>" for x,y,z in scope_rows())
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>马延青｜游戏留存实验分析与 AI 运营助手</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#f3f6fa;color:#23364b;font:15px/1.8 "Segoe UI","Microsoft YaHei",sans-serif}}
main{{max-width:1000px;margin:auto;padding:46px 28px 60px}}header{{padding-bottom:25px;border-bottom:1px solid #dce4ee}}.kicker{{font-size:11px;letter-spacing:2px;color:#607890;font-weight:700}}h1{{font-size:32px;line-height:1.4;letter-spacing:-.7px;margin:12px 0}}h2{{font-size:21px;margin:30px 0 14px}}h3{{font-size:16px;margin:0 0 9px}}p{{margin:10px 0}}.muted{{color:#708196;font-size:13px}}.lead{{font-size:17px;max-width:800px}}nav{{display:flex;flex-wrap:wrap;gap:10px;margin-top:20px}}a{{color:#007f86}}nav a{{border:1px solid #cbd9e6;background:white;border-radius:6px;padding:6px 13px;text-decoration:none;font-size:13px}}.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:13px;margin:20px 0}}.card,article{{padding:20px;background:white;border:1px solid #dfe6ef;border-radius:9px}}.value{{font-size:29px;font-weight:700;line-height:1.4}}.label{{font-size:12px;color:#78879b}}.decision{{padding:16px 20px;border-left:4px solid #d6974d;background:#fff8ec;border-radius:6px;margin:18px 0}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}ol,ul{{padding-left:21px}}li{{margin-bottom:9px}}.table-wrap{{overflow:auto}}table{{width:100%;border-collapse:collapse;font-size:13px;background:white}}th,td{{padding:13px 12px;text-align:left;border:1px solid #e1e7f0;vertical-align:top}}th{{font-weight:650;background:#f7f9fc;min-width:100px}}.note{{padding:13px 16px;background:#eaf4f5;border:1px solid #d2e7e9;border-radius:7px;font-size:13px}}details{{background:white;border:1px solid #dfe6ef;border-radius:8px;padding:14px 18px;margin-top:12px}}summary{{cursor:pointer;font-weight:600}}code{{overflow-wrap:anywhere;font-size:11px}}footer{{border-top:1px solid #dce4ee;margin-top:34px;padding-top:18px;font-size:12px;color:#75869a}}@media(max-width:640px){{main{{padding:26px 16px}}h1{{font-size:25px}}.cards{{grid-template-columns:1fr}}.grid{{grid-template-columns:1fr}}.value{{font-size:25px}}}}@media print{{body{{background:white}}main{{padding:0;max-width:none}}nav{{display:none}}article,.card,details{{break-inside:avoid}}a{{color:inherit}}}}
</style></head><body><main>
<header><div class="kicker">YANQING MA · GAME ANALYTICS PORTFOLIO</div><h1>游戏留存实验分析<br>与 AI 运营助手</h1>
<p class="lead">一次游戏机制改动，是否值得上线？<br>用指标、实验与可复核证据形成运营建议。</p>
<p class="muted">马延青｜个人作品，使用 AI 编程辅助｜公开历史实验案例</p>
<nav aria-label="阅读导航"><a href="#finding">先看结论</a><a href="#walkthrough">如何体验</a><a href="#scope">适用范围</a><a href="#status">完成情况</a></nav></header>
<section id="finding"><h2>01 / 一个明确的业务问题</h2><p>Cookie Cats 将进度门槛从第 30 关后移至第 40 关。这个项目分析玩家是否更愿意回来，并回答是否应全量上线。</p>
<div class="cards"><div class="card"><div class="label">公开实验玩家</div><div class="value">{a['rows']:,}</div></div><div class="card"><div class="label">对照组 D7 留存</div><div class="value">{c['d7_rate']:.2%}</div></div><div class="card"><div class="label">实验组 D7 留存</div><div class="value">{t['d7_rate']:.2%}</div></div></div>
<p>实验组减对照组为 <b>{d7['delta']*100:+.3f} 个百分点</b>，单指标 95% 区间 [{d7['ci_low']*100:+.3f}, {d7['ci_high']*100:+.3f}] 个百分点。D7 指安装后第七天是否返回，不是七天内累计返回。</p>
<div class="decision"><b>建议：暂缓全量上线，先核查实验完整性。</b><br>观察到负向留存差异；在未核实的 50:50 分流假设下，人数比例触发复核信号。需要分流与结果日志，才能进一步确认因果解释。</div></section>
<section><h2>02 / 作品展示的能力</h2><div class="grid"><article><h3>分析与判断</h3><p>SQL/Python 指标构建、实验效果评估、不确定性解释、极端值复核，以及有条件的运营建议。</p></article><article><h3>交付与自动化</h3><p>交互式工作台、情景导出、中英文简报、可追溯查询，以及已实现的 LLM 工具调用接口。</p></article></div></section>
<section id="walkthrough"><h2>03 / 如何查看与体验</h2><div class="note"><b>现在这份文件就能看。</b>它可直接用浏览器打开；无需安装 Python、注册账号或提供 API Key，也不会调用模型或发送数据。</div>
<div class="grid" style="margin-top:16px"><article><h3>HR：先读这份介绍</h3><ol><li>看业务问题、核心结论与能力展示。</li><li>查看适用范围与完成状态，了解项目定位。</li><li>交互演示：<a href="https://jackzmyq.github.io/game-retention-copilot/">打开免登录访客版</a>。</li></ol></article><article><h3>有交互版时：三分钟路线</h3><ol><li><b>实验决策</b>：看分组人数、留存区间与建议。</li><li><b>决策沙盘</b>：改变规模或容忍边界，查看情景变化。</li><li><b>行为与质量</b>：检查极端值与回访组合。</li><li><b>AI 助手</b>：选离线规则，问是否上线，再问地区问题，展开证据。</li></ol></article></div>
<p class="muted">访客版支持分析、沙盘、报告下载与离线规则，无需账号或 Key。SQL 为构建时执行的聚合证据；完整 Python 版可本地复现，localhost 不是公开地址。技术复现说明在单独的源码包 README.md 中，不需要 HR 自行搭建环境。</p></section>
<section id="scope"><h2>04 / 适用广度与边界</h2><div class="table-wrap"><table><thead><tr><th>分类</th><th>场景</th><th>当前支持程度</th></tr></thead><tbody>{scope}</tbody></table></div>
<p class="muted">当前适配固定数据，不支持任意 CSV 上传。方法可以迁移，结论不能直接外推至其他游戏或国家；新场景需重新接入数据、定义指标并验证。</p></section>
<section id="status"><h2>05 / 哪些已经完成</h2><div class="table-wrap"><table><tbody>
<tr><th>已完成</th><td>本地分析管线、实验工作台、情景、质量复核、双语简报、离线助手、查询边界、证据版本校验。</td></tr>
<tr><th>已实现、待实测</th><td>DeepSeek 云端工具调用接口；真实模型端到端验收需配置密钥后完成。本地测试不等于模型验收。</td></tr>
<tr><th>设计方案</th><td>地区、语言、时区与曝光数据契约；尚未用真实国际化数据实施。</td></tr>
<tr><th>尚未实现</th><td>实时游戏事件接入、任意数据上传、自动运营干预。</td></tr>
</tbody></table></div></section>
<details><summary>数据与方法说明</summary><p>数据来自 <a href="{escape(SOURCE_URL)}">DataCamp 公开实验 CSV</a>，不是米哈游内部数据。源材料说明随机分组，但预期分流比例、逐日时间、地区、付费与曝光日志未提供。累计局数的说明存在 7/14 天冲突，不能作为早期流失预测特征。</p><p>留存比较使用两比例检验、逐项 Newcombe 95% 区间及 D1/D7 的 Holm 校正。D7 是本作品事后选定的主指标，未声称预注册。沙盘人数是条件性规模换算，不是实测损失或预测。</p><p>来源 SHA-256：<code>{escape(a['source_sha256'])}</code></p></details>
<details lang="en"><summary>English overview</summary><p><b>Game Retention Experiment Analytics & AI Operations Copilot.</b> This independent portfolio case uses {a['rows']:,} publicly released Cookie Cats players to evaluate a progression-gate change. Treatment D7 retention is {abs(d7['delta'])*100:.3f} percentage points lower. The recommendation is conditional on an allocation-integrity audit.</p><p>Implemented: local analytics, interactive evidence, scenarios, bilingual briefs and a bounded LLM tool interface. Live-provider acceptance and public interactive hosting are pending. The app supports this fixed dataset; broader games and markets require new data and validation. This static file needs no installation or key.</p></details>
<footer>个人作品 · 历史公开实验 · 开发使用 AI 辅助 · 不代表米哈游官方项目<br>此文件是免安装阅读版；操作示例描述交互版能力，不会在本文件内执行数据库或模型调用。</footer>
</main></body></html>'''


def build():
    a=load_analysis()
    from scripts.build_hr_pdf import build as build_pdf
    pdf=build_pdf()
    output=ROOT/"output"
    output.mkdir(exist_ok=True)
    html=introduction_html(a)
    atomic_text(output/"HR项目介绍.html",html)
    for lang in ["zh","en"]:
        atomic_text(ROOT/f"docs/project_guide_{lang}.md",guide_markdown(a,lang))
    archive=output/"HR_review_pack.zip"
    with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("index.html",html)
        z.write(pdf,pdf.name)
        z.writestr("START_HERE.txt","请先解压，再打开两页 PDF 或双击 index.html。无需安装、账号或密钥。\n交互访客版：https://jackzmyq.github.io/game-retention-copilot/\n127.0.0.1/localhost 只能在运行项目的电脑上使用。\n\nExtract this archive and open the PDF or index.html. No installation or API key required.\n")
        for lang in ["zh","en"]:
            z.writestr(f"project_guide_{lang}.md",guide_markdown(a,lang))
            z.writestr(f"decision_brief_{lang}.md",decision_report(a,lang))
    print(f"HR introduction and review pack generated: {archive}")
    return archive


if __name__=="__main__":
    build()
