# Moonshot AI API 配置指南

本项目使用 **Moonshot AI (Kimi) 国内 API**，API 端点：`https://api.moonshot.cn/v1`

## 获取 API Key

1. 访问 [Moonshot AI 开放平台](https://platform.moonshot.cn/)
2. 注册并登录账户
3. 在左侧导航栏选择 **"API Key 管理"**
4. 点击 **"新建"** 生成新的 API Key
5. **重要**: 请妥善保存该 Key，因为它只会显示一次

## 配置方式

### 方式 1: 使用环境变量（推荐）

1. 复制 `.env.example` 为 `.env`：
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，填入您的 API Key：
   ```
   MOONSHOT_API_KEY=sk-your-api-key-here
   ```

### 方式 2: 使用配置文件

编辑 `config.yaml` 文件，在 `moonshot.api_key` 字段填入您的 API Key：

```yaml
moonshot:
  api_key: "sk-your-api-key-here"
  base_url: "https://api.moonshot.cn/v1"
  model: "moonshot-v1-8k"
  ...
```

## 模型选择

Moonshot AI 提供多种模型，根据论文长度选择合适的模型：

- **moonshot-v1-8k**: 支持 8K 上下文，适合短论文
- **moonshot-v1-32k**: 支持 32K 上下文，适合中等长度论文
- **moonshot-v1-128k**: 支持 128K 上下文，适合长论文和完整分析

在 `config.yaml` 中修改 `model` 字段即可切换模型。

## API 兼容性

本项目使用 **OpenAI SDK** 调用 Moonshot API，因为 Moonshot API 完全兼容 OpenAI API 设计。

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-api-key",
    base_url="https://api.moonshot.cn/v1"  # 国内端点
)
```

## 测试连接

配置完成后，可以运行以下命令测试 API 连接：

```bash
python src/main.py analyze papers/your_paper.pdf --type summary
```

如果配置正确，将看到论文分析结果。

## 费用说明

Moonshot AI API 按使用量计费，具体定价请参考：
- [定价与计费](https://platform.moonshot.cn/docs/guide/pricing)

## 优化建议

### 1. 使用 Context Caching（上下文缓存）

如果需要对同一篇论文进行多次查询，可以使用 Context Caching 功能来降低成本：

- 参考文档: [Context Caching 正式公测](https://platform.moonshot.cn/blog/posts/context-caching)

### 2. 合理选择模型

- 短论文（< 8K tokens）: 使用 `moonshot-v1-8k`
- 中等论文（8K-32K tokens）: 使用 `moonshot-v1-32k`
- 长论文（> 32K tokens）: 使用 `moonshot-v1-128k`

### 3. 调整参数

在 `config.yaml` 中可以调整：
- `temperature`: 控制输出随机性（0.0-2.0），较低值更精确
- `max_tokens`: 最大生成 token 数，根据需求调整

## 常见问题

### Q: API Key 在哪里获取？

A: 访问 [Moonshot AI 开放平台](https://platform.moonshot.cn/)，在 "API Key 管理" 中创建。

### Q: 为什么使用国内 API？

A: 国内 API 端点 (`api.moonshot.cn`) 访问速度更快，延迟更低，适合国内用户使用。

### Q: 支持哪些模型？

A: 支持所有 Moonshot AI 模型，包括 8K、32K、128K 上下文版本。

### Q: API 调用失败怎么办？

A: 
1. 检查 API Key 是否正确
2. 检查网络连接
3. 查看错误信息，确认是否超出配额或限制
4. 参考 [官方文档](https://platform.moonshot.cn/docs/guide/start-using-kimi-api)

## 参考资源

- [Moonshot AI 开放平台](https://platform.moonshot.cn/)
- [快速入门指南](https://platform.moonshot.cn/blog/posts/kimi-api-quick-start-guide)
- [API 文档](https://platform.moonshot.cn/docs/guide/start-using-kimi-api)
- [定价与计费](https://platform.moonshot.cn/docs/guide/pricing)
