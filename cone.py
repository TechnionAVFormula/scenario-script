import cognata_api
import cognata_api.scenario.ai_vehicle as AiVehicle
import cognata_api.scenario.position as Position
import PositionCalc
import enum
from enum import IntEnum

class ConeType(IntEnum):
    BigOrange = enum.auto()
    Orange = enum.auto()
    Blue = enum.auto()
    Yellow = enum.auto()

class Cone:
    index = 1
    TYPE_TO_NAME = {
        ConeType.BigOrange: "BigOrangeCone",
        ConeType.Orange: "SmallOrangeCone",
        ConeType.Blue: "BlueCone",
        ConeType.Yellow: "YellowCone"
    }
    TYPE_TO_INTERNAL_TYPE = {
        ConeType.BigOrange: "General_Props/Cones/Big_orange_cone_WEMAS_307.610500.00.00",
        ConeType.Orange: "General_Props/Cones/Small_Orange_Cone_WEMAS_400.000013.00.00",
        ConeType.Blue: "General_Props/Cones/Small_Blue_Cone_WEMAS_400.000043.00.00",
        ConeType.Yellow: "General_Props/Cones/Small_Yellow_Cone_WEMAS_400.000013.01.10"
    }

    def __init__(self, cone_type, lat, lng):
        self.cone_type = cone_type
        self.lat = lat
        self.lng = lng
        self.index = Cone.index
        Cone.index += 1

    def get_cone_at_relative_meters(self, relative_lat=None, relative_lng=None, new_cone_type=None):
        if new_cone_type is None:
            new_cone_type = self.cone_type
        new_lat = self.lat
        new_lng = self.lng
        if relative_lat is not None:
            new_lat = PositionCalc.add_meters_to_lat(self.lat, relative_lat)
        if relative_lng is not None:
            new_lng = PositionCalc.add_meters_to_lng(self.lng, new_lat, relative_lng)

        return Cone(new_cone_type, new_lat, new_lng)

    def add_to_scene(self, scene):
        cone_object = AiVehicle.create_moving_object(f'M{self.index}',
                                                     Cone.TYPE_TO_INTERNAL_TYPE[self.cone_type], 0, 0, 0, [], 
                                                     path=[Position.create_moving_object_waypoint(self.lat, self.lng, False)])
        # print(f"Added {Cone.TYPE_TO_NAME[self.cone_type]} at {self.lat}x{self.lng}")
        scene.add_moving_object(cone_object)
