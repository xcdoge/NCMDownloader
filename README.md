# NCMDownloader

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![PyNCM](https://img.shields.io/badge/powered%20by-PyNCM-lightgrey.svg)

NCMDownloader 是一个高效的网易云音乐下载工具，支持下载歌曲、专辑封面，并自动为音频文件添加完整的元数据标签。使用 Python 编写，简单易用，功能强大。

## 功能特点

- 🎶 一键下载
- 🖼️ 自动下载高清专辑封面
- 📝 为音频文件添加完整的元数据标签 (标题、艺术家、专辑、年份等) 
- 📋 支持批量下载
- 🛡️ 自动创建配置文件，用户友好

## 技术栈

- **核心库**: [PyNCM](https://github.com/mos9527/pyncm) - 网易云音乐 Python 接口
- **辅助API**: [落月API](https://doc.vkeys.cn/api-doc) - 用于获取歌曲下载链接

## 安装与使用

### 前置要求

- Python 3.11+
- 网易云音乐账号 (用于获取相关ID)

### 安装步骤

1. 克隆仓库：

   ```bash
   git clone https://github.com/xcdoge/NCMDownloader.git
   cd NCMDownloader
   ```

2.  (推荐) 创建虚拟环境

   **Windows**

   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

   **MacOS/Linux**

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

4. 配置歌单：
   - 首次运行选择模式 (目前支持歌单、专辑) 后，会自动创建相关文件
   - 打开文件添加ID (每行一个) 

   ```
   # 示例：
   123456789
   554127866
   1145141919810
   ```

### 使用方法

激活虚拟环境，运行主程序：

**Windows**

```bash
.\venv\Scripts\activate
python main.py
```

**MacOS/Linux**

```bash
source venv/bin/activate
python main.py
```

程序会自动：

1. 读取相关文件中的ID

2. 下载所有歌单中的歌曲至目录 `songs/`
3. 下载专辑封面至目录 `covers/`
4. 为音频文件添加元数据标签

注: 
下载目录及更多详细配置可自行在 `config/config.toml` 中自行调整

### 获取ID

1. 打开网易云音乐网页版: [网易云音乐官网](https://music.163.com/)
2. 登录账号
3. 进入需要下载的页面
4. 从URL中复制ID

## 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 项目仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 许可证

本项目采用 [MIT License](LICENSE) 开源。

## 免责声明

本项目仅用于学习和研究目的，请勿用于商业用途。下载的音乐版权归原作者所有，请在下载后24小时内删除。使用本软件产生的一切后果由使用者承担。

---

**快乐下载，享受音乐！** 🎧
