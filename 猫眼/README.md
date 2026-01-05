# 猫眼电影爬虫 Web应用

这是一个基于Flask框架的Web应用，用于爬取猫眼电影排行榜数据。

## 功能特性

- 🕷️ **数据爬取**：使用正则表达式（re库）爬取猫眼电影排行数据
- 📊 **数据展示**：表格形式显示电影信息
- 💾 **数据导出**：支持CSV和TXT格式导出
- 🎨 **美观界面**：现代化的Web界面设计
- 🔄 **实时更新**：支持多次爬取和数据更新

## 项目结构

```
.
├── app.py                 # Flask应用主文件
├── requirements.txt       # Python依赖列表
├── README.md             # 项目说明文档
├── templates/
│   └── index.html        # HTML主页面
└── static/
    ├── style.css         # 样式表
    └── script.js         # JavaScript脚本
```

## 安装和运行

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动应用
```bash
python app.py
```

### 3. 打开浏览器
访问 `http://127.0.0.1:5000`

## 使用说明

1. **爬取数据**：点击"开始爬取数据"按钮，系统会从猫眼电影网站爬取电影排行数据
2. **查看结果**：爬取完成后，数据会以表格形式展示
3. **导出数据**：
   - 点击"导出为CSV"按钮将数据保存为CSV文件
   - 点击"导出为TXT"按钮将数据保存为TXT文件
4. **清空数据**：点击"清空数据"按钮清除已爬取的数据

## API端点

### POST /api/scrape
执行爬虫，爬取猫眼电影数据

**响应：**
```json
{
  "success": true,
  "message": "成功爬取10部电影数据",
  "data": [...],
  "count": 10
}
```

### GET /api/data
获取当前已爬取的数据

**响应：**
```json
{
  "data": [...],
  "count": 10
}
```

### POST /api/export/csv
导出数据为CSV文件

### POST /api/export/txt
导出数据为TXT文件

## 技术栈

- **后端框架**：Flask 2.3.2
- **HTTP库**：requests 2.31.0
- **前端**：HTML5 + CSS3 + Vanilla JavaScript
- **数据解析**：正则表达式（re库）
- **文件格式**：CSV、TXT

## 爬虫说明

### 爬取流程
1. 向猫眼电影排行榜网址发送GET请求
2. 使用正则表达式匹配HTML中的电影信息块
3. 从每个块中提取排名、名称、评分和上映时间
4. 将数据保存到内存并返回给前端

### 正则表达式模式
```python
# 电影信息块的匹配模式
movie_blocks = re.findall(
    r'<div class="board-item-content">(.*?)</div>\s*</div>\s*</li>',
    html_content,
    re.DOTALL
)

# 从块中提取各个字段
- 排名：r'<i class="board-index board-index-\d+">.*?(\d+)'
- 名称：r'<p class="p-name"><a[^>]*title="([^"]*)"'
- 评分：r'<i class="score">([^<]*)</i>'
- 时间：r'<p class="p-release">(\d{4}-\d{2}-\d{2})</p>'
```

## 错误处理

应用包含完整的错误处理机制：
- ✅ 网络连接错误
- ✅ 请求超时处理（10秒）
- ✅ HTML解析失败处理
- ✅ 文件导出失败处理

## 注意事项

1. 首次运行需要安装依赖包
2. 需要网络连接来爬取数据
3. 爬取速度受网络影响
4. 建议不要过于频繁爬取（尊重网站服务器）
5. 爬取的数据仅供学习使用

## 快捷键

- **Ctrl+S** 或 **Cmd+S**：导出为CSV
- **Ctrl+E** 或 **Cmd+E**：导出为TXT

## 许可证

本项目仅供学习和教学使用。

## 作者

学生：郑显龙
学号：240593038
