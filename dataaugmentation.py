from pathlib import Path
import random

from PIL import Image, ImageOps, ImageEnhance, ImageFilter


class DataAugmentation:
    def __init__(
        self,
        input_dir="Data/Unprocessed",
        output_dir="Data/Processed",
        versions=3,
        output_ratio=(5, 7),
        output_scale=2,
    ):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.versions = versions
        self.output_ratio = output_ratio
        self.output_scale = output_scale
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def augment_all(self):
        for image_path in sorted(self.input_dir.glob("*.jpg")):
            self._augment_image(image_path)

    def _augment_image(self, image_path):
        name = image_path.stem
        card_folder = self.output_dir / self._sanitize_name(name)
        card_folder.mkdir(parents=True, exist_ok=True)

        with Image.open(image_path).convert("RGB") as img:
            img = self._crop_to_ratio(img, self.output_ratio)
            img = img.resize(
                (self.output_ratio[0] * self.output_scale, self.output_ratio[1] * self.output_scale),
                Image.Resampling.LANCZOS,
            )

            for version in range(1, self.versions + 1):
                augmented = self._make_augmented_version(img)
                out_path = card_folder / f"{name}_{version}.jpg"
                augmented.save(out_path, format="JPEG", quality=90)

    def _make_augmented_version(self, image):
        img = image.copy()

        # add more mods here
        ops = [
            lambda im: im.rotate(random.choice([0, 90, 180, 270]), expand=True),
            lambda im: ImageOps.mirror(im),
            lambda im: ImageOps.flip(im),
            lambda im: ImageEnhance.Brightness(im).enhance(random.uniform(0.8, 1.2)),
            lambda im: ImageEnhance.Color(im).enhance(random.uniform(0.7, 1.3)),
            lambda im: ImageEnhance.Contrast(im).enhance(random.uniform(0.8, 1.2)),
            lambda im: im.filter(ImageFilter.GaussianBlur(radius=random.uniform(0, 1.5))),
            lambda im: im.filter(ImageFilter.GaussianBlur(radius=random.uniform(0, 1.5))),
        ]

        for op in random.sample(ops, 3): # change the 3 to the amount of mods you want
            img = op(img)

        return img

    def _crop_to_ratio(self, image, ratio):
        target_w, target_h = ratio
        if target_w <= 0 or target_h <= 0:
            return image

        width, height = image.size
        target_ratio = target_w / target_h
        current_ratio = width / height

        if current_ratio > target_ratio:
            new_width = int(target_ratio * height)
            left = (width - new_width) // 2
            box = (left, 0, left + new_width, height)
        else:
            new_height = int(width / target_ratio)
            top = (height - new_height) // 2
            box = (0, top, width, top + new_height)

        return image.crop(box)

    def _sanitize_name(self, name):
        return "".join(c for c in name if c not in '<>:"/\\|?*').strip()


if __name__ == "__main__":
    DataAugmentation(output_ratio=(16, 9), output_scale=32).augment_all()