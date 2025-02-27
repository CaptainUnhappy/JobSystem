# 职位信息分析系统

## 项目简介
这是一个基于 Flask 开发的职位信息分析系统，提供以下功能：
- 用户登录注册
- 首页数据展示
- 职位精确查询
- 地图可视化
- 词云展示
- 实时数据
- 趋势分析
- 公司类型分析
- 贝叶斯预测

## 环境要求
- Python 3.7+
- MySQL 数据库
- Chrome 浏览器（用于爬虫）

## 🚀 快速开始 (Quick Start)

本节将指导您快速启动并运行本项目。请按照以下步骤操作：

**1. 创建并激活虚拟环境 (Create and Activate Virtual Environment)**

为了隔离项目依赖，强烈建议您创建一个虚拟环境。  
在项目根目录下，执行以下命令：

```bash
# 创建虚拟环境 (仅需执行一次)
    python -m venv venv

# 激活虚拟环境 (每次启动项目前都需要执行)
# 在 macOS/Linux 上：
source venv/bin/activate
# 在 Windows 上 (PowerShell)：
.\venv\Scripts\activate
# 在 Windows 上 (Command Prompt)：
venv\Scripts\activate
```

**2. 安装依赖包 (Install Dependencies)**

本项目的所有依赖包都列在 `requirements.txt` 文件中。  
在激活的虚拟环境中，执行以下命令安装所有依赖：
```bash
pip install -r requirements.txt
```

**3. 运行项目 (Run the Project)**

完成以上步骤后，您就可以运行本项目了。  

```bash
python app.py
# 或者
flask run
```


**4. 访问系统**
- 打开浏览器访问：http://localhost:5000
- 默认会跳转到登录页面：http://localhost:5000/login
- 首次使用需要注册账号 或 使用 账号/密码: admin/admin

<details>
  <summary>爬取数据 (可选)</summary>
如果需要最新数据，运行爬虫脚本：

**1. 创建数据库：**
```sql
CREATE DATABASE boss DEFAULT CHARACTER SET utf8mb4;
```

**2. 导入数据库表结构：**
`user.sql`
`jobs_info.sql`

**3. 修改数据库连接配置（utils/config.py）：**
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',     # 修改为您的数据库用户名
    'password': 'your_password', # 修改为您的数据库密码
    'database': 'boss',
    'charset': 'utf8mb4'
}
```

**4. 运行爬虫脚本**
```bash
python jobSpider.py
```
</details>

## 目录结构
```
├── app.py              # 主程序入口
├── jobSpider.py        # 爬虫程序
├── utils/             # 工具函数目录
│   ├── query.py      # 数据库查询
│   ├── utils.py      # 通用工具函数
│   ├── page_tool.py  # 分页工具
│   └── Bayes.py      # 贝叶斯模型
├── sqls/             # sql目录
│   ├── user.sql          # 用户表结构
│   ├── jobs_info.sql   # 职位信息表结构
├── templates/         # 模板文件目录
└── static/           # 静态文件目录
```

## 注意事项
1. 确保 MySQL 服务已经启动
2. 确保数据库连接配置正确
3. 建议使用虚拟环境运行项目
4. 首次运行需要有数据，可以通过导入示例数据或运行爬虫获取

# 图例

<details>
  <summary>系统架构流程图</summary>

```mermaid
flowchart TD
    A[用户] -->|访问| B[前端 （HTML/CSS/JavaScript）]
    B -->|请求| C[后端 （Python Flask）]
    C -->|操作| D[数据库 （MySQL）]
    subgraph 数据层
        D
    end
    subgraph 业务层
        C
    end
    subgraph 展示层
        B
    end
    C -->|调用| E[数据采集模块 （jobSpider.py）]
    C -->|调用| F[数据分析模块 （utils/）]
    C -->|渲染| G[可视化展示模块 （templates/）]
    E -->|存储| D
    F -->|查询| D
```

</details>

<details>
  <summary>核心模块时序图</summary>

```mermaid
sequenceDiagram
    participant 用户
    participant 前端
    participant 后端
    participant 数据库
    participant 数据采集模块
    participant 数据分析模块
    用户->>前端: 请求页面
    前端->>后端: 发送请求
    后端->>数据库: 查询数据
    数据库-->>后端: 返回数据
    后端->>数据分析模块: 调用分析函数
    数据分析模块-->>后端: 返回分析结果
    后端->>前端: 返回处理结果
    前端-->>用户: 渲染页面
    用户->>前端: 触发爬虫任务
    前端->>后端: 请求启动爬虫
    后端->>数据采集模块: 执行爬虫
    数据采集模块->>数据库: 存储爬取数据
    数据采集模块-->>后端: 爬虫完成
    后端-->>前端: 更新状态
    前端-->>用户: 显示更新结果
```

</details>

<details>
  <summary>核心模块类图</summary>

```mermaid
classDiagram
    class App {
        +handleRoutes()
        +renderPages()
        +authenticateUser()
    }
    class JobSpider {
        +crawlData()
        +cleanData()
        +storeData()
    }
    class Query {
        +executeQuery()
        +fetchResults()
    }
    class Utils {
        +processData()
        +analyzeTrends()
    }
    class Bayes {
        +trainModel()
        +predictOutcome()
    }
    App --> JobSpider : 调用
    App --> Query : 调用
    App --> Utils : 调用
    Utils --> Bayes : 包含
    JobSpider --> MySQL : 存储
    Query --> MySQL : 查询
