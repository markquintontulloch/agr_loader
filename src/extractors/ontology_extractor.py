import urllib.request, json

class OntologyExt(object):

    def get_data(self, ontName):

        term_ontology = None
        term_ontology_full = None

        # TODO Make size configurable?
        print('Downloading ontology terms via: https://www.ebi.ac.uk/ols/api/ontologies/' + ontName + '/terms?size=500')
        with urllib.request.urlopen("https://www.ebi.ac.uk/ols/api/ontologies/' + ontName + '/terms?size=500'") as url:
            term_ontology = json.loads(url.read().decode())

        print('Determining total number of terms and pages to request...')
        total_terms = term_ontology['page']['totalElements']
        total_pages = term_ontology['page']['totalPages']

        print('Requesting %s terms over %s pages.' % (total_terms, total_pages))

        processed_list = []
        for i in range(total_pages):
            request_url = 'https://www.ebi.ac.uk/ols/api/ontologies/' + ontName + '/terms?size=500' % (i)
            print('Retrieving terms from page %s of %s.' % (i+1, total_pages))
            with urllib.request.urlopen(request_url) as url:
                term_ontology_full = json.loads(url.read().decode())

                for terms in term_ontology_full['_embedded']['terms']:
                    if terms['obo_id'] is not None: # Avoid weird "None" entry from ontName ontology.
                        dict_to_append = {
                            'identifier' : terms['obo_id'],
                            'label' : terms['label']
                        }
                        processed_list.append(dict_to_append)

        return processed_list