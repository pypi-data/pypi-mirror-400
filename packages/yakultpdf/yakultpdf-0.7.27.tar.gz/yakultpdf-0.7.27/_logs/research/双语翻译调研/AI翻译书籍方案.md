# AI 翻译英文书籍/长文为中文方案

## 现有系统分析

### 当前 Typst 格式分析
当前文件 `/Users/fangjun/python/mark2pdf/_working/in/bi.typ` 采用简单的键值对格式：

```typst
#let data = (
  (cn: "这是一个示例。", en: "This is an example."),
  (cn: "Typst 很好用。", en: "Typst is very useful.")
)
```

**局限性**:
- 缺乏元数据支持
- 不支持版本控制
- 无翻译质量标记
- 难以处理长文本分段

## AI 翻译解决方案

### 推荐 API 选择

1. **OpenAI GPT-4/GPT-3.5**
   - 优点：上下文理解强，支持复杂文本
   - 成本：$0.01-0.03/1K tokens
   - 适合：高质量文学翻译

2. **Google Cloud Translation**
   - 优点：专业翻译引擎，稳定可靠
   - 成本：$20/百万字符
   - 适合：技术文档批量翻译

3. **DeepL API**
   - 优点：翻译质量极高
   - 成本：€5.99/百万字符起
   - 适合：追求最佳质量的场景

### 成本优化策略
- 技术文档：Google Translation + GPT 润色
- 文学作品：GPT-4 直接翻译
- 批量处理：Google Translation 为主

## 最佳存储格式设计

### JSON 格式（推荐）
```json
{
  "metadata": {
    "original_language": "en",
    "target_language": "zh",
    "translation_engine": "openai-gpt-4",
    "translation_date": "2024-01-15",
    "version": "1.0",
    "quality_score": 0.95
  },
  "segments": [
    {
      "id": "seg_001",
      "original": "This is the original English text.",
      "translation": "这是翻译后的中文文本。",
      "context": "introduction",
      "confidence": 0.92,
      "notes": "术语需要确认"
    }
  ]
}
```

### 文件组织结构
```
translations/
├── books/
│   ├── book-title/
│   │   ├── metadata.json
│   │   ├── segments.json
│   │   └── versions/
│   │       └── v1.0.json
├── cache/
│   └── raw-api-responses/
└── quality-assessments/
```

## 三种显示模式实现

### 1. 中文版 (Chinese Only)
```typst
#let chinese-data = (
  "这是翻译后的中文内容。",
  "这是第二段中文翻译。"
)

#for text in chinese-data {
  #par(justify: true, text)
}
```

### 2. 中英对照版 (Bilingual)
```typst
#let bilingual-data = (
  (cn: "中文内容", en: "English content"),
  (cn: "更多中文", en: "More English")
)

#for pair in bilingual-data {
  #block(
    width: 100%,
    stroke: 0.5pt,
    [
      #strong("中文:") #pair.cn \
      #strong("English:") #pair.en
    ]
  )
}
```

### 3. 英文版 (English Only)
```typst
#let english-data = (
  "Original English text.",
  "Second paragraph in English."
)

#for text in english-data {
  #par(justify: true, text)
}
```

## 技术实现流程

### 翻译处理流水线
1. **文本预处理**: 分段、清理、标记
2. **API 调用**: 批量翻译处理
3. **后处理**: 术语统一、格式调整
4. **质量评估**: 自动 + 人工校验
5. **存储**: JSON 格式持久化

### 集成到现有系统
```python
# 在现有 PDF 处理流程中加入翻译步骤
def process_with_translation(input_file, output_format="bilingual"):
    text = extract_text(input_file)
    segments = segment_text(text)
    translated = translate_segments(segments)
    
    if output_format == "chinese":
        return generate_chinese_output(translated)
    elif output_format == "bilingual":
        return generate_bilingual_output(translated)
    else:
        return generate_english_output(segments)
```

## 推荐实施方案

1. **第一阶段**: 实现基础翻译功能，使用 JSON 存储
2. **第二阶段**: 添加质量评估和版本管理
3. **第三阶段**: 实现高级显示模式和交互功能

**优先采用 JSON 存储格式**，便于扩展和工具集成，同时保持与现有 Typst 系统的兼容性。