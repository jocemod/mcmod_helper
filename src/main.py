import getopt
import os
import random
import sys
import time
import requests
import json
import re

file_path = "./config.json"  # 配置文件位置
config = {
    'username': 'root',
    'password': 'root1234',
    'Visited_id': '2',
    'pushed_mod_id': '2',
    'random_time_interval': '1,10',
    'max_retries': 5,
    'cookie_refresh': 30,
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
}
header = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Host': 'www.mcmod.cn',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': "Windows",
}


def main(argv):
    """主函数"""
    if os.path.exists(file_path):
        global config
        global header
        with open("config.json") as json_file:
            config = json.load(json_file)
        header.update({'user-agent': config['user-agent']})
    else:
        with open("config.json", 'w') as json_file:
            json_file.write(json.dumps(config, indent=""))
            json_file.close()
            sys.exit()  # 生成配置文件后关闭
    try:
        opts, args = getopt.getopt(argv, "h", ["get_cookies", "create_config", "help"])
        if not opts:
            if os.path.exists('./Cookie'):
                if time.time() - os.path.getmtime('./cookies.json') >= config['cookie_refresh'] * 86400:
                    login()
            else:
                login()
            with open("Cookie") as cookie_file:
                data = json.loads(cookie_file.read())
                header.update({
                    'Cookie': data['Cookie']
                })
                push()
                random_delay(None)
                user_check_in(data=data['nCenterID'])
                random_delay(None)
                view()
        else:
            for opt, arg in opts:
                if opt == '-h':
                    print('--get_cookies    获取cookies\n--create_config  创建配置文件\n-h               显示命令参数')
                    sys.exit()
                elif opt in "--get_cookies":
                    login()
                elif opt in "--create_config":
                    os.remove(file_path)
                    with open("config.json", 'w') as json_file:
                        json_file.write(json.dumps(config))
                        json_file.close()  # 写入默认设置
                        sys.exit(1)
    except getopt.GetoptError:
        print('--get_cookies    获取cookies\n--create_config  创建配置文件\n-h               显示命令参数')  # 指令参数


def random_delay(self: list | None):
    """随机延时函数，用来模拟动作比较快的点击操作"""
    min_waiting_time, max_waiting_time = str(config['random_time_interval']).split(',')
    if type(self) is list:
        min_waiting_time = self[0]
        max_waiting_time = self[1]
    else:
        pass
    sleep_time = random.uniform(float(min_waiting_time), float(max_waiting_time))
    time.sleep(sleep_time)
    return sleep_time


def retry():
    """重试函数"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for i in range(config['max_retries']):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"第{i+1}次尝试失败: {e}睡眠" + str(random_delay(None)) + "秒")
            print("重试失败...")
            sys.exit(0)
        return wrapper
    return decorator


@retry()
def login():
    """登陆函数,生成cookie"""
    header.update({
        'Origin': 'https://www.mcmod.cn',
        'Referer': 'https://www.mcmod.cn/login/',
    })
    data = ("data=%7B%22username%22%3A%22" + config['username'] + "%22%2C%22password%22%3A%22"
            + config['password'] + "%22%2C%22remember%22%3A1%2C%22captcha%22%3A%22%22%7D")
    dologin = requests.post(url='https://www.mcmod.cn/action/doLogin/', headers=header, data=data)
    del data
    with open("Cookie", 'w') as cookie_file:
        match = re.search(r"MCMOD_SEED=([\w\d]+);.*_uuid=([\w\d-]+);", str(dologin.headers))
        header.update({
            'Cookie': f"MCMOD_SEED={match.group(1)}" + ";" + f"_uuid={match.group(2)}",
            'Origin': '',
        })
        dologin = requests.get(url='https://www.mcmod.cn/login/', headers=header)
        match2 = re.search(r"/(\d+)/$", dologin.url)
        content = {
            "Cookie": f"MCMOD_SEED={match.group(1)}" + ";" + f"_uuid={match.group(2)}",
            "nCenterID": f"{match2.group(1)}",
        }
        cookie_file.write(json.dumps(content, indent=""))
        cookie_file.close()  # 写入cookie


@retry()
def user_check_in(data):
    """签到函数"""
    header.update({
        'Host': 'center.mcmod.cn',
        'Origin': 'https://center.mcmod.cn',
        'Referer': 'https://center.mcmod.cn/205548/',
    })
    dousercheckin = requests.post(url=f'https://center.mcmod.cn/action/doUserCheckIn/', headers=header, data=f'nCenterID={data}')
    print(dousercheckin.content)


@retry()
def view():
    header.update({
        'Origin': 'https://center.mcmod.cn',
        'Referer': 'https://center.mcmod.cn/205548/',
    })
    print(requests.get(url=f"https://center.mcmod.cn/{config['Visited_id']}/#/home/", headers=header).content)


@retry()
def push():
    """推荐函数"""
    header.update({
        'Origin': 'https://www.mcmod.cn',
        'Referer': 'https://www.mcmod.cn/class/10065.html',
    })
    doclass = requests.post(url=f'https://www.mcmod.cn/action/doClass/',
                            data=f"data=%7B%22todo%22%3A%22push%22%2C%22cid%22%3A{config['pushed_mod_id']}%7D",
                            headers=header)
    print(doclass.content)

if __name__ == "__main__":
    main(sys.argv[1:])
