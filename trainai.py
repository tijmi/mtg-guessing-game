import tensorflow as tf
from sklearn.model_selection import train_test_split
import json
from tqdm import tqdm
import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix,ConfusionMatrixDisplay

class trainer:
    def __init__(self,datapath: str = "data/processed_images",json_path: str = "data_labels.json"):
        self.datapath = datapath
        self.json_path = json_path
        self.input_shape = None
        with open(self.json_path, 'r') as f:
            self.data = json.load(f)
        if not isinstance(self.data, dict):
            raise ValueError("please first import data")
        self.x = []
        self.y = []
        print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
    
    
    def preparedata(self):
        with tqdm(total=len(self.data), desc="labeling data", unit="img", position=0, leave=True) as self.pbar:
            for i, key in enumerate(self.data.keys()):
                for image in self.data[key]["augmented_images"]:
                    img = cv2.imread(image, cv2.IMREAD_COLOR)
                    if img is None:
                        self.pbar.update(1)
                        continue
                    self.y.append(i)
                    self.x.append(img)
                    
                    self.pbar.update(1)
        print(self.y)
        self.x = np.array(self.x, dtype=np.float32) / 255.0
        self.y = np.array(self.y)
        self.input_shape = self.x.shape[1:]
        
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
        self.x, self.y, test_size=0.2, random_state=42, stratify=self.y
        )
        print(f"Training samples: {len(self.X_train)}, Testing samples: {len(self.X_test)}")
                    
    def model(self):
        if self.input_shape is None:
            raise ValueError("Run preparedata() before building the model")
        self.model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=self.input_shape),
        tf.keras.layers.MaxPooling2D((2, 2)),

        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(2, activation='softmax')
    ])
        
                
    def compile_model(self):
        self.model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',  # use this if y = integers
        metrics=['accuracy']
        )
        
    def train(self):
        checkpoint_cb = tf.keras.callbacks.ModelCheckpoint(
                "mtgmodel.keras", save_best_only=True, monitor="val_loss", mode="min"
        )
        hist = self.model.fit(
            self.X_train, self.y_train,
            epochs=20,
            batch_size=16,
            validation_split=0.2,
            callbacks=[checkpoint_cb]
        )

        plt.figure(figsize=(10,5))
        plt.plot(hist.history['accuracy'], label='accuracy')
        plt.plot(hist.history['val_accuracy'], label = 'val_accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.ylim([0, 1])
        plt.legend(loc='lower right')
        plt.savefig('training_accuracy.png')
        plt.show(block = False)
        
    def to_class_labels(self, predictions):
        predictions = np.asarray(predictions)
        if predictions.ndim > 1:
            return np.argmax(predictions, axis=1)
        return predictions

    def evaluate(self):
        test_loss, test_acc = self.model.evaluate(self.X_test, self.y_test)
        print(f"Test loss: {test_loss} Test accuracy: {test_acc}")
        y_pred = self.to_class_labels(self.model.predict(self.X_test))
        cm = confusion_matrix(self.y_test, y_pred)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm)
        disp.plot()
        plt.title("Confusion Matrix")
        plt.savefig('confusion_matrix.png')
        plt.show(block=False)
        
    def trainmodel(self):
        self.model()
        self.compile_model()
        self.train()
        self.evaluate()
        self.model.save("mtgmodel.keras") 
