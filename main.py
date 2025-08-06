from main_window import MyUI
from https_server import MyHttpsServer

if __name__ == '__main__':
    print("START!")
    server = MyHttpsServer()
    ui = MyUI()
    print("END!")
