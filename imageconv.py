from PIL import Image
from pathlib import Path
from shutil import rmtree, copyfile, copytree
from json import load
import traceback

page_header = '''
<!DOCTYPE html>
<html lang="en">
    <head>
        <title>m&#178;ft</title>
        <link rel="stylesheet" type="text/css" href="{root}style.css">
        <link rel="shortcut icon" href="{root}favicon.ico">
    </head>
    <body>
        <div id="menu">
            <img src="{root}logo.svg" />
            {menu}
        </div>
        <div class="content">
'''

page_footer = '''
        </div>
    </body>
</html>
'''


def image_converter(path, out_dir):
    in_img = Image.open(str(path))
    if in_img.size[0] > 850:
        ratio = in_img.size[1] / in_img.size[0]
        new_size = (850, int(850*ratio))
        in_img = in_img.resize(new_size, Image.BICUBIC)

    lum = in_img.convert('L')

    blue = Image.new('L', lum.size, (255,))

    blue_img = Image.merge('RGB', [lum, lum, blue])

    if in_img.mode == 'RGBA':
        mask = in_img.split()[3]
        tmp = Image.new("RGB", in_img.size, (255, 239, 239))
        blue_img = Image.composite(blue_img, tmp, mask)
        tmp.paste(in_img, mask=mask)
        in_img = tmp

    in_img.save(out_dir.joinpath('thumbnail.jpg'), quality=70, progressive=True)
    blue_img.save(out_dir.joinpath('thumbnail_blue.jpg'), quality=70, progressive=True)


def get_projects(in_projects_dir):
    json_fp = open(str(in_projects_dir.joinpath('list.json')), 'r')
    projects = load(json_fp)
    json_fp.close()
    return projects


def build_slideshow(proj):
    images = None
    try:
        images = proj['images']
    except KeyError:
        return ''

    def generateImgList(columnWidth, mobile=False):
        columnWidth -= 2
        imgList = ''
        n = 0
        for img in images:
            vis = 'hidden'
            if n == 0: vis = 'visible'

            printn = n
            if mobile: printn = 'm{0}'.format(n)

            columnheight = 40
            if mobile: columnheight = 66.5
            if img['aspect'] < (67.5 / 40):
                imgList += '<img id="image{n}" src="./images/{name}" style="margin-left: calc(-{aspect} * {columnheight}vw); visibility: {vis};">\n'.format(
                    n=printn, aspect=img['aspect']/2, name=img['name'], vis=vis, columnheight=columnheight)
            else:
                height = columnWidth/img['aspect']
                imgList += '<img id="image{n}" src="./images/{name}" style="margin-left: calc(-{width}vw / 2); visibility: {vis}; width: {width}vw; height: {height}vw; margin-top: {margintop}vw">\n'.format(
                    n=printn, name=img['name'], vis=vis, width=columnWidth, height=height, margintop=(columnheight / 2)-(height / 2))
            n += 1
        return imgList
    
    out = '''<div class="desktop slideshow">
        <script type="application/javascript">var num_images = {0};</script>
        <script src="../../slideshow.js"></script>
    '''.format(len(images))



    out += generateImgList(67.5)
    out += '''
        <a href="javascript:prev_image()">
            <img class="arrow prev" src="../../arrow.svg">
        </a>
        <a href="javascript:next_image()">
            <img class="arrow next" src="../../arrow.svg">
        </a>
    </div>'''
    
    out += '''<div class="mobile slideshow">
        <script type="application/javascript">var num_images = {0};</script>
        <script src="../../slideshow.js"></script>
    '''.format(len(images))

    out += generateImgList(100, mobile=True)

    out += '''
        <a href="javascript:prev_image()">
            <img class="arrow prev" src="../../arrow.svg">
        </a>
        <a href="javascript:next_image()">
            <img class="arrow next" src="../../arrow.svg">
        </a>
    </div>'''

    return out


def build_project_page(proj, in_proj_dir, out_proj_dir):
    in_proj_info_path = in_proj_dir.joinpath('project.html')
    in_proj_info_fd = open(str(in_proj_info_path), 'r')
    in_proj_info = in_proj_info_fd.read()
    in_proj_info_fd.close()

    out_proj_info_path = out_proj_dir.joinpath('project.html')
    out_proj_info_path.touch()
    out_proj_info = page_header + in_proj_info + page_footer
    out_proj_info = out_proj_info.format(
        root='../../',
        menu=build_menu(None, root='../../'),
        images=build_slideshow(proj))
    out_proj_info_fd = open(str(out_proj_info_path), 'w')
    out_proj_info_fd.write(out_proj_info)
    out_proj_info_fd.close()


