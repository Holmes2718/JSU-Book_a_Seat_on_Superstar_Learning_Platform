# ChaoXingLibrarySeatReservation
超星图书馆座位预约脚本


## 如何使用

> 为了安全，建议将你的真实配置保存在本地的 config.json 中，不要直接提交到 GitHub。仓库中提供了一个示例配置文件 config.example.json，可作为参考。

### 本地部署方式

#### 1、安装依赖

运行脚本前先安装一个包

```bash
pip install cryptography
```

如果有滑块验证，则需要额外安装numpy和opencv-python

```bash
pip install numpy, opencv-python
```

#### 2、 获取roomid（图书馆id）和seatid（座位号）

在使用之前需要先在如下获取图书馆对应的id和座位号，下面的配置里已经提供了上海大学图书馆的id。对于不知道id的，可以通过如下方式进行：

![获取图书馆id](./img/1.png)

在进入预约图书馆列表界面时断开网络，点击你想预约的图书馆的`选座`按钮，会提示网页无法打开，此时点击`右上角的三条杠`，选择`复制链接`，会得到类似这样的链接：

> https://office.chaoxing.com/front/apps/seat/select?id=5483&day=2023-10-12&backLevel=2&pageToken=0f46f3acc7be4c60862cb9815870ddfd

其中的`id=5483`的5483即为对应图书馆的id，将其填写到config.json中，座位联网后自己挑即可（详细填写参见后面的setting）

#### 3、running

复制一份配置文件并修改为你的实际信息：

```bash
copy config.example.json config.json
```

然后编辑 config.json，填写你的座位预约信息。

由于脚本是检测系统时间为7点时进行预约（在main.py 第16行），如果有特殊要求可以修改。通过 `python main.py` 运行脚本, 添加参数 `-u config.json` 来指明配置文件路径

运行`python main.py -m debug`可以立即运行查看配置是否正确。

关于运行的方式，现在提供了多种运行方式：

- Linux环境下：

在Linux下可以使用如下方式添加crontab , 运行：`crontab -e`添加指令 :`0 7 * * * python3 main.py`

- windows环境下：

windows下使用时间任务:

![windows下使用时间任务](./img/2.png)

### github actions部署方式（目前应该没有问题了）：

  这种方式可以不需要在本地部署环境，只需要把fork该仓库并修改配置文件即可。

1.**fork该仓库**

2.**修改config.json**：这个仿照之前的方式进行修改即可，但是注意，username和password请留空或者随便填以防止泄漏个人账号密码。（具体的需要填写在自己repo的settings中）。时间什么也是需要修改（修改到仓库中）不要忘记。

3.**配置账号密码**：在settings->secrets and variables->Repository secrets 创建两个secret keys。名称分别为USERNAMES，PASSWORDS，填写自己的账号和密码即可。（如果有多个用户，请使用,(英文逗号)隔开，如果密码中有逗号可能会出现问题）。

```
xxxxxxx,xxxxxxx
```

4.**运行action**：在action -> auto_reserve -> run workflows 选择main分支即可。


## config配置
之后编辑config.json并填写座位预约相关信息即可
```json
{
  // https://passport2.chaoxing.com/mlogin?loginType=1&newversion=true&fid=&  在这个网站查看是否可以顺利登陆 
  "reserve": [
    {
      "username": "XXXXXXXX",
      //账号
      "password": "XXXXXXXX",
      //密码
      "time": [
        "08:00",
        //预约的起始时间
        "22:00"
        //预约的结束时间
      ],
      "roomid": "2609",
      //图书馆id
      "seatid": "002",
      // 注意要用0补全至3位数，例如6号座位应该填006
      "daysofweek": [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday"
      ]
      //预约的星期
    },
    {
      "username": "xxxxxxxxxx",
      "password": "xxxxxxxxx",
      "time": [
        "20:00",
        "21:00"
      ],
      "roomid": "5483",
      "seatid": [
        "056"
      ],
      "daysofweek": [//预约的星期 没有参数就是预约所有星期
        "Saturday",
        "Sunday"
      ]
    }
  ],
  "mail": {//邮件配置
    "host": "smtp.qq.com",
    "port": 465,
    "secure": true,
    "auth": {
      "user": "xxxxxxxxxx@qq.com",
      "pass": "xxxxxxxxxxxxxxxx"
    }
  },
  "receivers": [//收件人列表
    "xxxxxxxxxx@qq.com"
  ]
}
```
参考前面的运行方式即可。


## 高级设置

在main.py中有四个参数可以选择

```python
SLEEPTIME = 0.2 # 每次抢座的间隔
ENDTIME = "07:01:00" # 根据学校的开始预约座位时间+1min即可

ENABLE_SLIDER = False # 是否有滑块验证，设置为True开启滑块验证
MAX_ATTEMPT = 4 # 最大尝试次数
```
可以直接进行修改，但是不建议把**SLEEPTIME**设置太小。

## 存在的问题
- {当前人数过多，请等待5分钟后尝试}。这种是请求方式错误或者请求键值错误导致的，通常是由于学习通更新了预约导致的
- 以字典格式输出的其他错误，仔细查看用户名密码，roomid和seatid是否填写正确。
- 

### 无法预约情况debug方式
> 1、电脑端访问："https://passport2.chaoxing.com/mlogin?loginType=1&newversion=true&fid=" 使用自己的用户名密码登录
> 2、电脑端访问：”https://office.chaoxing.com/front/third/apps/seat/code?id={图书馆id}&seatNum={座位id}“查看是否显示时间表
> 3、尝试预约看看是否会出现验证方式

源项目，从下面的链接改的
https://gitee.com/lcz2000/ChaoXingLibrarySeatReservation
