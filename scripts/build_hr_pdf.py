"""Render the two-page recruiter brief from the verified project evidence."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak
from src.config import ROOT,SOURCE_URL
from src.reporting import load_analysis


def build():
    a=load_analysis()
    c,t=a["arms"]
    d7=next(r for r in a["tests"] if r["metric"]=="D7")
    font=Path("C:/Windows/Fonts/msyh.ttc")
    if font.exists():
        pdfmetrics.registerFont(TTFont("BodyCN",str(font)))
        pdfmetrics.registerFont(TTFont("BoldCN","C:/Windows/Fonts/msyhbd.ttc"))
    else:
        pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
        pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
        # Keep Chinese glyph support on non-Windows; no external font download.
        pdfmetrics.registerFontFamily("STSong-Light",normal="STSong-Light",bold="STSong-Light")
    normal="BodyCN" if font.exists() else "STSong-Light"
    bold="BoldCN" if font.exists() else "STSong-Light"
    pdfmetrics.registerFontFamily(normal,normal=normal,bold=bold)
    ink=colors.HexColor("#20364c")
    muted=colors.HexColor("#6c7f95")
    teal=colors.HexColor("#087f86")
    line=colors.HexColor("#dce5ee")
    styles={
        "body":ParagraphStyle("Body",fontName=normal,fontSize=9,leading=15,textColor=ink,wordWrap="CJK",spaceAfter=7),
        "small":ParagraphStyle("Small",fontName=normal,fontSize=8,leading=13,textColor=muted,wordWrap="CJK",spaceAfter=5),
        "title":ParagraphStyle("Title",fontName=bold,fontSize=23,leading=33,textColor=ink,wordWrap="CJK",spaceAfter=12),
        "h2":ParagraphStyle("H2",fontName=bold,fontSize=12,leading=20,textColor=teal,spaceBefore=14,spaceAfter=8),
        "cell":ParagraphStyle("Cell",fontName=normal,fontSize=8.5,leading=14,textColor=ink,wordWrap="CJK"),
        "kpi":ParagraphStyle("KPI",fontName=normal,fontSize=8.5,leading=28,textColor=ink,wordWrap="CJK"),
    }
    def p(text,kind="body"):
        return Paragraph(text,styles[kind])
    def grid(rows,widths):
        table=Table([[p(cell,"cell") for cell in row] for row in rows],colWidths=widths,hAlign="LEFT")
        table.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("GRID",(0,0),(-1,-1),.5,line),
            ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#f2f7fa")),("LEFTPADDING",(0,0),(-1,-1),9),
            ("RIGHTPADDING",(0,0),(-1,-1),9),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
        return table
    output=ROOT/"output/马延青_游戏分析项目介绍.pdf"
    output.parent.mkdir(exist_ok=True)
    doc=SimpleDocTemplate(str(output),pagesize=A4,rightMargin=44,leftMargin=44,topMargin=62,bottomMargin=49,
        title="马延青｜游戏留存实验分析与 AI 运营助手",author="马延青")
    width=A4[0]-88
    story=[p("游戏留存实验分析<br/>与 AI 运营助手","title"),
        p("马延青 · 个人作品 · Python / SQL / Streamlit","small"),
        p("<b>业务问题：</b>游戏进度门槛从第 30 关后移至第 40 关，玩家是否更愿意回来？项目将数据检查、实验评估、运营判断和双语报告连接成可复核的工作台。"),Spacer(1,7)]
    cards=[]
    for label,value in [("公开实验玩家",f"{a['rows']:,}"),("对照组 D7 留存",f"{c['d7_rate']:.2%}"),("实验组 D7 留存",f"{t['d7_rate']:.2%}")]:
        cards.append(p(f'<font color="#6c7f95">{label}</font><br/><font size="21" face="{bold}">{value}</font>',"kpi"))
    kpis=Table([cards],colWidths=[width/3]*3)
    kpis.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#f1f6fa")),("BOX",(0,0),(-1,-1),.5,line),
        ("LEFTPADDING",(0,0),(-1,-1),13),("TOPPADDING",(0,0),(-1,-1),13),("BOTTOMPADDING",(0,0),(-1,-1),16)]))
    story.extend([kpis,Spacer(1,13),p(f"实验组减对照组：<b>{d7['delta']*100:+.3f} 个百分点</b>；单指标 95% 区间 [{d7['ci_low']*100:+.3f}, {d7['ci_high']*100:+.3f}] 个百分点。D7 指安装后第七天是否返回，不是七天内累计返回。"),
        p("<b>案例建议：暂缓全量上线，先核查实验完整性。</b><br/>预期分流比例未提供。在假设 50:50 分流时，人数比例触发复核信号；这不是已证实的随机化故障，也不直接证明留存变化的机制原因。"),
        p("作品展示的能力","h2"),grid([
            ("数据分析", "SQL/Python 构建 D1/D7 指标，核对分子分母，进行实验效果与不确定性分析。"),
            ("运营判断", "结合分流复核、极端值与业务容忍边界，形成有条件的上线建议，区分事实与假设。"),
            ("沟通交付", "交互式看板、可导出的情景、中英文简报和每条回答独立的证据入口。"),
            ("AI 工程", "已实现受限 SQL、指标知识检索和报告工具接口；真实模型调用验收待配置后完成。"),
        ],[90,width-90]),
        p("项目定位与数据来源","h2"),
        p(f'这是基于 <link href="{escape(SOURCE_URL)}" color="#087f86">DataCamp Cookie Cats 公开教学实验</link> 的个人分析作品，开发使用 AI 编程辅助。不是米哈游内部数据或已上线生产服务；跨游戏结论需要重新验证。'),
        PageBreak(),p("使用方式、适用范围<br/>与完成情况","title"),
        p("先看介绍，再按需要体验交互版；无需让招聘浏览者安装开发环境。","small"),
        p("三分钟体验路线","h2"),grid([
            ("第 1 分钟", "实验决策：查看结论、两组人数与区间；行为与质量：核对极端记录和回访组合。"),
            ("第 2 分钟", "决策沙盘：改变假设玩家规模或可接受下降，观察业务含义。人数换算是条件情景，不是实测损失。"),
            ("第 3 分钟", "AI 助手：选择离线规则，问“是否上线”，再问“欧洲上周 DAU 为何下降”，展开执行证据。无需 API Key。"),
        ],[90,width-90]),
        p("适用广度：方法与当前功能分别说明","h2"),grid([
            ("已实现的案例", "固定的 Cookie Cats 门槛调整数据，支持留存、实验复核、情景与双语简报；不支持任意 CSV 上传。"),
            ("可迁移的方法", "新手引导、内容解锁、功能或版本实验，需要新数据、重新定义指标并验证；尚未接入这些场景。"),
            ("国际化扩展", "双语汇报已实现；地区结论需国家、语言、时区及曝光数据。当前没有真实地区效果分析。"),
            ("当前不支持", "逐日 DAU、投放 ROI、付费效果、早期流失预测；缺少相应事件、成本或独立的早期观察窗口。"),
        ],[90,width-90]),
        p("交付方式与当前状态","h2"),
        p("<b>直接阅读：</b>本 PDF 或免安装 HTML 介绍，无需账号、密钥或 Python。<br/><b>交互体验：</b>当前运行在作者电脑；127.0.0.1 / localhost 不能供外部 HR 直接访问。远程操作需另行部署地址或现场演示。<br/><b>技术复现：</b>另附源码包与运行说明，供需要深入查看的技术评审使用。"),
        p("<b>已完成：</b>本地分析、看板、情景、质量与证据版本检查、双语报告、离线规则助手。<br/><b>待验收：</b>真实 DeepSeek 调用。<b>尚未实施：</b>公开交互部署、实时游戏接入与自动运营干预。","small")])
    def decorate(canvas,document):
        canvas.saveState()
        canvas.setStrokeColor(teal)
        canvas.setLineWidth(2)
        canvas.line(44,A4[1]-38,92,A4[1]-38)
        canvas.setFillColor(muted)
        canvas.setFont(normal,8)
        canvas.drawString(104,A4[1]-41,"GAME ANALYTICS PORTFOLIO / 作品介绍")
        canvas.setStrokeColor(line)
        canvas.setLineWidth(.5)
        canvas.line(44,36,A4[0]-44,36)
        canvas.setFont(normal,7.5)
        canvas.drawString(44,24,"马延青 · 历史公开实验案例 · 2026.10")
        canvas.drawRightString(A4[0]-44,24,f"{document.page} / 2")
        canvas.restoreState()
    doc.build(story,onFirstPage=decorate,onLaterPages=decorate)
    print(f"Recruiter PDF generated: {output}")
    return output


if __name__=="__main__":
    build()
