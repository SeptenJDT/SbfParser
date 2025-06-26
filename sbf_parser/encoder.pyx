# type: ignore 
# Created by Louis-Max Harter 2025
# Based on the sbfPythonParser by Jashandeep Sohi, Marco Job, and Meven Jeanne-Rose

from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t, int8_t, int16_t, int32_t, int64_t
from libc.stdlib cimport malloc, free
from libc.string cimport memcpy, memset
from libc.stdio cimport FILE, fwrite, fopen, fclose

from . import block_structure as BLOCKS
from .block_structure import BLOCKNAMES, BLOCKNUMBERS
from .block_parsers cimport BLOCKPARSERS
from .encoder cimport *
cimport cpython.array as array
import struct


HEADER_LEN = 8 # bytes
cdef struct Header:
    uint16_t Sync
    uint16_t CRC
    uint16_t ID
    uint16_t Length

cdef dict type_to_format = {
    'u1': 'B',    # unsigned char
    'u2': 'H',    # unsigned short
    'u4': 'I',    # unsigned int
    'u8': 'Q',    # unsigned long long
    'i1': 'b',    # signed char
    'i2': 'h',    # signed short
    'i4': 'i',    # signed int
    'i8': 'q',    # signed long long
    'f4': 'f',    # float
    'f8': 'd',    # double
    'c1': 's'     # char (string)
}


SUB_BLOCK_HANDLERS = {
    "MeasExtra": ("MeasExtraChannel", "MeasExtraChannelSub"),
    "ReceiverStatus": ("AGCState", "ReceiverStatus_AGCState"),
    "BaseVectorCart": ("VectorInfoCart", "BaseVectorCart_VectorInfoCart"),
    "BaseVectorGeod": ("VectorInfoGeod", "BaseVectorGeod_VectorInfoGeod"),
    "GEOFastCorr": ("FastCorr", "GEOFastCorr_FastCorr"),
    "GEOIonoDelay": ("IDC", "GEOIonoDelay_IDC"),
    "GEOServiceLevel": ("ServiceRegion", "GEOServiceLevel_ServiceRegion"),
    "GEOClockEphCovMatrix": ("CovMatrix", "GEOClockEphCovMatrix_CovMatrix"),
    "LBandTrackerStatus": ("TrackData", "LBandTrackerStatus_TrackData"),
    "GISStatus": ("DatabaseStatus", "DatabaseStatus"),
    "InputLink": ("InputStats", "InputLink_InputStats"),
    "RFStatus": ("RFBand", "RFBand"),
    "SatVisibility" : ("SatInfo", "SatVisibility_SatInfo"),
    "NTRIPClientStatus" : ("NTRIPClientConnection", "NTRIPClientConnection"),
    "NTRIPServerStatus" : ("NTRIPServerConnection", "NTRIPServerStatus"),
    "DiskStatus" : ("DiskData", "DiskData"),
    "P2PPStatus" : ("P2PPSession", "P2PPSession"),

    # Theses blocks need sub-sub-block parsing. Please contact Septentrio if you need them to be implemented 
    # "MeasEpoch": ("Type1", "")
    # "ChannelStatus" : ("ChannelSatInfo", ""),
    # "OutputLink" : ("OutputStats", ""),
}

PAYLOAD_PRIORITY_NO_PAYLOAD = 0
PAYLOAD_PRIORITY_ONLY_NOT_IMPLEMENTED = 1
PAYLOAD_PRIORITY_ONLY_ON_FAIL = 2
PAYLOAD_PRIORITY_ALWAYS = 3

