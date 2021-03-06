
# self-status-page

Build a status page with just one command. and only one output file.

- Demo: [https://self-status-page.phyng.com/](https://self-status-page.phyng.com/)
- Docker Hub [https://hub.docker.com/r/phyng/self-status-page](https://hub.docker.com/r/phyng/self-status-page)
- [中文简体文档](https://github.com/phyng/self-status-page/blob/main/README_CN.md)

## Quick start

```bash
docker run --rm -ti -p 8081:80 \
  -e STATUS_EXAMPLE_NAME=Example \
  -e STATUS_EXAMPLE_TYPE=http \
  -e STATUS_EXAMPLE_URL=http://www.example.com/ \
  phyng/self-status-page:latest
```

open [http://localhost:8081/](http://localhost:8081/) and everything is OK.

## Productized deployment

If you need to use more complex configuration and persistent history, you can create a `data` folder and mount it inside the container.
At the same time, it supports to manage the configuration through `data/config.env`, and then start it with the following command

```bash
# replace /path/to/data to you absolute path
docker run -d --restart always \
  -p 8081:80 \
  --name self-status-page \
  -v /path/to/data:/usr/src/app/data \
  phyng/self-status-page:latest
```

You can refer to the `data/config.env` file.

## Advanced Config

Since the environment variables are flat and the key cannot be repeated, we implement the complex configuration by using unique key for the environment variables. The following configuration file examples follow the following rules

- Use `STATUS_<taskId>_NAME` to declare a detection task, set the task type by `STATUS_<taskId>_TYPE`, and set the task attributes for other `STATUS_<taskId>_*`
- Use `STATUSGROUP_{groupId}_NAME` to declare a task group, use `STATUSGROUP_{taskId}_TASKS` to set the task ID under the group, ungrouped tasks are classified as `SERVICES` group by default

```bash
# declare a task with ID EXAMPLE, of type http
STATUS_EXAMPLE_NAME=Example
STATUS_EXAMPLE_TYPE=http
STATUS_EXAMPLE_URL=http://www.example.com/

STATUS_GITHUB_NAME=Github
STATUS_GITHUB_TYPE=http
STATUS_GITHUB_URL=https://github.com/

# declare the Search group, including two tasks BING and GOOGLE_DNS
STATUSGROUP_SEARCH_NAME=Search
STATUSGROUP_SEARCH_TASKS=BING,GOOGLE_DNS

# declare ping task
STATUS_GOOGLE_DNS_NAME=Google DNS
STATUS_GOOGLE_DNS_TYPE=ping
STATUS_GOOGLE_DNS_IP=8.8.8.8

STATUS_BING_NAME=Bing
STATUS_BING_TYPE=http
STATUS_BING_URL=https://bing.com/
```

## Other config

```bash
STATUS_CONFIG_TIMEOUT=10
STATUS_CONFIG_INTERVAL=30
STATUS_CONFIG_TITLE=Self status page
STATUS_CONFIG_TITLE_BACKGROUND=#607d8b
```

## Features

- One command: docker one-click creation
- One file: generate a `data/index.html` file regularly to facilitate integration and deployment
- Support for multiple types of detection tasks
- Support task grouping
- Support history

## Roadmap

- [x] schedule runner
  - [x] config parser
  - [x] log
  - [x] build
- [x] docker deployment
- [x] detection task
  - [x] http
  - [x] ping
  - [x] shell
- [x] advanced config
  - [x] title/background
  - [x] timeout/interval
- [ ] ui
  - [x] task group
  - [ ] history list
  - [ ] charts
