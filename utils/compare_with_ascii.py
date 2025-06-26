import sbf_parser
import traceback
import glob
import re
import sys

sbf_file = "all_blocks_0000.sbf"
sbf_path = f"./{sbf_file}"

SUB_BLOCKS_NAME = {
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
    # "MeasEpoch": ("Type1", "")
    # "ChannelStatus" : ("ChannelSatInfo", ""),
    # "OutputLink" : ("OutputStats", ""),
}

def repr_100(info):
    result = repr(info)
    if len(result) > 97:
        result = result[:97] + "..."
    return result


class ComparisonError(Exception):
    def __init__(self, message, previous_parsing_error=None):
        if previous_parsing_error is None:
            self.trace = [message]
        else:
            self.trace = [message] + previous_parsing_error.trace

        self.message = self.trace[0]
        super().__init__(self.message)

    def __str__(self):
        result = ""
        for elem in self.trace:
            if elem != "":
                result += "-- " + elem + "\n"
        return result

class VerificationError(Exception):
    def __init__(self, exit_code, details):
        self.exit_code = exit_code
        self.details = details
        super().__init__(self.exit_code)


def process(block_name, ascii_lines):
    exit_code = "OK" # Can be also OK_NO_SUBLOCKS
    def parse_key(key):
        key = key.split("[")[0].strip()

        if key == "lambda":
            return "Lambda" # lambda is a keyword of python, can't use it
        return key 
        # Remove units from the key. Ex: TOW [0.001 s] -> TOW

    columns = [parse_key(categorie) for categorie in ascii_lines[0].split(",")]
    data = [] # (TOW, WNc), [blocks, ...]

    for line in ascii_lines[2::]:
        if line == '':
            continue

        line = line.split(',')
        if len(columns) != len(line) and not "No sub-messages" in line:
            print("line    :", line)
            print("columns :", columns)
            raise ComparisonError("Line and header dont have the same number of elements.")

        json = {categorie: value for categorie, value in zip(columns, line)}
        json["No sub-messages"] = ("No sub-messages" in line)

        # print("Json: ", json)

        id = (json["TOW"], json["WNc"])
        if len(data) == 0 or data[-1][0] != id or block_name not in SUB_BLOCKS_NAME.keys():
            data.append((id, []))
        data[-1][1].append(json)



    # Now, create a json with sub-blocks
    # The main block will be the common values of all json with the same ID
    # Sub-blocks will be all blocks
    results = []


    if block_name not in SUB_BLOCKS_NAME.keys():
        exit_code = "OK"
        for id, blocks in data:
            if len(blocks) != 1:
                assert Exception("Multiples blocks with the same ID are detected, but block dont have sub-blocks")
            results.append(blocks[0])

    else:
        exit_code = "OK_NO_SUBLOCK"
        sub_blocks_name, sub_blocks_class = SUB_BLOCKS_NAME.get(block_name, None)

        for id, blocks in data:
            result = blocks[0]
            result[sub_blocks_name] = []

            for block in blocks:
                for key, value in block.items():
                    if key in result.keys() and result[key] != value:
                        # If not the same value, this may be a sub-block atribut
                        del result[key]

                if not json["No sub-messages"]:
                    result[sub_blocks_name].append(block)
                    exit_code = "OK"

            results.append(result)

    return (exit_code, results)


def compare(a, b, test_name=""):
    trace = test_name
    
    try:
        t_a = type(a).__name__
        t_b = type(b).__name__
        if t_a != t_b :
            trace += f"-> type of a ({t_a}) is not the same has b ({t_b})\n"
            match type(a).__name__:
                case "int" | "float":
                    if b == "":
                        casted_b = 0
                    elif len(b) < 100:
                        casted_b = float(b.replace(" ", ""))
                    else:
                        raise Exception(f"b is too long ({len(b)} char longs)to be converted to float.")
                    
                    trace += f"\tb before: {repr_100(b)}\n"
                    trace += f"\tb after : {repr_100(casted_b)}\n"
                    b = casted_b

                case "bytes" | "bytearray":
                    n_bytes = len(a)
                    trace += f"\ta {repr(a)}, use {n_bytes} bytes\n"
                    trace += f"\tb {repr(b)}\n"

                    batch_size = len(a) / len(b.split(" "))
                    if batch_size in (1.0, 2.0, 4.0):
                        batch_size = int(batch_size)
                        trace += f"Batch size detected : {batch_size}\n"
                    else:
                        trace += f"Batch size failed : {batch_size} -> 1\n"
                        batch_size = 1
                    

                    big_endian_array = []
                    little_endian_array = []
                    for i in range(0, len(a), batch_size):
                        value_b = 0
                        value_l = 0
                        for shift in range(0, batch_size):
                            value_l += a[i + shift] << ((shift) * 8)
                            value_b += a[i + shift] << ((batch_size - shift) * 8)
                        big_endian_array.append(value_b)
                        little_endian_array.append(value_l)

                    a_big = " ".join(map(str, big_endian_array))
                    a_little = " ".join(map(str, little_endian_array))
                    a = a_little
                    b = b.replace("00", "0")

                    trace += f"\ta big-endian    : {repr_100(a_big)}\n"
                    trace += f"\ta little-endian : {repr_100(a_little)} (default)\n"
                    trace += f"\tb after         : {repr_100(b)}\n"

                    if b == "": # Fill with 0
                        b = " ".join("0" for _ in a.split(" "))

                case "tuple" | "list":
                    if t_b in ("tuple", "list"):
                        pass
                    else:
                        raise ComparisonError("Conversion impossible")

                case _:
                    trace += f"\tDon't have specific behavior to convert b to {t_a}. Keep original.\n"
            # End match conversion
        # End conversion b to type of a
        
        match type(a).__name__:
            case "list" | "tuple":
                if len(a) != len(b):
                    if len(a) + len(b) < 10:
                        raise ComparisonError(f"Size miss-match :\n\ta: {a}\n\tb: {b}")
                    else:
                        raise ComparisonError(f"Size miss-match :\n\tlen(a): {len(a)}\n\tlen(b): {len(b)}")


                for i, x, y in zip(list(range(len(a))), a, b):
                    compare(x, y, f"Elements miss-match at index {i}")

            case "dict":
                # Compare if a is include into b
                a_not_in_b = list(
                    set(list(a.keys())) 
                -   set(list(b.keys()))
                )
                if len(a_not_in_b) > 0:
                    raise ComparisonError(f"Keys of a are not include into b, a_not_in_b {a_not_in_b} :\na:{list(a.keys())}\nb:{list(b.keys())}")

                for key in a.keys():
                    if key.startswith("Reserved"):
                        continue

                    compare(a[key], b[key], f"Comparing key {key}\n")

            case "str":
                if a != b:
                    raise ComparisonError(f"Miss-match string:\na: {repr(a)}\nb: {repr(b)}")
                
            case "int":
                if a != b:
                    raise ComparisonError(f"\ta: {a}\n\tb: {b}")

            case "float":
                if (
                    a != b
                and (a != 0 and abs(a-b)/a) > 0.01
                and (abs(a-b) > 0.001)
                ): # failed if > 1% relative error and > 0.001 absolute error
                    raise ComparisonError(f"\ta: {a}\n\tb: {b}")


            case  "bytes" | "bytearray":
                return compare(list(a), list(b), "Converting bytesArray to list")
            
            case _:
                raise ComparisonError(f"Type {type(a).__name__} not handled")

    except ComparisonError as pe:
        raise ComparisonError(trace, pe)

    except Exception as e:
        raise ComparisonError(f"{trace}: Unknow error {traceback.format_exc()}")


