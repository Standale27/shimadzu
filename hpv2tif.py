import os
import numpy as np
import cv2
import tifffile
import inquirer as inq
import pathlib
import argparse
import subprocess as sp
from alive_progress import alive_bar
import sys

os.chdir(pathlib.Path(__file__).parent.resolve())

parser = argparse.ArgumentParser(description="Convert .DAT files to TIFF files", allow_abbrev=True)
parser.add_argument("--batchprocess", action="store_true", default=False, help="Batch process all .DAT files in the current directory")
parser.add_argument("--addtimestamp", action="store_true", default=False, help="Add relative timestamps to the bottom right of the TIFF files")
parser.add_argument("--openfolder", action="store_true", default=False, help="Open the folder of TIFF files after processing")
parser.add_argument("--makemp4", action="store_true", default=False, help="Convert the TIFF files to an MP4 video file")
args = parser.parse_args()

class DAT_Selector:
    def __init__(self):
        self.ch = []
        for item in os.listdir():
            if os.path.isdir(item) == 0:
                if item.endswith(".dat"):                    # List directory items that aren't folders and are .dat files
                    self.ch.append(item)

    def userInput(self):
        self.inputStamp = args.addtimestamp
        self.inputChoice = args.openfolder
        self.batch = args.batchprocess
        if not dat_selector.ch:
            print("No .DAT files found in the current directory.")
            sys.exit(1)
        if self.batch == False:
            self.inputFile = inq.list_input("Pick the .DAT file from the directory the script is located in", choices=self.ch)  # Prompt user input for which of these .dat files should be processed

    def dirCreation(self):
        self.outputDir = self.inputFile[:-4]
        if not os.path.isdir(self.outputDir+"_TIFF"):    # Make a folder for all the TIFF files to be put in and change to it.
            os.mkdir(self.outputDir+"_TIFF")
        self.outputStr = self.outputDir.split("\\")[-1]

class BYTE_Recoverer:
    def __init__(self):    # The .dat file is raw binary, so we read it in as byte string
        with open(dat_selector.inputFile, 'rb') as fobj:
            self.raw_bytes = fobj.read()
    def byteSearch(self, location, offsetAdd, nbytes):
        offset = self.raw_bytes.find(location)
        offset += offsetAdd
        byte_data = self.raw_bytes[offset:nbytes+offset]
        return byte_data
    def dateMaker(self):
        year = int.from_bytes(tiff_writer.dateTime_byteData[0:2],byteorder = "little", signed=False)
        month = int.from_bytes(tiff_writer.dateTime_byteData[2:4],byteorder = "little", signed=False)
        day = int.from_bytes(tiff_writer.dateTime_byteData[6:8],byteorder = "little", signed=False)
        hour = int.from_bytes(tiff_writer.dateTime_byteData[8:10], byteorder = "little", signed=False )
        minute = int.from_bytes(tiff_writer.dateTime_byteData[10:12], byteorder = "little", signed=False )
        second = int.from_bytes(tiff_writer.dateTime_byteData[12:14], byteorder = "little", signed=False )
        print('Date: ' + str(year) + '-' + str(month).zfill(2) + '-' + str(day).zfill(2) )
        print('Time: ' + str(hour).zfill(2) + ':' + str(minute).zfill(2) + ':' + str(second).zfill(2) )

class TIFF_Writer:
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_PLAIN
        self.fontScale = 1
        self.color = (255, 255, 255)
        self.thickness = 1

    def relTimeStamp(self, image):
        if dat_selector.inputStamp == True:
            rt = f'{int(self.relTime):,}'
            frameText = rt + "ns"

            text_size, _ = cv2.getTextSize(frameText, self.font, self.fontScale, self.thickness)
            org = (400-text_size[0], 250-(text_size[-1]//2)+1)

            x, y, w, h = 400-text_size[0]-1, 250-text_size[-1]-6, 100, 50          # Origin and dimensions of background translucent rectangle behind timestamp
            rtWindow = image[y:y+h, x:x+w]
            blk_rect = np.zeros(rtWindow.shape, dtype=np.uint8)
            res = cv2.addWeighted(rtWindow, 0.75, blk_rect, 0.25, 1.0)
            image[y:y+h, x:x+w] = res
            cv2.putText(image, frameText, org, self.font, self.fontScale, self.color, self.thickness, cv2.LINE_4)

    def process_file(self, dat_file, byte_recoverer, tiff_writer):
        dat_selector.inputFile = dat_file
        dat_selector.dirCreation()
        os.chdir(dat_selector.outputDir+"_TIFF")
        recSpeed = byte_recoverer.byteSearch(b'\x30\x30\x07\x30', 14, 4).decode('utf-8')[:-1]
        self.dateTime_byteData = byte_recoverer.byteSearch(b'\x40\x40\x0e\x40', 14, 16)
        imageNum = int.from_bytes(byte_recoverer.byteSearch(b'\x60\x60\x05\x60', 14, 4), "little")
        self.relTime = byte_recoverer.byteSearch(b'\x60\x60\x06\x60', 14, 4).decode('ascii')
        images_byteData = byte_recoverer.byteSearch(b'\xa0\xa0\x01\xa0', 14, (imageNum * 250 * 400 * 4))
    
        first_img = None
        with alive_bar(imageNum, spinner="dots_waves", bar=None, calibrate=60, spinner_length=30) as bar:
            for i in range(imageNum):
                is_first_img = (i <= 1)
                frameNum = f"{i+1:03d}"
                imagebytes = np.frombuffer(images_byteData[i * 200000:(i + 1) * 200000], dtype=np.int16)
                imagebytes = np.reshape(imagebytes, (250, 400))
                imagebytes = np.flipud(imagebytes)
                tifffile.imwrite(dat_selector.outputStr + f'_{frameNum}.tiff', imagebytes)
        
                img = cv2.imread(dat_selector.outputStr + f'_{frameNum}.tiff')
                tiff_writer.relTimeStamp(img)
                cv2.imwrite(dat_selector.outputStr + f'_{frameNum}.tiff', img)
        
                self.relTime = int(self.relTime) + int(recSpeed)
                bar()
            
if __name__ == "__main__":
    dat_selector = DAT_Selector()
    dat_selector.userInput()
    tiff_writer = TIFF_Writer()

    if dat_selector.batch:
        for n, dat_file in enumerate(dat_selector.ch):
            dat_selector.inputFile = dat_file
            byte_recoverer = BYTE_Recoverer()
            tiff_writer.process_file(dat_file, byte_recoverer, tiff_writer)
            print(dat_selector.outputStr + " processed! " + str(n+1) + "/" + str(len(dat_selector.ch)))
            os.chdir("..")
            if args.makemp4:
                sp.run(["python", "convert.py", "--folder", os.getcwd()+"\\"+dat_selector.outputStr+"_TIFF"], check=True)
            if n == len(dat_selector.ch)-1:
                print("All files processed!")
        if(dat_selector.inputChoice == True):
            sp.Popen(r'explorer /open,'+os.getcwd()+"\\")
    else:
        byte_recoverer = BYTE_Recoverer()
        tiff_writer.process_file(dat_selector.inputFile, byte_recoverer, tiff_writer)
        print(dat_selector.outputStr + " processed!")
        if(dat_selector.inputChoice == True):
            sp.Popen(r'explorer /open,'+os.getcwd()+"\\")
        os.chdir("..")
        if args.makemp4:
            sp.run(["python", "convert.py", "--folder", os.getcwd()], check=True)
