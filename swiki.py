import argparse
from collections import defaultdict
import os
import re
import shutil
import sys

from marko import Markdown
import frontmatter

import modules.link_utilities as links


RESERVED = ['index', 'fatfile']
marko = Markdown(extensions=['codehilite', 'gfm'])


argparser = argparse.ArgumentParser(description='Create wiki at output dir from input dir.')
argparser.add_argument('input_dir', metavar='input', type=str, help='the path to the input directory')
argparser.add_argument('output_dir', metavar='output', type=str, help='the path to the output directory')
argparser.add_argument('--delete-current-html', action='store_true', help='delete all HTML in output directory before building')
argparser.add_argument('--no-fatfile', action='store_false', default=True, dest="build_fatfile", help='do not create fatfile on build')
args = argparser.parse_args()


#############
# Utilities #
#############


def delete_current_html(directory: str):
    """ Delete all existing HTML files in directory """
    for file in os.listdir(directory):
        if os.path.splitext(file)[1] == '.html':
            os.remove(os.path.join(directory, file))


def place_in_container(element: str, html_id: str, content: str) -> str:
    """ Place content in container with ID """
    id_attr = f' id="{html_id}"' if html_id else ''
    return f'<{element}{id_attr}>{content}</{element}>'


def copy_css_file(pages_dir: str, output_dir: str):
    """ If CSS file in _swiki directory, copy to output """
    if os.path.isdir(swiki_folder := os.path.join(pages_dir, '_swiki')):
        css_file = [file for file in os.listdir(swiki_folder) if os.path.splitext(file)[1] == '.css'][0]
        shutil.copy2(os.path.join(swiki_folder, css_file), os.path.join(output_dir, css_file))


################
# Wiki Helpers #
################


def make_page_dict(subfolder: str, file: str, rel_path: str, isIndex: bool = False) -> dict:
    """ Make dict of all page specific data """
    page = dict()
    page['folder'] = rel_path
    with open(os.path.join(subfolder, file), 'r') as f:
        file_contents = f.read()
    page['metadata'], page['content'] = frontmatter.parse(file_contents)
    if not page['metadata'].get('description'):
        page['metadata']['description'] = ''
    page['links'] = links.get_local(page.get('content'))
    if isIndex:
        page['index'] = True
    return page


def add_page_to_sitemap(page_info: dict, folder: str, sitemap: defaultdict):
    """ Add page info to sitemap """
    updated_folder = sitemap.get(folder, [])
    updated_folder.append(page_info)
    sitemap[folder] = updated_folder
    return sitemap


def fill_frame(frame: str, content: str, metadata: dict) -> str:
    """ Fill out HTML frame with page information """
    frame = frame.replace('{{title}}', metadata.get('title', ''))
    frame = frame.replace('{{description}}', metadata.get('description', ''))
    frame = frame.replace('{{content}}', content)
    return frame


def make_fatfile(info: dict, fatfile: str, frame: str, output_dir: str):
    """ Make fatfile out of content of every page """
    fatfile = re.sub(re.compile(r'\sid=".*?"'), '', fatfile)
    fatfile = '<h1>Fatfile</h1><p>This file contains the contents of every page in the wiki in no order whatsoever.</p>' + fatfile
    fatfile = place_in_container('section', 'fatfile', fatfile)
    fatfile = place_in_container('main', 'main', fatfile)
    filled_frame = fill_frame(frame, fatfile, info.get('metadata', dict()))
    with open(os.path.join(output_dir, 'fatfile.html'), 'w') as f:
        f.write(filled_frame)


def make_sitemap(index: dict, sitemap: dict, frame: str, output_dir: str):
    """ Make sitemap out of index and all seen pages """
    index_html = f'<h1 id="title">{index["metadata"].get("title", "Sitemap")}</h1>'
    index_html += marko.convert(index.get('content', ''))
    sitemap_html = ''

    def convert_folder_to_html(folder: str, display_name: str = None) -> str:
        if not display_name:
            display_name = folder if folder else "[root]"
        html = ''
        sorted_folder_list = sorted(sitemap.get(folder), key=lambda page: page.get('title').lower())
        html += f'<h2>{display_name}</h2><ul>'
        for page in sorted_folder_list:
            title, filename = page.get('title'), page.get('filename')
            html += f'<li><a href="{filename}.html">{title}</a></li>'
        html += '</ul>'
        html = place_in_container('div', '', html)
        return html

    sorted_folders = sorted(sitemap.keys(), key=lambda folder_name: folder_name.lower())
    for folder in sorted_folders:
        if folder == '.stubs':
            continue
        sitemap_html += convert_folder_to_html(folder)

    if sitemap.get('.stubs'):
        sitemap_html += '<hr>'
        sitemap_html += convert_folder_to_html('.stubs', 'Wiki Stubs')

    page_html = place_in_container('main', 'main', index_html + sitemap_html)
    filled_frame = fill_frame(frame, page_html, index.get('metadata', dict()))
    with open(os.path.join(output_dir, 'index.html'), 'w') as f:
        f.write(filled_frame)


