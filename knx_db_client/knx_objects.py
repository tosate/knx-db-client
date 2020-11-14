class GroupAddress:
    GROUP_ADDRESS_ID = 'groupAddressId'
    MAIN_GROUP = 'mainGroup'
    MIDDLE_GROUP = 'middleGroup'
    SUB_GROUP = 'subGroup'
    DATA_TYPE = 'dataType'
    FUNCTION = 'function'

    def __init__(self, main_group: int, middle_group: int, sub_group: int, function: str = None, data_type: str = None):
        self.group_address_id = None
        self.main_group = main_group
        self.middle_group = middle_group
        self.sub_group = sub_group
        self.function = function
        self.data_type = data_type
        self.device = None

    def get_main_group(self) -> int:
        return self.main_group

    def get_middle_group(self) -> int:
        return self.middle_group

    def get_sub_group(self):
        return self.sub_group

    def set_group_address_id(self, group_address_id: int):
        self.group_address_id = group_address_id

    def get_group_address_id(self):
        return self.group_address_id

    def set_data_type(self, data_type: str):
        self.data_type = data_type

    def get_data_type(self):
        return self.data_type

    def set_function(self, function: str):
        self.function = function

    def get_function(self):
        return self.function

    def set_device(self, device):
        self.device = device

    def get_device(self):
        return self.device

    def get_address(self) -> str:
        return f'{self.main_group}/{self.middle_group}/{self.sub_group}'

    def get_data(self) -> dict:
        result = {}
        if self.group_address_id is not None:
            result[self.GROUP_ADDRESS_ID] = self.group_address_id

        result[self.MAIN_GROUP] = self.main_group
        result[self.MIDDLE_GROUP] = self.middle_group
        result[self.SUB_GROUP] = self.sub_group

        if self.data_type is not None:
            result[self.DATA_TYPE] = self.data_type

        if self.function is not None:
            result[self.FUNCTION] = self.function

        return result

    @staticmethod
    def group_address_decoder(group_address_json: dict):
        result = GroupAddress(group_address_json[GroupAddress.MAIN_GROUP],
                              group_address_json[GroupAddress.MIDDLE_GROUP], group_address_json[GroupAddress.SUB_GROUP])
        result.set_group_address_id(group_address_json[GroupAddress.GROUP_ADDRESS_ID])

        if group_address_json[GroupAddress.DATA_TYPE] is not None:
            result.set_data_type(group_address_json[GroupAddress.DATA_TYPE])

        if group_address_json[GroupAddress.FUNCTION] is not None:
            result.set_function(group_address_json[GroupAddress.FUNCTION])

        return result

    @staticmethod
    def group_address_list_decoder(group_address_list_json: dict) -> list:
        result = []
        for group_address_json in group_address_list_json:
            result.append(GroupAddress.group_address_decoder(group_address_json))

        return result


class Device:
    DEVICE_ID = 'deviceid'
    LABEL = 'label'
    NAME_AFFIX = 'nameAffix'
    DEVICE_TYPE = 'deviceType'
    GROUP_ADDRESSES = 'groupAddresses'

    def __init__(self, label: str, device_type: str):
        self.device_id = None
        self.label = label
        self.name_affix = None
        self.device_type = device_type
        self.group_addresses = []
        self.room = None

    def set_name_affix(self, name_affix: str):
        self.name_affix = name_affix

    def get_name_affix(self) -> str:
        return self.name_affix

    def set_device_id(self, device_id: int):
        self.device_id = device_id

    def get_device_id(self):
        return self.device_id

    def add_group_address(self, group_address: GroupAddress):
        group_address.set_device(self)
        self.group_addresses.append(group_address)

    def get_label(self) -> str:
        return self.label

    def get_room(self):
        return self.room

    def set_room(self, room):
        self.room = room

    def get_group_addresses(self) -> list:
        return self.group_addresses

    def get_data(self) -> dict:
        result = {}
        if self.device_id is not None:
            result[self.DEVICE_ID] = self.device_id

        result[self.LABEL] = self.label
        if self.name_affix is not None:
            result[self.NAME_AFFIX] = self.name_affix
        result[self.DEVICE_TYPE] = self.device_type

        return result

    @staticmethod
    def device_decoder(device_json: dict):
        result = Device(device_json[Device.LABEL], device_json[Device.DEVICE_TYPE])
        if device_json[Device.NAME_AFFIX]:
            result.set_name_affix(device_json[Device.NAME_AFFIX])
        result.set_device_id(device_json[Device.DEVICE_ID])

        return result

    @staticmethod
    def device_list_decoder(device_list_json: dict) -> list:
        result = []
        for device_json in device_list_json:
            result.append(Device.device_decoder(device_json))

        return result


class Room:
    ROOM_ID = 'roomid'
    NAME = 'name'
    LABEL = 'label'
    FLOOR = 'floor'
    DEVICES = 'devices'

    def __init__(self, name: str, label: str, floor: str = None):
        self.room_id = None
        self.name = name
        self.label = label
        self.floor = floor
        self.devices = []
        self.project = None

    def set_room_id(self, room_id: int):
        self.room_id = room_id

    def get_room_id(self) -> int:
        return self.room_id

    def set_floor(self, floor: str):
        self.floor = floor

    def add_device(self, device: Device):
        device.set_room(self)
        self.devices.append(device)

    def get_name(self) -> str:
        return self.name

    def get_project(self):
        return self.project

    def set_project(self, project):
        self.project = project

    def get_devices(self) -> list:
        return self.devices

    def get_data(self) -> dict:
        result = {}
        if self.room_id is not None:
            result[self.ROOM_ID] = self.room_id

        result[self.NAME] = self.name
        result[self.LABEL] = self.label

        if self.floor is not None:
            result[self.FLOOR] = self.floor

        return result

    @staticmethod
    def room_decoder(room_json: dict):
        result = Room(room_json[Room.NAME], room_json[Room.LABEL])
        result.set_room_id(room_json[Room.ROOM_ID])
        if room_json[Room.FLOOR] and len(room_json[Room.FLOOR]) > 0:
            result.set_floor(room_json[Room.FLOOR])

        return result

    @staticmethod
    def room_list_decoder(room_list_json: dict) -> list:
        result = []
        for room_json in room_list_json:
            result.append(Room.room_decoder(room_json))

        return result


class Project:
    PROJECT_ID = 'projectid'
    NAME = 'name'
    ROOMS = 'rooms'

    def __init__(self, name: str):
        self.project_id = None
        self.name = name
        self.rooms = []

    def add_room(self, room: Room) -> None:
        room.set_project(self)
        self.rooms.append(room)

    def set_project_id(self, project_id: int) -> None:
        self.project_id = project_id

    def get_project_id(self) -> int:
        return self.project_id

    def get_name(self) -> str:
        return self.name

    def get_data(self) -> dict:
        result = {}
        if self.project_id is not None:
            result[self.PROJECT_ID] = self.project_id

        result[self.NAME] = self.name

        return result

    def get_rooms(self) -> list:
        return self.rooms

    @staticmethod
    def project_decoder(project_json: dict):
        result = Project(project_json[Project.NAME])
        result.set_project_id(project_json[Project.PROJECT_ID])

        return result

    @staticmethod
    def project_list_decoder(project_list_json: list) -> list:
        result = []
        for project_json in project_list_json:
            result.append(Project.project_decoder(project_json))

        return result
