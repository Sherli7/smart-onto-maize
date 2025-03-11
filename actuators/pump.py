import time

class PumpController:
    def __init__(self):
        self.status = False  # False means pump is off

    def start_pump(self, water_amount):
        """
        Simulate starting the pump for a required water amount.
        :param water_amount: Amount of water to be pumped (liters).
        """
        if not self.status:
            self.status = True
            print(f"Pump started. Delivering {water_amount} liters of water...")
            time.sleep(2)  # Simulate the pump running time
            self.stop_pump()
        else:
            print("Pump is already running.")

    def stop_pump(self):
        """
        Stop the pump.
        """
        if self.status:
            self.status = False
            print("Pump stopped.")
        else:
            print("Pump is already off.")

    def get_status(self):
        """
        Get the current status of the pump.
        """
        return "Running" if self.status else "Stopped"

# Example usage
if __name__ == "__main__":
    pump = PumpController()
    pump.start_pump(50)
    print("Pump status:", pump.get_status())
    pump.stop_pump()
