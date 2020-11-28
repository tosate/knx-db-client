#!/usr/bin/env python

from knx_db_client import *
import sys

MY_PROJECT_NAME = 'My Project'

try:
    client = knx_db_client.KnxDbClient()
    project_list = client.get_project_list(MY_PROJECT_NAME)
    print(f'{len(project_list)} project(s) found!')
except ValueError:
    print('Retrieving the project did not work')
    sys.exit()