def encode(block_data, payload_priority=PAYLOAD_PRIORITY_ONLY_NOT_IMPLEMENTED):
    """
    Converts a SBF block dictionary to binary format.
    
    Args:
        block_data: Dictionary containing the block data fields
        payload_priority: 
            -3: Never use payload
            -2: Use only for not implemented block
            -1: Use only when failed to encode or not implemented
             0: Prioritize payload over encoding
    Returns:
        Bytes object containing the binary SBF block
    """

    if payload_priority >= PAYLOAD_PRIORITY_ALWAYS and "payload" in block_data.keys():
        return ("payload", block_data.get("payload"))

    cdef Header header
    cdef const unsigned char[:] body_view
    cdef uint16_t crc_val = 0
    cdef const unsigned char[:] id_len_view

    try:
        # Block type
        block_type = block_data.get("blockType", None)
        block_name = block_data.get("blockName", None)
        block_struct = getattr(BLOCKS, block_name, None) if block_name else None
        
        if block_struct is None: 
            if payload_priority == PAYLOAD_PRIORITY_NO_PAYLOAD:
                raise ValueError(f"Encoding {block_type} / {block_name} is not implemented and payload_priority is not enough.")

            if not "payload" in block_data.keys():
                raise ValueError(f"Encoding {block_type} / {block_name} is not implemented and no payload is provided.")
            
            return ("fallback", block_data.get("payload"))

        if block_name is None:
            raise ValueError(f"No block name found in block structure.")

        # is complex ?
        is_complex = hasattr(BLOCKS, f"{block_name}_Type_1") or \
                    hasattr(BLOCKS, f"{block_name}_Type_2") or \
                    block_name in SUB_BLOCK_HANDLERS.keys()

        # Serialize block
        if is_complex:
            body_bytes = _handle_complex_block(block_name, block_struct, block_data)
        else:
            body_bytes = _serialize_block(block_name, block_struct, block_data)
        
        
        # Padding
        total_length = HEADER_LEN + len(body_bytes)
        if total_length % 4 != 0:
            padding = 4 - (total_length % 4)
            body_bytes += b'\x00' * padding
            total_length += padding
        

        # Header
        header.Sync = 16420  # SBF sync word (0x4020)
        header.Length = total_length
        header.ID = BLOCKNUMBERS[BLOCKNAMES.index(block_name)] & 0x1FFF
        

        # Calculate CRC
        id_len_bytes = struct.pack("<HH", header.ID, header.Length)
        body_view = body_bytes
        id_len_view = id_len_bytes
        crc_val = crc16(<void*>&id_len_view[0], 4, 0)
        header.CRC = crc16(<void*>&body_view[0], len(body_bytes), crc_val)
        

        # Create header bytes
        header_bytes = struct.pack("<HHHH", header.Sync, header.CRC, header.ID, header.Length)
        
        return ("encoded", header_bytes + body_bytes)

    except Exception as e:
        if payload_priority >= PAYLOAD_PRIORITY_ONLY_ON_FAIL and "payload" in block_data.keys():
            return ("failed", block_data["payload"])

        raise e



cdef bytes _serialize_block(block_name, tuple block_struct, dict block_data):
    """Serialize a simple block dictionary to bytes.
    
    Args:
        block_struct: Tuple of (field_name, type) pairs defining the block structure
        block_data: Dictionary containing the block data
    Returns:
        Bytes object containing the serialized block
    """
    values = []
    cdef str format_str = ""
    field_type = ""
    
    # print("Block data :", block_data, flush=True)
    # Convert each field according to its type
    for field_name, field_full_type in block_struct:
        if field_name not in block_data:
            print(block_data)
            raise ValueError(f"Missing field {field_name} in block {block_name}")
        value = block_data[field_name]


        if "[" in field_full_type:
            field_type, size = field_full_type.split("[")
            size = size.rstrip(']')

            if size.isdigit():
                size = int(size)
            elif size in block_data:
                size = block_data[size]
            else:
                raise ValueError(f"Size of {field_full_type} ({size}) can't be found in block data")
            
            multiplier = int(field_type[-1]) # u8 -> 8 bytes

            if len(value) != size * multiplier:
                raise ValueError(f"{block_name}: Field {field_name} is len of {len(value)}, expected {size*multiplier} = {size} * {multiplier} ({field_full_type}).")
        
            values.extend(value)
            format_str += "B" * (size * multiplier) # Encoding all has bytes

        else:
            values.append(value)
            format_str += type_to_format[field_full_type]
    
    # print(f"Encoding : {format_str} with {values}")
    return struct.pack("<" + format_str, *values)





def _handle_complex_block(str block_name, block_struct, dict block_data):
    """Handle serialization of complex blocks with subblocks."""    
    # Serialize main block
    main_block_bytes = _serialize_block(block_name, block_struct, block_data)
    
    # Get the subblock structure
    sub_block_key, sub_block_class_name = SUB_BLOCK_HANDLERS[block_name]
    sub_block_struct = getattr(BLOCKS, sub_block_class_name)
    if sub_block_struct is None:
        raise ValueError(f"Subblock structure definition not found for {sub_block_class_name}")
    
    # Serialize each subblock
    for sub_block_data in block_data[sub_block_key]:
        main_block_bytes += _serialize_block(sub_block_class_name, sub_block_struct, sub_block_data)
    
    return main_block_bytes
