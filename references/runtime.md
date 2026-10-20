# 独立制作流程

本包包含独立的项目初始化、音频导入、可选 TTS、时间轴、Remotion 模板与导出检查。不需要作者的 `ai-better` 或其他 Skill。已有成熟视频工程可以复用，但先核对等价的文字锁定、声音、动态预览与验收能力，不擅自改写既有工程。

## 路径与环境

将 `MINUTE_SKILL` 设为当前实际加载的技能包目录；`SHARED_VIDEO="$MINUTE_SKILL/assets/runtime/shared"`。项目在使用者自己的工作目录，默认 `videos/one-minute-<topic>/`；稿件默认 `docs/src/ai/one-minute/<topic>.md`。安装目录只读，所有 npm 依赖、音频、预览、日志和成片均在项目中。

需要 Node.js 22.20+、npm、Python 3.10+、FFmpeg（含 ffprobe）。Remotion 版本在模板 package.json 中固定；在项目 `remotion/` 运行 `npm install`，首次使用可能下载 Chromium。不要把 npm 或模型安装说成 Skill 安装已经执行。Windows 环境的符号链接可能需要开发者模式，无法创建时让使用者启用或改用经过核对的普通 public 目录同步方案，不虚称已支持。

下面各段是分阶段命令参考，不能一次顺序运行到底。

## ② 项目初始化、文字和声音

先读取源稿，明确提取可朗读正文到项目外的临时 `spoken.txt`，保留每个字词与标点，不自动凭正则猜测 Markdown 中哪些部分该念。初始化时传入这份文件；已有项目先读现状，不能再次初始化。

```bash
SHARED_VIDEO="$MINUTE_SKILL/assets/runtime/shared"
SOURCE="$PWD/docs/src/ai/one-minute/rrf.md"
PROJECT="$PWD/videos/one-minute-rrf"
python3 "$SHARED_VIDEO/tools/init_project.py" \
  --project "$PROJECT" --source "$SOURCE" --spoken /你的临时目录/spoken.txt --title "RRF"
```

`--config /你的配置/video.config.json` 可传入自己已有的配置；否则生成不含音色和服务地址的空配置，保留在 `project.json.config`。初始化不调用 TTS、不安装 npm、不覆盖旧项目。首次仅有一个完整 beat 是工程起点，应按完整意群拆分 `beats.json`，`chapters` 保持单个 `ch1`；拼接 `text` 必须等于 `spoken.txt` 去掉 CR/LF 的文本。

先由使用者选择声音，再锁定。配置至少包含：

```json
{
  "video": {"width": 1920, "height": 1080, "fps": 30},
  "tts": {
    "speakerId": "使用者自己的音色ID或导入声音标识",
    "resourceId": "",
    "apiBase": "",
    "speedRatio": 1.0,
    "atempo": 1.0,
    "audio": {"format": "mp3", "sampleRate": 24000}
  },
  "volc": {"apiKeyEnv": "VOLC_TTS_API_KEY"}
}
```

不要把示例中文标识当成实际音色 ID。导入现成音频时，`speakerId` 只是使用者提供的来源标签，不证明声纹身份；保留音频出处。无需填 resourceId、apiBase 或凭证，atempo=1，音频保持既定语速。TTS 模式则必须填写自己实际可用的服务参数。

```bash
python3 "$MINUTE_SKILL/scripts/one_minute.py" lock \
  --project "$PROJECT" --source "$SOURCE" --spoken "$PROJECT/spoken.txt"
```

锁定源稿、口播及当前声音配置，不包含密钥。经用户同意修改时先保存旧锁及原因，再用 `--replace`；不能为了检查通过而重锁未经同意的改稿。

### 方式 A：导入自己的配音（不调用云服务）

每个 beat 对应一份完整音频，先核对文字和声音，再按 ID 导入；长录音应从真实语音边界分段，不按均分秒数猜切点。转换为无损 PCM WAV，不改变语速。导入后的量时与拼接由同一份 PCM 生成。

```bash
python3 "$SHARED_VIDEO/tools/import_audio.py" \
  --project "$PROJECT" --id 1 --audio /你的音频/beat-1.wav
# 有多个 beat 时逐段导入，然后：
python3 "$SHARED_VIDEO/tools/gen_cues.py" --project "$PROJECT"
python3 "$MINUTE_SKILL/scripts/one_minute.py" check --project "$PROJECT"
```

### 方式 B：使用自己的兼容 TTS

`gen_audio.py` 是从二哥已使用的火山单向流式 SSE TTS 工具提取的适配器，**不是通用 OpenAI-compatible TTS 客户端**。只有 apiBase、speakerId、resourceId、响应协议与实际服务相符时使用；其他服务请使用现有客户端生成音频后走方式 A。设置凭证时按服务自己的文档操作，只读取 `volc.apiKeyEnv` 指定的环境变量，不打印值。项目级读音规则在 `assets/references/pronunciations.json` 中配置（格式同随包空词典）；默认词典为空，不能把别人的音色规则当作通用读法。