################
# Wiki Builder #
################


def make_wiki(pages_dir: str, output_dir: str):
    """ Create flat wiki out of all pages """
    pages = defaultdict(dict)

    for subfolder, _, files in os.walk(pages_dir):
        rel_path = subfolder.replace(pages_dir, '')
        # Ignore all files with preceding underscore
        if rel_path and rel_path[0] == '_':
            continue
        for file in files:
            filename, extension = os.path.splitext(file)
            # Ignore all files with preceding underscore or non-Markdown files
            if filename[0] == '_' or extension != '.md':
                continue
            page = make_page_dict(subfolder, file, rel_path)
            page_filename = links.kebabify(page['metadata'].get('title') or filename)
            if page_filename in RESERVED:
                page_filename += '_'

            # add backlinks to all pages this page links to
            for link in page['links']:
                link_filename = links.kebabify(link)
                # if page being linked to does not yet exist, give it the title
                # as seen in the current page (e.g. Bob Fossil, not bob-fossil).
                # This will be overwritten by the given title if the page exists.
                if not pages[link_filename].get('metadata'):
                    pages[link_filename]['metadata'] = {'title': link, 'description': ''}
                if not pages[link_filename].get('backlinks'):
                    pages[link_filename]['backlinks'] = []
                # add current page to "backlinks"
                pages[link_filename]['backlinks'].append({'title': page['metadata'].get('title', page_filename),
                                                          'filename': page_filename})

            # add page info to pages dict
            if pages.get(page_filename):
                pages[page_filename] |= page
            else:
                pages[page_filename] = page

    swiki_dir = os.path.join(pages_dir, '_swiki')

    # If there is an index file, build page dict
    if os.path.isfile(os.path.join(swiki_dir, 'index.md')):
        pages['{{SITE INDEX}}'] = make_page_dict(swiki_dir, 'index.md', '_swiki', True)

    # Load frame file
    with open(os.path.join(swiki_dir, 'frame.html'), 'r') as f:
        frame = f.read()
        # Remove extra space in frame code
        frame = re.sub(r'(?<=\n)\s*', '', frame)
        frame = re.sub(r'(?<=>)\s*(?=<)', '', frame)
        frame = re.sub(re.compile(r'(?<=[;{}(*/)])[\s]*'), '', frame)

    # Build all files and populate sitemap dict
    sitemap = defaultdict(dict)
    fatfile = ''
    index = {'metadata': dict()}
    for page, info in pages.items():
        # If it's the index/sitemap page, don't build it
        if info.get('index'):
            index = info
            continue
        # If page is linked to but it hasn't been made yet, give it placeholder metadata
        if not info.get('metadata'):
            info['metadata'] = dict()
        info['metadata'] = {'title': info['metadata'].get('title', page),
                            'description': info['metadata'].get('description', '')}
        content = marko.convert(info.get('content', 'There\'s currently nothing here.'))
        content = f'<h1 id="title">{info["metadata"].get("title")}</h1>\n{content}'
        content = links.add_external(content)
        content = links.add_local(content)
        content = links.add_backlinks(content, info.get('backlinks', []))

        if args.build_fatfile:
            fatfile_content = re.sub(rf'(?<=<h1 id="title">){info["metadata"].get("title")}(?=</h1>)',
                                     f'<a href="{page}.html">{info["metadata"].get("title")}</a>',
                                     content)
            fatfile += place_in_container('article', '', fatfile_content)

        content = place_in_container('article', 'content', content)
        content = place_in_container('main', 'main', content)
        filled_frame = fill_frame(frame, content, info.get('metadata', dict()))

        with open(os.path.join(output_dir, f'{page}.html'), 'w') as f:
            f.write(filled_frame)

        sitemap = add_page_to_sitemap({'title': info['metadata'].get('title'), 'filename': page},
                                      # If no folder here, then it is a stub
                                      info.get('folder', '.stubs'),
                                      sitemap)

    if args.build_fatfile:
        make_fatfile({'metadata': {'title': f'{index["metadata"].get("title")} - Fatfile'}}, fatfile, frame, output_dir)
    make_sitemap(index, sitemap, frame, output_dir)
    copy_css_file(pages_dir, output_dir)


if __name__ == "__main__":
    if not os.path.isdir(args.input_dir):
        sys.exit(f'Input folder not found: {args.input_dir}')
    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)
    if args.delete_current_html:
        delete_current_html(args.output_dir)

    make_wiki(args.input_dir, args.output_dir)
