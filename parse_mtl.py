filename = "E:\_Datastore\LandsatCDR\SotonNewForest\Normal\LE72020252002087EDC00_MTL.txt"
f = open(filename)

metadata = {}

group_metadata = {}

for line in f.readlines():
	if line.startswith("GROUP = L1_METADATA_FILE") or line.startswith("END_GROUP = L1_METADATA_FILE"):
		continue
	elif line.startswith("END") and "GROUP" not in line:
		print "Found END!"
		break
	elif line.strip().startswith("GROUP = "):
		# Create a new group
		group_metadata = {}
		group = line.replace("GROUP = ", "").strip()
		print group
	elif line.strip().startswith("END_GROUP = "):
		print "Found end group"
		# Save the group data
		metadata[group] = group_metadata
		group = None
	else:
		print line
		# Actual data here - rather than group start or end
		label, data = (s.strip() for s in line.split("="))
		group_metadata[label] = data