```bash
python3 "$SHARED_VIDEO/tools/gen_audio.py" --project "$PROJECT" --dry-run
# 核对配置与需求后，制作配音阶段才运行真实调用：
python3 "$SHARED_VIDEO/tools/gen_audio.py" --project "$PROJECT"
python3 "$SHARED_VIDEO/tools/gen_cues.py" --project "$PROJECT"
python3 "$MINUTE_SKILL/scripts/one_minute.py" check --project "$PROJECT"
```

`text` 是原文字幕；`ttsText` 仅作读音处理，不能借此改写含义。本包不附带私人音色，不自动训练或克隆声音。`atempo` 表示已选声音管线的固定处理参数，不能为了60秒目标提高；导入音频固定为1。

### 对齐和试听

`gen_cues.py` 给出真实 beat 的采样和帧边界，不等于逐字对齐。短句可以先按真实音频意群拆字幕；核心动画应按实际试听或自己已有的 ASR/forced-aligner 标注词语起点，记录方法与音频哈希。`align_words.py` 只提供能量片段，不能把它当作词语时间戳。

已有强制对齐结果时可复用 `build_timing.py`：在 `preview/ch1-forced-alignment.json` 写 `{model, units:[{id,audioSha256,items:[{text,start_time,end_time}]}]}`，时间是 beat 内秒数；在 `assets/references/ch1-spec.json` 定义逐句字幕和事件。脚本顶部包含格式细则。未运行 ASR 就报告未核查，不自动安装 Apple MLX 或下载模型，不宣称漏字检查已通过。

```bash
python3 "$SHARED_VIDEO/tools/build_timing.py" --project "$PROJECT" --chapter ch1
```

该轮交付完整 `build/voiceover.wav`、实测时长与待试听项，然后停下。超过60秒只报告，仍保留全文。

## ③ 分镜

用户推进后才写 `OUTLINE.md`。参考 [动画方法](motion.md) 的镜头表与布局规则，按真实音频设计，不实现下一阶段画面。配音未获确认时，不把“已生成”写成“已认可”。

## ④ 动画与动态预览

先按 [画面接入](huashu-runtime.md) 安装上游库。模板中的 `Scene.tsx` 是明确标注的工程占位；不能把它交付为完成视频。`Root.tsx` 已接真实音频与时长，但默认 beat 级字幕仍应按实际音频拆成完整、可读的短句。画面由 Agent 根据分镜写入 `Scene.tsx` 及其子模块。

```bash
python3 "$MINUTE_SKILL/scripts/install_huashu.py" --project "$PROJECT"
cd "$PROJECT/remotion"
npm install
node "$SHARED_VIDEO/tools/remotion.mjs" typecheck --project "$PROJECT"
```

`C` 从项目 `src/palette.ts` 导入。字体必须等待加载后绘制；默认画面保持在 y=890 以上，字幕独立于 Canvas 世界相机。记录 `assets/references/visual-provenance.json` 的上游 commit、真实调用的函数与场景用途。不能只贴方法名而没调用。

### Studio 必须后台启动

复用已确认属于本项目的可用服务，否则选择空闲端口后执行：

```bash
python3 "$MINUTE_SKILL/scripts/start_studio.py" \
  --shared-video "$SHARED_VIDEO" --project "$PROJECT" --port 3210
```

启动器立即返回 PID、日志和候选 URL；`starting` 不是已就绪。最多30秒内有限检查日志尾部、对应 PID/端口与有超时的 HTTP 请求，拿到实际 URL 后在使用者可访问的浏览器打开完整 Composition。检查播放时间、画面、字幕与音轨，暂停后保留服务供查看，再结束本阶段。不要等待常驻命令退出，不接 `head` 管道，不无限轮询。不终止其他项目占用的服务。

日志与状态在 `preview/studio/`。已有记录但服务失效时先核对 PID、项目与日志，保存旧记录再重试，不能循环拉起或覆盖诊断信息。只有静帧时记“关键帧已检查，动态预览待完成”，不能标④完成。浏览器在远端无法访问 localhost 时说明地址范围并使用可访问的预览方式，不能虚称本地链接对所有人可用。

## ⑤ 导出与验收

仅在用户推进到本阶段或明确授权连续出片时运行。若要用 `--detach`，检查返回的日志与产物，不重复启动。

```bash
node "$SHARED_VIDEO/tools/remotion.mjs" render --project "$PROJECT" --detach
# 渲染实际结束后：
python3 "$SHARED_VIDEO/tools/verify_export.py" --project "$PROJECT"
python3 "$MINUTE_SKILL/scripts/one_minute.py" check \
  --project "$PROJECT" --media "$PROJECT/output/one-minute-rrf.mp4"
```

输出名从 `project.json.outputName` 读取，RRF 仅为示例。导出工具将原始 WAV 重新封装到画面轨；`-t` 取实际完整时间轴长度而非固定60秒，末尾最多补不足一帧的静音，不截断配音。`verify_export.py` 检查全解码、帧数、尺寸与多个有声窗口的波形对应；仍要正常速度完整审片，不能用机械检查证明听感。

`one_minute.py check` 返回0表示机械检查通过；返回1表示文字、声音配置、媒体或时间轴不一致；返回2表示缺少实际音频/时间轴。超60秒以 warnings 和 overTargetSec 报告，不单独导致失败。必须披露未验证项，不为通过检查而删改源稿。
