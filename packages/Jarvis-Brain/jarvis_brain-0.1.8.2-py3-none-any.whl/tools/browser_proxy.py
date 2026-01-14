import threading
from collections import deque
import time
from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage._pages.chromium_tab import ChromiumTab
from DrissionPage._units.listener import DataPacket
from typing import Tuple, Optional
import json

one_turn_max_token = 20000


class DPProxyClient:
    def __init__(self, driver: ChromiumTab, self_kill=False):
        self.tab_id = driver.tab_id
        self.driver = ChromePageProxy(driver, self)
        self.thread = None
        self.self_kill = self_kill
        # self.packet_list = []
        self.packet_queue = deque()

    def get_driver(self, start_listen, count=None, timeout=10) -> ChromiumTab:
        """
        获取代理后的driver、tab
        :param start_listen: 若你自己写的代码里已经使用自动化框架监听发包的功能了，则该值应该置为False。若没监听，则必须将该值置为True
        :param count: 需捕获的数据包总数，为None表示无限
        :param timeout: 两个数据包之间等待的最大时长（秒），为None表示无限，默认为10秒
        :return:
        """
        if start_listen:
            self.driver.listen.set_targets(res_type="XHR")
            self.driver.listen.start()
            self.thread = threading.Thread(target=self.start_listen, args=(count, timeout,))
            self.thread.start()
        return self.driver

    def start_listen(self, count=None, timeout=10):
        for _ in self.driver.listen.steps(count=count, timeout=timeout, gap=1):
            pass

    # 每次调用函数，都从队列的左端弹出一个数据包
    def pop_first_packet(self):
        if self.packet_queue:
            result = self.packet_queue.popleft()
            return json.dumps(result, ensure_ascii=False)
        else:
            return None


class DPProxyClientManager:
    """浏览器池管理器 - 使用单例模式"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.tab_pool = {}
        return cls._instance

    def create_client(self, tab: ChromiumTab, self_kill=False) -> Tuple[str, DPProxyClient, ChromiumTab]:
        """创建新的tab页面代理实例"""
        client = DPProxyClient(tab, self_kill=self_kill)
        tab = client.get_driver(True)
        tab_id = tab.tab_id
        self.tab_pool[tab_id] = {"client": client, "driver": tab}
        return tab_id, client, tab

    def get_client(self, tab_id: str) -> Optional[DPProxyClient]:
        """根据端口获取浏览器实例"""
        return self.tab_pool.get(tab_id).get("client", None)

    def remove_client(self, tab_id: str) -> Tuple[bool, Optional[ChromiumPage]]:
        """根据端口移除浏览器实例"""
        client = self.tab_pool.pop(tab_id, None)
        return client is not None, client

    def list_clients(self) -> list[int]:
        """列出所有活跃的浏览器端口"""
        return list(self.tab_pool.keys())


class ChromePageProxy:
    def __init__(self, page, client=None):
        self.__dict__['page'] = page
        self.__dict__['client'] = client

    def __getattr__(self, item):
        attr = getattr(self.page, item)
        print(item, attr)
        if item == 'listen':
            listen_proxy = DrissionPageListenerProxy(attr, self.__dict__['client'])
            return listen_proxy
        return attr


class DrissionPageListenerProxy:
    def __init__(self, listener, client=None):
        self.listener = listener
        self.client = client

    def __getattr__(self, item):
        attr = getattr(self.listener, item)
        # 当监听到wait被调用的时候
        if item == "wait":
            def wrapper(*args, **kwargs):
                result = attr(*args, **kwargs)
                check_data_packet(result, self.client)
                return result

            return wrapper
        # 当监听到steps被调用的时候
        if item == "steps":
            def wrapper(*args, **kwargs):
                if kwargs.get("gap", 1) > 1:
                    raise Exception("暂不支持多包监控")
                result = attr(*args, **kwargs)
                if attr.__name__ == "steps":
                    for step in result:
                        check_data_packet(step, self.client)
                        yield step

            return wrapper
        return attr


def check_data_packet(packet: DataPacket, client: DPProxyClient):
    """
    封装监听到的数据包，并将其存放在client的packet_queue中
    :param packet:
    :param client:
    :return:
    """
    url = packet.url
    method = packet.request.method
    data = None
    if packet.request.hasPostData:
        data = packet.request.postData
    body = packet.response.body
    body_str = json.dumps(body, ensure_ascii=False)
    body_str_list = [body_str[i:i + one_turn_max_token] for i in range(0, len(body_str), one_turn_max_token)]
    body_completed = True
    for index, body_str in enumerate(body_str_list):
        if (index + 1) != len(body_str_list):
            body_completed = False
        temp_dict = {
            "url": url,
            "body_completed": body_completed,
            "method": method,
            "request_data": data,
            "request_headers": dict(packet.request.headers),
            "response_headers": dict(packet.response.headers),
            "response_body_segment": body_str,
        }
        client.packet_queue.append(temp_dict)


client_manager = DPProxyClientManager()

# if __name__ == '__main__':
#     co = ChromiumOptions().set_user_agent(
#         "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36")
#     tab = ChromiumPage(co).latest_tab
#     client = DPProxyClient(tab, self_kill=False)
#     # client = CaptchaClient(tab, self_kill=True)
#     tab = client.get_driver(True)
#     url = "https://api.toutiaoapi.com/feoffline/hotspot_and_local/html/hot_list/index.html?client_extra_params=%7B%22custom_log_pb%22%3A%22%7B%5C%22style_id%5C%22%3A%5C%2240030%5C%22%2C%5C%22entrance_hotspot%5C%22%3A%5C%22search%5C%22%2C%5C%22location%5C%22%3A%5C%22hot_board%5C%22%2C%5C%22category_name%5C%22%3A%5C%22hotboard_light%5C%22%7D%22%7D&count=50&log_pb=%7B%22style_id%22%3A%2240030%22%2C%22entrance_hotspot%22%3A%22search%22%2C%22location%22%3A%22hot_board%22%2C%22category_name%22%3A%22hotboard_light%22%7D&only_hot_list=1&tab_name=stream&enter_keyword=%23%E7%BE%8E%E5%9B%BD%E9%80%80%E5%87%BA66%E4%B8%AA%E5%9B%BD%E9%99%85%E7%BB%84%E7%BB%87%23"
#     tab.get(url)
#     for _ in range(5056):
#         new_packet = client.pop_first_packet()
#         print(new_packet, "23")
#         time.sleep(1)
