# 如何配置仓库

本文将介绍如何配置本仓库的“自动邮件转发”功能。整个过程分为三个主要步骤：获取 Google Token、配置 GitHub Secrets、启动 Actions。

## 一、获取 Gmail Token

为了调用 Gmail 的 API，我们需要首先在 Google Cloud 中创建一个项目，并生成一个 `credentials.json` 凭据，最后在本地运行脚本生成 Token。

### 1.1 创建 Google Cloud 项目

已有项目可以直接跳转到 [1.2](#12-启用-gmail-api)。

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)。
2. 点击页面顶部的项目选择器(或 "Select a project")，然后选择 **"New Project"**。
3. 给项目起个名字(例如 `Mail-Bridge`)，然后点击 **"Create"**。

### 1.2 启用 Gmail API

1. 确保已选中刚才创建的项目。
2. 在左侧菜单中，前往 **"API和服务" (APIs & Services)**。
3. 在搜索栏输入 **"Gmail API"**。
4. 点击搜索结果中的 Gmail API，然后点击 **"Enable"** 启用它。

### 1.3 OAuth Consent Screen (OAuth 同意屏幕)

1. 前往 **"API和服务" > "OAuth权限请求页面" (OAuth consent screen)**。
2. 用户类型 (User Type) 选择 **"External"** (个人 Gmail) 或 **"Internal"** (Workspace 组织账号)，点击 **"Create"**。
3. 填写必填项：
    * **App name:** `Mail Bridge`
    * **User support email:** 您的 Gmail。
    * **Developer contact info:** 您的 Gmail。
4. 点击 **"Save and Continue"**。在 "Scopes" 页面无需特别选择，直接点击 **"Save and Continue"**。
5. **重要 (如果选了 External)：** 在 **"目标对象 > 测试用户"** 页面，点击 **"Add Users"**，输入您需要接收邮件的 Gmail 地址。

### 1.4 创建凭据并下载 JSON

1. 前往 **"APIs & Services" > "Credentials"**。
2. 点击顶部的 **"+ Create Credentials"**，选择 **"OAuth client ID"**。
3. **Application type** 选择 **"Desktop App" (桌面应用)**。
4. **Name** 可以随意填写(如 `My Python Script`)，点击 **"Create"**。
5. 弹窗会出现 "OAuth client created"，点击 **"Download JSON"** 下载文件。
6. **重命名文件：** 将下载下来的那个带有长串字符的文件重命名为 `credentials.json`。

### 1.5 在本地生成 Token

1. 将 `credentials.json` 放到本仓库 `src/` 目录下（与 `gen_token.py` 同级）。
2. 在本地终端中，首先安装依赖：
   ```
   pip install -r requirements.txt
   ```
3. 运行生成脚本：
   ```
   python src/gen_token.py
   ```
4. 此时浏览器会自动弹出授权页面。**请务必勾选所有权限**（包括“查看您的电子邮件”，这是为了支持邮件长对话折叠功能）。
5. 授权成功后，当前目录下会生成一个 `token.json`。该文件包含了 `token, refresh_token` 等字段。**请妥善保管，不要提交到公开仓库中！**

## 二、配置 GitHub Secrets

接下来，我们需要将敏感信息配置到 GitHub 仓库的安全环境变量中。
进入您的 GitHub 仓库页面，点击 `Settings -> Secrets and variables -> Actions`，在 `Repository secrets` 区域点击 `New repository secret`。

### 2.1 添加 GMAIL_TOKEN_JSON

创建一个 Secret：
* **Name**: 填写 `GMAIL_TOKEN_JSON`
* **Secret**: 使用文本编辑器打开您在第一步中生成的 `token.json`，将里面的**全部内容**复制并粘贴到此处。

### 2.2 添加 ACCOUNTS_JSON

创建一个名为 `ACCOUNTS_JSON` 的 Secret，用于配置需要被“捕获”的第三方邮件账号。请严格按照以下 JSON 数组格式填写（可增减账号）：

```
[
  {
    "name": "Tencent_Exmail",
    "imap_server": "imap.exmail.qq.com",
    "imap_port": 993,
    "email": "username@example_tencent.email",
    "password": "YOUR_TENCENT_PASSWORD"
  },
  {
    "name": "Aliyun_Exmail",
    "imap_server": "imap.qiye.aliyun.com",
    "imap_port": 993,
    "email": "username@example_ali.com",
    "password": "YOUR_ALIYUN_PASSWORD"
  }
]
```

> **提示**：这里的 password 通常是第三方邮箱提供的“客户端专用密码（授权码）”，而不是您的网页登录密码。

## 三、启动并测试 Actions

1. 确保您的仓库中包含 `.github/workflows/mail_bridge.yml` 文件并已推送到主分支（`main` 或 `master`）。
2. 点击仓库顶部的 **Actions** 标签页。
3. 在左侧边栏选中 **IMAP to Gmail Bridge**。
4. 点击右侧的 **Run workflow** 按钮进行第一次手动测试。
5. 展开运行日志，如果看到 `[+] Successfully inserted message to Gmail`，则配置完美成功！此后，GitHub 会按照设定每 30 分钟自动为您拉取一次邮件。