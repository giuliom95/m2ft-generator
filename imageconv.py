from PIL import Image
from pathlib import Path
from shutil import rmtree, copyfile
from json import load

page_header = '''
<!DOCTYPE html>
<html lang="en">
    <head>
        <title>m&#178;ft</title>
        <link rel="stylesheet" type="text/css" href="style.css">
    </head>
    <body>
'''

page_footer = '''
    </body>
</html>
'''


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
        print('Building project "{0}"'.format(proj_id))

        in_proj_dir = Path.joinpath(in_projects_dir, proj_id)

        out_proj_dir = Path.joinpath(out_projects_dir, proj_id)
        out_proj_dir.mkdir()

        image_converter(Path.joinpath(in_proj_dir, 'preview.jpg'), out_proj_dir)


def copy_file(name, in_dir, out_dir):
    print('Copying {0}'.format(name))
    in_path = Path.joinpath(in_dir, name)
    out_path = Path.joinpath(out_dir, name)
    copyfile(in_path, out_path)


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


def build_project_list(page, projects, filter = None):
    projs = ''
    for p in projects:
        if p['category'] == page or page == 'home':
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


def build_projects_page(page, out_dir, projects, template):
    print('Building project page "{0}"'.format(page))
    out_home_html = template.format(
        menu = build_menu(page),
        list = build_project_list(page, projects))
    out_home_path = Path.joinpath(out_dir, '{0}.html'.format(page))
    out_home_path.touch()
    out_home_fp = open(str(out_home_path), 'w')
    out_home_fp.write(out_home_html)
    out_home_fp.close()


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

copy_file('style.css', in_dir, out_dir)
copy_file('logo.svg', in_dir, out_dir)


out_template_html = page_header + '''
<div id="menu">
    <img src="./logo.svg" />
    {menu}
</div>
<div id="list">
    {list}
</div>
''' + page_footer

build_projects_page('home', out_dir, projects, out_template_html)
build_projects_page('architecture', out_dir, projects, out_template_html)
build_projects_page('research', out_dir, projects, out_template_html)
