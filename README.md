# shimadzu

Enables conversion of proprietary .DAT files for Shimadzu HPV software from .DAT to however many .TIFF 16-bit frames are in the video
Include both scripts and the .DLL file in the directory with the .DAT files

hpv2tif.py with no flags:
-Select a .DAT file from the given list
-Indicate whether relative timestamps should be overlaid on the frames or not
-Indicate if the folder of .TIFF files should be opened after conversion
-Wait until completion

convert.py:
-Select a directory from the given list (assumes directory is full of .tiff files)
-Indicate if the MP4 file should be highlighted in the folder after conversion
-Wait until completion

hpv2tif.py has these available flags:
-ys for: yes, stamps
-ns for: no, stamps
-yc for: yes, open folder upon completion
-nc for: no, open folder upon completion
-mp4 for: Runs convert.py script immediately following completion

Example:
python hpv2tif.py -ys -nc -mp4
Will run hpv2tif.py, will include relative timestamps in the bottom right corner, will not open the folder upon completion, will run the convert.py script right after.

No flags:
-Run hpv2tif.py
-Select a .DAT file from the given list
-Indicate whether relative timestamps should be overlaid on the frames or not
-Indicate if the folder of .TIFF files should be opened after conversion
-Wait until completion
-Run convert.py
-Select a directory from the given list (assumes directory is full of .tiff files)
-Indicate if the MP4 file should be highlighted in the folder after conversion
-Wait until completion

With flags:
-Run hpv2tif.py
-Select a .DAT file from the given list
-Select a directory from the given list (assumes directory is full of .tiff files)
-Indicate if the MP4 file should be highlighted in the folder after conversion
-Wait until completion

Future work will involve streamlining the scripts and making it more modular, as well as implementing actual good coding practices. Could automate object tracking now as well. Could explore batch conversion as well. Could explore rewriting in rust for performance as well.
