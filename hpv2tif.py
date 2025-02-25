import os
import numpy as np
import cv2
import tifffile
import inquirer as inq
import pathlib, sys
import subprocess as sp
from alive_progress import alive_bar

class DAT_Selector:
    def __init__(self):
        self.ch = []
        for item in os.listdir():
            if os.path.isdir(item) == 0:
                if item.endswith(".dat"):                    # List directory items that aren't folders and are .dat files
                    self.ch.append(item)

    def userInput(self):
        self.inputFile = inq.list_input("Pick the .DAT file from the directory the script is located in", choices=self.ch)  # Prompt user input for which of these .dat files should be processed
        self.inputStamp = ''
        self.inputChoice = ''
        if "-ys" or "-ns" in sys.argv:
            if "-ys" in sys.argv:
                self.inputStamp = 'Yes'
            if "-ns" in sys.argv:
                self.inputStamp = 'No'
        if not ("-ys" or "-ns") in sys.argv:
            self.inputStamp = inq.list_input("Do you want the relative timestamps in the bottom-right?", choices=['Yes', 'No'])
        if "-yc" or "-nc" in sys.argv:
            if "-yc" in sys.argv:
                self.inputChoice = 'Yes'
            if "-nc" in sys.argv:
                self.inputChoice = 'No'
        if not "-yc" or not "-nc" in sys.argv:
            self.inputChoice = inq.list_input("Do you want the folder of TIFF files opened afterward?", choices=['No', 'Yes'])

    def dirCreation(self):
        self.outputDir = self.inputFile[:-4]
        if not os.path.isdir(self.outputDir+"_TIFF"):    # Make a folder for all the TIFF files to be put in and change to it.
            os.mkdir(self.outputDir+"_TIFF")
        if not os.path.isdir(self.outputDir+"_TIFF/DIFFs"):    # Make a folder for all the TIFF files to be put in and change to it.
            os.mkdir(self.outputDir+"_TIFF/DIFFs")
        self.outputStr = self.outputDir.split("\\")[-1]

class BYTE_Recoverer:
    def __init__(self):    # The .dat file is raw binary, so we read it in as byte string
        with open(ds.inputFile, 'rb') as fobj:
            self.raw_bytes = fobj.read()
    def byteSearch(self, location, offsetAdd, nbytes):
        offset = self.raw_bytes.find(location)
        offset += offsetAdd
        byte_data = self.raw_bytes[offset:nbytes+offset]
        return byte_data
    def dateMaker(self):
        year = int.from_bytes(dateTime_byteData[0:2],byteorder = "little", signed=False)
        month = int.from_bytes(dateTime_byteData[2:4],byteorder = "little", signed=False)
        day = int.from_bytes(dateTime_byteData[6:8],byteorder = "little", signed=False)
        hour = int.from_bytes(dateTime_byteData[8:10], byteorder = "little", signed=False )
        minute = int.from_bytes(dateTime_byteData[10:12], byteorder = "little", signed=False )
        second = int.from_bytes(dateTime_byteData[12:14], byteorder = "little", signed=False )
        print('Date: ' + str(year) + '-' + str(month).zfill(2) + '-' + str(day).zfill(2) )
        print('Time: ' + str(hour).zfill(2) + ':' + str(minute).zfill(2) + ':' + str(second).zfill(2) )

class TIFF_Writer:
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_PLAIN
        self.fontScale = 1
        self.color = (255, 255, 255)
        self.thickness = 1
        os.chdir(ds.outputDir+"_TIFF")

    def relTimeStamp(self, image):
        if ds.inputStamp == 'Yes':
            rt = f'{int(relTime):,}'
            frameText = rt + "ns"

            text_size, _ = cv2.getTextSize(frameText, self.font, self.fontScale, self.thickness)
            org = (400-text_size[0], 250-(text_size[-1]//2)+1)

            x, y, w, h = 400-text_size[0]-1, 250-text_size[-1]-6, 100, 50          # Origin and dimensions of background translucent rectangle behind timestamp
            rtWindow = image[y:y+h, x:x+w]
            blk_rect = np.zeros(rtWindow.shape, dtype=np.uint8)
            res = cv2.addWeighted(rtWindow, 0.75, blk_rect, 0.25, 1.0)
            image[y:y+h, x:x+w] = res
            cv2.putText(image, frameText, org, self.font, self.fontScale, self.color, self.thickness, cv2.LINE_4)

if __name__ == "__main__":
    os.chdir(pathlib.Path(__file__).parent.resolve())   # Change directory to that of where this script is located

    ds = DAT_Selector()
    ds.userInput()
    ds.dirCreation()

    br = BYTE_Recoverer()
    recSpeed = br.byteSearch(b'\x30\x30\x07\x30', 14, 4).decode('utf-8')[:-1]
    dateTime_byteData = br.byteSearch(b'\x40\x40\x0e\x40', 14, 16)
    #br.dateMaker() #    Uncomment to print date and time at time of recording
    imageNum = int.from_bytes(br.byteSearch(b'\x60\x60\x05\x60', 14, 4), "little")
    relTime = br.byteSearch(b'\x60\x60\x06\x60', 14, 4).decode('ascii')
    images_byteData = br.byteSearch(b'\xa0\xa0\x01\xa0', 14, (imageNum*250*400*4))

    tw = TIFF_Writer()
    
    first_img = None
    with alive_bar(imageNum, spinner="dots_waves", bar=None, calibrate=60, spinner_length=30) as bar:
        for i in range(0, imageNum):
            is_first_img = (i <= 1)
            frameNum = "{:03d}".format(i+1)  # Format index with leading zeros for use as the frame number
            imagebytes=np.frombuffer(images_byteData[(i)*200000:200000*(i+1)],dtype=np.int16)
            imagebytes=np.reshape(imagebytes,shape=(250,400))
            imagebytes=np.flipud(imagebytes) # flip vertically to match view in HPV viewer
            tifffile.imwrite(ds.outputStr+'_'+frameNum+'.tiff', imagebytes)    # Initially, all the frames w/o the relative timestamps are created.
            
            img = cv2.imread(ds.outputStr+'_'+frameNum+'.tiff')                # Read each file in and draw the translucent black background and white text of the timestamp
            tw.relTimeStamp(img)
            cv2.imwrite(ds.outputStr+'_'+(frameNum)+'.tiff', img)              # Overwrite all of the TIFF files

            diff_img = None
            if is_first_img:
                first_img = img.copy()
            else:
                diff_A = cv2.subtract(first_img, img) #cv2.absdiff(first_img, img)
                diff_B = cv2.subtract(diff_A, cv2.threshold(diff_A, 200, 255, cv2.THRESH_TOZERO)[1])
                diff_img = cv2.add(img, diff_B)
                diff_img = cv2.normalize(diff_img, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
            if not is_first_img:
                cv2.imwrite(f"DIFFs/diff_{ds.outputStr}_{frameNum}.tiff", diff_img)

            relTime = int(relTime) + (int(recSpeed))                        # Increment the relative time by adding recSpeed to it
            bar()
    print("Finished!")

    if(ds.inputChoice == "Yes"):
        sp.Popen(r'explorer /separate,'+os.getcwd())  # Show video file in explorer
    if "-mp4" in sys.argv:
        os.chdir("..")
        os.system("python convert.py ")