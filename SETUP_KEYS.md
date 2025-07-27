# API 密钥配置说明

## 🔐 安全配置指南

为了保护您的 API 密钥不被意外泄露到版本控制系统中，本项目使用 `keys.json` 文件来存储敏感信息。

## 📋 配置步骤

### 1. 创建密钥文件

```bash
# 复制示例文件
cp keys.json.example keys.json
```

### 2. 编辑 keys.json 文件

使用您喜欢的文本编辑器打开 `keys.json` 文件：

```bash
nano keys.json
# 或
vim keys.json
# 或
code keys.json
```

### 3. 填入您的 API 密钥

```json
{
    "gemini_api_key": "您的_Gemini_API_密钥",
    "luludict_token": "您的_LuLu词典_令牌"
}
```

## 🔑 获取 API 密钥

### Gemini API 密钥
1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 使用您的 Google 账户登录
3. 点击 "Create API Key"
4. 复制生成的 API 密钥
5. 将其粘贴到 `keys.json` 的 `gemini_api_key` 字段

### LuLu 词典令牌
1. 登录您的 LuLu 词典账户
2. 访问 API 设置页面
3. 获取您的访问令牌
4. 将其粘贴到 `keys.json` 的 `luludict_token` 字段

## ✅ 验证配置

运行以下命令验证您的配置：

```bash
python -c "from config import Config; print('✅ 配置有效' if Config.validate() else '❌ 配置无效')"
```

## 🛡️ 安全最佳实践

- ✅ **永远不要** 将 `keys.json` 文件提交到 Git
- ✅ `keys.json` 已添加到 `.gitignore` 中
- ✅ 定期轮换您的 API 密钥
- ✅ 不要在代码中硬编码密钥
- ✅ 使用环境变量作为备选方案

## 🔄 环境变量备选方案

如果您更喜欢使用环境变量：

```bash
# 设置环境变量
export GEMINI_API_KEY="您的_Gemini_API_密钥"
export LULUDICT_TOKEN="您的_LuLu词典_令牌"

# 添加到您的 shell 配置文件（~/.bashrc 或 ~/.zshrc）
echo 'export GEMINI_API_KEY="您的_Gemini_API_密钥"' >> ~/.bashrc
echo 'export LULUDICT_TOKEN="您的_LuLu词典_令牌"' >> ~/.bashrc
```

## 🔍 故障排除

### 常见错误

1. **文件不存在错误**
   ```
   ⚠️ Warning: keys.json file not found. Please create it from keys.json.example
   ```
   **解决方案**: 运行 `cp keys.json.example keys.json`

2. **JSON 格式错误**
   ```
   ❌ Error: keys.json file is not valid JSON format
   ```
   **解决方案**: 检查 JSON 语法，确保引号和逗号正确

3. **密钥验证失败**
   ```
   ❌ 错误：未设置 Gemini API 密钥
   ```
   **解决方案**: 检查 `keys.json` 中的密钥是否正确填写

### 重新加载配置

如果您更新了 `keys.json` 文件，可以重新加载配置：

```python
from config import Config
Config.reload_keys()
```

## 📞 获取帮助

如果您在配置过程中遇到问题：

1. 检查 `keys.json.example` 文件格式
2. 验证您的 API 密钥是否有效
3. 确保文件权限正确
4. 查看项目的详细文档 `README.md`
