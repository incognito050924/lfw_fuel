from __future__ import absolute_import
from __future__ import print_function
import numpy as np
np.random.seed(1337)  # for reproducibility

from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Conv2D, MaxPooling2D
from keras.utils import np_utils
from scipy.misc import imresize 

# this allows the example to be run in-repo
# (or can be removed if lfw_fuel is installed)
import sys
sys.path.append('.')

from lfw_fuel import lfw

'''
    Train a simple convnet on the LFW dataset.
'''

batch_size = 128
nb_classes = 2
nb_epoch = 12
feature_width = 32
feature_height = 32

def cropImage(im):
    im2 = np.dstack(im).astype(np.uint8)
    # return centered 128x128 from original 250x250 (40% of area)
    newim = im2[61:189, 61:189]
    sized1 = imresize(newim[:,:,0:3], (feature_width, feature_height), interp="bicubic", mode="RGB")
    sized2 = imresize(newim[:,:,3:6], (feature_width, feature_height), interp="bicubic", mode="RGB")
    return np.asarray([sized1[:,:,0], sized1[:,:,1], sized1[:,:,2], sized2[:,:,0], sized2[:,:,1], sized2[:,:,2]])

# the data, shuffled and split between train and test sets
(X_train, y_train), (X_test, y_test) = lfw.load_data("deepfunneled")
# crop features
X_train = np.asarray(list(map(cropImage, X_train)))
X_test = np.asarray(list(map(cropImage, X_test)))

# print shape of data while model is building
print("{1} train samples, {2} channel{0}, {3}x{4}".format("" if X_train.shape[1] == 1 else "s", *X_train.shape))
print("{1}  test samples, {2} channel{0}, {3}x{4}".format("" if X_test.shape[1] == 1 else "s", *X_test.shape))

# convert class vectors to binary class matrices
Y_train = np_utils.to_categorical(y_train, nb_classes)
Y_test = np_utils.to_categorical(y_test, nb_classes)

model = Sequential()

model.add(Conv2D(32, (3,3), input_shape=(6,32,32), padding='valid'))
model.add(Activation('relu'))
model.add(Conv2D(32, (3,3), input_shape=(6,32,32), padding='valid'))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(128))
model.add(Activation('relu'))
model.add(Dropout(0.5))

model.add(Dense(nb_classes))
model.add(Activation('softmax'))

model.compile(loss='categorical_crossentropy', metrics=['binary_accuracy'], optimizer='adadelta')

model.fit(X_train, Y_train, batch_size=batch_size, epochs=nb_epoch, verbose=1, validation_data=(X_test, Y_test))
score = model.evaluate(X_test, Y_test, verbose=0)
print('Test score:', score[0])
print('Test accuracy:', score[1])