```

</details>

<details>
  <summary>系统状态图</summary>

```mermaid
stateDiagram
    [*] --> 未登录
    未登录 --> 登录中 : 用户输入凭证
    登录中 --> 已登录 : 验证成功
    已登录 --> 数据查询 : 用户选择查询
    已登录 --> 可视化展示 : 用户查看图表
    已登录 --> 个性化分析 : 用户触发分析
    已登录 --> 未登录 : 用户登出
    数据查询 --> 已登录 : 返回主页
    可视化展示 --> 已登录 : 返回主页
    个性化分析 --> 已登录 : 返回主页
```

</details>

<details>
  <summary>文件目录树状图</summary>

```mermaid
graph TD
    Root[项目根目录] --> A[app.py]
    Root --> B[jobSpider.py]
    Root --> C[utils/]
    Root --> D[sqls/]
    Root --> E[templates/]
    Root --> F[static/]
    C --> C1[query.py]
    C --> C2[utils.py]
    C --> C3[Bayes.py]
    C --> C4[page_tool.py]
    E --> E1[index.html]
    E --> E2[map.html]
    E --> E3[word_cloud.html]
    E --> E4[realtime.html]
    E --> E5[trend.html]
    E --> E6[bayes.html]
```

</details>

<details>
  <summary>数据库关系图</summary>

```mermaid
erDiagram
    JOBS_INFO {
        varchar(500) job_id PK
        varchar(500) job_name
        varchar(500) salary
        varchar(500) degree
        varchar(500) categories
        varchar(500) major
        varchar(500) welfare
        varchar(500) head_count
        date publish_date
        date update_date
        varchar(500) source
        varchar(500) company_name
        varchar(500) area
        varchar(500) company_scale
        varchar(500) company_property
        INT num_id
    }
```

</details>

<details>
  <summary>数据流图</summary>

```mermaid
flowchart TD
    A[数据源 （网络爬虫）] --> B[数据采集模块 （jobSpider.py）]
    B -->|清洗和预处理| C[清洗后的数据]
    C -->|存储| D[MySQL 数据库 （jobs_info 表）]
    D -->|查询| E[数据分析模块 （utils/）]
    E -->|统计分析| F[分析结果]
    F -->|渲染| G[Web 应用模块 （app.py）]
    G -->|展示| H[可视化页面 （templates/）]
    subgraph 数据层
        D
    end
    subgraph 业务层
        B
        E
        G
    end
    subgraph 展示层
        H
    end
```

</details>

<details>
  <summary>核心功能分解图</summary>

```mermaid
mindmap
    root((职位信息分析系统))
        数据采集与存储
            职位信息爬取
            数据清洗
            MySQL 存储
        数据分析
            数据统计
            趋势分析
            贝叶斯预测
        可视化展示
            数据大盘
            地图展示
            词云图
            趋势图表
        用户功能
            账号管理
            数据查询
            个性化分析
```

</details>

<details>
  <summary>时序图 - 数据从采集到展示的流程</summary>

```mermaid
sequenceDiagram
    participant 爬虫模块
    participant 数据库
    participant 后端
    participant 前端
    participant 用户
    用户->>前端: 请求数据
    前端->>后端: 发送请求
    后端->>数据库: 查询 jobs_info 表
    数据库-->>后端: 返回查询结果
    后端->>前端: 处理并返回数据
    前端-->>用户: 渲染可视化页面
    用户->>前端: 触发爬虫任务
    前端->>后端: 请求启动爬虫
    后端->>爬虫模块: 执行爬虫
    爬虫模块->>数据库: 存储爬取数据
    爬虫模块-->>后端: 爬虫完成
    后端-->>前端: 更新状态
    前端-->>用户: 显示更新结果
```

</details>

<details>
  <summary>用户状态图</summary>

```mermaid
stateDiagram-v2
    [*] --> 未登录
    未登录 --> 登录中 : 用户输入凭证
    登录中 --> 已登录 : 验证成功
    已登录 --> 求职者功能 : 角色为求职者
    已登录 --> 企业招聘人员功能 : 角色为企业招聘人员
    已登录 --> 系统管理员功能 : 角色为系统管理员
    %% 求职者功能状态
    state 求职者功能 {
        查看职位信息 --> 数据查询 : 搜索职位
        数据查询 --> 查看职位详情 : 选择职位
        查看职位详情 --> 个性化分析 : 请求分析
        个性化分析 --> 可视化展示 : 查看趋势和预测
    }
    %% 企业招聘人员功能状态
    state 企业招聘人员功能 {
        发布职位信息 --> 数据录入 : 填写职位信息
        数据录入 --> 职位管理 : 编辑或删除职位
        职位管理 --> 数据概览 : 查看招聘数据
    }
    %% 系统管理员功能状态
    state 系统管理员功能 {
        系统监控 --> 数据采集 : 启动爬虫任务
        数据采集 --> 数据清洗 : 处理原始数据
        数据清洗 --> 数据存储 : 存入数据库
        数据存储 --> 数据分析 : 运行统计分析
        数据分析 --> 可视化配置 : 配置展示页面
    }
    %% 返回状态
    求职者功能 --> 已登录 : 返回主页
    企业招聘人员功能 --> 已登录 : 返回主页
    系统管理员功能 --> 已登录 : 返回主页
    已登录 --> 未登录 : 用户登出
```

</details>