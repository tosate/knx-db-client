#!/usr/bin/env python

from knx_db_client import *
import sys

try:
    project = knx_db_client.KnxDbClient.get_project(4)
    print(f'Project {project.get_name()} retrieved!')
except ValueError:
    print('Retrieving the project did not work')
    sys.exit()