def copy_project_images(proj, in_proj_dir, out_proj_dir):
    in_proj_img_dir = in_proj_dir.joinpath('images')
    if not in_proj_img_dir.exists():
        return proj
    out_proj_img_dir = out_proj_dir.joinpath('images')
    copytree(str(in_proj_img_dir), str(out_proj_img_dir))
    images = []
    for img in in_proj_img_dir.iterdir():
        img_data = Image.open(str(img))
        old_size = img_data.size
        ratio = old_size[1] / old_size[0]
        if old_size[0] > 1000:
            new_size = (1000, int(1000*ratio))
            img_data = img_data.resize(new_size, Image.BICUBIC)

        images.append({
            'name': img.name,
            'aspect': 1 / ratio
        })
        out_file = out_proj_img_dir.joinpath(img.name)
        print(f'IMG: {out_file}, {old_size} -> {img_data.size}')
        img_data.save(out_file, quality=70, progressive=True)

        
    proj['images'] = sorted(images, key=lambda d: d['name'])
    return proj
    

def build_projects_dirs(in_projects_dir, out_projects_dir, projects): 
    for p in projects:
        proj_id = p['id']
        print('Building project "{0}"'.format(proj_id))

        in_proj_dir = in_projects_dir.joinpath(proj_id)

        out_proj_dir = out_projects_dir.joinpath(proj_id)
        out_proj_dir.mkdir()

        try:
            image_converter(in_proj_dir.joinpath('preview.jpg'), out_proj_dir)
        except FileNotFoundError:
            image_converter(in_proj_dir.joinpath('preview.png'), out_proj_dir)

        p = copy_project_images(p, in_proj_dir, out_proj_dir)
        build_project_page(p, in_proj_dir, out_proj_dir)


def copy_file(name, in_dir, out_dir):
    print('Copying {0}'.format(name))
    in_path = in_dir.joinpath(name)
    out_path = out_dir.joinpath(name)
    copyfile(str(in_path), str(out_path))


def build_menu(page, root='./'):
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
                    <a href="{root}{0}.html">
                        <span>{0}</span>
                    </a>
                </div>
            '''.format(e, root=root)
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
                <a href="./projects/{id}/project.html">
                    <div class="text" style="color: {color_hover}">
                        {name}
                    </div>            
                    <div class="cover" style="background-image: url('./projects/{id}/thumbnail_blue.jpg'); color: {color}">
                        {name}
                    </div>
                </a>
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
        root = './',
        menu = build_menu(page),
        list = build_project_list(page, projects))
    out_home_path = out_dir.joinpath('{0}.html'.format(page))
    out_home_path.touch()
    out_home_fp = open(str(out_home_path), 'w')
    out_home_fp.write(out_home_html)
    out_home_fp.close()


def build_static_page(name, in_dir, out_dir):
    print('Building "{0}" page'.format(name))
    in_about_path = in_dir.joinpath('{0}.html'.format(name))
    out_about_path = out_dir.joinpath('{0}.html'.format(name))
    in_about_page_fd = open(str(in_about_path), 'r')
    about_page_html = page_header + in_about_page_fd.read() + page_footer
    about_page_html = about_page_html.format(root = './', menu = build_menu(name))
    in_about_page_fd.close()
    out_about_page_fd = open(str(out_about_path), 'w')
    out_about_page_fd.write(about_page_html)
    out_about_page_fd.close()
    

def build_website():
    out_dir = Path.cwd().joinpath('out')
    if out_dir.exists():
        rmtree(str(out_dir))
    out_dir.mkdir()

    in_dir = Path.cwd().joinpath('in')

    out_projects_dir = out_dir.joinpath('projects')
    out_projects_dir.mkdir()

    in_projects_dir = in_dir.joinpath('projects')

    projects = get_projects(in_projects_dir)

    build_projects_dirs(in_projects_dir, out_projects_dir, projects)

    projects_page_template = page_header + '''
    <div class="list">
        {list}
    </div>
    ''' + page_footer

    build_projects_page('home', out_dir, projects, projects_page_template)
    build_projects_page('architecture', out_dir, projects, projects_page_template)
    build_projects_page('research', out_dir, projects, projects_page_template)

    build_static_page('about', in_dir, out_dir)
    copy_file('about.jpg', in_dir, out_dir)

    build_static_page('contact', in_dir, out_dir)

    copy_file('style.css', in_dir, out_dir)
    copy_file('logo.svg', in_dir, out_dir)
    copy_file('slideshow.js', in_dir, out_dir)
    copy_file('index.html', in_dir, out_dir)
    copy_file('arrow.svg', in_dir, out_dir)
    copy_file('favicon.ico', in_dir, out_dir)


if __name__=='__main__':
    try:
        build_website()
    except Exception as e:
        print('### An error has occurred! ###')
        print(traceback.format_exc())
    else:
        print('All done!')
    input('Press enter to exit')

