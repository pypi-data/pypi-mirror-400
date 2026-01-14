import subprocess
import re
import math
import numpy as np

from xml.etree import ElementTree as ET


def get_sim_objects(world_file: str):
    """Get the included objects names and poses in the simulation.
    Returns a list of dict in this format:
    {
        "name": "green_apple"
        "pose": "0.20 0 1.0 0 0 0"
    }
    as well as a dict in this format;
    {
        "green_apple": "0.20 0 1.0 0 0 0",
    }
    """
    objects = []
    try:
        tree = ET.parse(world_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"File {world_file} not found, check your pathing.")

    root = tree.getroot()
    # Find all model elements
    for model in root.find("world").findall("model"):
        if "name" in model.attrib:
            object = {}
            object["name"] = model.get("name")
            # Check if the model has a 'pose' element and add it to the dictionary
            pose = model.find("pose")
            if pose is not None:
                object["pose"] = pose.text
            objects.append(object)

    objects_positions = {
        obj["name"]: [float(v) for v in obj["pose"].split(" ")[:3]]
        for obj in objects
        if "pose" in obj
    }
    # first one is legacy format for rc0, second one is new convenience format
    return objects, objects_positions


def get_model_location(model_name):
    """
    Function to get the location of a model
    """

    command = ["gz", "model", "-m", model_name, "-p"]

    try:
        result = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        result_output = result.stdout.read().decode("utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(
            "Gazebo not found in the system. Please install / source Gazebo."
        )

    x_variable = 0.0
    y_variable = 0.0
    z_variable = 0.0

    # Extract position data if it exists
    position_pattern = r"\[(.*?)\]"

    # Search for all matching instances of the list pattern in the text
    matches = re.findall(position_pattern, result_output)

    if len(matches) >= 2:
        position = matches[-2]

        # Extract the individual numbers from the matched string
        numbers = re.findall(r"[\d.-]+", position)

        if len(numbers) >= 3:
            x_variable = float(numbers[0])
            y_variable = float(numbers[1])
            z_variable = float(numbers[2])

        else:
            x_variable = 0.0
            y_variable = 0.0
            z_variable = 0.0
    else:
        print("No x, y, or z variables found in the text.")

    return x_variable, y_variable, z_variable


