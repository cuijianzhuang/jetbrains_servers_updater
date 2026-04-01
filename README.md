# JetBrains 激活服务器列表自动更新

[![Update JetBrains Servers](https://github.com/cuijianzhuang/jetbrains_servers_updater/actions/workflows/update-servers.yml/badge.svg)](https://github.com/cuijianzhuang/jetbrains_servers_updater/actions/workflows/update-servers.yml)
[![Deploy to GitHub Pages](https://github.com/cuijianzhuang/jetbrains_servers_updater/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/cuijianzhuang/jetbrains_servers_updater/actions/workflows/deploy-pages.yml)

这个项目使用 GitHub Actions 自动获取并更新 JetBrains IDE 的激活服务器列表。每天早上9点（北京时间）自动更新。

## 特性

- 🔄 每天自动更新服务器列表
- 📝 同时生成文本格式和HTML格式的服务器列表
- 🤖 使用 GitHub Actions 自动化部署
- 🔍 基于 Shodan API 搜索服务器
- 📋 支持一键复制服务器地址
- 📱 响应式设计，支持移动端访问

## 在线查看

你可以通过以下方式查看服务器列表：

- [HTML 格式](https://cuijianzhuang.github.io/jetbrains_servers_updater/) (推荐)
- [文本格式](jetbrains_servers.txt)

## 本地运行

如果你想在本地运行这个项目：

1. 克隆仓库
   ```bash
   git clone https://github.com/NixiakAI/jetbrains_servers_updater.git
   cd jetbrains_servers_updater


2. 无需安装依赖，请注册一个shando免费账号即可
   

3. 无需设置环境变量：


4. 运行
   ```bash
   python jetbrains_servers_updater.py
   
## 自动更新时间

- 更新频率：每天
- 更新时间：北京时间早上9:00（UTC+8）

## 手动触发更新

你可以通过以下方式手动触发更新：

1. 访问仓库的 Actions 页面
2. 选择 "Update JetBrains Servers" 工作流
3. 点击 "Run workflow"

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

[MIT License](LICENSE)

## 免责声明

本项目仅供学习和研究使用。请确保你的使用符合相关软件许可协议和法律法规。

## 更新记录

你可以在 [Actions](https://github.com/cuijianzhuang/jetbrains_servers_updater/actions) 页面查看所有的更新记录。

---
⭐ 如果这个项目对你有帮助，欢迎点个星！
