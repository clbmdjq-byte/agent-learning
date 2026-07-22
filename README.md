# Agent Learning

用于学习、验证和沉淀 AI Agent 相关知识与实践的实验仓库。

本仓库并非以构建生产级 Agent 框架为目标，而是通过动手实现的方式验证对 Agent 核心概念、架构模式和执行流程的理解。

## 学习目标

逐步理解并实践：

* Tool Calling
* Memory
* RAG（Retrieval Augmented Generation）
* Context Engineering
* ReAct
* Plan & Execute
* Multi-Agent

## 当前实现

* LLM Client
* Tool Registry
* Tool Calling
* Agent Loop（Demo）
* Memory（短期记忆已接入 Demo）
* Session（会话元信息持久化、恢复与切换）
* RAG（本地检索 Demo 已通过 Tool 接入）
* Context Builder（基础消息组装）

## 当前进度

### Memory

当前已接入短期记忆和历史消息持久化。历史消息用于记录真实 user/assistant 输入输出，短期记忆用于在当前 Session 中保留摘要和最近消息，并支持服务重启后的基础恢复。

Memory 内部负责判断何时生成摘要、选择待摘要消息、调用 LLM 和写回摘要。Memory Summary Prompt 与模板由 `memory` 包管理，不依赖 Agent 的 Context Builder。

### Session

`SessionInfo` 记录 Session ID、标题、创建时间、更新时间和最后一条消息 ID。`SessionRepository` 支持按 Session ID 读写元信息，并通过扫描 `session/*.json` 获取可恢复的会话列表。

Session 采用懒加载策略：Agent 启动时不加载所有会话内容，只在用户选择或运行指定 Session 时恢复对应的 SessionInfo 和短期记忆。新的 Session 只有在完成一轮成功对话后才持久化，避免空会话污染恢复列表。

本地存储通过 `STORE_DIR` 配置，当前结构为：

```text
data/store/
  history/
  short_term_memory/
  session/
```

### Context

跨模块使用的 LLM 消息统一为 `common.models.PromptMessage`，由 `LlmClient` 在调用边界转换为模型接口需要的消息格式。

`ContextDraft` 负责保存当前用户输入、`ShortTermMemory` 和本轮完整的 `ToolExchange`。`ContextEngine` 在每次调用 LLM 前先执行 `ContextSelector`，再调用 `ContextBuilder` 将选中材料渲染为 `PromptMessage`。当前默认使用 `NoOpContextSelector`，暂不删除任何材料。

assistant tool call 与其全部 tool result 被建模为不可拆分的 `ToolExchange`，为后续原子裁剪建立了边界。ContextEngine 还会对实际渲染的消息和本轮实际 Tool Schema 进行启发式 token 估算，并通过 `ContextUsage` 返回分类统计。

默认 `HeuristicTokenEstimator` 按 `ceil(UTF-8 字节数 / 3)` 估算文本，并计入每消息、每 Tool Schema 和整个请求的固定协议开销。这不是特定模型的精确 tokenizer，只用于观察 system 模板、会话、ToolExchange 和 Tool Schema 的相对开销及增长趋势。

窗口统计使用 `MAX_CONTEXT_TOKENS`（默认 8192）、`MAX_TOKENS`（默认 1024，作为输出预留）和 `CONTEXT_SAFETY_TOKENS`（默认 128）。当前只统计 `estimated_remaining_tokens`，即使结果为负也不会裁剪或阻断请求。设置 `PRINT_TRACE=1` 可以查看每次 LLM 调用对应的 Context Usage。

当前尚未实现主动 RAG、跨来源选择、实际 token 预算控制、裁剪策略和完整的 Context 选择报告。

### RAG

当前已实现本地文档加载、切分、检索、合并和重排序。RAG 对外保留结构化 `SearchResult`，并通过 `SearchTool` 接入当前 Agent Loop。`SearchTool` 将检索结果转换为统一 Tool `dict`，进入 Agent 对话时再由 Context 转换为 Tool Message。

如果 RAG 后续使用 LLM 实现 Query Rewrite 或 LLM Reranker，对应 Prompt Builder 和模板由 RAG 内部管理，不与 Agent 的 Context Builder 混用。

## DemoAgent 主流程

```mermaid
flowchart TD
    A[用户输入 + session_id] --> B[获取或恢复 Session]
    B --> C[读取 ShortTermMemory]
    C --> D[Agent 收集 ContextDraft]
    D --> E[ContextEngine 执行 Selector 与 Builder]
    E --> F[LLM 调用]
    F --> G{是否需要工具}
    G -- 是 --> H[BaseAgent 解析并执行 Tool]
    H --> I[Tool 返回结构化 dict]
    I --> J[构造完整 ToolExchange 并更新 Draft]
    J --> E
    G -- 否 --> K[得到最终答案]
    K --> L[追加历史消息]
    L --> M[更新短期记忆及摘要]
    M --> N[持久化 Memory 与 Session]
    N --> O[返回答案]
```

