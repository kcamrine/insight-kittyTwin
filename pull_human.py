import sys, os
import cv2
from flask import Flask, request, send_from_directory, send_file
import glob

def detect(path):
    print path
    img = cv2.imread(path)    
    if img is None:
        print "didn't detect file"
    cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml") #need to change this so it is accessible by the app
    rects = cascade.detectMultiScale(img, 1.4, 6, cv2.cv.CV_HAAR_SCALE_IMAGE, (20,20))
    if len(rects) == 0:
        print "no freaking face, yo"
        return [], img

    rects[:, 2:] += rects[:, :2]
    return rects, img

def box(rects, img, file_name,newdir):
    i = 0   #   Track how many faces found
    orig_filename = os.path.basename(file_name)
    sub = os.path.splitext(orig_filename)[0]
    for x1, y1, x2, y2 in rects:
        print "Found " + str(i) + " face!"  #   Tell us what's going on
        cut = img[y1:y2, x1:x2] #   Defines the rectangle containing a face
        file_name = orig_filename
        file_name = file_name.replace('.jpg','_')   #   Prepare the filename 
        file_name = file_name + str(i) + '.jpg'
        file_name = file_name.replace('\n','')
        print 'Writing ' + file_name
        cv2.imwrite(os.path.join(newdir,file_name), cut)   #   Write the file
        i += 1  #   Increment the face counter
#    objects = os.listdir(os.path.join(newdir,str(sub) + "*"))
    objects = glob.glob(os.path.join(newdir,str(sub)) + '*')
    print objects
    sofar = 0
    name = ""
    if not objects:
        name = -1
    for item in objects:
        size = os.path.getsize(item)
        if size > sofar:
                sofar = size
                name = item
    return name

def pull_human(file_name,newdir):
    rects, img = detect(file_name)
    new_filename = box(rects, img, file_name, newdir)
    return new_filename

def main():
    filename = pull_human(file_name = sys.argv[1],newdir=sys.argv[2])

            
if __name__ == "__main__":
    main()
