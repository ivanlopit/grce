import os
import xml.etree.cElementTree as ET
from pathlib import Path

module_folder = Path(__file__).absolute().parent

GRCE_fodler = 'grce'


def build_auto_import(repo_root_folder, autoinit_path):
    tree = ET.parse(os.path.join(repo_root_folder, '.repo',  'manifest.xml'))
    root = tree.getroot()

    with open(autoinit_path, 'w') as file:
        for p in root.findall('project'):
            project_path = p.get('path')
            project_name = p.get('name')
            if(Path(project_path).absolute() == module_folder.absolute()):
                continue

            print('Building autoimport for {} => {} ...'.format(
                project_name, project_path))
            file.write('add_subdirectory({})\n'.format(project_path))

    with open(autoinit_path, 'r') as file:
        print(file.read())


def prepare_cmake_configs(repo_root_folder):
    tree = ET.parse(os.path.join(repo_root_folder, '.repo',  'manifest.xml'))
    root = tree.getroot()

    grce_path = os.path.join(repo_root_folder, 'grce')
    if not os.path.isdir(grce_path):
        os.mkdir(grce_path)

    config = os.path.join(grce_path, 'c')
    if not os.path.isdir(config):
        os.mkdir(config)

    build = os.path.join(grce_path, 'b')
    if not os.path.isdir(build):
        os.mkdir(build)

    for p in root.findall('cmake_config'):
        args = 'cmake ' + p.get('args')
        name = p.get('name')

        current_b = os.path.join(build, name)
        if not os.path.isdir(current_b):
            os.mkdir(current_b)
        current_c = os.path.join(config, name + '.cmd')

        with open(current_c, 'w') as file:
            file.write(args + ' -B{} -H{}'.format(current_b, repo_root_folder))


def find_repo_properties():
    lookup = os.getcwd()
    while(True):
        print("Scan in {} ".format(lookup))
        path_to_try = os.path.join(lookup, '.repo')
        if(os.path.exists(path_to_try)):
            manifest_path = os.path.join(path_to_try, 'manifest.xml')
            manifest_name = os.path.basename(os.readlink(manifest_path))
            return lookup, manifest_name

        new_lookup = os.path.dirname(lookup)
        if lookup == new_lookup:
            return '', ''
        else:
            lookup = new_lookup

    return '', ''


def condifure_file(src, dst, patterns):
    old = ''
    with open(src, 'r') as f:
        old = f.read()
        for k, v in patterns.items():
            old = old.replace(k, v)
            print(v, k)

    with open(dst, 'w') as f:
        f.write(old)


def main(argv):
    size = len(argv)
    if size == 2 and argv[1] == '--configure':
        repo_root_folder, manifest_name = find_repo_properties()
        if repo_root_folder:
            print("Found in {} ".format(repo_root_folder))

            autoimport = os.path.join(repo_root_folder, GRCE_fodler)

            if not os.path.isdir(autoimport):
                os.mkdir(autoimport)

            autoimport = os.path.join(autoimport, 'autoimport')

            build_auto_import(repo_root_folder, autoimport)

            project_template = os.path.join(
                module_folder, 'templates', 'CMakeLists.txt.tmpl')
            project_cmake = os.path.join(repo_root_folder, 'CMakeLists.txt')

            autoimport_rel = os.path.relpath(autoimport, repo_root_folder)
            autoimport_rel = autoimport_rel.replace('\\', '/')
            print(autoimport_rel)
            patterns = {
                '@project_name@': manifest_name[:-4],
                '@auto_import@': autoimport_rel}

            condifure_file(project_template, project_cmake, patterns)
            prepare_cmake_configs(repo_root_folder)


if __name__ == "__main__":
    main(os.sys.argv)
