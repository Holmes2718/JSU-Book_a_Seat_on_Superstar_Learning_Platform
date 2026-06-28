# -*- coding: utf-8 -*-
from .encrypt import AES_Encrypt, enc, generate_captcha_key, verify_param
import json
import requests
import re
import time
import logging
import datetime
from urllib3.exceptions import InsecureRequestWarning


def get_date(day_offset: int = 0):
    today = datetime.datetime.now().date()
    offset_day = today + datetime.timedelta(days=day_offset)
    tomorrow = offset_day.strftime("%Y-%m-%d")
    return tomorrow


class reserve:
    def __init__(
        self,
        sleep_time=0.2,
        max_attempt=10,
        enable_slider=False,
        reserve_next_day=False,
    ):
        # API 端点
        self.login_page = "https://passport2.chaoxing.com/mlogin?loginType=1&newversion=true&fid="
        self.url = "https://office.chaoxing.com/front/third/apps/seat/code?id={}&seatNum={}"
        self.submit_url = "https://office.chaoxing.com/data/apps/seat/submit"
        self.login_url = "https://passport2.chaoxing.com/fanyalogin"
        
        # 预约结果存储
        self.token = ""
        self.success_results = []  # 存储所有成功的预约结果
        # 配置读取
        config = json.load(open("config.json", encoding="utf-8"))
        self.mail_config = config.get("mail", {})
        self.receivers = config.get("receivers", [])
        
        # HTTP 会话
        self.requests = requests.session()
        self.token_pattern = re.compile("token = '(.*?)'")
        self.headers = {
            "Referer": "https://office.chaoxing.com/",
            "Host": "captcha.chaoxing.com",
            "Pragma": "no-cache",
            "Sec-Ch-Ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Linux"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        }
        self.login_headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "cache-control": "no-cache",
            "Connection": "keep-alive",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.3 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1 wechatdevtools/1.05.2109131 MicroMessenger/8.0.5 Language/zh_CN webview/16364215743155638",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "passport2.chaoxing.com",
        }

        # 参数设置
        self.sleep_time = sleep_time
        self.max_attempt = max_attempt
        self.enable_slider = enable_slider
        self.reserve_next_day = reserve_next_day
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def _get_page_token(self, url, require_value=False):
        """获取预约页面的 token 和加密值"""
        response = self.requests.get(url=url, verify=False)
        html = response.content.decode("utf-8")
        
        # 从 hidden input submit_enc 中提取 token
        matches = re.findall(r'id="submit_enc"\s+value="(.*?)"', html)
        value_matches = re.findall(r'value="(.*?)"', html) if require_value else None
        
        if not matches:
            logging.error(f"Failed to get token from {url}")
            return "", ""
        if require_value and not value_matches:
            logging.error(f"Failed to get submit value from {url}")
            return matches[0], ""
            
        return matches[0] if matches else "", value_matches[0] if value_matches else ""

    def get_login_status(self):
        """获取登录状态（初始化会话）"""
        self.requests.headers = self.login_headers
        self.requests.get(url=self.login_page, verify=False)

    def login(self, username, password):
        username = AES_Encrypt(username)
        password = AES_Encrypt(password)
        parm = {
            "fid": -1,
            "uname": username,
            "password": password,
            "refer": "http%3A%2F%2Foffice.chaoxing.com%2Ffront%2Fthird%2Fapps%2Fseat%2Fcode%3Fid%3D4219%26seatNum%3D380",
            "t": True,
        }
        jsons = self.requests.post(url=self.login_url, params=parm, verify=False)
        obj = jsons.json()
        if obj["status"]:
            logging.info(f"用户 {username} 登录成功")
            return (True, "")
        else:
            logging.info(
                f"用户 {username} 登录失败。请检查您的密码和用户名! "
            )
            return (False, obj["msg2"])

    def roomid(self, encode):
        """列出所有可用的房间及座位信息"""
        url = f"https://office.chaoxing.com/data/apps/seat/room/list?cpage=1&pageSize=100&firstLevelName=&secondLevelName=&thirdLevelName=&deptIdEnc={encode}"
        json_data = self.requests.get(url=url).content.decode("utf-8")
        ori_data = json.loads(json_data)
        for i in ori_data["data"]["seatRoomList"]:
            info = f'{i["firstLevelName"]}-{i["secondLevelName"]}-{i["thirdLevelName"]} id为: {i["id"]}'
            print(info)

    def resolve_captcha(self):
        """解析滑块验证码"""
        logging.info("开始解析验证码")
        captcha_token, bg, tp = self.get_slide_captcha_data()
        logging.info(f"已获取验证码令牌")
        
        # 计算滑块距离
        x = self.x_distance(bg, tp)
        logging.info(f"滑块距离: {x}px")

        # 提交验证码结果
        params = {
            "callback": "jQuery33109180509737430778_1716381333117",
            "captchaId": "42sxgHoTPTKbt0uZxPJ7ssOvtXr3ZgZ1",
            "type": "slide",
            "token": captcha_token,
            "textClickArr": json.dumps([{"x": x}]),
            "coordinate": json.dumps([]),
            "runEnv": "10",
            "version": "1.1.18",
            "_": int(time.time() * 1000),
        }
        response = self.requests.get(
            f"https://captcha.chaoxing.com/captcha/check/verification/result",
            params=params,
            headers=self.headers,
        )
        text = response.text.replace(
            "jQuery33109180509737430778_1716381333117(", ""
        ).replace(")", "")
        data = json.loads(text)
        logging.info(f"验证码验证完成")
        try:
            validate_val = json.loads(data["extraData"])["validate"]
            return validate_val
        except KeyError as e:
            logging.info("无法加载验证值。可能服务器返回错误.")
            return ""

    def get_slide_captcha_data(self):
        url = "https://captcha.chaoxing.com/captcha/get/verification/image"
        timestamp = int(time.time() * 1000)
        capture_key, token = generate_captcha_key(timestamp)
        referer = f"https://office.chaoxing.com/front/third/apps/seat/code?id=3993&seatNum=0199"
        params = {
            "callback": f"jQuery33107685004390294206_1716461324846",
            "captchaId": "42sxgHoTPTKbt0uZxPJ7ssOvtXr3ZgZ1",
            "type": "slide",
            "version": "1.1.18",
            "captchaKey": capture_key,
            "token": token,
            "referer": referer,
            "_": timestamp,
            "d": "a",
            "b": "a",
        }
        response = self.requests.get(url=url, params=params, headers=self.headers)
        content = response.text

        data = content.replace(
            "jQuery33107685004390294206_1716461324846(", ")"
        ).replace(")", "")
        data = json.loads(data)
        captcha_token = data["token"]
        bg = data["imageVerificationVo"]["shadeImage"]
        tp = data["imageVerificationVo"]["cutoutImage"]
        return captcha_token, bg, tp

    def x_distance(self, bg, tp):
        """计算滑块验证码的水平距离（使用图像匹配）"""
        import numpy as np
        import cv2

        def cut_slide(slide):
            """剪裁滑块图像"""
            slider_array = np.frombuffer(slide, np.uint8)
            slider_image = cv2.imdecode(slider_array, cv2.IMREAD_UNCHANGED)
            slider_part = slider_image[:, :, :3]
            mask = slider_image[:, :, 3]
            mask[mask != 0] = 255
            x, y, w, h = cv2.boundingRect(mask)
            cropped_image = slider_part[y : y + h, x : x + w]
            return cropped_image

        c_captcha_headers = {
            "Referer": "https://office.chaoxing.com/",
            "Host": "captcha-b.chaoxing.com",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        }
        
        # 下载背景和滑块图像
        bgc, tpc = self.requests.get(bg, headers=c_captcha_headers), self.requests.get(tp, headers=c_captcha_headers)
        bg, tp = bgc.content, tpc.content
        
        # 图像处理：边界检测和模板匹配
        bg_img = cv2.imdecode(np.frombuffer(bg, np.uint8), cv2.IMREAD_COLOR)
        tp_img = cut_slide(tp)
        bg_edge = cv2.Canny(bg_img, 100, 200)
        tp_edge = cv2.Canny(tp_img, 100, 200)
        bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
        tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2RGB)
        
        # 匹配滑块位置
        res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(res)
        
        return max_loc[0]

    def _split_times(self, start_time, end_time, max_hours=5):
        """将超过max_hours的时间段切分成多个子段"""
        def to_minutes(t):
            h, m = map(int, t.split(":"))
            return h * 60 + m

        def to_str(m):
            return f"{m // 60:02d}:{m % 60:02d}"

        start_min = to_minutes(start_time)
        end_min = to_minutes(end_time)
        if end_min <= start_min:
            end_min += 24 * 60  # 跨天

        total_min = end_min - start_min
        max_min = max_hours * 60

        if total_min <= max_min:
            return [(start_time, end_time)]

        segments = []
        cur = start_min
        while cur < end_min:
            nxt = min(cur + max_min, end_min)
            segments.append((to_str(cur), to_str(nxt)))
            cur = nxt
        return segments

    def submit(self, times, roomid, seatid, action):
        """提交预约请求"""
        start_time, end_time = times[0], times[1]
        
        # 切分超过5小时的时间段
        segments = self._split_times(start_time, end_time)
        if len(segments) > 1:
            logging.info(f"时段长度超过5小时，切分为 {len(segments)} 段")

        # 逐个座位、逐个时段提交预约
        for seat in seatid:
            for seg_start, seg_end in segments:
                suc = False
                attempt = self.max_attempt
                
                # 重试逻辑
                while not suc and attempt > 0:
                    # 获取预约页面的token和加密参数
                    token, value = self._get_page_token(
                        self.url.format(roomid, seat), require_value=True
                    )
                    
                    # 如果启用滑块验证则解析验证码
                    captcha = self.resolve_captcha() if self.enable_slider else ""
                    
                    # 提交预约
                    suc = self.get_submit(
                        self.submit_url,
                        times=[seg_start, seg_end],
                        token=token,
                        roomid=roomid,
                        seatid=seat,
                        captcha=captcha,
                        action=action,
                        value=value,
                    )
                    
                    if suc:
                        logging.info(f"✓ 时段 {seg_start}~{seg_end} 预约成功")
                        break
                    
                    # 重试等待
                    time.sleep(self.sleep_time)
                    attempt -= 1
                if not suc:
                    logging.error(f"时段 {seg_start}~{seg_end} 预约失败，跳过后续时段")
                    return False
        return True

    def get_submit(
        self, url, times, token, roomid, seatid, captcha="", action=False, value=""
    ):
        """提交预约表单并处理响应"""
        # 计算预约日期
        delta_day = 1 if self.reserve_next_day else 0
        day = datetime.date.today() + datetime.timedelta(days=delta_day)
        if action:
            day += datetime.timedelta(days=1)  # GitHub Action 时区调整
        
        # 构建预约参数
        parm = {
            "roomId": roomid,
            "startTime": times[0],
            "endTime": times[1],
            "day": str(day),
            "seatNum": seatid,
            "captcha": captcha,
            "token": token,
            "type": "1",
            "verifyData": "1",
        }
        
        logging.info(f"提交预约 - 房间:{roomid} 座位:{seatid} 时间:{times[0]}-{times[1]} 日期:{day}")
        
        # 加密参数并发送请求
        parm["enc"] = verify_param(parm, value)
        html = self.requests.post(url=url, params=parm, verify=True).content.decode("utf-8")
        result = json.loads(html)
        
        # 处理预约结果
        if result["success"]:
            seat_info = result['data']['seatReserve']
            start_time = times[0]
            end_time = times[1]
            logging.info(f"✓ 预约成功 - 座位:{seat_info['seatNum']} {start_time}~{end_time}")
            
            # 保存成功结果用于后续邮件
            self.success_results.append({
                'seatNum': seat_info['seatNum'],
                'startTime': start_time,
                'endTime': end_time,
                'roomId': roomid,
                'day': str(day)
            })
        else:
            logging.info("✗ 预约失败")

        return result["success"]

    def send_all_results_email(self):
        """发送合并的邮件（包含所有成功的预约）"""
        if not self.success_results:
            logging.info("没有成功的预约，不发送邮件")
            return
        
        import smtplib
        from email.mime.text import MIMEText
        from email.header import Header

        # 构建邮件内容
        email_lines = ["超星图书馆预约座位成功！", " " * 60]
        for idx, result in enumerate(self.success_results, 1):
            email_lines.append(f"预约 {idx}:")
            email_lines.append(f"  房间代号: {result['roomId']}")
            email_lines.append(f"  座位: {result['seatNum']}")
            email_lines.append(f"  时间: {result['startTime']} ~ {result['endTime']}")
            email_lines.append(f"  日期: {result['day']}")
            email_lines.append(" " * 60)

        email_content = "\n".join(email_lines)
        
        # 发送邮件
        try:
            message = MIMEText(email_content, "plain", "utf-8")
            message["From"] = Header(self.mail_config["auth"]["user"])
            message["To"] = Header(",".join(self.receivers))
            message["Subject"] = Header(f"超星图书馆预约座位成功 - 共{len(self.success_results)}条")

            smtpObj = smtplib.SMTP_SSL(self.mail_config["host"], self.mail_config["port"])
            smtpObj.login(self.mail_config["auth"]["user"], self.mail_config["auth"]["pass"])
            smtpObj.sendmail(self.mail_config["auth"]["user"], self.receivers, message.as_string())
            logging.info("✓ 邮件发送成功")
        except smtplib.SMTPException as e:
            logging.error(f"✗ 邮件发送失败: {str(e)}")