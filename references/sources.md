# 来源与取舍

此独立版提取自二哥的一分钟课堂科普视频实践，分发时移除绝对路径、个人声音、头像与私人配置。它不要求使用者克隆作者的其他仓库。

## 花叔的画面能力

- 上游：[alchaincyf/huashu-art-motion](https://github.com/alchaincyf/huashu-art-motion)。随包固定版本：`8a0d7d72ca65fcce6f8ba82c4a6c8dfe35b8422c`。
- 实际提供 `util.js`、`motion.js`、`camera.js`、`diagram.js`、`t1_3b1b` 语法卡及三款字体。文件哈希见 `assets/huashu/provenance.json`，上游 MIT 与字体 OFL 许可原样保留。
- 采用对象动作、同例贯穿、连续形变、白板累积、有目的运镜、先验证核心画面的做法。画面默认用二哥色板，不沿用上游示范黑底；不复制作者角色、肖像或示范视频。
- 参考上游 `06-口播驱动的艺术短片` 与 `12-口播整片与经验回流`；前者为方法草案，不能说成已验证的完整生产流程。适配器只改变模块包装与依赖注入，算法归上游。
- 随包不是完整花叔引擎：依赖 PAINT/KIT 的画材功能没有默认提供，不能声称调用这些功能已经成功。按其他风格制作时按固定版本补齐相关依赖。

## 二哥的视频实践

- [itwanger/toBeBetterJavaer](https://github.com/itwanger/toBeBetterJavaer) 中的 `one-minute-remotion`、`ergo-remotion-video` 与写稿规范，以及 [itwanger/ai-better](https://github.com/itwanger/ai-better) 的共享视频工具。
- 保留源稿快照、声音配置锁定、整句意群、真实采样时间轴、字幕、原音频复用导出及波形/全解码检查。工具已在本包内提取并适配，不再查找作者机器上的路径或共享配置。
- 默认色板从 `ai-better` 的共享 `C` 提取，出处与版本见 `assets/palette.json`；不附带人物头像、私有音色、录音与密钥。使用者自己的声音优先。
- 不继承长片多章导航、营销尾段、固定长稿字数或其他 Skill 的安装要求。文字稿、配音、分镜、动态预览、正式出片分五阶段，“下一步”只推进一个阶段。
- RRF 实作反馈已形成通用规则：相关元素成组对齐、未命中保留身份、分组括号朝向对象、检查运动中间状态、主画面不复述字幕。

## 安装方式

标准 `SKILL.md` 目录可由支持该格式的 Agent 加载。终端示例依照 [Vercel Skills CLI](https://github.com/vercel-labs/skills) 的 `skills add`；没有列入其支持清单的宿主不声称能够自动安装，按其实际目录或 ZIP 导入机制处理。
