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
* Memory（进行中）
* RAG（进行中）

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

## 说明

本仓库中的代码、目录结构和设计方案可能会随着学习过程持续调整。

目标不是追求最终形态，而是记录从零理解 Agent 的完整过程。
