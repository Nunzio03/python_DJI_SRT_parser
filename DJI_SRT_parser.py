# DJI mini 3 pro SRT file to JSON file

import sys
import time 
import datetime
import json

def get_startTimestamp(first_block):
    startDate = first_block.split('\n')[3].split(' ')[0]
    startTime = first_block.split('\n')[3].split(' ')[1]

    # convert the start time and date to unix timestamp in milliseconds
    startTimestamp = int(time.mktime(datetime.datetime.strptime(startDate + " " + startTime, "%Y-%m-%d %H:%M:%S.%f").timetuple()) * 1000)
    # add the milliseconds to the timestamp
    startTimestamp += int(startTime.split('.')[1])
    return startTimestamp

def parse_camera_data(lines):
    cameraDict = {}
    cameraData = lines[4].split('],[')[0]
    # replace "] [" with "," in the camera data + remove spaces and brackets
    cameraData = cameraData.replace("] [", ",").replace(' ', '').strip('[')
    # split the camera data in key-value pairs
    cameraData = cameraData.split(',')
    # loop through the key-value pairs
    for c in cameraData:
        cameraDict[c.split(':')[0]] = c.split(':')[1]
    return cameraDict

def parse_gps_data(lines):
    gpsDict = {}
    gpsData = lines[4].split('],[')[1]
    # replace "] [" with "," in the gps data
    gpsData = gpsData.replace("] [", ",").replace(' ', ',').replace(':,', ':')
    gpsData = gpsData.split(',')
    # remove the last element, which is empty
    gpsData = gpsData[:-1]
    for g in gpsData:
        gpsDict[g.split(':')[0]] = g.split(':')[1].strip(']')
    return gpsDict

def output_json(blocksList, filename):
    # write the list to a json file with newline characters for each block
    outputfilename = filename.split('.SRT')[0] + '.json'
    print(outputfilename)
    with open(outputfilename, 'w') as outfile:
        json.dump(blocksList, outfile, indent=4)

def output_csv(blocksList, filename):
    # write the list to a 2 csv file camera and gps
    outputfilename = filename.split('.SRT')[0] + 'camera.csv'
    print(outputfilename)

    # write camera data
    with open(outputfilename, 'w') as outfile:
        outfile.write('id,timestamp,iso,shutter,fnum,ev,ct,color_md,focal_len,dzoom_ratio, delta')
        outfile.write('\n')
        for b in blocksList:
            outfile.write(b['id'] + ',' + str(b['timestamp']) + ',' + b['camera']['iso'] + ',' + b['camera']['shutter'] + ',' + b['camera']['fnum'] + ',' + b['camera']['ev'] + ',' + b['camera']['ct'] + ',' + b['camera']['color_md'] + ',' + b['camera']['focal_len'] + ',' + b['camera']['dzoom_ratio'] + ',' + b['camera']['delta'])
            outfile.write('\n')

    # write gps data
    outputfilename = filename.split('.SRT')[0] + 'gps.csv'
    print(outputfilename)
    with open(outputfilename, 'w') as outfile:
        outfile.write('id,timestamp,latitude,longitude,rel_alt,abs_alt')
        outfile.write('\n')
        for b in blocksList:
            outfile.write(b['id'] + ',' + str(b['timestamp']) + ',' + b['gps']['latitude'] + ',' + b['gps']['longitude'] + ',' + b['gps']['rel_alt'] + ',' + b['gps']['abs_alt'])
            outfile.write('\n')
sys.argv.append("-filename")

# get filename from arg "-filename"
try:
    filename = sys.argv[sys.argv.index("-filename") + 1]
except:
    print("Please specify a filename with the -filename argument")
    exit()

# open the file
f = open(filename, "r")

# Read the file and split it by the string "</font>\n\n"
blocks = f.read().split("</font>\n\n")
# remove the last block, which is empty
blocks = blocks[:-1]

# get the start timestamp
startTimestamp = get_startTimestamp(blocks[0])

# create a list for the blocks
blocksList = []

# loop through the blocks
for b in blocks:
    # create a dictionary for the block
    blockDict = {}
    # split the block in lines by '\n'
    lines = b.split('\n')
    # read id
    id = lines[0]
    # read elapsed time and compute the unix timestamp in milliseconds
    diffTime = lines[2].split(': ')[-1].strip('ms')
    timestamp = startTimestamp + int(diffTime)

    # read camera data
    cameraDict = parse_camera_data(lines)
    # read gps data
    gpsDict = parse_gps_data(lines)

    # add the data to the block dictionary
    blockDict['id'] = id
    blockDict['timestamp'] = timestamp
    blockDict['camera'] = cameraDict
    blockDict['gps'] = gpsDict

    # add the block dictionary to the list
    blocksList.append(blockDict)

# write the list to a json file with newline characters for each block
output_json(blocksList, filename)

# write the list to a 2 csv file camera and gps
output_csv(blocksList, filename)

# print the number of blocks
print(str(len(blocksList))+" blocks written to files")
