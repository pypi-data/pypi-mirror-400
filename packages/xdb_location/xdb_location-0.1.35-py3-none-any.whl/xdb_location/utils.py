def do_something_useful():
    print("Replace this with a utility function")


#################################################################
import logging
from pathlib import Path
import sys
import time

import xdb_location.xdb.maker as mk
import xdb_location.xdb.index as idx

# Format log
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s-%(name)s-%(lineno)s-%(levelname)s - %(message)s",
)
log = logging.getLogger(__name__)


def print_help():
    print("ip2region xdb python maker")
    print("{} [command] [command options]".format(sys.argv[0]))
    print("Command: ")
    print("  gen      generate the binary db file")


def gen_db(src: str, dst: str):
    src_file, dst_file = src, dst
    index_policy = idx.Vector_Index_Policy
    # Check input parameters
    start_time = time.time()
    # Make the binary file
    maker = mk.new_maker(index_policy, src_file, dst_file)
    maker.init()
    maker.start()
    maker.end()

    logging.info(
        "Done, elapsed: {:.0f}m{:.0f}s".format(
            (time.time() - start_time) / 60, (time.time() - start_time) % 60
        )
    )
