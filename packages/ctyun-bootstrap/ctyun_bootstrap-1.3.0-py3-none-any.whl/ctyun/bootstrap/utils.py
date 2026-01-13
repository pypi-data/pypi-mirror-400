import logging
import requests

logger = logging.getLogger(__name__)
'''
获取agent 下载地址。
'''


def get_agent_path(env):
    if env == "dev" :
        return "http://10.50.208.198:9624/dy/api/paas-mgr/nationarmsadmin/cmparms/app/agent/download?agentName=python_agent"
    
    return "https://arms.ctyun.cn/dy/api/paas-mgr/nationarmsadmin/cmparms/app/agent/download?agentName=python_agent"
    

'''
判断网络是否通
'''


def check_network(url, timeout=1):
    try:
        response = requests.request("GET", url, timeout=timeout)
        if response.status_code == 200:
            return True
    except Exception:
        return False
