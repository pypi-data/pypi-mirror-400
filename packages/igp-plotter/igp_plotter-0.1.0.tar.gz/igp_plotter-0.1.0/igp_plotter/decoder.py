# igp_plotter/decoder.py

def hex_to_208bit_binary(hex_str):
    """Convert hex string to 208-bit binary string"""
    return ''.join(f"{int(c, 16):04b}" for c in hex_str)


def get_active_igp_indices(bin_mask):
    """Return IGP indices where bit = 1 (1-based)"""
    return [i + 1 for i, bit in enumerate(bin_mask) if bit == "1"]


def decode_sbas_asc(asc_path, prn_min=120, prn_max=160):
    """
    Read SBAS18 ASC file and extract IGP arrays
    Returns: dict[prn][band] -> set(igp indices)
    """
    sbas_dict = {}

    with open(asc_path, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            line = line.strip()

            if not line.startswith("#SBAS18"):
                continue

            try:
                header, payload_crc = line.split(";", 1)
                payload = payload_crc.split("*", 1)[0]
                fields = payload.split(",")

                prn = int(fields[0])
                band = int(fields[2])
                igp_mask_hex = fields[4]

                if prn_min <= prn <= prn_max:
                    bin_mask = hex_to_208bit_binary(igp_mask_hex)
                    igps = get_active_igp_indices(bin_mask)

                    sbas_dict \
                        .setdefault(prn, {}) \
                        .setdefault(band, set()) \
                        .update(igps)

            except (ValueError, IndexError):
                continue

    return sbas_dict
