from  Server import *
from MetaData import *
import Pyro4
import threading
import socket
import FileServer
import Queue

Pyro4.config.SERIALIZER = 'pickle'
Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')

class Client():

    def __init__(self):
        self.name_server= Pyro4.locateNS()
        self.server = None
        self.id_num = None
        self.register_to_indexing_server()
        self.file_server = FileServer.FileServer(self)
        self.ip , self.port = self.file_server.start_server()
        self.client_daemon = None
        self.meta_data = None
        self.download_queue = Queue.Queue()

    def obtain(self,file_name):
        peer_with_file_id = self.server.search(file_name)
        print "peer: " + str(peer_with_file_id)
        if len(peer_with_file_id ) > 0:
            peer_uri = self.name_server.lookup(str(peer_with_file_id[0]))
            peer = Pyro4.Proxy(peer_uri)
            self.get_file(file_name,peer)

    def get_file(self,file_name,peer):
        peer_ip,peer_port = peer.get_addr()
        self.download_queue.put((peer_ip,peer_port,file_name))
        getter = threading.Thread(target= self.download_file)
        getter.start()
        print "Starting download thread"

    def download_file(self):
        peer_ip,peer_port, file_name = self.download_queue.get()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        file  = open(self.get_working_dir() + file_name + ".txt","wb+")
        try:
            print "Connecting to fileserver!!!!\n"
            sock.connect((peer_ip,peer_port))
            sock.sendall(file_name + "\n")
            while 1:
                file_data = sock.recv(1024)
                if not file_data:
                    break
                file.write(file_data)

        finally:
            file.close()
            sock.close()

    def get_addr(self):
        return (self.ip,self.port)

    def get_id(self):
        return self.id_num

    def delete_file(self,file_name):
        self.server.remove_from_index(self.id_num,file_name)
        #delete from disk

    def set_meta_data(self, meta_data):
        self.meta_data = meta_data

    def get_file_name(self):
        return self.meta_data.files[0].name

    def get_working_dir(self):
        return self.meta_data.working_directory

    def register_with_servers(self):
        self.client_daemon = Pyro4.Daemon()
        self.server.registry(self.id_num,self.ip,self.port
            ,self.meta_data.files)
        self.register_to_naming_server()
        self.client_daemon.requestLoop()

    def register_to_naming_server(self):
        client_uri = self.client_daemon.register(self)
        self.name_server.register(str(self.id_num),client_uri)

    def register_to_indexing_server(self):
        server_uri = self.name_server.lookup("Main_Server")
        self.server = Pyro4.Proxy(server_uri)
        self.id_num =self.server.generate_peer_id()

    def start_client(self):
        daemon_thread = threading.Thread(target=self.register_with_servers)
        daemon_thread.start()
        print "returning from start"

    def stop_client(self):
        self.file_server.stop_server()
        self.client_daemon.shutdown()
        print "Stopping client: " + str(self.id_num)

def main():
    c1 = Client()
    c2 = Client()
    c1.start_client()

if __name__=="__main__":
    main()


