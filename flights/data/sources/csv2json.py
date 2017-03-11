import csv
import json

# AIRLINES file
csvfile = open('airlines.csv', 'r')
jsonfile = open('airlines.py', 'w')

fieldnames = ("Ref","Name", "Unknown", "IATA Code", "ICAO Code", "Short Name", "Country", "Active")
reader = csv.DictReader( csvfile, fieldnames)

jsonfile.write('AIRLINES = [\n')
for row in reader:
    if row['Active'] == "Y":
        if row['IATA Code'] and row['ICAO Code']:
            row['Short Name'] = row['Short Name'].lower().title()
            row.pop('Ref', None)
            row.pop('Unknown', None)
            if row['Country'] == 'AVIANCA':
                row['Short Name'] = 'Avianca'
                row['Country'] = 'Colombia'
            if row['Short Name'] == 'Viet Nam Airlines':
                row['Short Name'] = 'Vietnam Airlines'
            if row['Short Name'] == 'Speedbird':
                row['Short Name'] = 'British Airways'

            json.dump(row, jsonfile)
            jsonfile.write(',\n')
jsonfile.write(']')

# AIRPORTS File
csvfile = open('airports.csv', 'r')
jsonfile = open('airports.py', 'w')

fieldnames = ("ident", "type", "name", "latitude_deg" , "longitude_deg" , "elevation_ft" , "continent", "iso_country", "iso_region", "municipality", "gps_code", "iata_code", "local_code")
reader = csv.DictReader( csvfile, fieldnames)

jsonfile.write('AIRPORTS = [\n')
for row in reader:
    json.dump(row, jsonfile)
    jsonfile.write(',\n')
jsonfile.write(']')
