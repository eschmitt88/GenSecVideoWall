import math


def best_fit(area_shape, section_shape, n):
    W, H = area_shape
    w, h = section_shape
    
    cols = 1
    rows = math.ceil(n / cols)
    width = W / cols
    height = H / rows
    scale_factor = min(width/w, height/h)
    improving = True
    while improving:
        cols += 1
        rows = math.ceil(n / cols)
        width = W / cols
        height = H / rows
        scale_factor_new = min(width/w, height/h)
        if scale_factor_new < scale_factor:
            improving = False
        else:
            scale_factor = scale_factor_new

    cols -= 1
    rows = math.ceil(n / cols)
    width = W / cols
    height = H / rows
    scale_factor = min(width/w, height/h)
    width = w * scale_factor
    height = h * scale_factor

    return (width, height), (cols, rows)


if __name__ == "__main__":
    output = best_fit((100, 50), (100, 10), 10)
    print(output)
    output = best_fit((900, 900), (300, 300), 10)
    print(output)
    output = best_fit((200, 1000), (1920, 1080), 16)
    print(output)
