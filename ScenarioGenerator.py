import argparse
import cognata_api
from cognata_api.scenario.conversions import kph_2_ms
from cognata_api.web_api.cognata_demo import CognataRequests as cog_api
from cognata_api.scenario.variable import Variable
import cognata_api.scenario.actor_script as Script
import cognata_api.scenario.position as Position
import cognata_api.scenario.ai_vehicle as AiVehicle
from cognata_api.scenario.scenario import Scenario
from cognata_api.scenario.terrain import Terrain
from cognata_api.scenario.rule_gen.rules_gen import *
import PositionCalc
import events_generator

def main():
    parser = argparse.ArgumentParser("Cognata Scenerio Generator")
    parser.add_argument("-c", "--company", required=True)
    parser.add_argument("-u", "--user", required=True)
    parser.add_argument("-p", "--password", required=True)
    args = parser.parse_args()

    company_id = args.company
    username = args.user
    password = args.password

    #################################################################################################
    # Create api connection to studio cloud instance
    # connects through API url
    backendIP = "https://{}-api.cognata-studio.com/v1".format(company_id)
    api = cog_api(backendIP, username, password)

    if not api.is_logged_in:
        raise ValueError("Please fill in the variables in the designated cell")
    print("Connected")

    ########################################################################################################
    # Create map of names:sku
    maps = {x['name']: x['sku'] for x in api.get_maps_list()}

    presets = {x['name']: x['sku'] for x in api.get_ego_cars_list()}

    # Create Terrain
    terrain = Terrain(maps["Synthetic Single"])

    # Create ego car

    ## Create Ego car scripts

    ## Create ego car spawn position
    ego_spawn_position = Position.create_position(lane=-1,
                                                  lat=41.712683,
                                                  lng=-116.948111)
    destination_position = None
    ego_car = AiVehicle.create_ego_car(
        spawn_pos=ego_spawn_position,
        sku=presets["DemoPreset"],
        dest_pos=destination_position,
        initial_speed=5,
        desired_speed=5,
        scripts=[]
    )

    # Create Scenario
    scene = events_generator.AccelerationGenerator("test acceleration 2", "testing the cones", terrain, ego_car, timeout=30)
    # scene = events_generator.SkidTrackGenerator("test skidtrack 2", "testing the cones", terrain, ego_car, timeout=30)
    scene.generate_cones()
    # print(api.get_scenrios_list())
    scene.create_scenario(api)

if __name__ == '__main__':
    main()