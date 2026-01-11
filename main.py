from main_window import MyUI
from https_server import MyHttpsServer
import local_images

if __name__ == '__main__':
    print("START!")
    server = MyHttpsServer()
    local_images.load_local_images()
    ui = MyUI()
    print("END!")
