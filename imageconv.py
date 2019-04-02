from PIL import Image
from pathlib import Path
from shutil import rmtree 

def image_converter(path, out_dir):
    parent_dir = path.parent
    in_img = Image.open(path)

    lum = in_img.convert('L')

    blue = Image.new('L', lum.size, (255,))

    out_img = Image.merge('RGB', [lum, lum, blue])

    in_img.save(Path.joinpath(out_dir, 'thumbnail.jpg'), quality=70, progressive=True)
    out_img.save(Path.joinpath(out_dir, 'thumbnail_blue.jpg'), quality=70, progressive=True)


out_dir = Path.joinpath(Path.cwd(), 'out')
rmtree(str(out_dir))
out_dir.mkdir()

in_dir = Path.joinpath(Path.cwd(), 'in')

out_projects = Path.joinpath(out_dir, 'projects')
out_projects.mkdir()

in_projects_dir = Path.joinpath(in_dir, 'projects')

for in_proj_dir in in_projects_dir.iterdir():

    out_proj_dir = Path.joinpath(out_projects, in_proj_dir.stem)
    out_proj_dir.mkdir()
    image_converter(Path.joinpath(in_proj_dir, 'preview.jpg'), out_proj_dir)
    