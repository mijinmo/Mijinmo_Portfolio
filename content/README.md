# 文案编辑指南

修改这里的 Markdown 文件并保存。运行本地预览时，页面会在约 1–2 秒内自动更新并刷新，不需要手动运行构建。

## 文件夹

`zh` 是中文，`en` 是英文；两者目录结构完全相同，分别维护，不会自动翻译。

| 文件位置（以中文为例） | 对应网页内容 |
| --- | --- |
| [zh/pages/about.md](zh/pages/about.md) | 关于我：个人介绍正文 |
| [zh/pages/about-intro.md](zh/pages/about-intro.md) | 关于我：顶部简介 |
| [zh/pages/about-timeline.md](zh/pages/about-timeline.md) | 关于我：右侧经历摘要 |
| [zh/pages/home-intro.md](zh/pages/home-intro.md) | 首页开场介绍 |
| [zh/pages/projects-intro.md](zh/pages/projects-intro.md) | 全部作品页说明 |
| [zh/projects/kwyjibo.md](zh/projects/kwyjibo.md) | Kwyjibo Adventure 介绍、职责与备注 |
| `zh/projects/*.md` | 每个项目的说明、个人贡献和备注，一项目一文件 |
| `zh/research/*.md` | 每项科研/课程项目的正文 |
| [zh/articles/journey.md](zh/articles/journey.md) | 《风之旅人》镜头分析全文 |
| `zh/pages/*-intro.md` | 各页面顶部介绍 |
| `zh/pages/*-note.md` | 归档或维护状态的补充说明 |
| [zh/pages/journey-summary.md](zh/pages/journey-summary.md) | 文章列表中的摘要 |
| [zh/pages/site-description.md](zh/pages/site-description.md) | 搜索引擎页面描述，不是正文 |

同一项目在首页、作品列表或研究页面出现时，共用同一个 Markdown 文件，改一次即可同步更新。

项目名、时间、分类、图片、外链、邮箱和维护状态开关等短字段仍在 `site/content.py`。新增文件不会自动创建新项目，需在该文件登记项目及其 ID；现有文件可自由修改正文。

## Markdown 写法

```md
这是一段正文。**加粗**、*斜体*、[链接](https://example.com) 都可以使用。

空一行开始新的段落。

## 小标题

- 列表第一项
- 列表第二项

> 补充说明，例如项目当前的兼容问题。
```

支持标题、段落、列表、引用、行内代码、代码块和表格。正文小标题建议从 `##` 开始，网页已经提供一级标题。行末两个空格表示手动换行；普通换行会合并为同一段落。

站内页面链接写成 `[关于](about.html)`，会留在当前语言。资源链接写成 `[文件](Files/文件名.pdf)` 或 `![说明](images/图片名.png)`；英文页会自动处理资源路径。图片请写清说明文字。

## 本地与正式网站

启动预览一次：

```sh
python scripts/serve.py
```

然后打开 <http://127.0.0.1:4173/Mijinmo_Portfolio/>，以后保存 Markdown 即自动更新。更新失败时保留上一次成功页面并显示错误，修复并保存后恢复。

GitHub Pages 仍是静态网站，**本地保存不会直接修改线上网站**。预览会自动生成 HTML；将 Markdown 和生成的 HTML 一起提交并推送后，沿用 GitHub Pages 的发布流程。未启动预览时，发布前运行 `python scripts/build.py`。

请勿直接编辑生成的 HTML，下一次保存 Markdown 时它会被重新生成。
