# Sihao Chen / mijinmo — Portfolio

中文优先、完整英文版本的静态作品集，继续部署于 GitHub Pages。保留原来的 HTML5 UP Massively 视觉风格：摄影背景、白色内容区、原字体与按钮。无需安装 npm 或 Python 第三方依赖。

## 编辑与预览

**较长的文字内容全部放在 `content/` 中。** 优先阅读 [文案编辑指南](content/README.md)。例如“关于我”：中文编辑 `content/zh/pages/about.md`，英文编辑 `content/en/pages/about.md`。

需要 Python 3.12 或更新版本：

```sh
python scripts/build.py
python scripts/check.py
python scripts/serve.py
```

本地预览：<http://127.0.0.1:4173/Mijinmo_Portfolio/>。启动时自动构建，保存 Markdown 后自动生成页面并刷新浏览器。也可使用 `npm run build`、`npm run check` 和 `npm run dev`。

- `content/zh/`、`content/en/`：按 pages、projects、research、articles 分类的双语 Markdown 正文。
- `site/content.py`：个人资料、项目名/日期/分类/图片/链接、科研标题、美术作品清单等短字段。双语字段依次为中文与英文。
- `scripts/build.py`：共享页面模板与静态生成器。
- `assets/css/main.css`：原版样式，保持不变。`assets/css/content.css` 仅补充新内容的布局、响应式与可访问性支持；`assets/js/portfolio.js` 提供分类筛选增强。

新增项目时，在 `PROJECTS` 添加一个条目，类别使用 `commercial`、`indie` 或 `experimental`。`archived=True` 表示学生作品已停止维护；不要将维护状态与商店是否仍可访问混为一谈。项目链接可以使用双语配对。无外部链接的项目不显示空按钮。

首页精选项为数据中的 Kwyjibo Adventure 与 Exp10sion，工作经历为 Arknights。调整首页精选逻辑时同步检查 `scripts/check.py`。

## GitHub Pages

根目录 `index.html` 为中文，`en/` 为英文。同页语言切换及所有资源都使用相对路径，兼容 `https://mijinmo.github.io/Mijinmo_Portfolio/`。

生成的 HTML 与源文件一起纳入版本控制。修改源文件后运行 build 和 check，将生成结果一并提交，再沿用仓库现有的 GitHub Pages 发布设置；本次改版不修改托管配置。

旧页面保留静态跳转，包括 `index_cn.html`、`index_2.html`、`Blogs.html`、`publicans.html`、`neuroscience.html`、`course_project.html` 与 `alt_games.html`。原模板示例 `ref.html` 也跳转首页；旧文章中的错误地址 `blog8.html` 跳转到文章。

正文在构建时生成，没有 JavaScript 时仍可访问。自动刷新脚本仅由本地预览服务注入，不写入发布的 HTML。MOV 视频为旧项目原始格式，浏览器不支持播放时可下载原文件。

Markdown 使用项目内附带的 Python-Markdown 3.8.2（`scripts/vendor/`），无需额外安装；原许可证随包保留。支持常用 Markdown、代码块和表格。

## 内容来源与维护约定

- 鹰角：用户确认于 2025 年 7 月正式入职，在《明日方舟》任关卡策划。只公开概述，不展示具体设计、角色名称或关卡截图。
- Kwyjibo Adventure：用户确认担任 Producer，负责主要设计及大量代码。游戏简介、2025-04-07 发售时间及封面于 2026-09-06 从 Steam 公共 API 核实；来源保存在 `site/content.py` 的 `SOURCES` 中。
- Scented Days：采用原发表页面的 CHI PLAY 2024 与 ACM DOI；旧 DIS 稿件保留但明确标为早期稿件。
- 学生项目均停止维护。CS 地图仍存在兼容问题。
- 原简历 PDF 保留但不作为最新简历推广。历史图片和文件没有删除，新页面不引用具体鹰角设计截图。

沿用原 HTML5 UP 模板、样式和脚本，并保留许可证 `LICENSE.txt` 与署名。
