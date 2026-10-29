# 国际化迁移设计：从教学实验到游戏运营

本文件是未来接入设计，不是已测得的地区结论，也不是已经实现的生产数据接入。

## 可迁移的业务问题

对米哈游游戏可提出“新手引导或内容解锁节奏调整，是否改善新玩家体验和留存”的假设。需要结合具体玩法、玩家阶段与活动周期重新设计；Cookie Cats 的门槛效果不能外推到开放世界、回合制或动作 RPG。

## 最小事件契约

| 表 / 事件 | 核心字段 | 用途 |
|---|---|---|
| player_install | player_key, installed_at_utc, install_timezone, country, locale, platform, acquisition_channel | 入组与地区分层；时区语义需定义 |
| experiment_assignment | player_key, experiment_id, arm, assigned_at_utc, planned_probability, eligibility_version | 分流与 SRM；保留全部合格分流玩家 |
| session_start | event_id, player_key, occurred_at_utc, ingested_at_utc, game_version | 去重、迟到事件、DAU 与留存 |
| feature_exposure | event_id, player_key, feature_id, occurred_at_utc | 检查真实曝光；不随意以曝光后样本替代 ITT |
| progression | player_key, milestone_id, occurred_at_utc | 关卡与内容节奏；区别尝试数与通关数 |
| optional purchase | transaction_id, player_key, currency, amount, occurred_at_utc | 收入护栏；需统一退款与汇率规则 |

这是拟议 schema，不是当前 CSV 的已有字段。数据量、地区分布、收入和上线效果均不预设。

## 指标规则

1. 全局监控使用明确的 UTC 日界；用户日留存另以安装时固定的时区计算，避免出差 / VPN / 夏令时改变归属。两套口径分开展示，不混用。
2. D1 / D7 指定为对应本地日活跃，不是“24/168 小时内任意返回”；同时记录完整观察期截止、数据延迟容忍窗和水位。
3. 地区选择使用安装或业务定义地区，语言单独存储；语言不是国家，外服不等于海外国籍。
4. 平台、地区、版本是实验前分层维度；累计局数、消费、门槛曝光是分流后变量，不能随意用来定义因果分组。
5. 固定总体分析与预先指定的地区交互检验；小地区报告样本量和区间，控制多重比较，不在多个地区中只挑显著结果。

## 上线前复核

预期分流比例是否随地区或平台不同？记录是否去重、跨设备是否合并？新版本或地区活动是否重叠？观察窗口是否成熟？数据接入延迟是否只影响某组？异常来自真实行为还是埋点丢失？任何因果解释都应先回答这些问题。

## LLM 可以辅助的工作

读取指标与地区规则，生成受控查询，区分绝对人数与留存率，分解组成变化，生成双语报告初稿，并列出缺失证据。新增字段未经契约和质量检查前，不允许模型猜测其含义。最终实验决策由业务与分析师复核，系统不自动改游戏配置、触达玩家或投放预算。
