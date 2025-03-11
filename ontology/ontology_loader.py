import rdflib
import sys
from pprint import pprint

class OntologyHandler:
    def __init__(self, ontology_path):
        """
        Initialize the ontology handler by loading the RDF ontology.
        :param ontology_path: Path to the RDF ontology file.
        """
        self.graph = rdflib.Graph()
        self.ontology_path = ontology_path
        self.load_ontology()

    def load_ontology(self):
        """
        Load the ontology from the provided RDF file.
        """
        try:
            self.graph.parse(self.ontology_path, format="xml")
            print("Ontology successfully loaded.")
        except Exception as e:
            print(f"Error loading ontology: {e}")

    def normalize_label(self, label):
        """
        Normalize a label to avoid issues with spaces and casing.
        """
        return label.strip().lower()

    def format_entity_name(self, label):
        """
        Convert a label to a proper URI format.
        """
        return label.replace(" ", "_").replace("(", "").replace(")", "").replace(",", "_")

    def get_water_need_for_stage(self, stage_label):
        """
        Retrieve water needs for a given maize growth stage.
        :param stage_label: Label of the growth stage (e.g., "Floraison").
        :return: Water need associated with the growth stage.
        """
        normalized_label = self.normalize_label(stage_label)
        query = f"""
        PREFIX ont: <http://www.semanticweb.org/pc/ontologies/2025/0/mergemaizeirrigonto#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?waterNeed WHERE {{
          ?stage rdfs:label ?label .
          FILTER(LCASE(STR(?label)) = "{normalized_label}")
          ?stage ont:waterNeed ?waterNeed .
        }}
        """

        results = self.graph.query(query)
        return [str(row[0]) for row in results]

    def list_growth_stages(self):
        """
        Retrieve all maize growth stages defined under 'Stade de croissance' in the ontology.
        :return: List of growth stages with their labels.
        """
        query = """
        PREFIX ont: <http://www.semanticweb.org/pc/ontologies/2025/0/mergemaizeirrigonto#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?stage ?label WHERE {
          ?stage rdfs:subClassOf ont:Stade_de_croissance ;
                 rdfs:label ?label .
        }
        """
        results = self.graph.query(query)
        return [(str(row[0]), str(row[1])) for row in results]

    def get_entity_properties(self, entity):
        """
        Get all properties and values for a given entity.
        :param entity: URI of the entity.
        :return: Dictionary of properties and their values.
        """
        formatted_entity = self.format_entity_name(entity)
        entity_uri = rdflib.URIRef(f"http://www.semanticweb.org/pc/ontologies/2025/0/mergemaizeirrigonto#{formatted_entity}")
        properties = {}
        for s, p, o in self.graph.triples((entity_uri, None, None)):
            properties[str(p)] = str(o)
        return properties

if __name__ == "__main__":
    ontology_file = "../data/MergeMaizeIrrigOnto.rdf"
    handler = OntologyHandler(ontology_file)

    # Example usage
    print("Listing growth stages:")
    stages = [
        "Emergence (VE)",
        "Floraison (VT/R1)",
        "Germination",
        "Maturation (R6)",
        "Remplissage des grains (R3/R4)",
        "Végétatif (V2, V5, V10)"
    ]

    for stage_label in stages:
        print(f"\nWater need for {stage_label} stage:")
        water_needs = handler.get_water_need_for_stage(stage_label)
        pprint(water_needs)

        if water_needs:
            besoin_eau_uri = water_needs[0].split("#")[-1]
            water_need_properties = handler.get_entity_properties(besoin_eau_uri)
            if water_need_properties:
                print(f"\nDetails of water need for {stage_label}:")
                for prop, value in water_need_properties.items():
                    print(f"{prop}: {value}")
            else:
                print(f"No properties found for {stage_label}.")