import re
import zipfile
from src.guide import guide_markdown,scope_rows
from src.reporting import load_analysis
from scripts.build_hr_pack import build,introduction_html


def test_guide_scope_and_current_status_are_explicit():
    a=load_analysis()
    zh=guide_markdown(a)
    en=guide_markdown(a,"en")
    assert "90,189" in zh and "不支持任意 CSV" in zh
    assert "localhost" in zh and "待完成" in zh
    assert "provider acceptance pending" in en
    assert len(scope_rows())==5


def test_hr_html_is_self_contained_and_links_resolve():
    html=introduction_html(load_analysis())
    assert "<script" not in html and "<iframe" not in html
    assert not re.search(r'<(?:link|img)\b',html)
    anchors=re.findall(r'href="#([^"]+)"',html)
    for anchor in anchors:
        assert f'id="{anchor}"' in html
    assert "19.02%" in html and "18.20%" in html
    assert "真实模型端到端验收" in html and "尚未实现" in html


def test_hr_bundle_has_no_runtime_or_credentials():
    archive=build()
    with zipfile.ZipFile(archive) as z:
        assert set(z.namelist())=={"index.html","START_HERE.txt","project_guide_zh.md","project_guide_en.md","decision_brief_zh.md","decision_brief_en.md","马延青_游戏分析项目介绍.pdf"}
        assert "无需安装" in z.read("START_HERE.txt").decode("utf-8")
        from pypdf import PdfReader
        from io import BytesIO
        pdf=PdfReader(BytesIO(z.read("马延青_游戏分析项目介绍.pdf")))
        assert len(pdf.pages)==2
        text="\n".join(page.extract_text() for page in pdf.pages)
        assert "90,189" in text and "localhost" in text
