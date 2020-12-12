import cognata_api
import cognata_api.scenario.ai_vehicle as AiVehicle
import cognata_api.scenario.position as Position
import PositionCalc
from cone import Cone, ConeType
import numpy as np
import matplotlib.pyplot as plt
from abc import ABCMeta, abstractmethod

from cognata_api.scenario.scenario import Scenario
import enum
from enum import IntEnum

class _EventGenerator():
    __metaclass__ = ABCMeta

    def __init__(self, scene_name, scene_description, terrain, ego_car, timeout=30):
        self.scene = Scenario(scene_name, scene_description, terrain, ego_car, timeout)
        self.start_lat = ego_car['starting_point']['lat']
        self.start_lng = ego_car['starting_point']['lng']

    @abstractmethod
    def generate_cones(self):
        raise NotImplementedError()

    def plot_scene(self):
        pass

    def add_variables(self, variables):
        for elm in variables:
            self.scene.add_variable(elm)

    def add_rules(self, rule_list):
        for rule in rule_list:
            self.scene.add_rule(rule)

    def create_scenario(self, api):
        return api.create_scenario(self.scene.get_formula())


class AccelerationGenerator(_EventGenerator):
    TRACK_LENGTH = 75
    STOP_AREA_LENGTH = 100
    TRACK_WIDTH = 3

    def __init__(self, scene_name, scene_description, terrain, ego_car, timeout=30):
        super().__init__(scene_name, scene_description, terrain, ego_car, timeout=timeout)

    def generate_cones(self):
        staging_latitude = PositionCalc.add_meters_to_lat(self.start_lat, 1)
        left_lng = PositionCalc.add_meters_to_lng(self.start_lng, staging_latitude, -AccelerationGenerator.TRACK_WIDTH/2)
        right_lng = PositionCalc.add_meters_to_lng(self.start_lng, staging_latitude, AccelerationGenerator.TRACK_WIDTH/2)
        
        right_cone = Cone(ConeType.BigOrange, staging_latitude, right_lng)
        right_cone.add_to_scene(self.scene)
        left_cone = Cone(ConeType.BigOrange, staging_latitude, left_lng)
        left_cone.add_to_scene(self.scene)
        
        right_cone = right_cone.get_cone_at_relative_meters(relative_lat=5)
        right_cone.add_to_scene(self.scene)
        left_cone = left_cone.get_cone_at_relative_meters(relative_lat=5)
        left_cone.add_to_scene(self.scene)

        for i in range(0, AccelerationGenerator.TRACK_LENGTH, 5):      
            right_cone = right_cone.get_cone_at_relative_meters(relative_lat=5, new_cone_type=ConeType.Yellow)
            right_cone.add_to_scene(self.scene)
            left_cone = left_cone.get_cone_at_relative_meters(relative_lat=5, new_cone_type=ConeType.Blue)
            left_cone.add_to_scene(self.scene)
        
        for i in range(2):      
            right_cone = right_cone.get_cone_at_relative_meters(relative_lat=5, new_cone_type=ConeType.BigOrange)
            right_cone.add_to_scene(self.scene)
            left_cone = left_cone.get_cone_at_relative_meters(relative_lat=5, new_cone_type=ConeType.BigOrange)
            left_cone.add_to_scene(self.scene)

        for i in range(0, AccelerationGenerator.STOP_AREA_LENGTH, 5):      
            right_cone = right_cone.get_cone_at_relative_meters(relative_lat=5, new_cone_type=ConeType.Orange)
            right_cone.add_to_scene(self.scene)
            left_cone = left_cone.get_cone_at_relative_meters(relative_lat=5, new_cone_type=ConeType.Orange)
            left_cone.add_to_scene(self.scene)

        for i in range(1, AccelerationGenerator.TRACK_WIDTH):      
            stop_cone = left_cone.get_cone_at_relative_meters(relative_lng=1, new_cone_type=ConeType.Orange)
            stop_cone.add_to_scene(self.scene)


