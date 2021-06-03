# http://www.blopig.com/blog/2016/08/processing-large-files-using-python-part-duex/
# https://www.blopig.com/blog/2016/08/processing-large-files-using-python/
import os.path

class Chunker(object):

    #Iterator that yields start and end locations of a file chunk of default size 1MB.
    @classmethod
    def chunkify(cls,fname,size=1024*1024):
        fileEnd = os.path.getsize(fname)
        with open(fname,'r') as f:
            chunkEnd = f.tell()
            while True:
                chunkStart = chunkEnd
                f.seek(size,1)
                cls._EOC(f)
                chunkEnd = f.tell()
                yield chunkStart, chunkEnd - chunkStart
                if chunkEnd >= fileEnd:
                    break

    #Move file pointer to end of chunk
    @staticmethod
    def _EOC(f):
        l = f.readline() #incomplete line
        p = f.tell()
        l = f.readline()
        while l and l[0] != '>': #find the start of sequence
            p = f.tell()
            l = f.readline()
        f.seek(p) #revert one line

    #read chunk
    @staticmethod
    def read(fname,chunk):
        with open(fname,'r') as f:
            f.seek(chunk[0])
            return f.read(chunk[1])

    #iterator that splits a chunk into units
    @staticmethod
    def parse(chunk):
        for line in chunk.splitlines():
            yield chunk