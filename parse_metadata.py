def parse_metadata(filename):
    """Parses a Landsat metadata file and returns a hierarchical dict with all of
    the metadata.

    The metadata file is the file that is named <SCENEID>_MTL.txt - for example
    LE72020252002087EDC00_MTL.txt

    Simply pass the filename of the MTL file to this routine and it will return
    the parsed data in a dict. """

    f = open(filename)

    metadata = {}

    group_metadata = {}

    for line in f.readlines():
        if (line.startswith("GROUP = L1_METADATA_FILE") or
           line.startswith("END_GROUP = L1_METADATA_FILE")):
            continue
        elif line.startswith("END") and "GROUP" not in line:
            break
        elif line.strip().startswith("GROUP = "):
            # Create a new group
            group_metadata = {}
            group = line.replace("GROUP = ", "").strip()
        elif line.strip().startswith("END_GROUP = "):
            # Save the group data
            metadata[group] = group_metadata
            group = None
        else:
            # Actual data here - rather than group start or end
            label, data = (s.strip() for s in line.split("="))
            group_metadata[label] = data

    return metadata
