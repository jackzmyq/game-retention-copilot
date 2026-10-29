"""Audience-facing project orientation shared by the app and HR handoff."""


def scope_rows(language="zh"):
    if language=="en":
        return [
            ("Current case", "Cookie Cats gate_30 vs gate_40 experiment", "Runs now: D1/D7, checks, scenarios, bilingual briefs"),
            ("Transferable method", "Onboarding, progression pacing and feature experiments", "Requires new data, metric definitions and validation; not connected today"),
            ("International extension", "Regional experiments and multilingual reporting", "Bilingual reporting works; regional measurement needs country, locale and timezone data"),
            ("Outside current evidence", "Daily DAU, acquisition ROI, payment effects and early churn prediction", "Required events, costs or earlier observation windows are absent"),
            ("AI connection", "Natural-language evidence queries and draft reporting", "Local rules work; live DeepSeek interface implemented, provider acceptance pending"),
        ]
    return [
        ("当前已适用", "Cookie Cats 门槛调整实验", "可直接查看 D1/D7、质量复核、决策情景和双语简报"),
        ("方法可迁移", "新手引导、内容解锁节奏、功能改动实验", "需要新数据、重新定义指标并核验；当前未接入这些游戏场景"),
        ("国际化扩展", "地区实验与多语言汇报", "双语汇报已实现；地区分析需补充国家、语言、时区等字段"),
        ("当前证据不足", "逐日 DAU、投放 ROI、付费效果、早期流失预测", "缺少事件、成本或独立的早期观察窗口"),
        ("AI 使用方式", "自然语言查证据、生成报告初稿", "离线规则可用；DeepSeek 接口已实现，真实调用验收待完成"),
    ]


def guide_markdown(analysis,language="zh"):
    c,t=analysis["arms"]
    d7=next(r for r in analysis["tests"] if r["metric"]=="D7")
    if language=="en":
        lines=["# Game Retention Experiment Analytics & AI Operations Copilot",
            "\nIndependent portfolio project by Yanqing Ma, developed with AI coding assistance. A historical public experiment case, not miHoYo telemetry or a deployed production service.",
            "\n## What decision does it support?",
            "Should a game's progression gate move from level 30 to 40? The workflow connects data checks, retention evidence, uncertainty and an operational recommendation.",
            f"\n## What was found?\n\nThe release includes {analysis['rows']:,} players. D7 retention is {c['d7_rate']:.2%} in gate_30 and {t['d7_rate']:.2%} in gate_40. The difference is {d7['delta']*100:+.3f} percentage points, with pointwise 95% CI [{d7['ci_low']*100:+.3f}, {d7['ci_high']*100:+.3f}] pp.",
            "Recommendation: pause a full rollout and verify assignment integrity first. The intended allocation is unknown; a 50:50 assumption triggers an allocation screen, not a proven randomization failure.",
            "\n## Review in three minutes\n\n1. Experiment decision: see the conclusion, group denominators and uncertainty.\n2. Decision lab: change a hypothetical population or tolerance; scenario outputs are not observed business loss.\n3. Behavior & quality: inspect outlier sensitivity and return combinations.\n4. AI copilot: choose offline mode and click Evaluate rollout, then Check regional coverage; inspect each answer's evidence. No API key is required for this route.",
            "\n## Scope\n\n| Classification | Scenario | Current support |\n|---|---|---|",
            *[f"| {x} | {y} | {z} |" for x,y,z in scope_rows("en")],
            "\n## What the work demonstrates\n\n- SQL/Python metric construction and experimental effect assessment.\n- Integrity checks, uncertainty interpretation and business decision boundaries.\n- Interactive delivery and bilingual communication.\n- Implemented, bounded LLM tool interface with inspectable evidence; live-provider verification pending.",
            "\n## How to access\n\nThe supplied static introduction opens in a browser with no Python, account or key. The interactive app currently runs on the author's own computer. A localhost URL is not accessible to external reviewers; an independently hosted URL or a live demonstration is required for remote interaction. Technical reviewers can run the separately supplied source package using README.md.",
            "\n## Key limitations\n\nThis release has no country, payment, timestamp or gate-exposure events. Recorded rounds have a 7/14-day source-description conflict and cannot serve as a prospective D7 predictor. The application currently supports this fixed reviewed dataset; it does not accept arbitrary CSVs, monitor live games or automatically change game settings.",
            f"\nSource fingerprint: `{analysis['source_sha256']}`.\n\nSource: https://assets.datacamp.com/production/project_184/datasets/cookie_cats.csv"]
    else:
        lines=["# 游戏留存实验分析与 AI 运营助手",
            "\n马延青｜个人作品，开发使用 AI 编程辅助。基于历史公开实验的分析案例，不是米哈游内部数据或已上线生产服务。",
            "\n## 一句话理解\n\n用数据回答“游戏进度门槛从第 30 关移到第 40 关，是否值得上线”，并将分析过程做成可查证据、可看情景、可输出双语报告的工作台。",
            f"\n## 核心发现\n\n公开样本包含 {analysis['rows']:,} 名玩家。D7 留存由对照组的 {c['d7_rate']:.2%} 变为实验组的 {t['d7_rate']:.2%}，差异 {d7['delta']*100:+.3f} 个百分点，单指标 95% 区间 [{d7['ci_low']*100:+.3f}, {d7['ci_high']*100:+.3f}] 个百分点。",
            "建议暂缓全量上线，先核查实验完整性。预期分流比例未提供；50:50 假设下的比例异常只是复核信号，不代表已证明实验失败。",
            "\n## 三分钟浏览路线\n\n1. **实验决策**：看结论、两组人数与留存区间。\n2. **决策沙盘**：改变假设玩家规模或容忍边界，查看业务含义；人数换算不是实际损失。\n3. **行为与质量**：看极端记录和回访组合，理解为什么不轻易作流失归因。\n4. **AI 分析助手**：选择离线规则，点击“评估是否上线”，再点击或输入地区问题，展开每条回答的证据。无需提供 API Key。",
            "\n## 适用范围\n\n| 分类 | 场景 | 当前支持程度 |\n|---|---|---|",
            *[f"| {x} | {y} | {z} |" for x,y,z in scope_rows("zh")],
            "\n## 能展示的岗位能力\n\n- **数据分析**：用 SQL/Python 构建留存指标，评估实验效果。\n- **业务判断**：结合区间、完整性和业务边界提出行动建议。\n- **交付沟通**：交互看板、可复核证据和中英文简报。\n- **AI 工程**：已实现受限工具调用接口；真实模型调用验收待完成。",
            "\n## 如何体验\n\n免安装介绍文件可直接用浏览器打开，不需要 Python、账号或密钥。交互版目前运行在作者电脑上，localhost 地址不能供外部 HR 直接访问；远程操作需要另行部署的地址或现场演示。技术面试官如需复现，可使用单独提供的源码包，按 README.md 运行。",
            "\n## 重要边界\n\n数据没有国家、付费、逐日时间或门槛曝光事件；累计局数的源说明存在 7/14 天冲突，不能作为早期预测特征。当前程序适配固定的已审核数据，不支持任意 CSV 上传，不是实时游戏监控平台，也不会自动修改游戏配置。",
            f"\n来源指纹：`{analysis['source_sha256']}`。\n\n来源：https://assets.datacamp.com/production/project_184/datasets/cookie_cats.csv"]
    return "\n".join(lines)+"\n"
