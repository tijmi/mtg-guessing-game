from pathlib import Path
import random

from PIL import Image, ImageOps, ImageEnhance, ImageFilter


class DataAugmentation:
    def __init__(self, input_dir="Data/Unprocessed", output_dir="Data/Processed", versions=10):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.versions = versions
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def augment_all(self):
        for image_path in sorted(self.input_dir.glob("*.jpg")):
            self._augment_image(image_path)

    def _augment_image(self, image_path):
        name = image_path.stem
        card_folder = self.output_dir / self._sanitize_name(name)
        card_folder.mkdir(parents=True, exist_ok=True)

        with Image.open(image_path).convert("RGB") as img:
            for version in range(1, self.versions + 1):
                augmented = self._make_augmented_version(img)
                out_path = card_folder / f"{name}_{version}.jpg"
                augmented.save(out_path, format="JPEG", quality=90)

    def _make_augmented_version(self, image):
        img = image.copy()

        # put the zaza image modifier functions here
        ops = [
            lambda im: im.rotate(random.choice([0, 90, 180, 270]), expand=True),
            lambda im: ImageOps.mirror(im),
            lambda im: ImageOps.flip(im),
            lambda im: ImageEnhance.Brightness(im).enhance(random.uniform(0.8, 1.2)),
            lambda im: ImageEnhance.Color(im).enhance(random.uniform(0.7, 1.3)),
            lambda im: ImageEnhance.Contrast(im).enhance(random.uniform(0.8, 1.2)),
            lambda im: im.filter(ImageFilter.GaussianBlur(radius=random.uniform(0, 1.5))),
            #lambda im: self._random_crop_and_resize(im),
        ]

        for op in random.sample(ops, 3): # applies 3 modifiers from the ops functions
            img = op(img)

        return img

    def _random_crop_and_resize(self, image):
        if random.random() < 0.5:
            return image
        width, height = image.size
        crop_w = random.randint(int(width * 0.9), width)
        crop_h = random.randint(int(height * 0.9), height)
        left = random.randint(0, width - crop_w)
        top = random.randint(0, height - crop_h)
        cropped = image.crop((left, top, left + crop_w, top + crop_h))
        return cropped.resize((width, height), Image.Resampling.LANCZOS)

    def _sanitize_name(self, name):
        return "".join(c for c in name if c not in '<>:"/\\|?*').strip()


if __name__ == "__main__":
    DataAugmentation().augment_all()