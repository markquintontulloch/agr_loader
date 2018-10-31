from .mod import MOD

class SGD(MOD):

    def __init__(self, batch_size):
        self.species = "Saccharomyces cerevisiae"
        super().__init__(batch_size, self.species)
        self.loadFile = "SGD_1.0.0.7_1.tar.gz"
        self.bgiName = "/SGD_1.0.0.7_basicGeneInformation.json"
        self.diseaseName = "/SGD_1.0.0.7_disease.daf.json"
        self.phenotypeName = "/SGD_1.0.0.7_phenotype.json"
        self.alleleName = ""
        self.wtExpressionName = "/SGD_1.0.0.7_expression.json"
        self.geneAssociationFile = "gene_association_1.7.sgd.gz"
        self.identifierPrefix = "SGD:"
        self.geoRetMax = "10000"
        self.dataProvider = "SGD"

    def load_genes(self):
        data = self.load_genes_mod(self.bgiName, self.loadFile)
        return data

    @staticmethod
    def get_organism_names():
        return ["Saccharomyces cerevisiae", "S. cerevisiae", "YEAST"]

    def extract_go_annots(self):
        go_annot_list = self.extract_go_annots_mod(self.geneAssociationFile, self.identifierPrefix)
        return go_annot_list

    def load_disease_gene_objects(self):
        data = self.load_disease_gene_objects_mod(self.diseaseName, self.loadFile)
        return data

# these are commented out because SGD has no allele data and no allele->disease data right now

    def load_disease_allele_objects(self):
        data = ""
        #self.load_disease_allele_objects_mod(SGD.diseaseName, SGD.loadFile)
        return data

    def load_allele_objects(self):
        data = ""
        #self.load_allele_objects_mod(self, self.alleleName, self.loadFile)
        return data

    def load_phenotype_objects(self):
        data = self.load_phenotype_objects_mod(self.phenotypeName, self.loadFile)
        return data

    def load_wt_expression_objects(self):
        data = self.load_wt_expression_objects_mod(self.wtExpressionName, self.loadFile)
        return data

    def extract_geo_entrez_ids_from_geo(self):
        xrefs = self.extract_geo_entrez_ids_from_geo_mod(self.geoRetMax)
        return xrefs

    def extract_ortho_data(self, mod_name):
        data = self.extract_ortho_data_mod(mod_name)
        return data