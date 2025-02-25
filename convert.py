import os
import inquirer as inq
import subprocess as sp
import pathlib, sys
import moviepy as mpy
from alive_progress import alive_bar

os.chdir(pathlib.Path(__file__).parent.resolve())              # Change directory to specified path

class mp4Constructor:
    def __init__(self):
        os.chdir(inq.list_input("Pick folder of TIFF16s files for conversion to MP4", choices=[x for x in os.listdir() if os.path.isdir(os.path.join(os.getcwd(), x))]))
        self.inputChoice = inq.list_input("Do you want the MP4 file highlighted in the folder afterward?", choices=['No', 'Yes'])
    def fileName(self):
        self.video_name = os.getcwd().split("\\")[-1] + ".MP4"   # Identify name of target video. If exists in folder, replace. If not, continue.
        if self.video_name in os.listdir():
            print("File already exists! Replacing...")
            os.remove(self.video_name)
    def imgList(self):                                           # Create list of the tiff files in the target folder (no dirs, no non-tiffs)
        self.imgs = []
        for item in os.listdir():
            if os.path.isdir(item) == 0:
                if item.endswith(".tiff"):
                    self.imgs.append(item)

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