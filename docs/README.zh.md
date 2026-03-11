[![English](https://img.shields.io/badge/English-README-blue)](../README.md) [![Tutorial](https://img.shields.io/badge/教程-8CA1AF?logo=readthedocs&logoColor=fff)](Tutorial.zh.md)

# IMAP to Gmail 邮件桥接器

本仓库是干什么的？用一句话来说就是：

> **Third Party Mail** `--IMAP->` **Github Action** `--Gmail API->` **Google Workspace**

随着 Google 逐渐淘汰基于基础认证的 POP3 代收邮件功能，将第三方邮件——例如，腾讯企业邮件、阿里企业邮件——无缝集成到 Gmail (Not APP) 变得越来越困难。因此，本仓库实现了一个基于 Github Action 的自动邮件抓取功能，旨在将第三方邮件通过 IMAP 拉取，并利用 Gmail API 原生注入(Insert)到 Google Workspace 中。

于是，我们现在：

1. 通过 Github Action 抓取邮件到Workspace中；
2. 在Workspace中依然通过SMTP发送(回复)邮件。

## 一、核心亮点

- **零成本**：完全依托 GitHub Actions 的定时任务(cron)运行，无需购买和维护云服务器。
- **安全**：所有的邮箱密码、Google API Token 均保存在 GitHub Secrets 中。
- **长对话折叠**：代码会自动提取原邮件的 `Message-ID` 并通过 Gmail API 检索关联的 `threadId`，让所有回复完美折叠在同一个邮件会话中(Threading)，告别散落的独立回复。
- **状态同步**：成功注入 Gmail 后，自动将原邮箱服务器上的邮件标记为已读(`\Seen`)，避免重复拉取。

## 二、工作原理

1. GitHub Actions 每半小时触发一次 Python 脚本。
2. 脚本登录第三方 IMAP 服务器，筛选出所有未读(`UNSEEN`)的邮件。
3. 抓取完整的 RFC822 原始字节流。
4. 在 Gmail 中检索上下文 ID，绑定 Thread 会话。
5. 通过 Gmail API 直接将原封不动的邮件注入到您的收件箱中。

## 三、快速开始

如果您想为自己的 Google Workspace 部署这套系统，请阅读[这篇教程](Tutorial.zh.md)。