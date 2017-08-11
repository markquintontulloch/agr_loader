from neo4j.v1 import GraphDatabase

class Transaction(object):

    def __init__(self, graph):
        self.graph = graph

    def execute_transaction(self, query, data):
        with self.graph.session() as session:
            with session.begin_transaction() as tx:
                tx.run(query, data=data)
        print("Processed %s entries." % (len(data)))

    def execute_transaction_batch(self, query, data, batch_size):
        print("Executing batch query. Please wait.")

        for submission in self.split_into_chunks(data, batch_size):
            self.execute_transaction(query, submission)
        print("Finished batch loading.")

    def split_into_chunks(self, data, batch_size):
        return (data[pos:pos + batch_size] for pos in range(0, len(data), batch_size))

    # def batch_load_simple(self, label, data, primary_key):
    #     '''
    #     Loads a list of dictionaries (data) into nodes with label (label) and primary_key (primary_key).
    #     Dictionary entries must contain the string (primary_key) as the key of a key : value pair.
    #     '''
    #     query = """
    #         UNWIND $data as row \
    #         MERGE (n:%s {primary_key:row.%s})
    #     """ % (label, primary_key)

    #     self.execute_transaction(query, data)