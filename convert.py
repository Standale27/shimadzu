import os
import inquirer as inq
import subprocess as sp
import pathlib, sys
import moviepy as mpy
import argparse
from alive_progress import alive_bar

parser = argparse.ArgumentParser(description="Convert .DAT files to TIFF files", allow_abbrev=True)
parser.add_argument("--batchprocess", action="store_true", default=False, help="Batch process all .DAT files in the current directory")
parser.add_argument("--folder", type=str, default=None, help="Specify a .DAT file to process")

args = parser.parse_args()

os.chdir(pathlib.Path(__file__).parent.resolve())              # Change directory to specified path

class mp4Constructor:
    """
    Class to convert a folder of TIFF16s files to an MP4 video file.
    """
    def __init__(self):
        """
        Initialize the mp4Constructor class.
        """
        if args.folder is None and args.batchprocess == False:
            os.chdir(inq.list_input("Pick folder of TIFF16s files for conversion to MP4", choices=[x for x in os.listdir() if os.path.isdir(os.path.join(os.getcwd(), x))]))
            self.inputChoice = inq.list_input("Do you want the MP4 file highlighted in the folder afterward?", choices=['No', 'Yes'])
        else:
            os.chdir(args.folder)
            self.inputChoice = 'No'
    def fileName(self):
        """
        Create the name of the MP4 file based on the current working directory.
        """
        self.video_name = os.getcwd().split("\\")[-1] + ".MP4"
        if self.video_name in os.listdir():
            print("File already exists! Replacing...")
            os.remove(self.video_name)
    def imgList(self):
        """
        Create a list of all TIFF files in the current working directory.
        """
        self.imgs = [item for item in os.listdir() if item.endswith(".tiff") and not os.path.isdir(item)]


if __name__ == "__main__":
    mc = mp4Constructor()
    mc.fileName()
    mc.imgList()
    print("Creating MP4...")

    with alive_bar(1, spinner="dots_waves", bar=None, calibrate=60, spinner_length=6) as bar:
        clips = []
        for img in mc.imgs:
            clips.append(mpy.ImageClip(img).with_duration(15**-1))
        concat_clip = mpy.concatenate_videoclips(clips, method="compose")
        concat_clip.write_videofile(mc.video_name, fps=60, preset="slow", codec='h264', logger=None, bitrate="16M", threads=4)
        bar()
    print(mc.video_name + " has been created!")
    if(mc.inputChoice == "Yes"):
        sp.Popen(r'explorer /select,'+os.getcwd()+"\\"+mc.video_name)  # Show video file in explorer