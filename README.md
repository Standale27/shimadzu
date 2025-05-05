# shimadzu

>Example .DAT file available here: https://drive.google.com/file/d/1J8KFRbFUlyxr1bG1Lk7j8ygkmhae3aHw/view?usp=sharing

Enables conversion of proprietary .DAT files for Shimadzu HPV software from .DAT to however many .TIFF 16-bit frames are in the video using the hpv2tif.py script
Also allows for conversion of the .TIFF files to .MP4 files with the convert.py script
Include both scripts and the .DLL file in the directory with the .DAT files


Running hpv2tif.py with no specified arguments will list the .DAT files in the directory in which the script is located. Choose a file to create the folder of TIFF images.

There are four arguments you can use when running hpv2tif.py:
>--batchprocess
      Batch processes all .DAT files in current directory
>--addtimestamp
      Adds timestamps in the bottom right corner of the generated .TIFF files
>--openfolder
      Opens the folder for the converted .DAT file/files
>--makemp4
      Runs convert.py after the .DAT file has been converted. This takes ~25 seconds per .DAT file

Convert.py works similarly, where running the script by itself will list the folders in the directory. Choose a folder with .TIFF files in it for conversion to a .MP4 video
