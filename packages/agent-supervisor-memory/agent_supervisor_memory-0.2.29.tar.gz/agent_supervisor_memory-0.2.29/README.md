# agent-supervisor-memory (MCP server)

本目录提供一个 **单进程** 的 Python MCP server（stdio），默认启用：

- `workflow_*`: 生成最小化 spec（lite/spike/heavy）+ 路由建议（模型/effort）
- `memory_*`: 个人记忆（JSON 存储，关键词+tags+key 命名空间检索；无向量数据库/无 embedding）

MCP server ID：`agent-supervisor-memory`（见 `mcp-tools/agent-supervisor-memory/src/agent_supervisor_memory/server.py`）。

代码结构（便于加载更小的上下文）：
- `server.py`: wiring（组合 config + services + tools）
- `config.py`: env/flag 解析（主前缀 `AGENT_SUPERVISOR_MEMORY_*`）
- `services/`: `dispatch.py` / `memory_store.py` / `policy.py` / `workflow_spec.py`
- `tools/`: `core.py` / `dispatch.py` / `memory.py` / `workflow.py`
- `utils/`: env/fs/text helpers（路径推断、tail 截断、verbosity 归一化）

## Quickstart

```sh
cd mcp-tools/agent-supervisor-memory
poetry install
poetry run agent-supervisor-memory --dispatch-dir "$HOME/.codex/codex-dispatch"
```

环境变量（优先顺序）：
- 推荐前缀：`AGENT_SUPERVISOR_MEMORY_*`（如 DISPATCH_DIR / MEMORY_PATH / POLICY_PATH / *_ENABLED / MEMORY_MAX_* / VERBOSE / VERBOSITY）

默认存储文件：

- Memory：优先使用“最近的祖先目录中已存在的 `.codex/`”下的 `.codex/memory.json`；若不存在，则用 `<cwd>/.codex/memory.json`
- Policy：同理，默认 `.codex/agent-policy.json`
- Dispatch：`--dispatch-dir` 指定一个 **base 目录**，server 会按项目自动分桶：
  - `<dispatch-dir>/<project_bucket>/<job_id>/{meta.json,stdout.jsonl,stderr.log,last_message.txt}`
  - `project_bucket` 会尽量从 `codex_dispatch_start(cwd=...)` 的 cwd 向上推断（优先 `.codex/`，其次 `.git/`），并用 hash 保证稳定且不会太长
  - `job_id` 形如 `<project_bucket>--<uuid>`

说明：Poetry 会统一管理虚拟环境与依赖，避免你本机 shell 的 `python/pip` alias 干扰。

## 如何引用（MCP client 注册）

不同 MCP client 的配置方式不同，但核心信息通常是：

- `command`: `uvx`
- `args`: `["agent-supervisor-memory", "...flags"]`

工具名引用方式是 `tool name`，例如：`memory_search`、`workflow_route`。

### 参考配置片段（TOML 风格）

如果你的 client 支持类似下面这种配置（你贴的 `exa` 例子就是这种风格），可以这样写：

```toml
[mcp_servers.supervisor_memory]
command = "uvx"
args = ["agent-supervisor-memory", "--dispatch-dir", "/ABS/PATH/TO/.codex/codex-dispatch"]
# 或仅配置 env：AGENT_SUPERVISOR_MEMORY_DISPATCH_DIR=/ABS/...
```

说明：

- `[mcp_servers.supervisor_memory]` 里的 `supervisor_memory` 是 **client 侧别名**，你可以随便取（只要不跟别的 server 重名）。
- 是否“唯一”由你的 client 配置决定；PyPI 包名的唯一性是另一层（发布时）。

### 常用开关

```toml
[mcp_servers.supervisor_memory]
command = "uvx"
args = ["agent-supervisor-memory", "--dispatch-dir", "/ABS/PATH/TO/.codex/codex-dispatch", "--global-memory", "--global-policy"]
```

关闭某些能力（默认都是启用）：

```toml
[mcp_servers.supervisor_memory]
command = "uvx"
args = ["agent-supervisor-memory", "--dispatch-dir", "/ABS/PATH/TO/.codex/codex-dispatch", "--no-memory", "--no-subagents", "--no-policy"]
```

### 高级覆盖（一般不需要）

为兼容少数 client 场景，仍保留路径覆盖参数（优先级最高；不建议作为默认配置）：

```sh
agent-supervisor-memory --dispatch-dir /abs/path/to/codex-dispatch --memory-path /abs/path/to/memory.json --policy-path /abs/path/to/agent-policy.json
```

每次 tool 调用也可传：

- `options.enable_memory`: `true|false`
- `options.enable_subagents`: `true|false`

