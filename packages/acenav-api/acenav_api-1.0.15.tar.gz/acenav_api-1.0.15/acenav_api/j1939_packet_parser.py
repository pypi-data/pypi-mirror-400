from typing import Optional, Dict

class J1939PacketDefine:
    __priority: int
    __pgn: int
    def __init__(self, priority:int, pgn:int):
        self.__priority = priority
        self.__pgn = pgn

    def build_arbitration_id(self, destination_address: int = 0, source_address: int = 0) -> int:
        # PDU format calculation
        pf = (self.__pgn >> 8) & 0xFF
        ps = self.__pgn & 0xFF
        if pf >= 240:  # PDU2 format
            pgn = (pf << 8)
        else:  # PDU1 format
            pgn = (pf << 8) | destination_address
        return (self.__priority << 26) | (pgn << 8) | source_address


class J1939PacketParser:
    __j1939_packets: Dict[str, J1939PacketDefine]
    
    def __init__(self, j1939_packets:Dict[str, Dict[str, int]]):
        for name, pkt in j1939_packets.items():
            j1939_packets[name] = J1939PacketDefine(pkt['priority'], pkt['pgn'])

        self.__j1939_packets = j1939_packets
        
    def get(self, name:str) -> Optional[J1939PacketDefine]:
        return self.__j1939_packets.get(name, None)