def kill_gazebo():
    """kill the gazebo process. Tested with harmonic"""
    try:
        subprocess.run(["pkill", "-f", "gz sim server"], check=True)
        subprocess.run(["pkill", "-f", "gz sim gui"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error killing gazebo: {e}")


def make_actor(
    actor_name,
    waypoints,
    walk_speed=0.8,
    rotate_speed=1.8,
    enable_loop=True,
    output_type="xml",
):
    """
    Generate XML for actor based on waypoints and walk_speed, rotate_speed.
    Notes:
        - waypoints (assume walking in x-y plane):
            - position + rotation: waypoints = [[x, y, z, roll, pitch, yaw], ..]
            - position only: waypoints = [[x,y,z], ..]

        - output_type: 'xml' or 'str' -> returns 'xml' object or string
    """

    # initial checks:
    try:
        waypoints_np = np.array(waypoints)
        if waypoints_np.shape[1] not in [3, 6]:
            raise Exception(
                "Waypoints in wrong format. Expect: [[x,y,z], ..] or [[x,y,z,roll,pitch,yaw], ..]"
            )

    except ValueError:
        raise ValueError("Waypoints data inconsistent")
        return

    if output_type not in ["xml", "str"]:
        raise Exception(
            "Unknown output type. Expect: 'xml' for object, or 'str' for string"
        )

    # preprocessing: if loop enabled, last pose should be same as first pose
    if enable_loop and waypoints[0] != waypoints[-1]:
        waypoints.append(waypoints[0])

    # contains the states for each waypoint attribute
    waypoint_data = {k: [] for k in ["delta_t", "x", "y", "z", "roll", "pitch", "yaw"]}

    def _add_waypoint_data(values):
        for k, v in zip(waypoint_data.keys(), values):
            waypoint_data[k].append(v)

    delta_t = 0  # elapsed time from beginning

    # iterate to fill waypoint states
    for i, waypoint in enumerate(waypoints):
        x, y, z, roll, pitch, yaw = 0, 0, 1.0, 0, 0, 0

        if i == 0:  # 1st pose
            x, y, yaw = (
                waypoint[0],
                waypoint[1],
                waypoint[5] if len(waypoint) == 6 else 0,
            )

        else:  # next poses
            if len(waypoint) == 6:  # position + rotation
                x, y, z, roll, pitch, yaw = waypoint

                delta_x = x - x_prev
                delta_y = y - y_prev
                delta_yaw = yaw - yaw_prev

                delta_s = math.sqrt(delta_x**2 + delta_y**2)  # traversed distance

                delta_t = delta_t + delta_s / walk_speed + abs(delta_yaw) / rotate_speed

            elif len(waypoint) == 3:  # position only
                x, y, z = waypoint

                delta_x = x - x_prev
                delta_y = y - y_prev
                yaw = np.arctan2(
                    delta_y, delta_x
                )  # yaw computed based on heading direction of next waypoint
                delta_yaw = abs(yaw - yaw_prev)

                if i > 1 and delta_yaw != 0:
                    # rotate first before move (keep same position, only change rotation)
                    delta_t = delta_t + delta_yaw / rotate_speed
                    _add_waypoint_data([delta_t, x_prev, y_prev, z, roll, pitch, yaw])

                delta_s = math.sqrt(delta_x**2 + delta_y**2)  # traversed distance

                delta_t = delta_t + delta_s / walk_speed

        x_prev, y_prev, yaw_prev = x, y, yaw

        # move to next waypoint
        _add_waypoint_data([delta_t, x, y, z, roll, pitch, yaw])

    # post-processing waypoint states:
    # - if position-only, 1st yaw should be same as 2nd, instead of 0
    # - if loop enabled, rotation in last pose should be same as first pose
    if len(waypoints[0]) == 3:
        waypoint_data["yaw"][0] = waypoint_data["yaw"][1]

    if enable_loop:
        delta_yaw = abs(waypoint_data["yaw"][0] - waypoint_data["yaw"][-1])

        if delta_yaw != 0:
            delta_t = delta_t + delta_yaw / rotate_speed
            # no moving, only rotate
            _add_waypoint_data(
                [
                    delta_t,
                    waypoint_data["x"][-1],
                    waypoint_data["y"][-1],
                    waypoint_data["z"][-1],
                    waypoint_data["roll"][-1],
                    waypoint_data["pitch"][-1],
                    waypoint_data["yaw"][0],
                ]
            )

    # create actor_xml object
    actor_xml_str = """
    <actor>
        <skin>
            <filename>https://fuel.gazebosim.org/1.0/Mingfei/models/actor/tip/files/meshes/walk.dae</filename>
        </skin>
        
        <animation name="walking">
            <filename>https://fuel.gazebosim.org/1.0/Mingfei/models/actor/tip/files/meshes/walk.dae</filename>
            <interpolate_x>true</interpolate_x>
        </animation>

        <script>
            <loop></loop>
            <delay_start>0.0</delay_start>
            <auto_start>true</auto_start>
            
            <trajectory id="0" type="walking">
            </trajectory>
        </script>
    </actor>
    """

    actor_xml = ET.fromstring(actor_xml_str)
    actor_xml.set("name", actor_name)
    actor_xml.find("./script/loop").text = "true" if enable_loop else "false"

    # create each waypoint_xml object, then insert into actor_xml
    waypoint_xml_str = """
    <waypoint>
        <time />
        <pose />
    </waypoint>
    """

    for i in range(len(waypoint_data["delta_t"])):
        waypoint_xml = ET.fromstring(waypoint_xml_str)
        waypoint_xml.find("./time").text = str(waypoint_data["delta_t"][i])
        waypoint_xml.find(
            "./pose"
        ).text = f"{waypoint_data['x'][i]} {waypoint_data['y'][i]} {waypoint_data['z'][i]} {waypoint_data['roll'][i]} {waypoint_data['pitch'][i]} {waypoint_data['yaw'][i]}"

        actor_xml.find("./script/trajectory").insert(i, waypoint_xml)

    return actor_xml if output_type == "xml" else serialize_xml(actor_xml)


def load_world(world_file: str):
    try:
        world_xml = ET.parse(world_file)
        world_xml = world_xml.getroot()

    except FileNotFoundError:
        raise FileNotFoundError(f"File {world_file} not found, check your path.")

    return world_xml


def add_entity(world_xml, entity_xml):
    """
    Insert entity_xml into first child of world_xml (in-place operation)

    Note:
        world_xml: In format '<sdf>...</sdf>'. Type: xml.etree.ElementTree.Element
        entity_xml: Type: xml.etree.ElementTree.Element

    """

    world_xml.find('./world').insert(0, entity_xml)


def serialize_xml(xml_object, space="\t"):
    # pretty re-format xml
    ET.indent(xml_object, space=space, level=0)

    return ET.tostring(xml_object, encoding="unicode")
