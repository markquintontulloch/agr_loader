from .mod import MOD

class FlyBase(MOD):

    def __init__(self, batch_size):
        self.species = "Drosophila melanogaster"
        super().__init__(batch_size, self.species)
        self.loadFile = "FB_1.0.0.7_4.tar.gz"
        self.bgiName = "/FB_1.0.0.7_BGI.json"
        self.diseaseName = "/FB_1.0.0.7_disease.json"
        self.phenotypeName = "/FB_1.0.0.7_phenotype.json"
        self.alleleName = "/FB_1.0.0.7_feature.json"
        self.wtExpressionName = "/FB_1.0.0.7_expression.json"
        self.geneAssociationFile = "gene_association_1.7.fb.gz"
        self.identifierPrefix = "FB:"
        self.geoRetMax = "20000"
        self.dataProvider = "FB"

    def load_genes(self):
        data = self.load_genes_mod(self.bgiName, self.loadFile)
        return data

    @staticmethod
    def get_organism_names():
        return ["Drosophila melanogaster", "D. melanogaster", "DROME"]

    def extract_go_annots(self):
        go_annot_list = self.extract_go_annots_mod(self.geneAssociationFile, self.identifierPrefix)
        return go_annot_list

    def load_disease_gene_objects(self):
        data = self.load_disease_gene_objects_mod(self.diseaseName, self.loadFile)
        return data

    def load_disease_allele_objects(self):
        data = self.load_disease_allele_objects_mod(self.diseaseName, self.loadFile)
        return data

    def load_allele_objects(self):
        data = self.load_allele_objects_mod(self.alleleName, self.loadFile)
        return data

    def load_phenotype_objects(self):
        data = self.load_phenotype_objects_mod(self.phenotypeName, self.loadFile)
        return data

    def load_wt_expression_objects(self):
        data = self.load_wt_expression_objects_mod(self.wtExpressionName, self.loadFile)
        return data

    def extract_geo_entrez_ids_from_geo(self):
        data = self.extract_geo_entrez_ids_from_geo_mod(self.geoRetMax)
        return data
        
    def extract_ortho_data(self, mod_name):
        data = self.extract_ortho_data_mod(mod_name)
        return data
