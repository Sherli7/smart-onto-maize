from actuators.pump import PumpController
from ontology.ontology_loader import OntologyHandler

class IrrigationSystem:
    def __init__(self, ontology_file):
        self.ontology_handler = OntologyHandler(ontology_file)
        self.pump = PumpController()

    def irrigate(self, stage_label, current_moisture):
        water_needs = self.ontology_handler.get_water_need_for_stage(stage_label)
        if not water_needs:
            return f"No irrigation required for {stage_label}."

        besoin_eau_uri = water_needs[0].split("#")[-1]
        properties = self.ontology_handler.get_entity_properties(besoin_eau_uri)
        required_water = float(properties.get("http://www.semanticweb.org/pc/ontologies/2025/0/mergemaizeirrigonto#waterAmount", 0))

        if current_moisture < (required_water * 0.6):
            print(f"Irrigation triggered for {stage_label}, {required_water} liters required.")
            self.pump.start_pump(required_water)
            return f"Irrigation started for {stage_label} with {required_water} liters."
        else:
            return "Moisture level sufficient, no irrigation needed."

if __name__ == "__main__":
    irrigation = IrrigationSystem("../data/MergeMaizeIrrigOnto.rdf")
    print(irrigation.irrigate("Floraison (VT/R1)", 25.0))