## 模型与模式（跨模型路由）

本 server **不直接调用模型**；它只提供“建议路由”，由你的 Supervisor/Client 负责真正使用什么模型去执行。

- `policy_get`: 读取策略文件
- `workflow_route`: 根据任务文本 + `mode/effort/auto` 给出建议的 `supervisor_model/coder_model/effort`

默认配置：

- Supervisor：`codex-5.2`
- Coder：`gpt-5.1-codex-max`
- `saving`：默认 `effort=medium`
- `efficient`：默认 `effort=medium`

## 如何确认正在使用（VSCode/其他 client）

- 调用 `capabilities_get`，查看返回里的 `memory.mode` / `policy.mode`（`project|global|disabled`）以及落盘 `path`。
- 写入/检索验证：`memory_put` 写入一条，然后 `memory_search` 搜索关键字。

## VSCode：自动“主/子模型”分工（推荐）

如果你同时启用了：

- `mcp__supervisor_memory__*`（本 server 的 tools）
- `mcp__codex__codex` / `mcp__codex__codex-reply`（Codex MCP）

那么可以在一个 Supervisor 会话里自动启动 Coder 子会话，并显式指定 coder 使用 `model=gpt-5.1-codex-max`（或按策略自动选择）：

1) 生成最小 spec（供 coder 执行）：
- 调用 `mcp__supervisor_memory__workflow_ensure_spec`（输入你的任务文本）

2) 获取路由建议（选择 coder 模型与 effort）：
- 调用 `mcp__supervisor_memory__workflow_route`（`task_text` 传上一步的 spec）

3) 启动 coder 子会话并执行：
- 调用 `mcp__codex__codex`，并设置：
  - `cwd`: 项目根目录
  - `model`: 上一步返回的 `coder_model`
  - `prompt`: spec + 约束（例如：只做必要改动、不要跑 build gate、先做最小校验）

4) 迭代直至完成：
- 用 `mcp__codex__codex-reply`（`conversationId` 为上一步返回）继续

### 如果 `mcp__codex__codex` 超时/返回类型不兼容

部分环境下，Codex MCP tool 可能会遇到 tool-call 超时（例如 60s）或 “Unexpected response type”。
此时可以改用本 server 自带的 dispatch 工具：它会在本机启动 `codex exec` 作为后台任务，并通过轮询查询结果。

流程：

1) 启动任务（内部记录 `job_id`，可按需返回）：
- 调用 `codex_dispatch_start`（`model` 用 `workflow_route` 返回的 `coder_model`；`cwd` 为项目根目录；`prompt` 传 spec）
- 默认 **异步**：返回 `{state:\"running\", job_id, job_ref}`（`job_ref` 为本进程内短句柄）；如需 job 目录等完整字段，请传 `options={\"verbosity\":\"full\"}`。
- 如需进一步缩短返回：传 `options={\"omit_job_id\":true}`（仅保留 `job_ref`）；如需路径 artifacts：传 `options={\"include_artifacts\":true}`。
- 如需“阻塞等待”一小段时间：传 `options={\"wait\":true,\"max_wait_seconds\":45}`（到点仍在运行则返回 `state:\"running\"`，避免 tool-call 60s 超时）。
- 为避免大 prompt 导致 UI/context 膨胀：用 `prompt_path=\"/abs/path/to/spec.txt\"`（或 `options={\"prompt_path\":\"...\"}`）替代直接传 `prompt`。
- 支持 `options.max_model_reasoning_effort`（例如 medium）来限制 codex exec 的推理开销。
- 如项目根目录存在 `.codex/structured-request.json`，可用 `options={\"use_project_prompt\":true}` 让 server 自动读取作为 prompt（避免在参数里携带文本）。

