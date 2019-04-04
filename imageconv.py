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


def get_projects(in_projects_dir):
    json_fp = open(str(Path.joinpath(in_projects_dir, 'list.json')), 'r')
    projects = load(json_fp)
    json_fp.close()
    return projects


def build_projects_dirs(in_projects_dir, out_projects_dir, projects):    
    for p in projects:
        proj_id = p['id']
        print('Building project {0}'.format(proj_id))

        in_proj_dir = Path.joinpath(in_projects_dir, proj_id)

        out_proj_dir = Path.joinpath(out_projects_dir, proj_id)
        out_proj_dir.mkdir()

        image_converter(Path.joinpath(in_proj_dir, 'preview.jpg'), out_proj_dir)


def copy_css(in_dir, out_dir):
    in_css_path = Path.joinpath(in_dir, 'style.css')
    out_css_path = Path.joinpath(out_dir, 'style.css')
    copyfile(in_css_path, out_css_path)
    print('CSS file copied')


def copy_logo(in_dir, out_dir):
    in_logo_path = Path.joinpath(in_dir, 'logo.svg')
    out_logo_path = Path.joinpath(out_dir, 'logo.svg')
    copyfile(in_logo_path, out_logo_path)
    print('Logo copied')


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
        text_color = 'blue'
        text_color_hover = 'black'
        if p['white_title']:
            text_color = 'white'
            text_color_hover = 'white'
        projs += '''
        <div class="block" style="background-image: url('./projects/{id}/thumbnail.jpg')">
            <div class="text" style="color: {color_hover}">
                {name}
            </div>            
            <div class="cover" style="background-image: url('./projects/{id}/thumbnail_blue.jpg'); color: {color}">
                {name}
            </div>
        </div>
        '''.format(
            id = p['id'], 
            name = p['name'],
            color = text_color,
            color_hover = text_color_hover)
    return projs


out_dir = Path.joinpath(Path.cwd(), 'out')
if out_dir.is_dir():
    rmtree(str(out_dir))
out_dir.mkdir()

in_dir = Path.joinpath(Path.cwd(), 'in')

out_projects_dir = Path.joinpath(out_dir, 'projects')
out_projects_dir.mkdir()

in_projects_dir = Path.joinpath(in_dir, 'projects')

projects = get_projects(in_projects_dir)

build_projects_dirs(in_projects_dir, out_projects_dir, projects)

copy_css(in_dir, out_dir)
copy_logo(in_dir, out_dir)

out_home_html = '''
<!DOCTYPE html>
<html lang="en">
    <head>
        <title>m2ft</title>
        <link rel="stylesheet" type="text/css" href="style.css">
    </head>
    <body>
        <div id="menu">
            <img src="./logo.svg" />
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
