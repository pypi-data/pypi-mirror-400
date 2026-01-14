import os
from itertools import (
    repeat,
)

from PIL import (
    ImageFont,
)
from PIL.Image import (
    Image,
)
from PIL.Image import (
    new as new_image,
)
from PIL.Image import (
    open as open_image,
)
from PIL.ImageDraw import (
    Draw,
    ImageDraw,
)

DUMMY_IMG: Image = new_image("RGB", (0, 0))
DUMMY_DRAWING: ImageDraw = Draw(DUMMY_IMG)


def boxify(
    *,
    width_to_height_ratio: int = 3,
    string: str,
) -> str:
    lines: list[str] = string.splitlines()

    width, height = max(map(len, [*lines, ""])), len(lines)

    missing_height: int = width // width_to_height_ratio - height

    filling: list[str] = list(repeat("", missing_height // 2))

    return "\n".join(filling + lines + filling)


def clarify_blocking(image: Image, ratio: float) -> Image:
    image_mask: Image = image.convert("L")
    image_mask_pixels = image_mask.load()

    image_width, image_height = image_mask.size

    for i in range(image_width):
        for j in range(image_height):
            if image_mask_pixels is not None and image_mask_pixels[i, j]:
                image_mask_pixels[i, j] = int(ratio * 0xFF)

    image.putalpha(image_mask)

    return image


async def to_png(*, string: str, margin: int = 25) -> Image:
    font = ImageFont.truetype(
        font=os.environ["SKIMS_ROBOTO_FONT"],
        size=18,
    )
    watermark: Image = clarify_blocking(
        image=open_image(os.environ["SKIMS_FLUID_WATERMARK"]),
        ratio=0.15,
    )
    string = boxify(string=string)
    size = DUMMY_DRAWING.multiline_textbbox((0, 0), string, font=font)[-2:]

    size = (int(size[0] + 2 * margin), int(size[1] + 2 * margin))
    watermark_size = (
        int(size[0] // 2),
        int(watermark.size[1] * size[0] // watermark.size[0] // 2),
    )
    watermark_position = (
        int((size[0] - watermark_size[0]) // 2),
        int((size[1] - watermark_size[1]) // 2),
    )

    img: Image = new_image("RGB", size, (0xFF, 0xFF, 0xFF))

    drawing: ImageDraw = Draw(img)
    drawing.multiline_text(
        xy=(margin, margin),
        text=string,
        fill=(0x33, 0x33, 0x33),
        font=font,
    )

    watermark = watermark.resize(watermark_size)
    img.paste(watermark, watermark_position, watermark)
    return img
