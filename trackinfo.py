from PIL import Image, ImageFont, ImageDraw, ImageEnhance


def duration(t):
    h = t // 3600
    m = t % 3600 // 60
    s = t % 60
    return f'{h}:{m:02}:{s:02}' if h > 0 else f'{m}:{s:02}'


def draw_progress(draw, total, current):
    h = 64
    draw.rounded_rectangle((0, h-16, 127, h-16+4), fill="black", outline="white",
                           width=1, radius=4)
    draw.rectangle((1, h-16, 1 + current/total * 127, h-16+4), fill="white")
    font = ImageFont.truetype("DotMatrixDigits", 7)
    draw.text((0, h), duration(current), font=font, fill="white", anchor="ls")
    draw.text((129, h), duration(total), font=font, fill="white", anchor="rs")


def draw_text(draw, text, y, font, tick):
    w, _ = draw.textsize(text, font)
    x = (128 - w) / 2
    if w > 128:
        offscreen_width = (w - 128)
        pause_ticks = 50
        i = tick % (offscreen_width * 2 + pause_ticks * 2)
        o = 0
        if i < pause_ticks:
            o = 0
        elif i < pause_ticks + offscreen_width:
            o = i-pause_ticks
        elif i < pause_ticks + offscreen_width + pause_ticks:
            o = offscreen_width
        else:
            o = 2*offscreen_width - (i - pause_ticks*2)
        x = -o
    draw.text((x, y), text, font=font, fill="white")


def render(title, artist, time_total, time_current, tick):
    img = Image.new("RGB", (128, 64))
    draw = ImageDraw.Draw(img)
    # draw.rectangle((0, 0, 128, 64), fill=(42, 42, 42))
    draw.fontmode = "1"
    title_font = ImageFont.truetype("OpenSansBit-Bold", 13)
    artist_font = ImageFont.truetype("OpenSansBit-Light", 13)
    draw_text(draw, title, 0, title_font, tick)
    draw_text(draw, artist, 25, artist_font, tick)
    draw_progress(draw, time_total, time_current)
    return img


if __name__ == "__main__":

    frames = []
    fps = 10
    length = 42

    pixel_per_mm = 128 / 55
    rect_w = round(215 * pixel_per_mm)
    rect_h = round(50 * pixel_per_mm)
    rect_r = round(0.25 * 25.4 * pixel_per_mm)
    margin = round(10 * pixel_per_mm)
    bg_w = rect_w + 2 * margin
    bg_h = rect_h + 2 * margin

    bg_img = Image.new("RGB", (bg_w, bg_h), color=(255, 255, 255))
    bg_draw = ImageDraw.Draw(bg_img)
    bg_draw.rounded_rectangle(
        (margin, margin, rect_w + margin, rect_h + margin), fill="black", width=0, radius=rect_r)
    for i in range(fps * length):
        frame = render("Music Sounds Better With You",
                       "Stardust", length, i//fps, i)
        frame_with_bg = bg_img.copy()
        frame_with_bg.paste(frame, ((bg_w-128)//2, (bg_h-64)//2))
        frames.append(frame_with_bg)

    frames[0].save('demo.gif', format='GIF', append_images=frames[1:],
                   save_all=True, fps=fps, disposal=2, loop=0)