def compare_blocks(block_name, json_blocks):
    try:
        # Find ascii file corresponding
        pattern = f"./ascii/{sbf_file}_SBF_{block_name}*.txt"
        matching_files = glob.glob(pattern)
        if len(matching_files) > 1:
            raise VerificationError(
                f"Failed to find sbf2asc file",
                f"Only one file need to match the expression {pattern}, got {matching_files}"
            )
        elif len(matching_files) == 0:
            return "No ascii file detected"
        path = matching_files[0]

        # Parse ascii
        with open(path, "r") as f:
            ascii_lines = f.read().split("\n") 
        try:
            exit_code, ascii_blocks = process(block_name, ascii_lines)
        except ComparisonError as pe:
            raise VerificationError("Parsing sbf2asc error", str(pe))

        # Check json 
        if len(json_blocks[0].keys()) == 0:
            return "Not Implemented"

        # Compare size
        if len(json_blocks) != len(ascii_blocks):
            details = f"Number of blocks in json ({len(json_blocks)}) different from ascii file ({len(ascii_blocks)}). Can't compare"
            if len(json_blocks) + len(ascii_blocks) < 15:
                details += f"Number of blocks in json {json_blocks} dont match number of ascii blocks: {ascii_blocks}"
            raise VerificationError(f"Wrong number of blocks", details)

        # Compare
        try:
            for json, ascii in zip(json_blocks, ascii_blocks):
                compare(json, ascii)

        except ComparisonError as pe:
            raise VerificationError("Miss-match", str(pe))

    except VerificationError as ve:
        raise ve
    except Exception as e:
        raise VerificationError("Unexpected error", traceback.format_exc())

    return exit_code


def verify_blocks(block_name, json_blocks):
    exit_code = "Error"
    try:
        exit_code = compare_blocks(block_name, json_blocks)

    except VerificationError as ve:
        print('\nComparing {:20}'.format(block_name), exit_code)
        print(ve.details)
        print()
        return ve.exit_code
    
    except Exception as e:
        print('\nComparing {:20}'.format(block_name), exit_code)
        traceback.format_exc()
        print()
        return "Unknow error"

    print('Comparing {:20}'.format(block_name), exit_code)
    return exit_code
    

# Read file :
blocks = {}
not_implemented = {}
with open(sbf_path, "rb") as f:
    for block_name, infos in sbf_parser.load(f):
        
        if block_name == "Unknown":
            continue

        if not block_name in blocks.keys():
            blocks[block_name] = []

        if infos.get("blockType", "SBF") != "SBF":
            continue

        if infos.get("blockName", block_name) == "Unknown":
            print("Warning: Skipping Unknown sbf block")
            continue

        # Delete info that are only from sbf parser and not in sbf2asc
        if "payload" in infos.keys():
            del infos["payload"]
        if "blockName" in infos.keys():
            del infos["blockName"]
        if "blockType" in infos.keys():
            del infos["blockType"]

        blocks[block_name].append(infos)

# Compare
print("\n")
print(f"Messages decoded : {sum([len(messages) for messages in blocks.values()])}")
print(f"Blocks detected  : {len(blocks.keys())}")
print(list(blocks.keys()))
print("\n")

summary = {}
for block_name, infos in blocks.items():
    result = verify_blocks(block_name, infos)
    summary[result] = summary.get(result, 0) + 1


print("")
print("Summary")
for key, count in sorted(list(summary.items()), key=lambda elem: elem[1], reverse=True):
    print(f"\t{key:30} : {count}")
print(f"Total : {sum(summary.values())}")
