import shutil


class Archiving:
    def __init__(self, filename, path, expansion):
        self.filename = filename
        self.path = path
        self.expansion = expansion

    def make_archive(self):
        shutil.make_archive(self.path+'/'+self.filename, self.expansion, self.path)