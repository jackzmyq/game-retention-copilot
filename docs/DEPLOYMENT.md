# GitHub Pages 访客版

目标：任何访客无需登录、无需 API Key，即可查看分析、操作决策沙盘、下载报告并体验离线规则。

## 两个运行版本

- `web/`：浏览器访客版，由 GitHub Pages 托管。只读取已验证的聚合证据；场景交互在浏览器计算，分流及样本量网格使用 Python 预先计算值。没有密钥输入或模型调用，会话仅保存在当前页面内存。
- `app.py`、`src/`、`scripts/`：完整 Python/SQL/Streamlit 分析源码，保留本地复现、受限 SQL 和可选 DeepSeek 接口。真实模型调用尚未验收。

访客版的 SQL 面板展示构建时执行并保存的查询结果，不执行任意 SQL。离线规则不是 LLM，也不具备通用多轮理解。网页不含原始玩家记录，不把访客问题发送到模型服务；GitHub 托管本身仍受其服务政策约束。

## 更新访客版

```bash
python scripts/download_data.py
python scripts/build_pipeline.py
python -m src.reporting
python scripts/build_hr_pack.py
python scripts/build_web.py
node --test web/core.test.cjs
```

将更新后的源码、报告及 `web/` 提交。Pages 工作流先检验浏览器脚本与计算一致性，再发布 `web/`；Python CI 另外下载原始数据重建并运行测试。原始数据不会进入仓库或 Pages 部署包。

仓库 Settings → Pages 的 Source 选择 GitHub Actions，随后 `Publish visitor demo` 工作流负责部署。只有工作流成功并实际检查站点后，才把部署地址视为可用于投递的链接。

## 发布内容

包括源码、指标与报告、HR 介绍、浏览器版和 CI 配置。排除 `.env`、密钥、`.venv`、`.cache`、原始数据、派生玩家级 SQLite、私人调用轨迹和临时文件。不把复制打包的源码 ZIP 再嵌套进仓库。

## 回滚与后续维护

通过正常 Git 提交恢复上一版本，等待 Pages 工作流重新发布；不直接改生产页面上的结果。新增数据或指标必须先修改和核验 Python 管线，再生成浏览器证据，避免两个版本口径漂移。未来如需真实模型，使用另行部署的 Python 服务或本地版；访客版目前不提供密钥入口。
