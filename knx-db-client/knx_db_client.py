import requests
import json
from http import HTTPStatus
import knx_objects

BASE_PATH = '/knx-db'
HEADER_CONTENT_TYPE = 'Content-type'
HEADER_ACCEPT = 'Accept'
APPLICATION_JSON = 'application/json'
HOST = 'localhost'
PORT = 8081


class KnxDbClient:
    URL_START = f'http://{HOST}:{PORT}{BASE_PATH}'

    @staticmethod
    def create_project(project: knx_objects.Project) -> knx_objects.Project:
        request_headers = {HEADER_CONTENT_TYPE: APPLICATION_JSON, HEADER_ACCEPT: APPLICATION_JSON}
        response = requests.post(f'{KnxDbClient.URL_START}/projects', data=json.dumps(project.get_data()),
                                 headers=request_headers)
        if response.status_code == HTTPStatus.CREATED:
            print(f'Project [{project.get_name()}] saved')
            return knx_objects.Project.project_decoder(json.loads(response.text))
        else:
            raise ValueError(f'Create project returned HTTP status [{response.status_code}]')

    @staticmethod
    def replace_project(project: knx_objects.Project) -> knx_objects.Project:
        if project.project_id is None:
            raise ValueError(f'Project ID cannot be empty')
        request_headers = {HEADER_CONTENT_TYPE: APPLICATION_JSON, HEADER_ACCEPT: APPLICATION_JSON}
        response = requests.put(f'{KnxDbClient.URL_START}/projects/{project.get_project_id()}',
                                data=json.dumps(project.get_data()), headers=request_headers)
        if response.status_code == HTTPStatus.OK:
            print(f'Project [{project.get_name()}] replaced')
            return knx_objects.Project.project_decoder(json.loads(response.text))
        else:
            raise ValueError(f'Replace project returned HTTP status [{response.status_code}]')

    @staticmethod
    def get_project(project_id: int) -> knx_objects.Project:
        request_headers = {HEADER_ACCEPT: APPLICATION_JSON}
        response = requests.get(f'{KnxDbClient.URL_START}/projects/{project_id}', headers=request_headers)
        if response.status_code == HTTPStatus.OK:
            print(f'Retrieved project with ID [{project_id}]')
            return knx_objects.Project.project_decoder(json.loads(response.text))
        else:
            raise ValueError(f'Get project returned HTTP status [{response.status_code}]')

    @staticmethod
    def delete_project(project: knx_objects.Project) -> bool:
        if project.get_project_id() is None:
            raise ValueError('Unable to delete project: project has no ID')
        request_headers = {HEADER_ACCEPT: APPLICATION_JSON}
        response = requests.delete(f'{KnxDbClient.URL_START}/projects/{project.get_project_id()}',
                                   headers=request_headers)
        if response.status_code == HTTPStatus.OK:
            print(f'Project [{project.get_name()}] deleted')
            return True
        else:
            print(f'Delete project returned HTTP status [{response.status_code}]')
            return False

    @staticmethod
    def add_room(room: knx_objects.Room) -> knx_objects.Room:
        if room.get_project() is None or room.get_project().get_project_id() is None:
            raise ValueError('Unable to add room: invalid parent project')

        request_headers = {HEADER_CONTENT_TYPE: APPLICATION_JSON, HEADER_ACCEPT: APPLICATION_JSON}
        response = requests.post(f'{KnxDbClient.URL_START}/projects/{room.get_project().get_project_id()}/rooms',
                                 data=json.dumps(room.get_data()), headers=request_headers)
        if response.status_code == HTTPStatus.CREATED:
            print(f'Room [{room.get_name()}] added to project [{room.get_project().get_name()}]')
            saved_room = knx_objects.Room.room_decoder(json.loads(response.text))
            room.set_room_id(saved_room.get_room_id())
            return room
        else:
            raise ValueError(f'Create room returned HTTP status [{response.status_code}]')

    @staticmethod
    def get_room(project_id: int, room_id: int):
        request_headers = {HEADER_ACCEPT: APPLICATION_JSON}
        response = requests.get(f'{KnxDbClient.URL_START}/projects/{project_id}/rooms/{room_id}',
                                headers=request_headers)
        if response.status_code == HTTPStatus.OK:
            print(f'Retrieved room with ID [{room_id}]')
            return knx_objects.Room.room_decoder(json.loads(response.text))
        else:
            raise ValueError(f'Get room returned HTTP status [{response.status_code}]')

    @staticmethod
    def delete_room(room: knx_objects.Room) -> bool:
        if room.get_room_id() is None:
            raise ValueError('Unable to delete room: room has no ID')
        if room.get_project() is None or room.get_project().get_project_id() is None:
            raise ValueError('Unable to delete room: invalid parent project')
        request_headers = {HEADER_ACCEPT: APPLICATION_JSON}
        response = requests.delete(
            f'{KnxDbClient.URL_START}/projects/{room.get_project().get_project_id()}/rooms/{room.get_room_id()}',
            headers=request_headers)
        if response.status_code == HTTPStatus.OK:
            print(f'Room [{room.get_name()}] deleted')
            return True
        else:
            print(f'Delete room returned HTTP status [{response.status_code}]')

    @staticmethod
    def add_device(device: knx_objects.Device, room: knx_objects.Room,
                   project: knx_objects.Project) -> knx_objects.Device:
        if room is None or room.get_room_id() is None:
            raise ValueError('Unable to save device: invalid parent room')
        device_json = device.get_data()
        request_headers = {HEADER_CONTENT_TYPE: APPLICATION_JSON, HEADER_ACCEPT: APPLICATION_JSON}
        response = requests.post(
            f'{KnxDbClient.URL_START}/projects/{project.get_project_id()}/rooms/{room.get_room_id()}/devices',
            data=device_json, headers=request_headers)
        if response.status_code == HTTPStatus.CREATED:
            print(f'Device [{device.get_label()}] added to room [{room.get_name()}]')
            return knx_objects.Device.device_decoder(json.loads(response.text))
        else:
            raise ValueError(f'Create device returned HTTP status [{response.status_code}]')
