# LuLu 词典单词笔记生成器

一个全面的 Python 项目，可以使用 Google 的 Gemini AI 自动生成详细的单词笔记，并无缝地管理您的欧陆词典单词列表。

## ✨ 功能特色

- 📚 **智能单词检索** 从 LuLu 词典 API 获取单词并支持过滤
- 🤖 **AI 驱动的笔记生成** 使用 Gemini AI 包括：
  - 清晰的定义和含义  
  - 词性识别
  - 发音指南（IPA 音标）
  - 语境示例句子
  - 常见搭配和短语
  - 词源和单词起源
  - 记忆技巧辅助
- 📝 **自动笔记上传** 回传到 LuLu 词典
- ⚡ **双重处理模式**：批处理（快速）和单独处理（仔细）
- 🛡️ **智能过滤** 跳过已有笔记的单词
- 🕐 **速率限制** 可配置的 API 调用延迟保护
- 🔧 **统一库架构** 便于重用和自定义
- 📊 **全面结果跟踪** 详细的成功/失败报告

## 📁 项目结构

```
LuLuDictOperator/
├── main.py                    # 批处理模式入口点
├── update_notes.py            # 单独处理模式入口点  
├── examples.py                # 使用示例和演示
├── config.py                  # 集中配置管理
├── keys.json                  # API 密钥配置文件 (需要创建)
├── keys.json.example          # API 密钥配置模板
├── requirements.txt           # Python 依赖
├── setup.sh                   # 安装和设置脚本
├── src/
│   ├── word_processor.py      # 🆕 统一的 WordNoteProcessor 库
│   ├── luludict/
│   │   └── client.py          # LuLu 词典 API 客户端
│   └── gemini/
│       └── tools.py           # Gemini AI 笔记生成器（带速率限制）
├── test/
│   └── test_gemini.py         # 测试文件
├── README.md                  # 本文件
└── README_LIBRARY.md          # 详细的库文档
```

## 🚀 快速设置

### 1. 克隆和安装

```bash
git clone <repository-url>
cd LuLuDictOperator

python -m venv venv
```

激活环境，然后安装依赖。

```bash
pip install -r requirements.txt
```

### 2. 配置 API 密钥

**重要：为了避免 API 密钥泄露，本项目使用 `keys.json` 文件存储敏感信息**

1. 复制配置模板：
```bash
cp keys.json.example keys.json
```

