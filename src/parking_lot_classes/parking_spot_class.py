class ParkingSpot:
    def __init__(self, spot_id):
        self.spot_id = spot_id
        self.coordinates = None
        self.det_record = []
        self.is_current = False
        self.best_detection = None
        self.is_occupied = False
        self.det_time = None
        self.average_occupation = 0
     
    def update_occupancy_status(self):
        # Check if there's a detection assigned
        if self.detection:
            # Assuming the detection provides occupancy information
            self.is_occupied = True
        else:
            self.is_occupied = False
