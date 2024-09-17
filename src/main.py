import json, random, getopt, sys, time, os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By


def read_config():
    """"读取配置"""
    with open("config.json") as json_file:
        config = json.load(json_file)
        return config


def initialization_config(self):
    """"配置文件初始化"""
    file_path = "./config.json"  # 配置文件位置
    default_config = """{
  "display_windows": false, 
  "cookie_refresh": 30, 
  "user_name": "default", 
  "password": "root123", 
  "min_waiting_time": "0", 
  "max_waiting_time": "5", 
  "visited_user": "2", 
  "recommend_mod": "https://www.mcmod.cn/class/5253.html", 
  "uid": "2"
}"""  # 默认配置
    if os.path.exists(file_path):
        config = read_config()
        if self == 'del':
            os.remove(file_path)
            with open("config.json", 'w') as json_file:
                json_file.write(default_config)
                json_file.close()  # 写入默认设置
    else:
        with open("config.json", 'w') as json_file:
            json_file.write(default_config)
            json_file.close()
            sys.exit()  # 生成配置文件后关闭
    return config


def random_delay():
    """随机延时函数，用来模拟动作比较快的点击操作"""
    delay = random.uniform(float(min_waiting_time), float(max_waiting_time))
    time.sleep(delay)


def main(argv):
    globals().update(initialization_config('None'))
    try:
        opts, args = getopt.getopt(argv, "h", ["get_cookies", "create_config", "help"])
        if not opts:
            if os.path.exists('./cookies.json'):
                register()
            else:
                get_cookie()
        else:
            for opt, arg in opts:
                if opt == '-h':
                    print('--get_cookies    获取cookies\n--create_config  创建配置文件\n-h               显示命令参数')
                    sys.exit()
                elif opt in "--get_cookies":
                    get_cookie()
                elif opt in "--create_config":
                    initialization_config('del')
    except getopt.GetoptError:
        print('--get_cookies    获取cookies\n--create_config  创建配置文件\n-h               显示命令参数')  # 指令参数


def register():
    if time.time() - os.path.getmtime('./cookies.json') >= cookie_refresh * 24 * 60 * 60:
        get_cookie()  # cookie定期更新
    service = Service()
    options = Options()

    options.add_argument("--start-maximized")  # 启动时最大化窗口
    options.add_argument("--disable-blink-features=AutomationControlled")  # 使浏览器不显示自动化控制的信息
    # options.add_argument("--disable-gpu")  # 禁用GPU硬件加速
    if not display_windows:
        options.add_argument('--headless')  # 设置为无头
    options.add_argument("--disable-infobars")  # 隐藏信息栏
    options.add_argument("--disable-extensions")  # 禁用所有扩展程序
    options.add_argument("--disable-popup-blocking")  # 禁用弹出窗口拦截
    options.add_argument("--no-sandbox")  # 关闭沙盒模式（提高性能）
    options.add_argument("--disable-dev-shm-usage")  # 使用/dev/shm分区以避免共享内存问题
    options.page_load_strategy = 'normal'

    # 初始化 WebDriver，并传入 ChromeDriver Service
    driver = webdriver.Edge(service=service, options=options)

    with open("cookies.json", "r") as file:  # 读取cookie文件
        cookies = json.load(file)

    driver.get("https://mcmod.cn")

    for cookie in cookies:  # 注入cookie
        driver.add_cookie(cookie)
    random_delay()
    del cookie, cookies, file
    try:
        driver.get("https://center.mcmod.cn/"+str(uid)+"/#/task/")
        random_delay()
        driver.find_element(by=By.ID, value='task-check-in').click()  # 签到
        random_delay()
        driver.get(recommend_mod)
        random_delay()
        try:
            driver.find_element(by=By.CLASS_NAME, value='fc-button-label').click()
        except:
            time.sleep(0.01)
        try:
            driver.find_element(by=By.ID, value='dismiss-button').click()
        except:
            time.sleep(0.01)
        driver.find_element(by=By.CLASS_NAME, value='push').click()  # 推荐
        random_delay()
        driver.get("https://center.mcmod.cn/"+visited_user+"/")  # 窜门
        random_delay()
    finally:
        driver.close()


def get_cookie():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    if not display_windows:
        options.add_argument('--headless')  # 设置为无头
    driver = webdriver.Chrome(service=Service(), options=options)

    try:
        os.remove('cookies.json')
    finally:
        try:
            driver.get("https://www.mcmod.cn/login/")
            random_delay()
            driver.find_element(by=By.ID, value='login-username').send_keys(user_name)
            random_delay()
            driver.find_element(by=By.ID, value='login-password').send_keys(password)
            random_delay()
            driver.find_element(by=By.ID, value='login-remember').click()
            random_delay()
            driver.find_element(by=By.ID, value='login-action-btn').click()
            random_delay()
            driver.refresh()
            random_delay()
            driver.get("https://www.mcmod.cn")
            random_delay()
            # 获取登录后的 cookie
            cookies = driver.get_cookies()

            # 将 cookie 保存到文件
            with open("cookies.json", "w") as file:
                json.dump(cookies, file)
        finally:
            driver.quit()
        sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])