2) 轮询结果：
- 调用 `codex_dispatch_status(job_id=... 可省略)` 直到 `state` 变为 `completed|failed`（默认仅回传最小字段）
- 默认输出最小化：运行/完成返回 `{state, message}`（`message` 为提取后的“最后一条用户可读消息”，非原始 JSONL）；失败返回 `{state:'failed', exit_code?, message}`（message 优先 stderr 摘要）；未找到返回 `{state:'not_found'}`。默认不会返回 `job_id` / `meta` / `artifacts` / `last_message`；若需原始 JSONL/full meta，请用 `options={\"verbosity\":\"full\"}`。
- 默认 tail 读取约 2KB 的 stdout/stderr（可通过 `stdout_tail_bytes`/`stderr_tail_bytes` 调整）；需要完整日志时，请使用 full 模式。
- `job_id` 参数可选：缺省时自动使用 server 进程内记录的上一次 `codex_dispatch_start` job；也可用 `job_ref`（短句柄）替代 `job_id`。
- 增量轮询（推荐，减少重复 tail）：传 `stdout_cursor`/`stderr_cursor`（首次传 `0`），并设置 `stdout_tail_bytes`/`stderr_tail_bytes` 作为“本次最多返回的新增字节”；响应会附带 `cursor={stdout,stderr}` 与 `stdout_delta`/`stderr_delta`（如有新增）。
- 默认增量轮询只回 `{state,cursor,has_*_delta,*_delta_len}`；如需实际文本，传 `options={\"include_deltas\":true,\"delta_max_chars\":1200}`。
- 如需原始/完整响应（含 `meta`/`artifacts`/`last_message` 等），请传 `options={\"verbosity\":\"full\"}` 或 `options={\"verbose\":true}`，或在启动 server 时设置 `AGENT_SUPERVISOR_MEMORY_VERBOSE=1`（或 `AGENT_SUPERVISOR_MEMORY_VERBOSITY=full`）。
- summary 游标：`options.include_summary_cursor=true` 时，`codex_dispatch_status` 输出会附带基于内部增量的 `summary_cursor`（cursor/非 cursor 模式均支持）；`codex_dispatch_wait_all` 也会在 summary-only entries 与详细 jobs 中附带 `summary_cursor`，便于增量判断摘要是否更新。
- 批量等待：`codex_dispatch_wait_all(job_ids? , options?)` 默认 summary-only（返回 `{state, jobs:[{job_id,state,summary?}], counts?}`，每个 job 都包含状态及近期 summary；跳过 stdout/stderr tail）；若需 jobs 详情/last_message/artifacts，传 `options={\"summary_only\":false}`。`options.problem_only=true`（可配合 `options.problem_states`，支持 JSON list 或逗号分隔字符串，默认集合为 failed/timeout/not_found/canceled）时 jobs 仅保留问题状态且强制返回 counts；`options.include_problem_job_ids=true` 会额外返回 `failed_job_ids` / `timeout_job_ids` / `not_found_job_ids` / `canceled_job_ids`（以及额外的 `problem_job_ids` map）；`options.include_summary_cursor=true` 让 summary-only entries/详细 jobs 附带 `summary_cursor`。
- 取消任务：`codex_dispatch_cancel(job_id|job_ref)` 会发送 SIGTERM 并标记 cancel requested；任务退出后状态会变为 `canceled|failed|completed`。
- 事件级增量（推荐，最省 context）：`codex_dispatch_events(job_id|job_ref, cursor=0)` 返回解析后的 stdout.jsonl events（默认已过滤噪声并压缩 text），并用 `cursor` 增量拉取；`options.max_paths`（默认 20，仅 compact 生效）限制 `file_change` 事件的 `paths` 长度并返回 `paths_total`/`paths_extra`，`text` 仍展示前 3 个路径并用 `+N` 表示剩余数量；如需原始事件对象（不裁剪 `paths`），传 `options={\"raw\":true}`。

## 兼容性（Compatibility）

保留 `MCP_*` 路径/开关 与 `SUPERVISOR_MEMORY_*`（verbosity 只读）的解析，便于旧配置继续工作；新配置请统一使用 `AGENT_SUPERVISOR_MEMORY_*`。

## Tools

- `capabilities_get`
- `health_get`（快速健康检查，无磁盘 I/O）
- `policy_get`
- `memory_put`
- `memory_search`
- `memory_delete`
- `memory_compact`（生成 `profile.json`，把“杂乱记忆”压缩为分类摘要）
- `workflow_ensure_spec`
- `workflow_route`
- `subagents_echo`（示例）
- `codex_dispatch_start`（启动 `codex exec` 后台任务）
- `codex_dispatch_status`（轮询任务状态/输出）
- `codex_dispatch_cancel`（取消后台任务）
- `codex_dispatch_events`（增量读取 stdout.jsonl events）

## 发布到 PyPI（维护者）

PyPI 不允许覆盖已发布的同版本号，所以每次发布前都需要 bump version。

```sh
cd mcp-tools/agent-supervisor-memory

# 1) release helper（bump patch + build + publish + 清理 uv/uvx 缓存）
chmod +x scripts/bump_patch_and_clear_uv_cache.sh # 一次即可
./scripts/bump_patch_and_clear_uv_cache.sh [--dry-run] [--verbose] [--testpypi] [--cache-only]
# token：优先用 Poetry 配置（如 `poetry config pypi-token.pypi ...`）；也可用环境变量覆盖：`PYPI_TOKEN` / `TESTPYPI_TOKEN`
```
