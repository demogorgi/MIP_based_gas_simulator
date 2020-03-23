from os import listdir
from .readers.csv_reader import read_csv

class Net:
    def __init__(self):
        pass
        
    def read_instance_folder(self, folder_path):
        print(">> instance folder path", folder_path)
        files = list(filter(self.filename_is_valid, listdir(folder_path)))
        print(">> files found:\n\t-", "\n\t- ".join(files))
        files = map(lambda f: folder_path + "/" + f, files)
        for f in files:
            ext = f.split(".")[1]
            content = self.file_content(f)
            if ext == "csv": read_csv(self, content)
    
    def filename_is_valid(self, n):
        splits = n.split(".")
        if len(splits) < 2: return False
        ext = splits[1]
        return ext in ["csv"]
        
    def file_content(self, path):
        file = open(path, "r")
        content = file.read()
        file.close()
        return content

    