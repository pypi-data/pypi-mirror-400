__all__ = ['create_parser', 'create_command_builder', 'create_j1939_packet_parser']

from .command_builder import CommandBuilder
from .packet_parser import PacketParser
from .j1939_packet_parser import J1939PacketParser
from .message_protocol import (create_internel_protocol,create_protocol_from_path,MessageProtocol)

def create_protocol(device_type:str, config_path=None)->MessageProtocol:
    if config_path == None:
        protocol = create_internel_protocol(device_type)
    else:
        protocol = create_protocol_from_path(config_path)
    
    return protocol

def create_parser(device_type:str, config_path=None)->PacketParser:
    protocol = create_protocol(device_type, config_path)
    
    return PacketParser(device_type, protocol)

def create_command_builder(device_type:str, config_path=None)->CommandBuilder:
    parser = create_parser(device_type, config_path)
    
    return CommandBuilder(parser)

def create_j1939_packet_parser(device_type:str, config_path=None)->J1939PacketParser:
    import json
    with open(config_path, 'r') as f:
        config = json.load(f)
    j1939_packets = config.get('j1939_packets', {})
    
    return J1939PacketParser(j1939_packets)