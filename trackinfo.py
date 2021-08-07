from PIL import Image, ImageFont, ImageDraw, ImageEnhance


def duration(t):
    h = t // 3600
    m = t % 3600 // 60
    s = t % 60
    return f'{h}:{m:02}:{s:02}' if h > 0 else f'{m}:{s:02}'


def draw_progress(draw, total, current):
    h = 64
    draw.rounded_rectangle((0, h-15, 127, h-15+4), fill="black", outline="white",
                           width=1, radius=4)
    draw.rectangle((1, h-15, current/total * 128, h-15+4), fill="white")
    font = ImageFont.truetype("OpenSans-Light", 10)
    draw.text((0, h), duration(current), font=font, fill="white", anchor="ls")
    draw.text((127, h), duration(total), font=font, fill="white", anchor="rs")


def draw_text(draw, text, y, font, tick):
    x = 0
    w, _ = draw.textsize(text, font)
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
    draw.text((x, y), text, font=font, fill=(255, 255, 255))


def render(title, artist, time_total, time_current, tick):
    img = Image.new("RGB", (128, 64))
    draw = ImageDraw.Draw(img)
    draw.fontmode = "1"
    font_offset = -4
    title_font = ImageFont.truetype("OpenSans-Bold", 14)
    artist_font = ImageFont.truetype("OpenSans-Light", 14)
    draw_text(draw, title, 0 + font_offset, title_font, tick)
    draw_text(draw, artist, 14 + 10 + font_offset, artist_font, tick)
    draw_progress(draw, time_total, time_current)
    return img


if __name__ == "__main__":

    frames = []
    fps = 10
    length = 42

    bg_img = Image.new("RGB", (1024, 400), color=(255, 255, 255))
    bg_draw = ImageDraw.Draw(bg_img)
    bg_draw.rounded_rectangle((10, 10, 1024 - 20, 400 - 20),
                              fill="black", width=0, radius=20)
    for i in range(fps * length):
        frame = render("Could You Be Loved",
                       "Bob Marley & The Wailers", length, i//fps, i)
        frame_with_bg = bg_img.copy()
        frame_with_bg.paste(frame, ((1024-128)//2, (400-64)//2))
        frames.append(frame_with_bg)

    frames[0].save('test.gif', format='GIF',
                   append_images=frames[1:], save_all=True, fps=fps, loop=0)
