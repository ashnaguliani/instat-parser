import xml.etree.ElementTree as ET
import csv
import sys

# open the XML file - uses the first argument from command line as filename
xml_file_name = sys.argv[1]
tree = ET.parse(xml_file_name)
root = tree.getroot()

# open a file for writing - named the same as the XML file appended with -parsed
output_file_name = xml_file_name.split('.')[0] + "-parsed.csv"
game_data = open(output_file_name, "w")

# write to the file
csvwriter = csv.writer(game_data)
with game_data:
	#the first row of the CSV file (column names) -- list of lists is CSV writer syntax (each list is a row)
	headers = [["ID", "start", "end", "code", "team", "action", "half", "pos_x", "pos_y"]]
	csvwriter.writerows(headers) 

	# we want to look through each "instance" in the XML file
	for elem in tree.findall('.//instance'):

	# create an empty list to store all the data for this instance
		instance = []
		instance.append(elem.find('ID').text)
		instance.append(elem.find('start').text)
		instance.append(elem.find('end').text)
		instance.append(elem.find('code').text)

		# there's a couple instances that don't have every variable - here we'll check that the
		# instance does have at least one of them (so we'll assume it has all the rest) to make 
		# sure that doing a get is safe
		if elem.find('label') is not None:
			instance.append(elem[4][1].text)
			instance.append(elem[5][1].text)
			instance.append(elem[6][1].text)
			instance.append(elem.find('pos_x').text)
			instance.append(elem.find('pos_y').text)

		# write the row to the file
		csvwriter.writerows([instance]) 

# close the file #safetyfirst
game_data.close()