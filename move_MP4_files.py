import os
from datetime import datetime
import itertools
from pathlib import Path
import argparse


root = 'G'
subdir = None

parser = argparse.ArgumentParser()

parser.add_argument('-r', '--root', help='Specify the root directory of the memory card, default is: ' + str(root), type=str)
parser.add_argument('-s', '--subdir', help='Specify a sub-directory where to move files (example: Max), default is: ' + str(subdir), type=str)

args = parser.parse_args()

if args.root:
    root = args.root
if args.subdir:
    subdir = args.subdir

os.chdir(root+':\\DCIM')

processed = {}
for path in Path().rglob('*.MP4'):
    if str(path) not in list(itertools.chain.from_iterable(processed.values())):
        ts = os.path.getmtime(path)
        date = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')
        name = path.name
        if name.startswith('DJI'): # DJI files
            if (name.count('_') > 1): # if the file have sequel files, then move all sequels into the same folder 
                                      # example:
                                      # if DJI_0024_001.MP4 is created on 2020-06-13 and DJI_0024_002.MP4 is created on 2020-06-14
                                      # then both files will go into the 2020-06-13 folder
                for path in Path().rglob(name.rsplit('_',1)[0]+'*.MP4'):
                    processed.setdefault(date, []).append(str(path))
            else: # if no sequel files, normal move
                processed.setdefault(date, []).append(str(path))
        else: # GOPRO files
            if name.startswith('GOPR'):
                processed.setdefault(date, []).append(str(path)) # normal move
                # if the file have sequel files, then move all sequels into the same folder 
                # example:
                # if GOPR0598.MP4 is created on 2020-06-17 and GP010598.MP4 is created on 2020-06-18
                # then both files will go into the 2020-06-17 folder
                possible_sequel = sorted(Path().rglob('GP*'+str(name[4:])))
                if possible_sequel != []:
                    for path in possible_sequel:
                        processed.setdefault(date, []).append(str(path))
            else:
                if name.startswith('GP'):
                    processed.setdefault(date, []).append(str(path)) # if sequel file is remaining, but should not. Except for forgotten files ^^
                else:
                    print("Error: file not recognized (" + str(path) + ")")
# Create the processed dir if not exists
Path('./processed').mkdir(parents=False, exist_ok=True)
for date in processed:
    if subdir is not None:
        date_folder_path = './processed/'+str(date)+"/"+str(subdir)
    else:
        date_folder_path = './processed/'+str(date)
    Path(date_folder_path).mkdir(parents=False, exist_ok=True)
    for path in processed[date]:
        try:
            os.rename(path,date_folder_path + '/' +  str(Path(path).name))
        except FileExistsError as e:
            print(e)

for path in Path().rglob('*.LRV'): # delete GoPro's Low-Resolution Video files
    os.remove(path)
for path in Path().rglob('*.THM'): # delete GoPro's thumbnails files
    os.remove(path)