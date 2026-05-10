# 典型案例：《我们为什么要睡觉》

这个案例展示 Books Skill 处理单本 EPUB 的完整产物。

## 输入文件

- 原书：《我们为什么要睡觉》
- 作者：[英] 马修·沃克
- 输入格式：EPUB
- 本地原文件大小：约 5.6 MB
- 正文抽取结果：约 241002 字符
- 源文件说明：原书 EPUB 是用户本地输入文件，不随本仓库分发；复现测试时可放入自己有权使用的 EPUB。本案例保留整理版、EPUB 整理版和审计结果，方便参考工作流效果。

## 输出文件

- `summary.md`：Markdown 精读整理版。
- `summary.epub`：由 Markdown 导出的 EPUB 整理版。
- `self-check.md`：整理质量自检。
- `quality-audit.json`：内容质量审计结果。
- `output-audit.json`：Markdown、EPUB、自检文件结构审计结果。

## 运行信息

- 使用技能：Books Skill，本地调用名为 `book.skill`
- Agent 工具：Codex
- 模型：GPT-5
- 处理日期：2026-05-10
- 运行环境：Windows PowerShell + Python

## 结果摘要

- Markdown 字数：10839 字符
- 一级标题数：4
- EPUB 结构：通过
- 自检文件：存在
- 内容质量审计：0 个红旗，0 个警告
- 输出结构审计：`all_ok: true`
