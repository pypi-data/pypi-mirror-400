# GitHub Gist 上传使用说明

## 功能概述

lunar-birthday-ical 现在支持将生成的 iCalendar 文件自动上传到 GitHub Gist. 你可以:

1. 首次创建新的 Gist
2. 通过 gist_id 更新已有的 Gist

## 配置步骤

### 1. 创建 GitHub Personal Access Token

访问 https://github.com/settings/tokens/new?scopes=gist 创建一个带有 gist 权限的 token.

### 2. 配置文件设置

在你的配置文件 (如 `config/example-lunar-birthday.yaml`) 中添加 `github_gist` 配置:

```yaml
github_gist:
    # 启用 GitHub Gist 上传
    enabled: true
    # 你的 GitHub Personal Access Token
    token: "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    # Gist ID (首次上传时留空)
    gist_id: ""
    # Gist 描述
    description: "我的农历生日日历"
    # 是否公开 (false 为私密 gist)
    public: false
```

### 3. 首次上传

运行命令:

```bash
lunar-birthday-ical config/example-lunar-birthday.yaml
```

程序会输出类似以下信息:

```
INFO: GitHub Gist operation successful: gist_id=abc123def456, url=https://gist.github.com/abc123def456
INFO: Add 'gist_id: abc123def456' to your config file to update this gist in the future
```

### 4. 更新已有 Gist

将上一步获得的 `gist_id` 添加到配置文件:

```yaml
github_gist:
    enabled: true
    token: "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    gist_id: "abc123def456" # 添加这一行
    description: "我的农历生日日历"
    public: false
```

再次运行命令时, 程序会更新同一个 Gist 而不是创建新的.

## 同时使用多个上传方式

你可以同时启用 `pastebin` 和 `github_gist`:

```yaml
pastebin:
    enabled: true
    base_url: https://komj.uk
    manage_url: ""

github_gist:
    enabled: true
    token: "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    gist_id: ""
```

两种上传方式会依次执行, 互不影响.

## 安全注意事项

⚠️ **重要提示**:

1. **不要将包含 token 的配置文件提交到公开仓库**
2. 建议使用环境变量 `GITHUB_TOKEN` 来存储 token
3. 定期轮换你的 Personal Access Token
4. 如果 token 泄露, 立即在 GitHub 设置中撤销它
