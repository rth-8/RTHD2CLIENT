from main_window import MyUI
from https_server import MyHttpsServer
from pages import load_local_images

if __name__ == '__main__':
    print("START!")
    server = MyHttpsServer()
    load_local_images()
    ui = MyUI()
    print("END!")
