# Chinese Calendar / 川象曆

本仓库收录川象曆分年日曆网页。

## 当前内容

- `index.html`：网站首页，目前直接显示 401–500 年日曆。
- `calendar/401-500.html`：401–500 年独立日曆页面。
- `.github/workflows/pages.yml`：GitHub Pages 自动发布配置。
- `.nojekyll`：关闭 Jekyll 处理，确保静态文件原样发布。

## GitHub Pages

将本仓库上传到 GitHub 后：

1. 打开仓库 **Settings → Pages**。
2. 在 **Build and deployment** 中选择 **GitHub Actions**。
3. 推送到 `main` 后，工作流会自动发布网站。

预计访问地址：

`https://jiruiwang.github.io/chinese_calendar/`

## 更新方式

后续更新日曆时，替换：

- `index.html`
- `calendar/401-500.html`

然后提交并推送即可。
