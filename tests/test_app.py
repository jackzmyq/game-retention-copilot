from pathlib import Path
from streamlit.testing.v1 import AppTest


def test_workspace_navigation_and_offline_demo():
    at=AppTest.from_file(str(Path(__file__).resolve().parents[1]/"app.py"),default_timeout=45).run()
    assert not at.exception
    assert at.sidebar.radio[0].value=="作品导览"
    at.button(key="guide_decision").click().run()
    assert not at.exception
    assert at.sidebar.radio[0].value=="实验决策"
    at.sidebar.radio[0].set_value("决策沙盘").run()
    assert not at.exception
    assert any("情景" in m.label for m in at.metric)
    at.slider[0].set_value(1.5).run()
    assert not at.exception
    at.sidebar.radio[0].set_value("行为与质量").run()
    assert not at.exception
    at.sidebar.radio[0].set_value("AI 分析助手").run()
    assert not at.exception
    at.button(key="ask_0").click().run()
    assert not at.exception
    assert at.session_state["agent_result"]["mode"]=="offline_rules"
    assert len(at.chat_message)==2
    at.chat_input[0].set_value("为什么欧洲上周 DAU 下降？").run()
    assert not at.exception
    assert len(at.chat_message)==4
    assert "无法回答" in at.session_state["agent_result"]["answer"]
    at.sidebar.radio[0].set_value("指标与项目说明").run()
    assert not at.exception
    at.sidebar.selectbox[0].set_value("English").run()
    assert not at.exception
