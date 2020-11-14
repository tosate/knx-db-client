import requests
import json
from http import HTTPStatus
from knx_db_client import knx_objects

BASE_PATH = '/knx-db'
HEADER_CONTENT_TYPE = 'Content-type'
HEADER_ACCEPT = 'Accept'
APPLICATION_JSON = 'application/json'
HOST = 'localhost'
PORT = 8081


class KnxDbClient:
    URL_START = f'http://{HOST}:{PORT}{BASE_PATH}'

    @staticmethod
    def get_project_list(filter_by_name: str = None) -> list:
        try:
            project_list = KnxDbClient.__get_project_list_request(filter_by_name)
            for project in project_list:
                rooms_list = KnxDbClient.get_room_list(project.get_project_id())
                for room in rooms_list:
                    project.add_room(room)
            return project_list
        except ValueError as err:
            print(f'Get project list failed: {err}')

    @staticmethod
    def get_room_list(project_id: int) -> list:
        try:
            room_list = KnxDbClient.__get_room_list_request(project_id)
            for room in room_list:
                device_list = KnxDbClient.get_device_list(room.get_room_id(), project_id)
                for device in device_list:
                    room.add_device(device)
            return room_list
        except ValueError as err:
            print(f'Get room list failed: {err}')

    @staticmethod
    def get_device_list(room_id: int, project_id) -> list:
        try:
            device_list = KnxDbClient.__get_device_list_request(room_id, project_id)
            for device in device_list:
                group_address_list = KnxDbClient.get_group_address_list(device.get_device_id(), room_id, project_id)
                for address in group_address_list:
                    device.add_group_address(address)
            return device_list
        except ValueError as err:
            print(f'Get device list failed: {err}')

    @staticmethod
    def get_group_address_list(device_id: int, room_id: int, project_id: int) -> list:
        try:
            return KnxDbClient.__get_group_address_list_request(device_id, room_id, project_id)
        except ValueError as err:
            print(f'Get group address list failed: {err}')

    @staticmethod
    def create_project(project_to_save: knx_objects.Project) -> knx_objects.Project:
        if project_to_save is None:
            raise ValueError('Project has no value!')
        try:
            project = KnxDbClient.__create_project_request(project_to_save)
            project_to_save.set_project_id(project.get_project_id())
            for room_to_save in project_to_save.get_rooms():
                KnxDbClient.create_room(room_to_save)
            return project_to_save
        except ValueError as err:
            print(f'Saving project failed: {err}')

    @staticmethod
    def create_room(room_to_save: knx_objects.Room) -> knx_objects.Room:
        if room_to_save is None:
            raise ValueError('Room has no value!')
        if room_to_save.get_project() is None:
            raise ValueError('Room has no parent project!')
        if room_to_save.get_project().get_project_id() is None:
            raise ValueError('Parent project has no ID!')
        try:
            room = KnxDbClient.__create_room_request(room_to_save, room_to_save.get_project().get_project_id())
            room_to_save.set_room_id(room.get_room_id())
            for device_to_save in room_to_save.get_devices():
                KnxDbClient.create_device(device_to_save)
            return room_to_save
        except ValueError as err:
            print(f'Saving room failed: {err}')

    @staticmethod
    def create_device(device_to_save: knx_objects.Device) -> knx_objects.Device:
        if device_to_save.get_room() is None:
            raise ValueError('Device to save has no parent room')
        if device_to_save.get_room().get_room_id() is None:
            raise ValueError('Parent room has no room ID')
        if device_to_save.get_room().get_project() is None:
            raise ValueError('Room has no parent project!')
        if device_to_save.get_room().get_project().get_project_id() is None:
            raise ValueError('Parent project has no ID!')
        try:
            device = KnxDbClient.__create_device_request(device_to_save, device_to_save.get_room().get_room_id(),
                                                         device_to_save.get_room().get_project().get_project_id())
            device_to_save.set_device_id(device.get_device_id())
            for address_to_save in device_to_save.get_group_addresses():
                KnxDbClient.create_group_address(address_to_save)
            return device_to_save
        except ValueError as err:
            print(f'Saving device failed: {err}')

    @staticmethod
    def create_group_address(address_to_save: knx_objects.GroupAddress) -> knx_objects.GroupAddress:
        if address_to_save.get_device() is None:
            raise ValueError('Group address has no parent device')
        if address_to_save.get_device().get_device_id() is None:
            raise ValueError('Parent device has no device ID')
        if address_to_save.get_device().get_room() is None:
            raise ValueError('Group Address has no parent room')
        if address_to_save.get_device().get_room().get_room_id() is None:
            raise ValueError('Parent room has no room ID')
        if address_to_save.get_device().get_room().get_project() is None:
            raise ValueError('Group Address has no parent project')
        if address_to_save.get_device().get_room().get_project().get_project_id() is None:
            raise ValueError('Parent project has no ID')
        try:
            device = address_to_save.get_device()
            address = KnxDbClient.__create_group_address_request(address_to_save,
                                                                 device.get_device_id(),
                                                                 device.get_room().get_room_id(),
                                                                 device.get_room().get_project().get_project_id())
            address_to_save.set_group_address_id(address.get_group_address_id())
            return address_to_save
        except ValueError as err:
            print(f'Saving group address failed: {err}')

    @staticmethod
    def delete_project(project: knx_objects.Project):
        for room in KnxDbClient.get_room_list(project.get_project_id()):
            KnxDbClient.delete_room(room, project.get_project_id())
        KnxDbClient.__delete_project_request(project)

    @staticmethod
    def delete_room(room: knx_objects.Room, project_id: int):
        for device in KnxDbClient.get_device_list(room.get_room_id(), project_id):
            KnxDbClient.delete_device(device, room.get_room_id(), project_id)
        KnxDbClient.__delete_room_request(room, project_id)

    @staticmethod
    def delete_device(device: knx_objects.Device, room_id: int, project_id: int):
        for address in KnxDbClient.get_group_address_list(device.get_device_id(), room_id, project_id):
            KnxDbClient.delete_group_address(address, device.get_device_id(), room_id, project_id)
        KnxDbClient.__delete_device_request(device, room_id, project_id)

    @staticmethod
    def delete_group_address(address: knx_objects.GroupAddress, device_id: int, room_id: int, project_id: int):
        KnxDbClient.__delete_group_address_request(address, device_id, room_id, project_id)

    @staticmethod
    def __create_project_request(project: knx_objects.Project) -> knx_objects.Project:
        request_headers = {HEADER_CONTENT_TYPE: APPLICATION_JSON, HEADER_ACCEPT: APPLICATION_JSON}
        response = requests.post(f'{KnxDbClient.URL_START}/projects', data=json.dumps(project.get_data()),
                                 headers=request_headers)
        if response.status_code == HTTPStatus.CREATED:
            print(f'Project [{project.get_name()}] saved')
            return knx_objects.Project.project_decoder(json.loads(response.text))
        else:
            raise ValueError(f'Create project returned HTTP status [{response.status_code}], error: {response.text}')

    @staticmethod
    def __replace_project_request(project: knx_objects.Project) -> knx_objects.Project:
        if project.project_id is None:
            raise ValueError(f'Project ID cannot be empty')
        request_headers = {HEADER_CONTENT_TYPE: APPLICATION_JSON, HEADER_ACCEPT: APPLICATION_JSON}
        response = requests.put(f'{KnxDbClient.URL_START}/projects/{project.get_project_id()}',
                                data=json.dumps(project.get_data()), headers=request_headers)
        if response.status_code == HTTPStatus.OK:
            print(f'Project [{project.get_name()}] replaced')
            return knx_objects.Project.project_decoder(json.loads(response.text))
        else:
            raise ValueError(f'Replace project returned HTTP status [{response.status_code}], error: {response.text}')

    @staticmethod
    def __get_project_request(project_id: int) -> knx_objects.Project:
        request_headers = {HEADER_ACCEPT: APPLICATION_JSON}
        response = requests.get(f'{KnxDbClient.URL_START}/projects/{project_id}', headers=request_headers)
        if response.status_code == HTTPStatus.OK:
            print(f'Retrieved project with ID [{project_id}]')
            return knx_objects.Project.project_decoder(json.loads(response.text))
        else:
            raise ValueError(f'Get project returned HTTP status [{response.status_code}] and error: {response.text}')

    @staticmethod
    def __get_project_list_request(filter_by_name: str = None) -> list:
        request_headers = {HEADER_ACCEPT: APPLICATION_JSON}
        url = f'{KnxDbClient.URL_START}/projects'
        if filter_by_name is not None:
            url = url + f'?name={filter_by_name}'
        response = requests.get(url, headers=request_headers)
        if response.status_code == HTTPStatus.OK:
            print('Project list retrieved')
            return knx_objects.Project.project_list_decoder(json.loads(response.text))
        else:
            raise ValueError(f'Get project list returned HTTP status [{response.status_code}], error: {response.text}')

    @staticmethod
    def __delete_project_request(project: knx_objects.Project) -> bool:
        if project.get_project_id() is None:
            raise ValueError('Unable to delete project: project has no ID')
        request_headers = {HEADER_ACCEPT: APPLICATION_JSON}
        response = requests.delete(f'{KnxDbClient.URL_START}/projects/{project.get_project_id()}',
                                   headers=request_headers)
        if response.status_code == HTTPStatus.OK:
            print(f'Project [{project.get_name()}] deleted')
            return True
        else:
            print(f'Delete project returned HTTP status [{response.status_code}] and error: {response.text}')
            return False

    @staticmethod
    def __create_room_request(room: knx_objects.Room, project_id: int) -> knx_objects.Room:
        if project_id is None:
            raise ValueError('Unable to add room: invalid parent project ID')

        if project_id is None:
            raise ValueError('Unable to add room: invalid project ID')

        request_headers = {HEADER_CONTENT_TYPE: APPLICATION_JSON, HEADER_ACCEPT: APPLICATION_JSON}
        response = requests.post(f'{KnxDbClient.URL_START}/projects/{project_id}/rooms',
                                 data=json.dumps(room.get_data()), headers=request_headers)
        if response.status_code == HTTPStatus.CREATED:
            print(f'Room [{room.get_name()}] added to project with ID [{project_id}]')
            saved_room = knx_objects.Room.room_decoder(json.loads(response.text))
            room.set_room_id(saved_room.get_room_id())
            return room
        else:
            raise ValueError(f'Create room returned HTTP status [{response.status_code}] and error: {response.text}')

    @staticmethod
    def __get_room_request(project_id: int, room_id: int):
        request_headers = {HEADER_ACCEPT: APPLICATION_JSON}
        response = requests.get(f'{KnxDbClient.URL_START}/projects/{project_id}/rooms/{room_id}',
                                headers=request_headers)
        if response.status_code == HTTPStatus.OK:
            print(f'Retrieved room with ID [{room_id}]')
            return knx_objects.Room.room_decoder(json.loads(response.text))
        else:
            raise ValueError(f'Get room returned HTTP status [{response.status_code}] and error: {response.text}')

    @staticmethod
    def __delete_room_request(room: knx_objects.Room, project_id: int) -> bool:
        if room.get_room_id() is None:
            raise ValueError('Unable to delete room: room has no ID')
        if project_id is None:
            raise ValueError('Unable to delete room: invalid parent project ID')
        request_headers = {HEADER_ACCEPT: APPLICATION_JSON}
        response = requests.delete(
            f'{KnxDbClient.URL_START}/projects/{project_id}/rooms/{room.get_room_id()}',
            headers=request_headers)
        if response.status_code == HTTPStatus.OK:
            print(f'Room [{room.get_name()}] deleted')
            return True
        else:
            print(f'Delete room returned HTTP status [{response.status_code}] and error: {response.text}')
            return False

    @staticmethod
    def __create_device_request(device: knx_objects.Device, room_id: int, project_id: int) -> knx_objects.Device:
        if room_id is None:
            raise ValueError('Unable to save device: invalid parent room ID')
        if project_id is None:
            raise ValueError('Unable to save device: invalid parent project ID')
        device_json = device.get_data()
        request_headers = {HEADER_CONTENT_TYPE: APPLICATION_JSON, HEADER_ACCEPT: APPLICATION_JSON}
        response = requests.post(
            f'{KnxDbClient.URL_START}/projects/{project_id}/rooms/{room_id}/devices',
            data=json.dumps(device_json), headers=request_headers)
        if response.status_code == HTTPStatus.CREATED:
            print(f'Device [{device.get_label()}] added to room with ID [{room_id}]')
            return knx_objects.Device.device_decoder(json.loads(response.text))
        else:
            raise ValueError(f'Create device returned HTTP status [{response.status_code}], error: {response.text}')

    @staticmethod
    def __delete_device_request(device: knx_objects.Device, room_id: int, project_id: int) -> bool:
        if room_id is None:
            raise ValueError('Unable to delete device: invalid parent room ID')
        if project_id is None:
            raise ValueError('Unable to delete device: invalid parent project ID')
        request_headers = {HEADER_ACCEPT: APPLICATION_JSON}
        response = requests.delete(
            f'{KnxDbClient.URL_START}/projects/{project_id}/rooms/{room_id}/devices/{device.get_device_id()}',
            headers=request_headers)
        if response.status_code == HTTPStatus.OK:
            print(f'Device {device.get_label()} deleted')
            return True
        else:
            print(f'Delete device returned HTTP status [{response.status_code}] and error: {response.text}')
            return False

    @staticmethod
    def __delete_group_address_request(address: knx_objects.GroupAddress, device_id: int, room_id: int,
                                       project_id: int):
        if device_id is None:
            raise ValueError('Unable to delete group address: invalid parent device ID')
        if room_id is None:
            raise ValueError('Unable to delete group address: invalid parent room ID')
        if project_id is None:
            raise ValueError('Unable to delete group address: invalid parent project ID')
        request_headers = {HEADER_ACCEPT: APPLICATION_JSON}
        device_path = f'devices/{device_id}/group-addresses/{address.get_group_address_id()}'
        response = requests.delete(
            f'{KnxDbClient.URL_START}/projects/{project_id}/rooms/{room_id}/{device_path}',
            headers=request_headers)
        if response.status_code == HTTPStatus.OK:
            print(f'Group address {address.get_address()} deleted')
            return True
        else:
            print(f'Delete device returned HTTP status [{response.status_code}] and error: {response.text}')
            return False

    @staticmethod
    def __create_group_address_request(address: knx_objects.GroupAddress, device_id: int,
                                       room_id: int, project_id: int) -> knx_objects.GroupAddress:
        if device_id is None:
            raise ValueError('Unable to save group address: invalid parent device ID')
        if room_id is None:
            raise ValueError('Unable to save group address: invalid parent room ID')
        if project_id is None:
            raise ValueError('Unable to save group address: invalid parent project ID')
        address_json = address.get_data()
        request_headers = {HEADER_CONTENT_TYPE: APPLICATION_JSON, HEADER_ACCEPT: APPLICATION_JSON}
        response = requests.post(
            f'{KnxDbClient.URL_START}/projects/{project_id}/rooms/{room_id}/devices/{device_id}/group-addresses',
            data=json.dumps(address_json), headers=request_headers)
        if response.status_code == HTTPStatus.CREATED:
            ga = address.get_address()
            print(f'Group address [{ga}] added to device with ID [{device_id}]')
            return knx_objects.GroupAddress.group_address_decoder(json.loads(response.text))
        else:
            raise ValueError(
                f'Create group address returned HTTP status [{response.status_code}], error: {response.text}')

    @staticmethod
    def __get_room_list_request(project_id: int) -> list:
        if project_id is None:
            raise ValueError('Unable to retrieve room list: invalid project ID')
        request_headers = {HEADER_ACCEPT: APPLICATION_JSON}
        response = requests.get(f'{KnxDbClient.URL_START}/projects/{project_id}/rooms', headers=request_headers)
        if response.status_code == HTTPStatus.OK:
            print('Rooms list retrieved')
            return knx_objects.Room.room_list_decoder(json.loads(response.text))
        else:
            raise ValueError(f'Get room list returned HTTP status [{response.status_code}], error: {response.text}')

    @staticmethod
    def __get_device_list_request(room_id: int, project_id: int):
        if room_id is None:
            raise ValueError('Unable to retrieve device list: invalid room ID')
        if project_id is None:
            raise ValueError('Unable to retrieve device list: invalid project ID')
        request_headers = {HEADER_ACCEPT: APPLICATION_JSON}
        response = requests.get(f'{KnxDbClient.URL_START}/projects/{project_id}/rooms/{room_id}/devices',
                                headers=request_headers)
        if response.status_code == HTTPStatus.OK:
            print('Device list retrieved')
            return knx_objects.Device.device_list_decoder(json.loads(response.text))
        else:
            raise ValueError(f'Get device list returned HTTP status [{response.status_code}], error: {response.text}')

    @staticmethod
    def __get_group_address_list_request(device_id, room_id, project_id):
        if device_id is None:
            raise ValueError('Unable to retrieve group address list: invalid device ID')
        if room_id is None:
            raise ValueError('Unable to retrieve group address list: invalid room ID')
        if project_id is None:
            raise ValueError('Unable to retrieve group address list: invalid project ID')
        request_headers = {HEADER_ACCEPT: APPLICATION_JSON}
        response = requests.get(
            f'{KnxDbClient.URL_START}/projects/{project_id}/rooms/{room_id}/devices/{device_id}/group-addresses',
            headers=request_headers)
        if response.status_code == HTTPStatus.OK:
            print('Group address list retrieved')
            return knx_objects.GroupAddress.group_address_list_decoder(json.loads(response.text))
        else:
            raise ValueError(
                f'Get group address list returned HTTP status [{response.status_code}], error: {response.text}')