当前 RAG 通过 `SearchTool` 进入 Tool Loop，因此检索结果在主流程中表现为 Tool 的结构化输出。未来增加主动 RAG 后，`SearchResult` 将先进入 Context Selector，再由 Context Builder 渲染。

## 包职责与调用关系

| 包 | 当前职责 | 主要依赖 |
|---|---|---|
| `agent` | Agent 生命周期、Session 恢复、Tool 执行编排、LLM Loop | Context、Memory、Session、Tools、LLM、Trace |
| `common` | 跨模块消息契约、角色类型、时间与本地存储基础能力 | Config |
| `config` | LLM、存储目录和 RAG 路径配置 | 无业务包依赖 |
| `context` | 保存 ContextDraft、选择上下文材料、维护 ToolExchange 原子边界并渲染 `PromptMessage` | Common、Memory 输出模型、RAG 输出模型 |
| `llm` | 模型客户端及模型接口转换 | Common、Config |
| `memory` | 历史消息、短期记忆、摘要策略与内部摘要 Prompt | Common、LLM |
| `rag` | 文档加载、切分、召回、合并与重排 | Config |
| `session` | Session 元信息与持久化 | Common |
| `tools` | Tool 定义、注册、结构化执行结果和 RAG Tool 适配 | RAG |
| `trace` | Agent 执行过程记录与纯文本输出 | 无业务包依赖 |

```mermaid
flowchart LR
    Main[main] --> Agent[agent]
    Agent --> Context[context]
    Agent --> Memory[memory]
    Agent --> Session[session]
    Agent --> Tools[tools]
    Agent --> LLM[llm]
    Agent --> Trace[trace]

    Context --> Memory
    Context --> RAG[rag]
    Context --> Common[common]
    Tools --> RAG
    Memory --> LLM
    Memory --> Common
    Session --> Common
    LLM --> Common
    LLM --> Config[config]
    RAG --> Config
    Common --> Config
```

图中的 `Context --> Memory/RAG` 表示 Context 消费其结构化输出模型，不表示 Context 执行记忆更新或检索策略。模块内部为了生成自身输出而进行的 LLM 调用和 Prompt 构建仍由对应模块负责。

## Context 演进方向

目标流程：

```text
Memory / RAG / Tool 产出结构化结果
        ↓
Agent 收集为 ContextDraft
        ↓
ContextSelector 统一选择与裁剪
        ↓
ContextBuilder 渲染 PromptMessage[]
        ↓
LLM
```

当前已完成基础生命周期：

1. `ContextDraft` 集中保存当前用户输入、Memory 和本轮 Tool Exchange。
2. `ToolExchange` 保证 assistant tool call 与全部 tool result 成组处理。
3. `NoOpContextSelector` 固定每次 LLM 调用前执行 Selector 的生命周期。
4. `ContextEngine` 统一编排 Selector 与 Builder。
5. `TokenEstimator` 和 `ContextUsage` 统计实际渲染消息、Tool Schema 与固定协议开销。
6. Agent Trace 按每次 LLM 调用展示 Context Usage。

接下来按以下顺序演进：

1. 先通过 Context Usage 观察不同来源和 Tool Loop 的上下文增长。
2. 如后续需要控制预算，再实现确定性选择策略，始终保留系统指令和当前用户输入。
3. 增加完整 Context Trace，记录材料入选和裁剪原因。
4. 增加主动 RAG 后，再补充多来源竞争与裁剪测试。

## 设计原则

### 先理解，再抽象

优先验证核心概念与执行流程，而不是提前设计复杂框架。

### 先实现，再优化

通过最小可运行实现（MVP）验证思路，后续再根据实际问题进行重构和抽象。

### 关注原理

重点关注：

* Agent 如何思考
* Agent 如何调用工具
* Agent 如何组织上下文
* Agent 如何使用记忆
* Agent 如何使用外部知识

而不仅仅是框架使用方式。

## 规划路线

```text
LLM
 ↓
Tool Calling
 ↓
Memory
 ↓
RAG
 ↓
Context Engineering
 ↓
ReAct
 ↓
Plan & Execute
 ↓
Multi-Agent
```

## 下一步计划

* 使用 Context Usage 观察固定模板、历史消息、Tool Schema 和 ToolExchange 的实际估算开销。
* 继续按模块学习 Context、Tool、Memory 和 RAG 的职责边界。
* 如 Demo 后续需要真实控制上下文，再为 ContextSelector 增加确定性裁剪策略和预算边界测试。
* Context 基础流程稳定后，再继续验证 ReAct 和 Plan & Execute。
* 后续再评估长期记忆提取与存储结构；当前 Memory Demo 先以短期记忆和历史消息持久化为主。

## 说明

本仓库中的代码、目录结构和设计方案可能会随着学习过程持续调整。

目标不是追求最终形态，而是记录从零理解 Agent 的完整过程。
