def generate_local(name, zodiac):
    import os
    path='outputs/sigils'
    os.makedirs(path,exist_ok=True)
    fn=f'{path}/{name}_{zodiac}.png'
    from PIL import Image
    Image.new('RGB',(200,200)).save(fn)
    return fn