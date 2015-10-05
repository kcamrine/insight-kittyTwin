'''
 this script is an adaptation to download a list of files via a
 text file and extracting faces from them, to a list of cat
 pictures, extracting faces and saving them to a folder.
 will adapt later to store in mySQL database
 
 Adapted from: edent/Tate-Hack downloadface.py script on 9/17/15
'''

import petfinder
import cv2
import urllib
from urlparse import urlparse
import sys, os


# Query away!
#for shelter in api.shelter_find(location=zip_code, count=count):
#    print(shelter['name'])

def ensure_dir(f): #this doesn't work
    if f != '':
        d = os.path.dirname(f)
        if not os.path.exists(d):
            os.makedirs(d)

def detect(path):
    img = cv2.imread(path)
    cascade = cv2.CascadeClassifier("/usr/local/Cellar/opencv/2.4.12/share/OpenCV/haarcascades/haarcascade_frontalcatface.xml") #need to change this so it's not looking locally on my machine
    rects = cascade.detectMultiScale(img, 1.4, 6, cv2.cv.CV_HAAR_SCALE_IMAGE, (20,20))
    if len(rects) == 0:
        return [], img
    rects[:, 2:] += rects[:, :2]
    return rects, img

def box(rects, img, file_name_base):
    i = 0   #   Track how many faces found
    for x1, y1, x2, y2 in rects:
#        print "Found " + str(i) + " face!"  #   Tell us what's going on
        cut = img[y1:y2, x1:x2] #   Defines the rectangle containing a face
#        dir_name = 'detected/' + str(file_name)
        file_name = file_name_base + '.jpg'
        file_name = file_name.replace('.jpg','_')   #   Prepare the filename 
        file_name = file_name + str(i) + '.jpg'
        file_name = file_name.replace('\n','')
#        print 'Writing ' + file_name
        cv2.imwrite('detected/' + str(file_name), cut)   #   Write the file
        i += 1  #   Increment the face counter
    return i

def run_algo(pet):
    sub_image_detect = 0
    for i in range(len(pet['photos'])):
        line = pet['photos'][i]['url']
        file_name = urlparse(line).path.split('/')[-3] #find cat ID
#        print "URL is " + line
        if (urllib.urlopen(line).getcode() == 200):
            #   Download to a temp file
            urllib.urlretrieve(line, "temp.jpg") #save original picture to detect face
            #   Detect the face(s)
            rects, img = detect("temp.jpg")
            #   Cut and keep
            face = box(rects, img, file_name) #save the cat face if detected with cat ID as filename
            sub_image_detect += face
        else:
            print '404 - ' + line   
    return sub_image_detect

def write_DescTable(pet): #save descriptions
    fo = open("descriptions.txt", "ab")
    description = pet['description']
    fo.write('%s,"%s"\n' %(str(pet['id']),unicode(description).encode('utf8')))
    fo.close()
    
def write_nameTable(pet): #save pet name
    fo = open("names.txt","ab")
    fo.write("%s,%s,%s\n" %(str(pet['id']),str(pet['name']),str(pet['photos'][0]['url'])))
    fo.close()
    
def write_contactInfo(pet): #save contact Information for shelter
    fo = open("website.txt","ab")
    fo.write("%s,%s,%s,%s,%s,%s\n" %(str(pet['id']),str(pet['contact']['city']),str(pet['contact']['email']),str(pet['contact']['phone']),str(pet['shelterId']),str(pet['contact']['zip'])))
    fo.close()

def main():
    ###### set this to a file you don't upload to github before you upload (.gitignore)
    api_key = "c0970e23404e1cd9306244fcf82fa453"
    api_secret = "ab608af1987034a67e0f5f9d8ecd67d1"
    zip_code = '93063' #change to input 

    # Instantiate the client with your credentials.
    api = petfinder.PetFinderClient(api_key=api_key, api_secret=api_secret)

    image_detect = 0 #how many cats actually have detectable faces
    cat = 0
    for pet in api.pet_find(animal="cat", location=zip_code, output="full"):
        cat+=1
        try:
            line = pet['photos'][0]['url'] #detect picture URL
        except IndexError:
            line = 'null'
        sub_image_detect = 0
        if line != 'null': #if no picture, skip record
            sub_image_detect = run_algo(pet)
        if sub_image_detect > 0:
            write_DescTable(pet)
            write_nameTable(pet)
            write_contactInfo(pet)
            image_detect+=1
        if image_detect % 10 == 0:
            print 'images detected: ' + str(image_detect)
            print 'cats looped: ' + str(cat)
            
            
if __name__ == "__main__":
    main()