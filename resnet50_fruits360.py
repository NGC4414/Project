# -*- coding: utf-8 -*-
"""ResNet50 Fruits2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Oqg4IjDbsrCxCrF3GbeKHWryrW-n4rmH
"""

!pip install kaggle

from google.colab import drive  #mounting the google drive
drive.mount('/content/drive')

!mkdir /root/.kaggle  # creating a kaggle directory in the root folder, transfer the kaggle.json file in this folder

!cp /content/drive/MyDrive/kaggle.json /root/.kaggle/kaggle.json

!chmod 600 /root/.kaggle/kaggle.json # set the permissions

!mkdir /content/drive/MyDrive/datasets # create a directory to store all the datasets in the Google drive

!kaggle datasets download moltean/fruits  #downloading the dataset from Kaggle

!unzip fruits -d /content/drive/MyDrive/datasets/fruits360  # unzipping the folder dowloaded

!ls /content/drive/MyDrive/datasets/fruits360/fruits-360_dataset/fruits-360  # exploring what's inside the folder

import tensorflow as tf
from collections import Counter
from tensorflow.keras.layers import Input, Lambda, Dense, Flatten
from tensorflow.keras.models import Model
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import confusion_matrix
import numpy as np
import matplotlib.pyplot as plt

from glob import glob
import itertools
import warnings
warnings.filterwarnings("ignore")

import os
os.listdir('/content/drive/MyDrive/datasets/fruits360/fruits-360_dataset/fruits-360/Training') # checking the training folder

os.listdir('/content/drive/MyDrive/datasets/fruits360/fruits-360_dataset/fruits-360/Test')  #checking the test folder

#Setting Training & Test dir paths
train_path_initial = '/content/drive/MyDrive/datasets/fruits360/fruits-360_dataset/fruits-360/Training/' 

valid_path_initial = '/content/drive/MyDrive/datasets/fruits360/fruits-360_dataset/fruits-360/Test/'

# calculating the top 20 classes 

classes = []
fruit_item = []
for i in os.listdir(train_path_initial):
  for image_filename in os.listdir(train_path_initial+i):
    classes.append(i)
    fruit_item.append(i+'/'+ image_filename)

count = Counter(classes)
most_frequent = count.most_common(20)
print("Top 20 frequent Fruits:")
most_frequent

# re-size all the images to this
IMAGE_SIZE = [100, 100]

# training config:
epochs = 10
batch_size = 32

# setting new reduced training and test paths
train_path = '/content/drive/MyDrive/datasets/fruits360/fruits-360_dataset/fruits-360/Training/Training2/' 
valid_path = '/content/drive/MyDrive/datasets/fruits360/fruits-360_dataset/fruits-360/Test/Test2/'

os.listdir('/content/drive/MyDrive/datasets/fruits360/fruits-360_dataset/fruits-360/Training/Training2')

os.listdir('/content/drive/MyDrive/datasets/fruits360/fruits-360_dataset/fruits-360/Test/Test2')

# getting number of files
image_files = glob(train_path + '/*/*.jp*g')
valid_image_files = glob(valid_path + '/*/*.jp*g')

folders = glob(train_path + '/*')

# look at a random image
plt.imshow(image.load_img(np.random.choice(image_files)));

# Data Augmentation of ImageDataGenerator

train_gen = ImageDataGenerator(
  rotation_range= 40,
  width_shift_range=0.5,
  height_shift_range=0.1,
  shear_range=0.2,
  zoom_range=0.1,
  horizontal_flip=True,
  vertical_flip=True,
  preprocessing_function=preprocess_input)

val_gen = ImageDataGenerator(
  preprocessing_function=preprocess_input
)

# creating iterators
train_generator = train_gen.flow_from_directory(
  train_path,
  target_size=IMAGE_SIZE,
  shuffle=True,
  batch_size=batch_size,
  class_mode='sparse',
)

valid_generator = val_gen.flow_from_directory(
  valid_path,
  target_size=IMAGE_SIZE,
  shuffle=False,
  batch_size=batch_size,
  class_mode='sparse',
)

# Uploading ResNet50 and then applying some output layers
pretrained_model= tf.keras.applications.ResNet50(include_top=False,
                   input_shape=(100, 100, 3),
                   weights='imagenet')

for layer in pretrained_model.layers:
        layer.trainable=False

model = tf.keras.models.Sequential([    
    pretrained_model,
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.25),
    tf.keras.layers.Dense(5,activation='softmax')
])
model.summary()

# tell the model what cost and optimization method to use
model.compile(
  loss='sparse_categorical_crossentropy',
  optimizer='adam',
  metrics=['accuracy'])

# defining a callback function to stop the model 
class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self,epoch,logs={}):
    if(logs['accuracy']>=0.99):
      self.model.stop_training=True

callbacks=myCallback()

# fitting the model
hist = model.fit(
  train_generator,
  validation_data=valid_generator,
  epochs=epochs,
  steps_per_epoch=len(image_files) // batch_size,
  validation_steps=len(valid_image_files) // batch_size,
  callbacks = [callbacks],
)

#accuracy plot
plt.plot(hist.history['accuracy'], label='train accuracy')
plt.plot(hist.history['val_accuracy'], label='val accuracy')
plt.axis(ymin=0.4,ymax=1.05)
plt.grid()
plt.title('ResNet50 Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epochs')
plt.legend(['train', 'validation'])
plt.show()

# loss plot
plt.plot(hist.history['loss'], label='train loss')
plt.plot(hist.history['val_loss'], label='val loss')
plt.axis(ymin=0,ymax=1)
plt.grid()
plt.title('ResNet50 Loss')
plt.ylabel('Loss')
plt.xlabel('Epochs')
plt.legend(['train', 'validation'])
plt.show()

model.save('fruits-360_dataset/fruits-360')

model.evaluate(valid_generator)

from tensorflow import keras
model = keras.models.load_model('fruits-360_dataset/fruits-360')