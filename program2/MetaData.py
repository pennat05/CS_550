class MetaData():

#### This class represents it file that the Peers own
    def __init__(self,working_dir, files):
        self.working_directory = working_dir
        self.files = files

    def add_file(self,file_name):
        self.files.append(FileInfo(file_name,"default"))

    def remove_file(self,file_name):
        for f in self.files:
            if f.name == file_name:
                print "Removing File"
                self.files.remove(f)

    def has_file(self,file_name):
        for f in self.files:
            if f.name == file_name:
                print "Found File in Index"
                return True

class FileInfo():
    def __init__(self,name,size):
        self.size = size
        self.name = name

    def get_name(self):
        return self.name

    def get_size(self):
        return size


