
# self-status-page

一条命令创建一个状态展示页面网站。

## 快速开始

```bash
docker run --rm -ti -p 8081:80 \
  -e STATUS_EXAMPLE_NAME=Example \
  -e STATUS_EXAMPLE_TYPE=http \
  -e STATUS_EXAMPLE_URL=http://www.example.com/ \
  phyng/self-status-page:latest
```

打开 [http://localhost:8081/](http://localhost:8081/) 即可看到网站。

## 产品化部署

如果需要使用更复杂的配置以及持久化历史记录，可以创建一个 `data` 文件夹挂载到容器内部，
同时支持通过 `data/config.env` 管理配置，然后通过以下命令启动

```bash
docker run -d -p 8081:80 --name self-status-page -v /path/to/data:/usr/src/app/data phyng/self-status-page:latest
```

可以参考 `data/config.env` 文件。

## 高级配置

因为环境变量是扁平化且名称不能重复，所以我们通过为环境变量带上唯一名称的方式实现只用环境变量就能实现复杂的配置，下面的配置文件例子遵循以下规则

- 使用 `STATUS_<taskId>_NAME` 声明一个检测任务，通过 `STATUS_<taskId>_TYPE` 设置任务类型，其他 `STATUS_<taskId>_*` 设置任务属性
- 使用 `STATUSGROUP_{groupId}_NAME` 声明一个任务分组，使用 `STATUSGROUP_{taskId}_TASKS` 设定分组下的任务 ID，未分组任务默认归类为 `SERVICES` 分组

```bash
# 声明 ID 为 EXAMPLE 的任务，类型为 http
STATUS_EXAMPLE_NAME=Example
STATUS_EXAMPLE_TYPE=http
STATUS_EXAMPLE_URL=http://www.example.com/

STATUS_GITHUB_NAME=Github
STATUS_GITHUB_TYPE=http
STATUS_GITHUB_URL=https://github.com/

# 声明 Search 分组，包含 BING 和 GOOGLE_DNS 两个任务
STATUSGROUP_SEARCH_NAME=Search
STATUSGROUP_SEARCH_TASKS=BING,GOOGLE_DNS

# 声明 ping 任务
STATUS_GOOGLE_DNS_NAME=Google DNS
STATUS_GOOGLE_DNS_TYPE=ping
STATUS_GOOGLE_DNS_IP=8.8.8.8

STATUS_BING_NAME=Bing
STATUS_BING_TYPE=http
STATUS_BING_URL=https://bing.com/
```

## 特点

- 一条命令：docker 一键创建
- 一个文件：最终会生成一个 `data/index.html` 文件，方便集成部署
- 多种类型的检测任务支持
- 支持任务分组和时间检测
- 支持历史记录
