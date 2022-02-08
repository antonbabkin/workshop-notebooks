#!/usr/bin/env python
# coding: utf-8

import os
import re
import inspect
import shutil
from urllib.parse import urlparse
from pathlib import Path
import io

import yaml
import requests
import nbconvert
import nbformat
import mkdocs.config, mkdocs.commands.build


class Nbd:
    def __init__(self, pkg_name):
        self.pkg_name = pkg_name
        self.nbs_dir = 'nbs'
        self.root = self._locate_root_path()
        p = self.pkg_path = self.root/pkg_name
        assert p.exists() and p.is_dir()
        p = self.nbs_path = self.root/'nbs'
        assert p.exists() and p.is_dir()
        self._make_symlinks()
        
        self._make_docs_dirs()
        self.docs_config = mkdocs.config.load_config((self.root/'mkdocs.yml').open())
        self.docs_path = Path(self.docs_config['docs_dir'])
        
    def _locate_root_path(self):
        # call stack: 0=this function, 1=__init__(), 2=caller
        caller = inspect.stack()[2].filename
        if any(x in caller for x in ['<ipython-input', 'xpython_', 'ipykernel_', '<stdin>']):
            # class initialized from interactive shell or notebook
            p0 = '.'
        else:
            # class initialized from a Python module
            p0 = caller
        p = p0 = Path(p0).resolve()
        while p != p.anchor:
            if (p/self.pkg_name).exists() and (p/self.nbs_dir).exists():
                return p
            p = p.parent
        raise Exception(f'Could not find project root above "{p0}".')
        
    def _make_symlinks(self):
        # support for nested subpackages can be added by recursing into subdirs of nbs/ and making links in them
        cur_dir = Path.cwd()
        os.chdir(self.nbs_path)
        link = Path(self.pkg_name)
        if link.exists():
            assert link.is_symlink(), f'Symbolic link expected at "{link.absolute()}".'
        else:
            to = Path(f'../{self.pkg_name}')
            link.symlink_to(to, target_is_directory=True)
            link = link.absolute().relative_to(self.root)
            to = to.resolve().relative_to(self.root)
            print(f'Creating symbolic link "{link}" -> "{to}"')
            
        os.chdir(cur_dir)
        
    def _make_docs_dirs(self):
        docs_conf = yaml.safe_load(open(self.root/'mkdocs.yml'))
        
        d = self.root / docs_conf['docs_dir']
        if not d.exists():
            print(f'Creating directory "{d.relative_to(self.root)}"')
        d.mkdir(exist_ok=True)

        d = self.root / docs_conf['site_dir']
        if not d.exists():
            print(f'Creating directory "{d.relative_to(self.root)}"')
        d.mkdir(exist_ok=True)
        
        
    def nb2mod(self, nb_rel_path):
        """`nb_rel_path` is relative to project's notebook directory."""
        nb_rel_path = Path(nb_rel_path)
        nb_path = self.nbs_path/nb_rel_path
        assert nb_path.exists() and nb_path.is_file(), f'Notebook not found at "{nb_path}".'
        nb = nbformat.read(nb_path, nbformat.current_nbformat)
        nb.cells = [c for c in nb.cells if (c.cell_type == 'code') and ('module' in self.get_cell_flags(c))]
        exporter = nbconvert.exporters.PythonExporter(exclude_input_prompt=True)
        script, _ = exporter.from_notebook_node(nb)
        mod_path = self.pkg_path/nb_rel_path.with_suffix('.py')
        
        # remove #nbd lines, convert abs to rel imports
        script = '\n'.join(self._relative_import(l, mod_path.relative_to(self.root))
                           for l in script.split('\n')
                           if not l.startswith('#nbd'))
        
        mod_path.parent.mkdir(parents=True, exist_ok=True)
        mod_path.write_text(script)
        
        src = nb_path.relative_to(self.root)
        dst = mod_path.relative_to(self.root)
        print(f'Converted notebook "{src}" to module "{dst}".')
        
    def _relative_import(self, line, file_rel_path):
        """Replace line like "from pkg.subpkg.mod1 import obj" in file "pkg/subpkg/mod2.py"
        with "from .mod1 import obj"
        """
        pattern = r'^(\s*)from \s*(\S+)\s* import (.*)$'
        m = re.match(pattern, line)
        if not m: 
            return line
        indent, mod, obj = m.groups()
        if not mod.startswith(self.pkg_name):
            return line
        # mod is like "pkg.subpkg.mod1", mod_path is like "pkg/subpkg/mod2.py"
        # need to replace each part of common prefix with a dot
        mod_parts = mod.split('.')
        path_parts = list(Path(file_rel_path).parts)
        common_len = 0
        while ((common_len < len(mod_parts))
               and (common_len < len(path_parts))
               and (mod_parts[common_len] == path_parts[common_len])):
            common_len += 1
        dots = '.' * (len(path_parts) - common_len)
        rel_mod = dots + '.'.join(mod_parts[common_len:])
        return f'{indent}from {rel_mod} import {obj}'

    @staticmethod
    def get_cell_flags(cell):
        first_line = cell.source.split('\n', 1)[0].strip()
        if cell.cell_type == 'code' and first_line.startswith('#nbd'):
            return first_line.split()[1:]
        if cell.cell_type == 'markdown' and first_line.startswith('[nbd]:'):
            return first_line.split('"')[1].split()
        return []
    
    def nb2doc(self, nb_rel_path):
        """`nb_rel_path` is relative to project's notebook directory."""
        nb_rel_path = Path(nb_rel_path)
        nb_path = self.nbs_path/nb_rel_path
        assert nb_path.exists() and nb_path.is_file(), f'Notebook not found at "{nb_path}".'
        nb = nbformat.read(nb_path, nbformat.current_nbformat)
        nb.cells = [c for c in nb.cells if ('docs' in self.get_cell_flags(c))]
        exporter = nbconvert.exporters.MarkdownExporter()
        md, res = exporter.from_notebook_node(nb)
        
        # remove #nbd lines, change img paths
        md = '\n'.join(self.rename_img(l, nb_rel_path.stem)
                       for l in md.split('\n')
                       if not (l.startswith('#nbd') or l.startswith('[nbd]:')))
        
        w = nbconvert.writers.FilesWriter(build_directory=str(self.docs_path))
        md_path = w.write(md, res, nb_rel_path.stem)
        
        # move imgs to new paths
        imgs = []
        if res['outputs'] != '':
            for img in res['outputs'].keys():
                old = self.docs_path/Path(img)
                new_dir = old.parent/'img'
                new_dir.mkdir(parents=True, exist_ok=True)
                new = new_dir/f'{nb_rel_path.stem}_{img}'
                old.rename(new)
                imgs.append(new)
        
        src = nb_path.relative_to(self.root)
        dst = md_path.relative_to(self.root)
        imgs = (' and images ' + ', '.join(f'"{p.relative_to(self.root)}"' for p in imgs)
                if imgs else '')
        print(f'Converted notebook "{src}" to document "{dst}"{imgs}.')

    @staticmethod
    def rename_img(line, nb_basename):
        """
        Replace line like "![png](output.png)" with "![png](notebook_output.png)"
        """
        pattern = r'^.*!\[.+?\]\((.+?)\).*$'
        m = re.match(pattern, line)
        if not m: 
            return line
        old = m.group(1)
        new = str(Path('img')/f'{nb_basename}_{old}')
        return line.replace(old, new)

    def build_docs(self):
        print(f'Cleaning docs directory at "{self.docs_path.relative_to(self.root)}"...')
        shutil.rmtree(self.docs_path)
        self.docs_path.mkdir(parents=True, exist_ok=True)
        for item in self.docs_config['nav']:
            md_path = list(item.values())[0]
            assert isinstance(md_path, str) and md_path.endswith('.md'), md_path
            if md_path == 'README.md':
                s = self.root/'README.md'
                d = self.docs_path/'README.md'
                shutil.copyfile(s, d)
                print(f'Copied "{s.relative_to(self.root)}" to "{d.relative_to(self.root)}".')
            else:
                self.nb2doc(Path(md_path).with_suffix('.ipynb'))
        mkdocs.commands.build.build(self.docs_config)
        p = Path(self.docs_config['site_dir']).relative_to(self.root)
        print(f'Documentation built in "{p}".')


def download_file(url, dir=None, fname=None, overwrite=False, verbose=True):
    """Download file from given `url` and put it into `dir`.
    Current working directory is used as default. Missing directories are created.
    File name from `url` is used as default.
    Return absolute pathlib.Path of the downloaded file."""
    
    if dir is None:
        dir = '.'
    dpath = Path(dir).resolve()
    dpath.mkdir(parents=True, exist_ok=True)

    if fname is None:
        fname = Path(urlparse(url).path).name
    fpath = dpath / fname
    
    if not overwrite and fpath.exists():
        print(f'File {fname} already exists.')
        return fpath

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(fpath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=2**20):
                f.write(chunk)
    
    if verbose: print(f'Download complete: {fname}.')
    return fpath

