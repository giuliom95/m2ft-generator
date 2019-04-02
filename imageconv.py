from PIL import Image
from pathlib import Path
from shutil import rmtree 
from json import load


def image_converter(path, out_dir):
    parent_dir = path.parent
    in_img = Image.open(path)

    lum = in_img.convert('L')

    blue = Image.new('L', lum.size, (255,))

    out_img = Image.merge('RGB', [lum, lum, blue])

    in_img.save(Path.joinpath(out_dir, 'thumbnail.jpg'), quality=70, progressive=True)
    out_img.save(Path.joinpath(out_dir, 'thumbnail_blue.jpg'), quality=70, progressive=True)


def build_menu(page):
    menu = ''
    for e in ['home', 'architecture', 'research', 'about', 'contact']:
        if page == e:
            menu += '''
                <div>
                    <span>{0}</span>
                </div>
            '''.format(e)
        else:
            menu += '''
                <div>
                    <a href="./{0}.html">
                        <span>{0}</span>
                    </a>
                </div>
            '''.format(e)
    return menu


def build_list():
    return ''


out_dir = Path.joinpath(Path.cwd(), 'out')
rmtree(str(out_dir))
out_dir.mkdir()

in_dir = Path.joinpath(Path.cwd(), 'in')

out_projects = Path.joinpath(out_dir, 'projects')
out_projects.mkdir()

in_projects_dir = Path.joinpath(in_dir, 'projects')

projects = {}   # Stores info of all projects

for in_proj_dir in in_projects_dir.iterdir():

    proj_id = in_proj_dir.stem
    print(proj_id)

    out_proj_dir = Path.joinpath(out_projects, proj_id)
    out_proj_dir.mkdir()

    json_fp = open(str(Path.joinpath(in_proj_dir, 'info.json')), 'r')
    info_json = load(json_fp)
    projects[proj_id] = info_json
    json_fp.close()

    # Create thumbnails
    image_converter(Path.joinpath(in_proj_dir, 'preview.jpg'), out_proj_dir)
    

home_html = '''
<!DOCTYPE html>
<html lang="en">
    <head>
        <title>m2ft</title>
        <link rel="stylesheet" type="text/css" href="style.css">
    </head>
    <body>
        <div id="menu">
            {menu}
        </div>
        <div id="list">
            {list}
        </div>
    </body>
</html>
'''.format(menu=build_menu('home'), list=build_list())
home_path = Path.joinpath(out_dir, 'home.html')
home_path.touch()
home_fp = open(str(home_path), 'w')
home_fp.write(home_html)
home_fp.close()
