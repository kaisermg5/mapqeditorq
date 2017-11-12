

class ImageFormatError(Exception):
    pass


def has_valid_size(img):
    w, h = img.size
    return h % 8 == 0 and w % 8 == 0


def validate_gbaimage(img):
    if img.mode != 'P':
        raise ImageFormatError('Image is not indexed')
    if not has_valid_size(img):
        raise ImageFormatError('Image\'s height and width must be multiple of 8')


def format_palette(palette, colors=16):
    formated = [[255, 255, 255]] * colors
    for i in range(colors):
        formated[i] = palette[i * 3: (i + 1) * 3]
    return formated


def img_to_gba_16colors(img):
    validate_gbaimage(img)
    data = b''
    imgdata = img.getdata()
    w, h = img.size
    tiles_h, tiles_w = h // 8, w // 8
    for tile in range(tiles_h * tiles_w):
        tile_data = b''
        index = 8 * (tile % tiles_w) + w * 8 * (tile // tiles_w)
        for j in range(8):
            for i in range(4):
                n = (imgdata[index + 2*i + j*w] & 0xf) | ((imgdata[index + 2*i + j*w + 1] & 0xf)<< 4)
                tile_data += n.to_bytes(1, 'little')

        data += tile_data
    return data


def img_palette_to_gba(img):
    return palette_to_gba(img.getpalette())


def palette_to_gba(palette):
    formatted = format_palette(palette)
    return pal_to_gba(formatted)


def pal_to_gba(palette):
    data = b''
    for color in palette:
        r, g, b = color
        r >>= 3
        g >>= 3
        b >>= 3
        data += (r | (g << 5) | (b << 10)).to_bytes(2, 'little')
    return data

