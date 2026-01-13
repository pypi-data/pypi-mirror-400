import time
import json
from onvif_device_manage import checkPwdAndGetCam, ptzChangeByClient, OnvifClient, ws_discovery

def main():
    print("Hello from yms-mcp!")

    # 设备发现
    print(ws_discovery())

    # client = OnvifClient('10.17.20.88', 80, 'admin', 'admin123', needSnapImg=False)
    # client = OnvifClient('10.17.20.77', 80, 'admin', 'admin123', needSnapImg=False)
    # client = OnvifClient('10.17.20.66', 80, 'admin', 'admin123', needSnapImg=False)
    client = OnvifClient('10.17.20.110', 80, 'admin', 'qwer1234', needSnapImg=False)
    # 如果要控制特定摄像头，可以下边这样写
    # client = OnvifClient('192.168.1.10', 80, 'admin', '123456', token="ProfileToken002", sourceToken= "VideoSourceToken002", nodeToken="NodeToken002", needSnapImg=False)

    # 获取所有画面所有码流的RTSP地址、token(即ProfileToken)、sourceToken、nodeToken等信息

    # 获取设备信息
    print(json.dumps(client.get_deviceInfo()))

    # # 设置时间
    # client.set_cam_time()

    # 云台与聚焦控制
    # 云台上移
    ptzChangeByClient(client, 'Down', 1)
    # 移动一秒
    time.sleep(10)
    # 然后停止
    ptzChangeByClient(client, 'Up', 0)
    time.sleep(10)


if __name__ == "__main__":
    
    client = OnvifClient('10.17.20.110', 80, 'admin', 'qwer1234', needSnapImg=True)
    image_base64 = client.snap_image()
    # 上传到minio
    from utils.minio import upload_to_minio
    # base64转二进制
    import base64
    image_bytes = base64.b64decode(image_base64)
    upload_to_minio(image_bytes)