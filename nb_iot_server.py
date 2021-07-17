'''

Created Date: Friday, October 19th 2018, 5:48:46 am
Author: akira

Copyright (c) 2018 
'''


import socketserver
import threading
import queue
import time
import signal

app_running = True
bridge_queue = queue.Queue()


def data_check(payload):
    rslt = False

    # Is payload ok
    if payload is not None:
        # bridge_queue.put_nowait((payload, data_time))
        bridge_queue.put_nowait((payload))
        rslt = True
    return rslt


def signal_handler(signum, frame):
    global app_running
    print('Got signals')
    app_running = False


class MyUDPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print("{} wrote:".format(self.client_address[0]))
        print(data)

        if data_check(payload=data):
            socket.sendto(str(time.time()).encode(), self.client_address)
            print("return ok to client")
        else:
            socket.sendto('no'.encode(), self.client_address)


class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Port 0 means to select an arbitrary unused port
    ADDR, PORT = "", 8080

    server = ThreadedUDPServer((ADDR, PORT), MyUDPHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()

    while app_running:
        try:
            queue_payload = bridge_queue.get_nowait()
            print('data in queue : %s' % (str(queue_payload)))
            # convert data
            tmpstr = queue_payload.decode("utf-8")
            dat = tmpstr.split(':')
            print(dat)
        except queue.Empty:
            # Sleep if not have data
            time.sleep(0.2)
        finally:
            pass

    server.shutdown()
    server.server_close()