class SkidTrackGenerator(_EventGenerator):
    INNER_RADIUS = 15.25/2
    TRACK_WIDTH = 3
    OUTER_RADIUS = INNER_RADIUS + TRACK_WIDTH
    START_ROAD_LENGTH = 15
    END_ROAD_LENGTH = 25
    ROAD_OFFSET_FROM_VERTICAL_CENTER = 10
    INNER_CONES_COUNT = 16
    OUTER_CONES_COUNT = 13

    def __init__(self, scene_name, scene_description, terrain, ego_car, timeout=30):
        super().__init__(scene_name, scene_description, terrain, ego_car, timeout=timeout)

    def generate_cones(self):
        staging_latitude = PositionCalc.add_meters_to_lat(self.start_lat, 1)
        left_lng = PositionCalc.add_meters_to_lng(self.start_lng, staging_latitude, -SkidTrackGenerator.TRACK_WIDTH/2)
        right_lng = PositionCalc.add_meters_to_lng(self.start_lng, staging_latitude, SkidTrackGenerator.TRACK_WIDTH/2)
        
        right_cone = Cone(ConeType.Orange, staging_latitude, right_lng)
        right_cone.add_to_scene(self.scene)
        left_cone = Cone(ConeType.Orange, staging_latitude, left_lng)
        left_cone.add_to_scene(self.scene)
        
        for i in range(0, SkidTrackGenerator.START_ROAD_LENGTH - SkidTrackGenerator.ROAD_OFFSET_FROM_VERTICAL_CENTER, 5):   
            right_cone = right_cone.get_cone_at_relative_meters(relative_lat=5)
            right_cone.add_to_scene(self.scene)
            left_cone = left_cone.get_cone_at_relative_meters(relative_lat=5)
            left_cone.add_to_scene(self.scene)
        
        right_cone = right_cone.get_cone_at_relative_meters(relative_lat=SkidTrackGenerator.ROAD_OFFSET_FROM_VERTICAL_CENTER * 2)
        right_cone.add_to_scene(self.scene)
        left_cone = left_cone.get_cone_at_relative_meters(relative_lat=SkidTrackGenerator.ROAD_OFFSET_FROM_VERTICAL_CENTER * 2)
        left_cone.add_to_scene(self.scene)
        
        for i in range(SkidTrackGenerator.ROAD_OFFSET_FROM_VERTICAL_CENTER, SkidTrackGenerator.END_ROAD_LENGTH, 5):   
            right_cone = right_cone.get_cone_at_relative_meters(relative_lat=5)
            right_cone.add_to_scene(self.scene)
            left_cone = left_cone.get_cone_at_relative_meters(relative_lat=5)
            left_cone.add_to_scene(self.scene)

        inner_radius = SkidTrackGenerator.INNER_RADIUS
        outer_radius = SkidTrackGenerator.OUTER_RADIUS

        circle_center_lat = PositionCalc.add_meters_to_lat(staging_latitude, SkidTrackGenerator.START_ROAD_LENGTH)
        left_circle_center_lng = PositionCalc.add_meters_to_lng(self.start_lng, circle_center_lat, -SkidTrackGenerator.TRACK_WIDTH/2 - inner_radius)
        right_circle_center_lng = PositionCalc.add_meters_to_lng(self.start_lng, circle_center_lat, SkidTrackGenerator.TRACK_WIDTH/2 + inner_radius)


        left_inner_angles = np.linspace(0, np.pi * 2, SkidTrackGenerator.INNER_CONES_COUNT, endpoint=False)
        left_inner_lng = PositionCalc.add_meters_to_lng(left_circle_center_lng, circle_center_lat, np.cos(left_inner_angles) * inner_radius)
        left_inner_lat = PositionCalc.add_meters_to_lat(circle_center_lat, np.sin(left_inner_angles) * inner_radius)
        
        left_outer_angles = np.concatenate(([np.arccos(inner_radius/outer_radius)], left_inner_angles[3:-2], [-np.arccos(inner_radius/outer_radius)]))
        left_outer_lng = PositionCalc.add_meters_to_lng(left_circle_center_lng, circle_center_lat, np.cos(left_outer_angles) * outer_radius)
        left_outer_lat = PositionCalc.add_meters_to_lat(circle_center_lat, np.sin(left_outer_angles) * outer_radius)

        right_inner_angles = np.linspace(np.pi, np.pi * 3, SkidTrackGenerator.INNER_CONES_COUNT, endpoint=False)
        right_inner_lng = PositionCalc.add_meters_to_lng(right_circle_center_lng, circle_center_lat, np.cos(right_inner_angles) * inner_radius)
        right_inner_lat = PositionCalc.add_meters_to_lat(circle_center_lat, np.sin(right_inner_angles) * inner_radius)

        right_outer_angles = np.concatenate(([np.arccos(-inner_radius/outer_radius)], right_inner_angles[3:-2], [-np.arccos(-inner_radius/outer_radius)]))
        right_outer_lng = PositionCalc.add_meters_to_lng(right_circle_center_lng, circle_center_lat, np.cos(right_outer_angles) * outer_radius)
        right_outer_lat = PositionCalc.add_meters_to_lat(circle_center_lat, np.sin(right_outer_angles) * outer_radius)

        for lat, lng in zip(left_inner_lat, left_inner_lng):
            Cone(ConeType.Blue, lat, lng).add_to_scene(self.scene)

        for lat, lng in zip(left_outer_lat, left_outer_lng):
            Cone(ConeType.Yellow, lat, lng).add_to_scene(self.scene)

        for lat, lng in zip(right_inner_lat, right_inner_lng):
            Cone(ConeType.Yellow, lat, lng).add_to_scene(self.scene)

        for lat, lng in zip(right_outer_lat, right_outer_lng):
            Cone(ConeType.Blue, lat, lng).add_to_scene(self.scene)

        angle_diff = (right_inner_angles[1] - right_inner_angles[0]) / 2

        lng = PositionCalc.add_meters_to_lng(right_circle_center_lng, circle_center_lat, np.cos(right_inner_angles[0] + angle_diff) * inner_radius)
        lat = PositionCalc.add_meters_to_lat(circle_center_lat, np.sin(right_inner_angles[0] + angle_diff) * inner_radius)
        Cone(ConeType.BigOrange, lat, lng).add_to_scene(self.scene)

        lng = PositionCalc.add_meters_to_lng(right_circle_center_lng, circle_center_lat, np.cos(right_inner_angles[0] - angle_diff) * inner_radius)
        lat = PositionCalc.add_meters_to_lat(circle_center_lat, np.sin(right_inner_angles[0] - angle_diff) * inner_radius)
        Cone(ConeType.BigOrange, lat, lng).add_to_scene(self.scene)

        lng = PositionCalc.add_meters_to_lng(left_circle_center_lng, circle_center_lat, np.cos(left_inner_angles[0] + angle_diff) * inner_radius)
        lat = PositionCalc.add_meters_to_lat(circle_center_lat, np.sin(left_inner_angles[0] + angle_diff) * inner_radius)
        Cone(ConeType.BigOrange, lat, lng).add_to_scene(self.scene)

        lng = PositionCalc.add_meters_to_lng(left_circle_center_lng, circle_center_lat, np.cos(left_inner_angles[0] - angle_diff) * inner_radius)
        lat = PositionCalc.add_meters_to_lat(circle_center_lat, np.sin(left_inner_angles[0] - angle_diff) * inner_radius)
        Cone(ConeType.BigOrange, lat, lng).add_to_scene(self.scene)