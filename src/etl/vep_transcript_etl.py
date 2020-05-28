"""VEP Transcript ETL"""

import logging
import multiprocessing
import uuid
import re
from etl import ETL
from files import TXTFile

from transactors import CSVTransactor
from transactors import Neo4jTransactor

class VEPTranscriptETL(ETL):
    """VEP Transcript ETL"""

    logger = logging.getLogger(__name__)

    # Query templates which take params and will be processed later

    vep_transcript_query_template = """
            USING PERIODIC COMMIT %s
            LOAD CSV WITH HEADERS FROM \'file:///%s\' AS row

                MATCH (g:Transcript {gff3ID:row.transcriptId})
                MATCH (a:Variant {hgvsNomenclature:row.hgvsNomenclature})

                CREATE (gc:TranscriptLevelConsequence {primaryKey:row.primaryKey})
                SET gc.transcriptLevelConsequence = row.transcriptLevelConsequence,
                    gc.transcriptId = g.primaryKey,
                    gc.variantId = a.hgvsNomenclature,
                    gc.impact = row.impact,
                    gc.aminoAcidReference = row.aminoAcidReference,
                    gc.aminoAcidVariation = row.aminoAcidVariation,
                    gc.aminoAcidChange = row.aminoAcidChange,
                    gc.cdnaStartPosition = row.cdnaStartPosition,
                    gc.cdnaEndPosition = row.cdnaEndPosition,
                    gc.cdnaRange = row.cdnaRange,
                    gc.cdsStartPosition = row.cdsStartPosition,
                    gc.cdsEndPosition = row.cdsEndPosition,
                    gc.cdsRange = row.cdsRange,
                    gc.proteinStartPosition = row.proteinStartPosition,
                    gc.proteinEndPosition = row.proteinEndPosition,
                    gc.proteinRange = row.proteinRange,
                    gc.codonChange = row.codonChange,
                    gc.codonReference = row.codonReference,
                    gc.codonVariation = row.codonVariation,
                    gc.hgvsProteinNomenclature = row.hgvsProteinNomenclature,  
                    gc.hgvsCodingNomenclature = row.hgvsCodingNomenclature, 
                    gc.hgvsVEPGeneNomenclature = row.hgvsVEPGeneNomenclature            

                CREATE (g)-[ggc:ASSOCIATION {primaryKey:row.primaryKey}]->(gc)
                CREATE (a)-[ga:ASSOCIATION {primaryKey:row.primaryKey}]->(gc)
                CREATE (g)-[gv:ASSOCIATION {primaryKey:row.primaryKey}]->(a)

                MERGE(syn:Synonym:Identifier {primaryKey:row.hgvsVEPGeneNomenclature})
                        SET syn.name = row.hgvsVEPGeneNomenclature
                MERGE (a)-[aka2:ALSO_KNOWN_AS]->(syn) 
            
            """




    def __init__(self, config):
        super().__init__()
        self.data_type_config = config

    def _load_and_process_data(self):
        thread_pool = []

        for sub_type in self.data_type_config.get_sub_type_objects():
            process = multiprocessing.Process(target=self._process_sub_type, args=(sub_type,))
            process.start()
            thread_pool.append(process)

        ETL.wait_for_threads(thread_pool)

    def _process_sub_type(self, sub_type):
        self.logger.info("Loading VEP Data: %s", sub_type.get_data_provider())
        commit_size = self.data_type_config.get_neo4j_commit_size()
        filepath = sub_type.get_filepath()

        # This needs to be in this format (template, param1, params2) others will be ignored
        query_template_list = [
            [self.vep_transcript_query_template, commit_size,
             "vep_transcript_data_" + sub_type.get_data_provider() + ".csv"]
        ]

        # Obtain the generator
        generators = self.get_generators(filepath)

        query_and_file_list = self.process_query_params(query_template_list)
        CSVTransactor.save_file_static(generators, query_and_file_list)
        Neo4jTransactor.execute_query_batch(query_and_file_list)

    def get_generators(self, filepath):
        """Get Generators"""

        data = TXTFile(filepath).get_data()
        vep_maps = []
        impact = ''
        hgvs_p = ''
        hgvs_c = ''
        hgvs_g = ''

        for line in data:
            columns = line.split()
            if columns[0].startswith('#'):
                continue

            notes = columns[13]
            kvpairs = notes.split(";")
            if kvpairs is not None:
                for pair in kvpairs:
                    key = pair.split("=")[0]
                    value = pair.split("=")[1]
                    if key == 'IMPACT':
                        impact = value
            if columns[3].startswith('Gene:'):
                gene_id = columns[3].lstrip('Gene:')
            elif columns[3].startswith('RGD:'):
                gene_id = columns[3].lstrip('RGD:')
            else:
                notes = columns[13]
                kvpairs = notes.split(";")
                if kvpairs is not None:
                    impact = ''
                    hgvs_p = ''
                    for pair in kvpairs:
                        key = pair.split("=")[0]
                        value = pair.split("=")[1]
                        if key == 'IMPACT':
                            impact = value
                        if key == 'HGVSp':
                            hgvs_p = value
                        if key == 'HGVSc':
                            hgvs_c = value
                        if key == 'HGVSg':
                            hgvs_g = value
                if columns[3].startswith('Gene:'):
                    gene_id = columns[3].lstrip('Gene:')
                elif columns[3].startswith('RGD:'):
                    gene_id = columns[3].lstrip('RGD:')
                else:
                    gene_id = columns[3]

                position_is_a_range = re.compile('[0-9]+-[0-9]+')
                cdna_range_match = re.search(position_is_a_range, columns[7])
                cds_range_match = re.search(position_is_a_range, columns[8])
                protein_range_match = re.search(position_is_a_range, columns[9])

                if cdna_range_match:
                    cdna_start_position = columns[7].split("-")[0]
                    cdna_end_position = columns[7].split("-")[1]
                    cdna_range = columns[7]
                else:
                    if columns[7] == '-':
                        cdna_start_position = ""
                        cdna_end_position = ""
                        cdna_range = ""
                    else:
                        cdna_start_position = columns[7]
                        cdna_end_position = columns[7]
                        cdna_range = columns[7]

                if cds_range_match:
                    cds_start_position = columns[8].split("-")[0]
                    cds_end_position = columns[8].split("-")[1]
                    cds_range = columns[8]
                else:
                    if columns[8] == '-':
                        cds_start_position = ""
                        cds_end_position = ""
                        cds_range = ""
                    else:
                        cds_start_position = columns[8]
                        cds_end_position = columns[8]
                        cds_range = columns[8]

                if protein_range_match:
                    protein_start_position = columns[9].split("-")[0]
                    protein_end_position = columns[9].split("-")[1]
                    protein_range = columns[9]
                else:
                    if columns[9] == '-':
                        protein_start_position = ""
                        protein_end_position = ""
                        protein_range = ""
                    else:
                        protein_start_position = columns[8]
                        protein_end_position = columns[8]
                        protein_range = columns[8]

                before_after_change = re.compile("'+/'+")
                amino_acid_range_match = re.search(before_after_change, columns[10])
                codon_range_match = re.search(before_after_change, columns[11])

                if amino_acid_range_match:
                    amino_acid_reference = columns[10].split("/")[0]
                    amino_acid_variation = columns[10].split("/")[1]
                    amino_acid_change = columns[10]
                else:
                    if columns[10] == '-':
                        amino_acid_reference = ""
                        amino_acid_variation = ""
                        amino_acid_change = ""
                    else:
                        amino_acid_reference = columns[10]
                        amino_acid_variation = columns[10]
                        amino_acid_change = columns[10]


                if codon_range_match:
                    codon_reference = columns[11].split("/")[0]
                    codon_variation = columns[11].split("/")[1]
                    codon_change = columns[11]
                else:
                    if columns[11] == '-':
                        codon_reference = ""
                        codon_variation = ""
                        codon_change = ""
                    else:
                        codon_reference = columns[11]
                        codon_variation = columns[11]
                        codon_change = columns[11]

                vep_result = {"hgvsNomenclature": columns[0],
                              "transcriptLevelConsequence": columns[6],
                              "primaryKey": str(uuid.uuid4()),
                              "impact": impact,
                              "hgvsProteinNomenclature": hgvs_p,
                              "hgvsCodingNomenclature": hgvs_c,
                              "hgvsVEPGeneNomenclature": hgvs_g,
                              "gene": gene_id,
                              "transcriptId": columns[4],
                              "aminoAcidReference": amino_acid_reference,
                              "aminoAcidVariation": amino_acid_variation,
                              "aminoAcidChange": amino_acid_change,
                              "cdnaStartPosition": cdna_start_position,
                              "cdnaEndPosition": cdna_end_position,
                              "cdnaRange": cdna_range,
                              "cdsStartPosition": cds_start_position,
                              "cdsEndPosition": cds_end_position,
                              "cdsRange": cds_range,
                              "proteinStartPosition":protein_start_position,
                              "proteinEndPosition":protein_end_position,
                              "proteinRange": protein_range,
                              "codonReference": codon_reference,
                              "codonVariation": codon_variation,
                              "codonChange": codon_change}

                vep_maps.append(vep_result)

        yield [vep_maps]