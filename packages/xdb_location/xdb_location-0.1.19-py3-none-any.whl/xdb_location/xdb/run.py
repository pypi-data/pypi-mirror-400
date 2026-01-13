from xdb_location.xdb.xdbSearcher import XdbSearcher
from pathlib import Path


def searchWithVectorIndex():
    # 1. 预先加载整个 xdb
    dbPath = Path(__file__).parent / "ip2region.xdb"
    vi = XdbSearcher.loadVectorIndexFromFile(dbfile=dbPath)

    # 2. 使用上面的缓存创建查询对象, 同时也要加载 xdb 文件
    searcher = XdbSearcher(dbfile=dbPath, vectorIndex=vi)

    # 3. 执行查询
    ip = "1.2.3.4"
    region_str = searcher.search(ip)
    print(region_str)

    # 4. 关闭searcher
    searcher.close()


def searchWithVectorIndex():
    # 1. 预先加载整个 xdb
    dbPath = Path(__file__).parent / "ip2region.xdb"
    vi = XdbSearcher.loadVectorIndexFromFile(dbfile=dbPath)

    # 2. 使用上面的缓存创建查询对象, 同时也要加载 xdb 文件
    searcher = XdbSearcher(dbfile=dbPath, vectorIndex=vi)

    # 3. 执行查询
    ip = "1.2.3.4"
    region_str = searcher.search(ip)
    print(region_str)

    # 4. 关闭searcher
    searcher.close()

def searchWithContent(target_ip):
    # 1. 预先加载整个 xdb
    dbPath = Path(__file__).parent / "ip2region.xdb"
    # dbPath = os.path.join(os.path.dirname(__file__),"ip2region.xdb")
    cb = XdbSearcher.loadContentFromFile(dbfile=dbPath)
    # 2. 仅需要使用上面的全文件缓存创建查询对象, 不需要传源 xdb 文件
    searcher = XdbSearcher(contentBuff=cb)
    # 3. 执行查询
    region_str = searcher.search(target_ip)
    # 4. 关闭searcher
    return region_str


def searchWithContentCache():
    # 1. 预先加载整个 xdb
    dbPath = Path(__file__).parent / "ip2region.xdb"
    # dbPath = os.path.join(os.path.dirname(__file__),"ip2region.xdb")
    cb = XdbSearcher.loadContentFromFile(dbfile=dbPath)
    searcher = XdbSearcher(contentBuff=cb)
    return searcher


if __name__ == "__main__":
    print(searchWithContent(target_ip="1.15.241.228"))
    