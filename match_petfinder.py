import os
import sys
import cv2
import numpy as np
import pickle

savedata = pickle.load( open( "dirpaths_config.p", "rb" ) )


def match_faces(image, threshold,model_name):
    t = float(threshold)
    model = cv2.createEigenFaceRecognizer(threshold=t)

    # Load the model
    model.load(model_name)

    # Read the image we're looking for
    sampleImage = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
    sampleImage = cv2.resize(sampleImage, (256,256))

    # Look through the model and find the face it matches
    [p_label, p_confidence] = model.predict(sampleImage)

    # Print the confidence levels
#    print "Predicted label = %d (confidence=%.2f)" % (p_label, p_confidence)

    # If the model found something, print the file path
    if (p_label > -1):
        subdirname_return = savedata['filelist'][p_label]
        return str(subdirname_return)
    else:
        return -1

if __name__ == "__main__":

    # Requires path to training image folder, and image we want to find.
    # Each subfolder should be of the same subject.
    """
     Eg:
    |-path
      |-Alice
      | |-0.jpg
      | |-1.jpg
      |
      |-Bob
      | |-0.jpg
      |
      |-Carly
      ...
    """
   
    if len(sys.argv) < 3:
        print "USAGE: recognise.py </path/to/images> sampleImage.jpg threshold"
        print "threshold is an float. Choose 100.0 for an extremely close match.  Choose 100000.0 for a fuzzier match. Have you updated the file pickle for a new model creation with new data?"
        print str(len(sys.argv))
        sys.exit()
        
    print match_faces(image=sys.argv[1],threshold=sys.argv[2],model_name=sys.argv[3])
