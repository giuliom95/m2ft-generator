from PIL import Image
from pathlib import Path
from shutil import rmtree, copyfile
from json import load


def image_converter(path, out_dir):
    in_img = Image.open(path)

    lum = in_img.convert('L')

    blue = Image.new('L', lum.size, (255,))

    out_img = Image.merge('RGB', [lum, lum, blue])

    in_img.save(Path.joinpath(out_dir, 'thumbnail.jpg'), quality=70, progressive=True)
    out_img.save(Path.joinpath(out_dir, 'thumbnail_blue.jpg'), quality=70, progressive=True)


def scan_projects(in_projects_dir, out_projects_dir):

    for in_proj_dir in in_projects_dir.iterdir():

        proj_id = in_proj_dir.stem
        print(proj_id)

        out_proj_dir = Path.joinpath(out_projects_dir, proj_id)
        out_proj_dir.mkdir()

        json_fp = open(str(Path.joinpath(in_proj_dir, 'info.json')), 'r')
        info_json = load(json_fp)
        projects[proj_id] = info_json
        json_fp.close()

        # Create thumbnails
        image_converter(Path.joinpath(in_proj_dir, 'preview.jpg'), out_proj_dir)


def copy_css(in_dir, out_dir):
    in_css_path = Path.joinpath(in_dir, 'style.css')
    out_css_path = Path.joinpath(out_dir, 'style.css')
    copyfile(in_css_path, out_css_path)
    print('CSS file copied')


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


def build_project_list(projects, filter = None):
    projs = ''
    for p in projects:
        projs += '''
        <div>
            {0}
        </div>
        '''.format(projects[p]['name'])
    return projs


out_dir = Path.joinpath(Path.cwd(), 'out')
if out_dir.is_dir():
    rmtree(str(out_dir))
out_dir.mkdir()

in_dir = Path.joinpath(Path.cwd(), 'in')

out_projects_dir = Path.joinpath(out_dir, 'projects')
out_projects_dir.mkdir()

in_projects_dir = Path.joinpath(in_dir, 'projects')

projects = {}   # Stores info of all projects

scan_projects(in_projects_dir, out_projects_dir)
    
copy_css(in_dir, out_dir)

out_home_html = '''
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
'''.format(menu=build_menu('home'), list=build_project_list(projects))
out_home_path = Path.joinpath(out_dir, 'home.html')
out_home_path.touch()
out_home_fp = open(str(out_home_path), 'w')
out_home_fp.write(out_home_html)
out_home_fp.close()
