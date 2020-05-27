####################################
#   File name: SiteScan_Image_Formatter_Source.py
#   About: Embeds Drone Flight CSV GPS Info into Image Metadata/EXIF
#   Author: Geoff Taylor | Imagery & Remote Sensing Team | Esri
#   Date created: 12/12/2019
#   Date last modified: 12/13/2019
#   Python Version: 3.7
####################################

"""
Dependencies: piexif & pillow
    if ArcGIS Pro install access conda via command by entering:
        "%PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\proenv"
    install piexif by entering:
        conda install -c conda-forge piexif
    install pillow by entering:
        conda install -c anaconda pillow
"""

import piexif
import csv
from PIL import Image
from fractions import Fraction
from os import path, remove


def to_deg(value, loc):
    """convert decimal coordinates into degrees, munutes and seconds tuple
    Keyword arguments: value is float gps-value, loc is direction list ["S", "N"] or ["W", "E"]
    return: tuple like (25, 13, 48.343 ,'N')
    """
    if value < 0:
        loc_value = loc[0]
    elif value > 0:
        loc_value = loc[1]
    else:
        loc_value = ""
    abs_value = abs(value)
    deg = int(abs_value)
    t1 = (abs_value-deg)*60
    min = int(t1)
    sec = round((t1 - min) * 60, 5)
    return deg, min, sec, loc_value


def change_to_rational(number):
    """convert a number to rantional
    Keyword arguments: number
    return: tuple like (1, 2), (numerator, denominator)
    """
    f = Fraction(str(number))
    return f.numerator, f.denominator


def set_gps_location(file_name, lat, lng, altitude):
    """Adds GPS position as EXIF metadata
    Keyword arguments:
    file_name -- image file
    lat -- latitude (as float)
    lng -- longitude (as float)
    altitude -- altitude (as float)
    """
    lat_deg = to_deg(lat, ["S", "N"])
    lng_deg = to_deg(lng, ["W", "E"])

    exiv_lat = (change_to_rational(lat_deg[0]), change_to_rational(lat_deg[1]), change_to_rational(lat_deg[2]))
    exiv_lng = (change_to_rational(lng_deg[0]), change_to_rational(lng_deg[1]), change_to_rational(lng_deg[2]))

    gps_ifd = {
        piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
        piexif.GPSIFD.GPSAltitudeRef: 1,
        piexif.GPSIFD.GPSAltitude: change_to_rational(round(altitude)),
        piexif.GPSIFD.GPSLatitudeRef: lat_deg[3],
        piexif.GPSIFD.GPSLatitude: exiv_lat,
        piexif.GPSIFD.GPSLongitudeRef: lng_deg[3],
        piexif.GPSIFD.GPSLongitude: exiv_lng,
    }

    exif_dict = {"GPS": gps_ifd}
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, file_name)


def getGPSInfo(inFile):
    """ Prints the GPS Information for a given Image
    Keyword
    arguments:
    inFile -- image File with fill path
    """
    img = Image.open(inFile)
    exif_dict = piexif.load(img.info['exif'])
    latitude = exif_dict['GPS'][piexif.GPSIFD.GPSLatitude]
    longitude = exif_dict['GPS'][piexif.GPSIFD.GPSLongitude]
    altitude = exif_dict['GPS'][piexif.GPSIFD.GPSAltitude]
    print(latitude)
    print(longitude)
    print(altitude)


def write_list_to_file(inList, csvFile):
    """Write a list to a csv file.
    Keyword
    arguments:
    inList -- input Python structured list
    csvFile -- csv file to write output data to
    """
    if path.exists(csvFile):
        remove(csvFile)
    with open(csvFile, "w") as outfile:
        for entries in inList:
            outfile.write(entries)
            outfile.write("\n")


def main(sourceImageFolder,
     gpscsv,
     errorLogCSV,
     img_Name_Column,
     Lat_Y_Column,
     Long_X_Column,
     Alt_Z_Column):
    """ Embeds Drone Flight CSV GPS Info into Image Metadata/EXIF for all images in a given folder
        arguments:
        sourceImageFolder -- input folder containing images for embedding GPS Info.
        gpscsv -- input CSV containing Image Name, Lat, Lon, Alt attributes
        img_Name_Column -- Column in CSV containing the image file name ex: flight_07.jpg
        Lat_Y_Column -- Column in CSV containing the image name
        """
    failedFiles = []
    with open(gpscsv) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        next(readCSV, None)  # Skip the header
        for row in readCSV:
            imgFile = path.join(sourceImageFolder, row[img_Name_Column])
            if not path.exists(imgFile):
                print("Skipped {0} as file does not exist in Source Image Folder Location".format(row[img_Name_Column]))
                failedFiles.append(row[img_Name_Column])
            else:
                print(imgFile)
                set_gps_location(imgFile, float(row[Lat_Y_Column]), float(row[Long_X_Column]), float(row[Alt_Z_Column]))
        if len(failedFiles) != 0:
            print("could not locate {0} files at path specified".format(len(failedFiles)))
            print("appending names of failed files to CSV to errorLog {0}".format(errorLogCSV))
            write_list_to_file(failedFiles, errorLogCSV)
            print("see {0} for list of failed files... locate the files and reprocess".format(errorLogCSV))
        del failedFiles


if __name__ == "__main__":

    #####################
    # User Input Values
    #####################
    sourceImageFolder = r'E:\WrightsvilleBeach\Sony\Flight_3'
    gpscsv = r'E:\WrightsvilleBeach\Sony\GPS\GPS_Flight_3.csv'
    errorLogCSV = r'E:\WrightsvilleBeach\errorLog.csv'
    img_Name_Column = 0
    Lat_Y_Column = 1
    Long_X_Column = 2
    Alt_Z_Column = 3

    ################
    # Begin Script
    ################
    main(sourceImageFolder, gpscsv, errorLogCSV, img_Name_Column, Lat_Y_Column, Long_X_Column, Alt_Z_Column)
