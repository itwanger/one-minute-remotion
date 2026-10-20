# 第三方文件与依赖

- `assets/huashu/{util,motion,camera,diagram}.js`、`references/grammar-t1_3b1b.md` 与从花叔方法改写的内容：来自 alchaincyf/huashu-art-motion，commit `8a0d7d72ca65fcce6f8ba82c4a6c8dfe35b8422c`，Copyright © 2026 alchaincyf（花叔 · 花生），MIT。原许可保存在 `assets/huashu/LICENSE` 和 `references/upstream-LICENSE.txt`。
- `assets/huashu/fonts/NotoSansSC-500.woff`：Noto Sans SC（GB2312 子集）；`cmunrm.woff`、`cmunti.woff`：Computer Modern Unicode。沿用 SIL OFL 1.1，原字体归属、来源与全文见 `assets/huashu/fonts/LICENSES.md`、`OFL.txt`。上游说明中列出的其他字体没有随包附带。
- `assets/runtime/shared/tools/` 部分工具提取并改写自 itwanger/ai-better 的视频工作流；由本仓库作者提供并按本仓库 MIT 许可分发。配置与个人素材没有随工具提取。
- Remotion、React、TypeScript 等由使用者安装的 npm 依赖遵循各自许可；本仓库不打包 node_modules。Remotion 许可：https://www.remotion.dev/license 。

哈希列表在 `assets/huashu/provenance.json`。原始第三方文件不为格式检查或换色而修改；适配、色板与场景在独立代码中处理。
