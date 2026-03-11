[![Chinese](https://img.shields.io/badge/中文-README-blue)](docs/README.zh.md) [![Tutorial](https://img.shields.io/badge/Tutorial-8CA1AF?logo=readthedocs&logoColor=fff)](docs/Tutorial.md)

# IMAP to Gmail Bridge

What does this repository do? In a nutshell:

> **Third Party Mail** `--IMAP->` **Github Action** `--Gmail API->` **Google Workspace**

As Google phases out legacy POP3 fetching and basic authentication, pulling emails from third-party business accounts -- like Tencent Exmail or Aliyun -- into Gmail (not APP) has become increasingly difficult. This repository implements an automated email forwarding system based on GitHub Actions, designed to fetch third-party emails via IMAP and safely inject them into your Google Workspace.

Thus, we have:

1. Fetch emails to the Workspace using Github Action;
2. Emails are still sent (and replied to) via SMTP in the Workspace.

## I. Key Features

- **Serverless Automation**: Fully powered by GitHub Actions `cron` jobs. No VPS or server maintenance required.
- **High Security**: Uses GitHub Actions Secrets to store IMAP passwords and Gmail API Tokens.
- **Native Conversation Threads**: Unlike traditional forwarding, this tool parses `Message-ID`, `In-Reply-To`, and `References` headers. It matches existing `threadId` via the Gmail API, perfectly combining replies into long conversation threads, just like native Gmail.
- **Read State Sync**: Automatically marks emails as `\Seen` on the source IMAP server after successful injection to prevent duplicates.

## II. Architecture Workflow

1. GitHub Actions triggers the Python script every 30 minutes.
2. The script logs into your third-party IMAP server and searches for `UNSEEN` emails.
3. It fetches the raw RFC822 bytes of the email.
4. It searches your Gmail for previous message IDs to maintain Conversation Threads.
5. It uses Gmail API (`messages.insert`) to inject the email into your Inbox, marked as unread.

## III. Quick Start

To deploy this mail bridge for your own Google Workspace, please read [this Tutorial](docs/Tutorial.md).