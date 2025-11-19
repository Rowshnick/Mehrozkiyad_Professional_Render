from PIL import Image, ImageDraw, ImageFont
import os

SYMS = {'Aries':'♈','Taurus':'♉','Gemini':'♊','Cancer':'♋','Leo':'♌','Virgo':'♍','Libra':'♎','Scorpio':'♏','Sagittarius':'♐','Capricorn':'♑','Aquarius':'♒','Pisces':'♓'}

def generate_local(name, zodiac, out_path=None):
    os.makedirs('outputs/sigils', exist_ok=True)
    safe_name = ''.join(c for c in name if c.isalnum() or c in (' ','_')).strip().replace(' ','_')
    if out_path is None:
        out_path = f"outputs/sigils/{safe_name}_{zodiac}.png"
    img = Image.new('RGB',(800,800),(18,24,44))
    draw = ImageDraw.Draw(img)
    sym = SYMS.get(zodiac,'?')
    font = None
    try:
        FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
        font = ImageFont.truetype(FONT, 160)
    except Exception:
        pass
    if font:
        w,h = draw.textsize(sym,font=font)
        draw.text(((800-w)/2,120), sym, font=font, fill=(245,220,130))
    else:
        draw.text((350,120), sym, fill=(245,220,130))
    try:
        f2 = ImageFont.truetype(FONT, 28) if font else None
        if f2:
            w,h = draw.textsize(name,font=f2)
            draw.text(((800-w)/2,700), name, font=f2, fill=(230,230,230))
        else:
            draw.text((300,700), name, fill=(230,230,230))
    except Exception:
        pass
    img.save(out_path)
    return out_path
