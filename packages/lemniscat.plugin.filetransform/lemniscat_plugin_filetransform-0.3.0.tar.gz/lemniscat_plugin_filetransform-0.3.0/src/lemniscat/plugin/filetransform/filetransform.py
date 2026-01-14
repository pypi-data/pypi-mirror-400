# -*- coding: utf-8 -*-
# above is for compatibility of python2.7.11

import logging
import os
import subprocess, sys   
from lemniscat.core.util.helpers import LogUtil
import re

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.setLoggerClass(LogUtil)
log = logging.getLogger(__name__.replace('lemniscat.', ''))

class FileTransform:
    def __init__(self):
        pass
    
    # parse yaml file to dict
    @staticmethod
    def parseYamlFile(filePath) -> dict:
        import yaml
        with open(filePath, 'r') as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                log.error(exc)
                return None
            
    # parse json file to dict
    @staticmethod
    def parseJsonFile(filePath) -> dict:
        import json
        with open(filePath, 'r') as stream:
            try:
                return json.load(stream)
            except json.JSONDecodeError as exc:
                log.error(exc)
                return None

    # parse hcl file to dict
    @staticmethod
    def parseHclFile(filePath) -> dict:
        import hcl2
        with open(filePath, 'r') as stream:
            try:
                return hcl2.load(stream)
            except Exception as exc:
                log.error(exc)
                return None

    # save dict to yaml file
    @staticmethod
    def saveYamlFile(filePath, data: dict) -> None:
        import yaml
        with open(filePath, 'w') as stream:
            try:
                yaml.dump(data, stream, indent=4)
            except yaml.YAMLError as exc:
                log.error(exc)

    # save dict to json file
    @staticmethod
    def saveJsonFile(filePath, data: dict) -> None:
        import json
        with open(filePath, 'w') as stream:
            try:
                json.dump(data, stream, indent=4)
            except json.JSONDecodeError as exc:
                log.error(exc)

    # save dict to hcl file
    @staticmethod
    def saveHclFile(filePath, data: dict) -> None:
        with open(filePath, 'w') as stream:
            try:
                content = FileTransform._dictToHcl(data)
                stream.write(content)
            except Exception as exc:
                log.error(exc)

    @staticmethod
    def _dictToHcl(data: dict, indent: int = 0) -> str:
        """Convert Python dict to HCL format"""
        lines = []
        indent_str = "  " * indent

        for key, value in data.items():
            if isinstance(value, dict):
                # Dicts are always map assignments in HCL: key = { ... }
                # This works for both .tfvars and .tf files
                lines.append(f'{indent_str}{key} = {{')
                lines.append(FileTransform._dictToHcl(value, indent + 1).rstrip())
                lines.append(f'{indent_str}}}')
            elif isinstance(value, list):
                # Lists of dicts are blocks (like variable, resource, output)
                for item in value:
                    if isinstance(item, dict):
                        # Block syntax: key { ... } (no =)
                        lines.append(f'{indent_str}{key} {{')
                        lines.append(FileTransform._dictToHcl(item, indent + 1).rstrip())
                        lines.append(f'{indent_str}}}')
                    else:
                        # List of primitives: key = value (multiple times)
                        lines.append(f'{indent_str}{key} = {FileTransform._formatHclValue(item)}')
            else:
                # Primitives are always assignments: key = value
                lines.append(f'{indent_str}{key} = {FileTransform._formatHclValue(value)}')

        return '\n'.join(lines) + '\n'

    @staticmethod
    def _formatHclValue(value):
        """Format a Python value for HCL output"""
        if isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, str):
            return f'"{value}"'
        elif value is None:
            return 'null'
        else:
            return str(value)

    # get files path match pattern in directory
    @staticmethod
    def getFilesPathMatchPattern(directory, pattern) -> list:
        import glob
        return glob.glob(f'{directory}/{pattern}')
    
    @staticmethod
    def getFileNameFromPath(filePath) -> str:
        return os.path.basename(filePath)

    # replace variable in dict
    @staticmethod
    def replaceVariable(data: dict, key: str, value: object, prefix: str = '') -> dict:
        for k, v in data.items():
            if(f'{prefix}{k}'.casefold() == key.casefold()):
                log.info(f'Found {key}. Replace {key}...')
                data[k] = value
            else:
                if(isinstance(v, dict) and key.casefold().startswith(f'{prefix}{k}'.casefold()) ):
                    data[k] = FileTransform.replaceVariable(v.copy(), key, value, f'{prefix}{k}.')
                elif(isinstance(v, list) and key.casefold().startswith(f'{prefix}{k}'.casefold()) ):
                    # Handle lists (important for HCL2 structure)
                    new_list = []
                    for item in v:
                        if isinstance(item, dict):
                            new_list.append(FileTransform.replaceVariable(item.copy(), key, value, f'{prefix}{k}.'))
                        else:
                            new_list.append(item)
                    data[k] = new_list
        return data

    def run(self, folderPath: str, targetFiles: str, fileType: str, folderOutPath: str, variables: dict = {}) -> None:
        # get all files path match pattern
        files = self.getFilesPathMatchPattern(folderPath, targetFiles)
        # loop files
        for file in files:
            # parse file
            if(fileType == 'yaml'):
                data = self.parseYamlFile(file)
            elif(fileType == 'json'):
                data = self.parseJsonFile(file)
            elif(fileType == 'hcl'):
                data = self.parseHclFile(file)
            else:
                log.error('File type not supported')
                return 1, '','File type not supported'
            # replace variables
            for key, value in variables.items():
                data = self.replaceVariable(data, key, value.value)
            # save file
            outfile = f'{folderOutPath}/{self.getFileNameFromPath(file)}'
            if(fileType == 'yaml'):
                self.saveYamlFile(outfile, data)
            elif(fileType == 'json'):
                self.saveJsonFile(outfile, data)
            elif(fileType == 'hcl'):
                self.saveHclFile(outfile, data)
            else:
                log.error('File type not supported')
                return 1, '','File type not supported'
        return 0, '',''