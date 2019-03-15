import logging
import os
from test import TestObject
import time

from etl.helpers import ResourceDescriptorHelper

logger = logging.getLogger(__name__)

class ETL(object):

    xrefUrlMap = ResourceDescriptorHelper().get_data()

    def __init__(self):

        if "TEST_SET" in os.environ and os.environ['TEST_SET'] == "True":
            logger.warn("WARNING: Test data load enabled.")
            time.sleep(1)
            self.testObject = TestObject(True)
        else:
            self.testObject = TestObject(False)

    def run_etl(self):
        self._load_and_process_data()

    def wait_for_threads(thread_pool):
        for thread in thread_pool:
            thread.join()

        while len(thread_pool) > 0:
            for (index, thread) in enumerate(thread_pool):
                sleep(0.5)
                if thread.exitcode is None and not thread.is_alive():
                    thread.join()
                    del thread_pool[index]
                elif thread.exitcode < 0:
                    # Kill all child threads
                    for thread1 in thread_pool:
                        thread1.terminate()
                        sys.exit(-1)
                else:
                    pass


    def process_query_params(self, query_list_with_params):
        # generators = list of yielded lists from parser
        # query_list_with_parms = list of queries, each with batch size and CSV file name.
        query_and_file_names = []

        for query_params in query_list_with_params:
            cypher_query_template = query_params.pop(0)  # Remove the first query + batch size + CSV file name
            #  from the list. Format the query with all remaining paramenters.
            query_to_run = cypher_query_template % tuple(query_params)

            while len(query_params) > 2:  # We need to remove extra params before we append
                # the modified query. Assuming the last entry in the list is the filepath
                query_params.pop()

            file_name = query_params.pop()
            query_and_file_names.append([query_to_run, file_name])

        return query_and_file_names
