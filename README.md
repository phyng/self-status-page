
# self-status-page

Build a status page with just one config file and one output file.

## How to run

Create a `docker-compose.yml` as config file (or download this):

```yaml
version: '3'
services:
  self-status-page:
    image: 'phyng/self-status-page:latest'
    environment:
      # use STATUS_<id>_NAME to config multiple task
      - STATUS_GITHUB_NAME=Github
      - STATUS_GITHUB_TYPE=http
      - STATUS_GITHUB_URL=https://github.com/
      # you can use config type: http/ping/shell ...
      - STATUS_GOOGLE_DNS_NAME=Google DNS
      - STATUS_GOOGLE_DNS_TYPE=ping
      - STATUS_GOOGLE_DNS_IP=8.8.8.8
      # you can group tasks, the default group is 'services'
      - STATUSGROUP_SERVICES_NAME=Services
      - STATUSGROUP_SERVICES_TASKS=GITHUB,GOOGLE_DNS
```

## Why self-status-page

- Just one config file
- Just one output file `index.html`, so you can simply deploy to any environment
- Support service group and response time and history data
- Support `http/ping/shell` check method

## How it works

- Use python to run parse rule and run
- Use Nginx to server html file
- Use ofelia as job scheduler
- Use json to save history data

## Advanced Config

```yaml
id
name
type
```

### type: url

```yaml
url
method
```

### type: ping

```yaml
ip
```

### type: shell

```
cmd
```

## other

```bash
timeout 10 ping -c 1 baidu.com | tail -n 1 | awk '{print $4}' | cut -d'/' -f1
```
