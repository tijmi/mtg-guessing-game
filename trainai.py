import tensorflow as tf
from sklearn.model_selection import train_test_split
import json
from tqdm import tqdm
import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix,ConfusionMatrixDisplay
from sklearn.utils.class_weight import compute_class_weight

class trainer:
    def __init__(self,datapath: str = "data/processed_images",json_path: str = "data_labels.json"):
        self.datapath = datapath
        self.json_path = json_path
        self.input_shape = None
        with open(self.json_path, 'r') as f:
            self.data = json.load(f)
        if not isinstance(self.data, dict):
            raise ValueError("please first import data")
        self.class_names = list(self.data.keys())
        self.num_classes = len(self.class_names)
        self.x = []
        self.y = []
        self.class_weight = None
        self.gpus = tf.config.list_physical_devices('GPU')
        for gpu in self.gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
            
    
    def preparedata(self):
        self.x = []
        self.y = []
        total_images = sum(len(self.data[key].get("augmented_images", [])) for key in self.class_names)
        print(list(enumerate(self.class_names)))
        with tqdm(total=total_images, desc="labeling data", unit="img", position=0, leave=True) as self.pbar:
            for i, key in enumerate(self.class_names):
                for image in self.data[key]["augmented_images"]:
                    img = cv2.imread(image, cv2.IMREAD_ANYCOLOR)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    if img is None:
                        self.pbar.update(1)
                        continue
                    self.y.append(i)
                    self.x.append(img)
                    
                    self.pbar.update(1)
        if not self.x:
            raise ValueError("No readable images found in prepared dataset.")

        max_height = max(img.shape[0] for img in self.x)
        max_width = max(img.shape[1] for img in self.x)
        
        padded_images = []
        for img in self.x:
            h, w = img.shape[:2]
            bottom = max_height - h
            right = max_width - w
            padded = cv2.copyMakeBorder(
                img,
                0,
                bottom,
                0,
                right,
                borderType=cv2.BORDER_CONSTANT,
                value=(0, 0, 0),
            )
            padded_images.append(padded)

        self.x = np.stack(padded_images).astype(np.float32)
        self.y = np.array(self.y, dtype=np.int32)
        self.input_shape = self.x.shape[1:]
        
        if self.input_shape[0] < 96 or self.input_shape[1] < 96:
            print("Resizing images to 96x96 for MobileNetV2...")
            self.x = tf.image.resize(self.x, [96, 96]).numpy()
            self.input_shape = self.x.shape[1:]

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.x, self.y, test_size=0.2, random_state=42, stratify=self.y
        )
        print(f"Training samples: {len(self.X_train)}, Testing samples: {len(self.X_test)}")

                    
    def model(self):
        if self.input_shape is None:
            raise ValueError("Run preparedata() before building the model")

        # ── Pretrained base ──────────────────────────────────────────────
        self.base_model = tf.keras.applications.MobileNetV2(
            input_shape=self.input_shape,
            include_top=False,
            weights='imagenet'
        )
        self.base_model.trainable = False  # Frozen for phase 1

        # ── Build model ──────────────────────────────────────────────────
        inputs = tf.keras.Input(shape=self.input_shape)
        
        x = tf.keras.layers.RandomFlip("horizontal")(inputs)
        x = tf.keras.layers.RandomRotation(0.15)(x)
        x = tf.keras.layers.RandomZoom(0.2)(x)
        x = tf.keras.layers.RandomBrightness(0.2)(x)
        x = tf.keras.applications.mobilenet_v2.preprocess_input(x) 
        x = self.base_model(x, training=False)
        x = tf.keras.layers.GlobalAveragePooling2D()(x)
        x = tf.keras.layers.Dense(128, activation='relu')(x)
        x = tf.keras.layers.Dropout(0.4)(x)
        outputs = tf.keras.layers.Dense(self.num_classes, activation='softmax')(x)

        self.model = tf.keras.Model(inputs, outputs)


    def compile_model(self, learning_rate=1e-3):
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
    def train(self):
        callbacks = [
            tf.keras.callbacks.ModelCheckpoint(
                "mtgmodel.keras", save_best_only=True, monitor="val_loss", mode="min"
            ),
            tf.keras.callbacks.EarlyStopping(
                monitor="val_loss", patience=10, restore_best_weights=True
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor="val_loss", factor=0.5, patience=4, min_lr=1e-6
            ),
        ]

        print("\nPhase 1: Training head only...")
        hist1 = self.model.fit(
            self.X_train, self.y_train,
            epochs=20,
            batch_size=32,
            validation_split=0.2,
            callbacks=callbacks
        )

        print("\nPhase 2: Fine-tuning top layers...")
        self.base_model.trainable = True
        for layer in self.base_model.layers[:-30]:
            layer.trainable = False

        self.compile_model(learning_rate=1e-5)

        hist2 = self.model.fit(
            self.X_train, self.y_train,
            epochs=50,
            batch_size=16,
            validation_split=0.2,
            callbacks=callbacks
        )
        
        acc = hist1.history['accuracy'] + hist2.history['accuracy']
        val_acc = hist1.history['val_accuracy'] + hist2.history['val_accuracy']
        plt.figure(figsize=(10,5))
        plt.plot(acc, label='accuracy')
        plt.plot(val_acc, label = 'val_accuracy')
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
        # ── Standard confusion matrix ────────────────────────────────────
        cm = confusion_matrix(self.y_test, y_pred)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm)
        disp.plot()
        plt.title("Confusion Matrix (Test Set)")
        plt.savefig('confusion_matrix.png')
        plt.show(block=False)

        # ── Predict on scryfall images ───────────────────────────────────
        scryfall_images = []
        scryfall_labels = []

        for i, key in enumerate(self.class_names):
            imgs_path = self.data[key].get("scryfall_image")
            for img_path in imgs_path or []:
                if img_path:
                    img = cv2.imread(img_path)
                    if img is not None:
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                        # Apply same preprocessing as training
                        h, w = img.shape[:2]
                        max_h = max(self.input_shape[0], h)
                        max_w = max(self.input_shape[1], w)
                        img = cv2.copyMakeBorder(
                            img, 0, max_h - h, 0, max_w - w,
                            borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0)
                        )
                        img = cv2.resize(img, (self.input_shape[1], self.input_shape[0]))
                        scryfall_images.append(img.astype(np.float32))
                        scryfall_labels.append(i)
                    else:
                        print(f"Warning: could not load scryfall image for {key}")
                else:
                    print(f"Warning: no scryfall_image key for {key}")

        if not scryfall_images:
            print("No scryfall images found, skipping scryfall confusion matrix.")
            return

        X_scryfall = np.stack(scryfall_images)
        y_scryfall = np.array(scryfall_labels, dtype=np.int32)

        y_scryfall_pred = self.to_class_labels(self.model.predict(X_scryfall))

        # Print per-card result

        # ── Scryfall confusion matrix ────────────────────────────────────
        cm_scryfall = confusion_matrix(y_scryfall, y_scryfall_pred, labels=list(range(self.num_classes)))
        disp2 = ConfusionMatrixDisplay(
            confusion_matrix=cm_scryfall,
            display_labels=self.class_names
        )
        disp2.plot(xticks_rotation=45)
        plt.title("Confusion Matrix (Scryfall Images)")
        plt.tight_layout()
        plt.savefig('confusion_matrix_scryfall.png')
        plt.show(block=False)
        
        
    def trainmodel(self):
        self.model()
        self.compile_model()
        self.train()
        self.evaluate()
        self.model.save("mtgmodel.keras") 