2. 编辑 `keys.json` 文件，填入您的 API 密钥：
```json
{
    "Gemini": "your_gemini_api_key_here",
    "LuLuDict": "your_luludict_token_here",
    "DeepSeek": "deepseek_api"
}
```

   - 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
   - 访问 [DeepSeek](https://platform.deepseek.com/api_keys)
   - 访问 [欧陆词典](https://my.eudic.net/OpenAPI/Authorization)

**注意**: `keys.json` 文件已被添加到 `.gitignore` 中，不会被提交到版本控制系统。

## 🎯 使用方法

### 选项 1：快速开始 - 批处理模式（推荐）

```bash
python main.py
```

**功能说明：**
- 从 LuLu 词典检索您的单词列表
- 为没有现有笔记的单词生成笔记
- 以高效的批次处理单词
- 一次性上传所有笔记
- 将结果保存到 `word_notes_results.json`

### 选项 2：细致处理 - 单独模式

```bash
python update_notes.py
```

**功能说明：**
- 逐个处理每个单词
- 更好的错误恢复和详细进度
- 跳过失败的单词并继续处理
- 适合大数据集或不稳定的网络连接

### 选项 3：使用库进行高级操作

```python
from src.word_processor import create_processor_from_config, save_results

# 使用配置快速设置
processor = create_processor_from_config()

# 批处理（快速）
results = processor.process_word_notes(
    max_words=20,
    processing_mode="batch",
    gemini_delay=3.0,
    skip_existing_notes=True
)

# 单独处理（仔细）
results = processor.process_word_notes(
    max_words=10,
    processing_mode="individual", 
    gemini_delay=5.0
)

# 处理特定单词
specific_words = ["serendipity", "ubiquitous", "ephemeral"]
results = processor.process_specific_words(specific_words)

# 保存结果
save_results(results)
```

## 📈 结果和输出

### 批处理模式结果
```json
{
    "total_words_processed": 10,
    "notes_generated": 8,
    "successful_uploads": 7,
    "failed_uploads": 1,
    "upload_results": {...},
    "word_notes": {...}
}
```

### 单独模式结果  
```json
{
    "total_words_processed": 10,
    "notes_generated": 8,
    "successful_uploads": ["word1", "word2"],
    "failed_uploads": ["word3"],
    "existing_notes": ["word4", "word5"],
    "word_notes": {...}
}
```

## 🔍 生成笔记示例
单词 figure 的笔记
```
#用法
1. N. 数字，数目。代表数量、顺序等的符号。
e.g. in figures (用数字表示)
e.g. sales figures (销售数据)
e.g. budget figures (预算数据)
e.g. unemployment figures (失业数据)
e.g. Write the amount in words and figures.
2. N. 人物。指一个特定的人，尤指重要或有名望的人。
e.g. high-profile/prominent/public/historical/political figure
e.g. She's a leading figure in the fashion world.
e.g. a stick figure (火柴人, 简笔画小人)
3. N. 身材，体形。指人的身体的形状或轮廓。
e.g. a slim/slender/full figure (苗条的/丰满的身材)
e.g. She has a slender figure.
4. N. 图形，图表。用于说明信息或数据的视觉表示。
e.g. Please refer to Figure 3 for more details.
5. VT. 认为，估计。在思考后得出结论或判断。
e.g. figure in (考虑在内, 参与)
e.g. figure on (指望, 预计)
e.g. I figured he'd be late.
6. VT. 计算。通过数学运算确定数量。
e.g. figure out (弄懂, 算出)
e.g. Can you figure out the total cost?
7. VI. 出现，扮演角色。在某事中起到作用或参与。
e.g. figure prominently (显著地出现)
e.g. He figures prominently in the story.

#联想
1.形近词/音近词:
finger /ˈfɪŋɡər/ (n. 手指；v. 用手指触摸)
disfigure /dɪsˈfɪɡjər/ (v. 损毁...的外形)

2.近义词:
figure (n. 数字, 人物, 身材, 图形；v. 认为, 计算, 出现): 含义广泛，作为名词可以指代数字、人物、图形或体形；作为动词可以表示思考、计算或在某事中扮演角色。
number /ˈnʌmbər/ (n. 数字, 数量): 主要指用来计数或表示数量的符号或概念。
digit /ˈdɪdʒɪt/ (n. 数字, 位): 特指阿拉伯数字0到9中的任一个。

3. 反义词:
ignore /ɪɡˈnɔr/ (v. 忽视) (与 figure '认为' 相对)
unknown /ˌʌnˈnoʊn/ (n. 未知数) (与 figure '数字' 相对)

4. 同根词/派生词
figuration /ˌfɪɡjəˈreɪʃən/ (n. 形状, 图案)
figurative /ˈfɪɡjərətɪv/ (adj. 比喻的, 象征的)
figuring /ˈfɪɡjərɪŋ/ (n. 计算, 估计)

5. 其他联想词:
chart /tʃɑrt/ (n. 图表)
diagram /ˈdaɪəˌɡræm/ (n. 图解)
```

## 🛠️ 高级功能

### 智能单词过滤
- 自动跳过已有笔记的单词
- 通过 `skip_existing_notes` 参数可配置
- 节省时间和 API 调用

### 速率限制保护
- 内置 API 调用间延迟
- 两个 API 都可配置延迟
- 防止违反速率限制

### 错误恢复
- 单独模式在失败时继续处理
- 详细的错误报告和日志
- 优雅处理网络问题

### 灵活输出
- 带详细统计的 JSON 结果
- 可配置的输出文件位置
- 易于与其他工具集成

## 🤝 贡献

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 进行更改
4. 为新功能添加测试
5. 确保所有测试通过 (`python -m pytest test/`)
6. 提交拉取请求

## 📄 许可证

本项目仅供教育和个人使用。请尊重 API 使用条款和速率限制。
