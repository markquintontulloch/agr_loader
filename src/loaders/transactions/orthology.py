from .transaction import Transaction

class OrthoTransaction(Transaction):

    def __init__(self, graph):
        Transaction.__init__(self, graph)

    def ortho_tx(self, ortho_data, matched_algorithm_data, unmatched_algorithm_data, not_called_data):
        '''
        Loads the orthology data into Neo4j.

        '''
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(data)
        # quit()

        query = """
            UNWIND $data as row

            //using match here to limit ortho set to genes that have already been loaded by bgi.
            MATCH(g1:Gene {primaryKey:row.gene1AgrPrimaryId})
            MATCH(g2:Gene {primaryKey:row.gene2AgrPrimaryId})

            MERGE (g1:Gene)-[orth:ORTHOLOGOUS {primaryKey:row.uuid}]->(g2:Gene)
                SET orth.isBestScore = row.isBestScore,
                 orth.isBestRevScore = row.isBestRevScore,
                 orth.confidence = row.confidence,
                 orth.strictFilter = row.strictFilter,
                 orth.moderateFilter = row.moderateFilter

            //Create the Association node to be used for the object/doTerm
            CREATE (oa:Association:OrthologyGeneJoin {primaryKey:row.uuid})
                SET oa.joinType = 'orthologous'
            MERGE (g1:Gene)-[a1:ASSOCIATION]->(oa:Association:OrthologyGeneJoin)
            MERGE (oa:Association:OrthologyGeneJoin)-[a2:ASSOCIATION]->(g2:Gene)

        """

        matched_algorithm = """
            UNWIND $data as row
            MATCH (oa:Association:OrthologyGeneJoin {primaryKey:row.uuid})
            MERGE (match:OrthoAlgorithm {name:row.algorithm})
                MERGE (oa:Association:OrthologyGeneJoin)-[m:MATCHED]->(match:OrthoAlgorithm)
        """

        unmatched_algorithm = """
            UNWIND $data as row
            MATCH (oa:Association:OrthologyGeneJoin {primaryKey:row.uuid})
            MERGE (notmatch:OrthoAlgorithm {name:row.algorithm})
                MERGE (oa:Association:OrthologyGeneJoin)-[m:NOT_MATCHED]->(notmatch:OrthoAlgorithm)
        """

        not_called = """
            UNWIND $data as row
            MATCH (oa:Association:OrthologyGeneJoin {primaryKey:row.uuid})
            MERGE (notcalled:OrthoAlgorithm {name:row.algorithm})
                MERGE (oa:Association:OrthologyGeneJoin)-[m:NOT_CALLED]->(notcalled:OrthoAlgorithm)
        """

        Transaction.execute_transaction(self, query, ortho_data)
        Transaction.execute_transaction(self, matched_algorithm, matched_algorithm_data)
        Transaction.execute_transaction(self, unmatched_algorithm, unmatched_algorithm_data)
        Transaction.execute_transaction(self, not_called, not_called_data)