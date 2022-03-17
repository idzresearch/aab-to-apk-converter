from subprocess import Popen, PIPE, run
from tempfile import TemporaryDirectory
import os
from zipfile import ZipFile

FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')


def _convert_and_install(aab_path, keystore_path, keystore_pass, keystore_alias, install, open_in_explorer):
    bundletool = 'bundletool-all-1.8.2.jar'
    aab_dir_path = os.path.dirname(aab_path)
    with TemporaryDirectory(prefix='my-app-') as tmp_dir:
        apks_path = tmp_dir + '/my_app.apks'
        print(f"Temporary apks path: {apks_path}")
        if keystore_path != "" and keystore_pass != "" and keystore_alias != "":
            p = Popen(
                ['java', '-jar', bundletool, "build-apks", f"--bundle={aab_path}", f"--output={apks_path}",
                 f"--ks={keystore_path}", f"--ks-pass=pass:{keystore_pass}", f"--ks-key-alias={keystore_alias}",
                 "--mode=universal"])
        else:
            p = Popen(
                ['java', '-jar', bundletool, "build-apks", f"--bundle={aab_path}", f"--output={apks_path}",
                 f"--ks=./keystore/debug.keystore", f"--ks-pass=pass:android", f"--ks-key-alias=androiddebugkey",
                 "--mode=universal"])

        p.wait()

        if install:
            p = Popen(
                ['java', '-jar', bundletool, "install-apks", f"--apks={apks_path}"])

            p.wait()

        try:
            # Renaming to zip file
            source = apks_path
            destination = os.path.join(tmp_dir, 'my-app.zip')
            os.rename(source, destination)

            # Extract from zip file
            with ZipFile(destination, 'r') as my_zip_file:
                # extracting all the files
                print('Extracting all the files now...')
                my_zip_file.extractall(aab_dir_path)

            source = os.path.join(aab_dir_path, 'universal.apk')
            destination = os.path.join(aab_dir_path, f"{os.path.splitext(aab_path)[0]}.apk")
            if os.path.exists(destination):
                os.remove(destination)
            os.rename(source, destination)
            if open_in_explorer:
                explore(destination)
        except Exception as e:
            print("Unexpected Error: ", e)

        print('Task Completed.')


def convert_and_install(aab_path, keystore_path="", keystore_pass="", keystore_alias="", install=True,
                        open_in_explorer=False):
    _convert_and_install(aab_path, keystore_path, keystore_pass, keystore_alias, install, open_in_explorer)


def get_alias_name(keystore_path, keystore_pass):
    p = Popen(
        ['keytool', '-v', '-list', '-keystore', keystore_path, '-storepass', keystore_pass], stdout=PIPE, stderr=PIPE)

    stdout, stderr = p.communicate()
    for line in stdout.splitlines():
        line_str = line.decode()
        if 'Alias name:' in line_str:
            alias = line_str.split('Alias name:')[1].strip()
            return alias
    return None


def explore(path):
    path = os.path.normpath(path)

    if os.path.isdir(path):
        run([FILEBROWSER_PATH, path])
    elif os.path.isfile(path):
        run([FILEBROWSER_PATH, '/select,', os.path.normpath(path)])
