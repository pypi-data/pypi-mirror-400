#!/usr/bin/env python3

import logging
logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%H:%M:%S', level=logging.DEBUG)
basic_logger = logging.getLogger('BASIC')
basic_logger.info(f'start {__file__}')

import pathlib, sys, os
import time, re, shutil, importlib, toml # type: ignore
import subprocess
from packaging import version as packaging_version

# from library_core.constants_lib import *
from . constants_lib import *

PRODUCTION_DIRECTORY_STR = f'{PART2_VAL}/My Documents/software projects/operative' 
REQUIRED_VERSION_REGEX_STR = r'\s*version\s*=\s*\'(\d+\.\d+\.\d+)\''

def main():
    # find where the call is coming from    
    cwd = pathlib.Path.cwd()
    # one of the ancestor directories of the cwd must contain the string "workspace"
    workspace_found = False
    for cwd_ancestor_dir in cwd.parts:
        cwd_ancestor_dir_lc = cwd_ancestor_dir.lower()
        if 'workspace' in cwd_ancestor_dir_lc:
            workspace_found = True
            break
        # but ... in fact if this script is being called from inside an installed package what you would hope to 
        # find is one of the parts being f"dev_{cwd.name}"
        if f'dev_{cwd.name}'.lower() in cwd_ancestor_dir_lc:
            workspace_found = True
            break
    if not workspace_found:
        basic_logger.error(f'FATAL. This script was not called from a development project directory: {cwd}')
        return    
    caller_proj_name = cwd.name
    basic_logger.info(f'Calling deploy for project |{cwd.name}|')
    dev_proj_dir_path = cwd
    # check that the calling project has a valid version file and version
    dev_version = get_version('development', dev_proj_dir_path)
    if dev_version == None: 
        return
    explanation = \
    """
    Explanation:
    What you should do therefore is create a new Virtual Environment with the name of this project but with the prefix "dev_...".
    Then you need to change the file which activates the VE (e.g. start_ve.bat).
    Then you will need to do "pip install ..." for all the required packages. That list can be obtained by starting the existing and 
    then installing them all (i.e. > pip freeze > requirement.txt).
    When the deployment takes place the activation file will be tweaked by the code to remove that "dev_" prefix, so don't delete the existing
    VE.
    Finally, if you have installed any new Python modules (ditto for Rust: Cargo.toml files, etc.) since the last deploy, the relevant upgrades 
    to the "run environment" will have to be made, i.e. for the "non-dev" VE, etc.
    """
    if IS_LINUX:
        # the file lin_ve_path should be tweaked: the content should be one line, 
        dev_lin_ve_file_path = dev_proj_dir_path.joinpath('lin_ve_path')
        with open(dev_lin_ve_file_path) as file:
            file_lines = list(file)
        if len(file_lines) != 1:
            basic_logger.error(f'FATAL. ve_path_linux should be one line but it has {len(file_lines)} lines')
            return
        expected_line = f'. ${PART2_NAME}/apps/Python/virtual_envs/dev_{caller_proj_name}/bin/activate' # should be using "development VE" in the dev location
        if file_lines[0].strip() != expected_line:
            explanation = \
            basic_logger.error(f'FATAL. ve_path_linux should contain this line:\n|{expected_line}|\n... but contains this line:\n|{file_lines[0]}|\n{explanation}')
            return
    else:
        # the file start_ve.bat should be tweaked: the content should be one line, 
        dev_start_ve_w10_file_path = dev_proj_dir_path.joinpath('start_ve.bat')
        with open(dev_start_ve_w10_file_path) as file:
            file_lines = list(file)
        if len(file_lines) != 1:
            basic_logger.error(f'FATAL. start_ve.bat should be one line but it has {len(file_lines)} lines')
            return
        expected_line = fr'%{PART2_NAME}%\apps\Python\virtual_envs\dev_{caller_proj_name}\Scripts\activate' # should be using "development VE" in the dev location
        if file_lines[0].strip() != expected_line:
            basic_logger.error(f'FATAL. start_ve.bat should contain this line:\n|{expected_line}|\n... but contains this line:\n|{file_lines[0]}|\n{explanation}')
            return
    prod_dir_path = pathlib.Path(PRODUCTION_DIRECTORY_STR)
    if not prod_dir_path.is_dir():
        basic_logger.error(f'FATAL. The string given for the production directory is not a directory: |{PRODUCTION_DIRECTORY_STR}|')
        return
    prod_proj_dir_path = prod_dir_path.joinpath(caller_proj_name)
    if prod_proj_dir_path.is_file():
        basic_logger.error(f'FATAL. The project production dir is a file: |{prod_proj_dir_path}|')
        return
    # if the proj production dir exists ...
    if prod_proj_dir_path.is_dir():      
        # ... try to get the version
        prod_version = get_version('production', prod_proj_dir_path)
        if prod_version == None: 
            basic_logger.error(f'FATAL. Could not get production version')
            return
        proceed_anyway = False
        if dev_version > prod_version:
            basic_logger.info('OK - dev version higher')
        else:
            msg = f'ANOMALY. The development version is {dev_version}. This must be higher than production version, but this is {prod_version}. Do you want to proceed anyway? [y/N]'
            reply = input(msg)
            proceed_anyway = reply.strip().lower() == 'y'
            if not proceed_anyway:
                return
            shutil.rmtree(prod_proj_dir_path)
        if not proceed_anyway:
            # try to rename the existing production directory to show the version: if failure, error and exit`
            renamed_prod_proj_dir_path = prod_proj_dir_path.parent.joinpath(f'{caller_proj_name}_{prod_version}')
            if renamed_prod_proj_dir_path.exists():
                basic_logger.error(f'FATAL. Can\'t rename production project directory as path to which it is to be renamed already exists as file or directory: {renamed_prod_proj_dir_path}')
                return
            try:
                prod_proj_dir_path.replace(renamed_prod_proj_dir_path)
            except PermissionError as e:
                basic_logger.error(f'FATAL. permission error: {e}. The production application may be running...')
                return
    else:
        basic_logger.info(f'prod_proj_dir_path {prod_proj_dir_path} is not a directory. prod_proj_dir_path.exists() {prod_proj_dir_path.exists()}')        
    # try to copy over the upgrade to the production environment
    shutil.copytree(dev_proj_dir_path, prod_proj_dir_path)
    # NB various things are not needed by the production version in the production location
    # delete "tests" dir if it exists
    tests_dir_path = prod_proj_dir_path.joinpath('tests')
    if tests_dir_path.is_dir():
        shutil.rmtree(tests_dir_path)
    # delete ".git" dir if it exists
    git_dir_path = prod_proj_dir_path.joinpath('.git')
    if git_dir_path.is_dir():
        shutil.rmtree(git_dir_path)
    # delete .settings, etc.
    settings_dir_path = prod_proj_dir_path.joinpath('.settings')
    if settings_dir_path.is_dir():
        shutil.rmtree(settings_dir_path)
    for path in prod_proj_dir_path.glob('pyt.*'):
        path.unlink()
    for path in prod_proj_dir_path.glob('*.txt'):
        path.unlink()
    for path in prod_proj_dir_path.glob('.*project'):
        path.unlink()
    for path in prod_proj_dir_path.glob('.git*'):
        path.unlink()

    if IS_LINUX:
        basic_logger.info(f'caller_proj_name |{caller_proj_name}|')
        prod_lin_ve_file_path = prod_proj_dir_path.joinpath('lin_ve_path')
        with open(prod_lin_ve_file_path, 'w') as file:
            file.write(f'. {PART2_VAL}/apps/Python/virtual_envs/{caller_proj_name}/bin/activate') # will use the "production VE" for production runs
    else:
        prod_start_ve_w10_file_path = prod_proj_dir_path.joinpath('start_ve.bat')
        with open(prod_start_ve_w10_file_path, 'w') as file:
            file.write(f'{PART2_VAL}/apps/Python/virtual_envs/{caller_proj_name}/Scripts/activate') # will use the "production VE" for production runs

    """
    now that the production and dev projects use different VEs, these VEs will in fact be using different
    compiled Rust modules. "> maturin develop --release" (or "cargo build" for non-PyO3 modules) must therefore be run in 
    the production location.
    But in fact I've also decided that the production and dev projects should also have separate Rust "targets"
    ... this means that in dev populate_index_module/.cargo/config.toml must contain the following:
    [build]
    target-dir = ".../apps/rust/auto_generated/dev_doc_indexer_populate_index_module/target"
    ... and that in production populate_index_module/.cargo/config.toml must contain the following:
    [build]
    target-dir = ".../apps/rust/auto_generated/doc_indexer_populate_index_module/target"

    ... to make this as universal as possible, it is essential to "walk" through all directories from the root:
    - if the name of the dir is .cargo
    - and if there is a file config.toml there
    - and if there is a section "build"
    - and if there is a line "target_dir"
    - then that line should match pattern ".../apps/rust/auto_generated/dev_[root_dir].*/target" - if not, WARN
    - otherwise, in the copied over file, change to ".../apps/rust/auto_generated/[root_dir].*/target"
    - also run "> maturin develop --release"/"cargo build" in that directory

    """
    warnings_reported = False
    for path in prod_proj_dir_path.rglob("*"):
        if not path.is_dir(): continue
        if path.name != '.cargo': continue
        config_toml_file_path = path.joinpath('config.toml')
        if not config_toml_file_path.is_file(): 
            basic_logger.warning(f'\nWARN. {config_toml_file_path} is not a file')
            warnings_reported = True            
            continue
        try:
            configs = toml.load(config_toml_file_path)
        except BaseException as e:
            basic_logger.warning(f'\nWARN. toml.load failure on {config_toml_file_path}: {e}')
            warnings_reported = True            
            continue
        if 'build' not in configs:
            basic_logger.warning(f'\nWARN. {config_toml_file_path} does not have key "build"')
            warnings_reported = True            
            continue
        if 'target-dir' not in configs['build']:
            basic_logger.warning(f'\nWARN. {config_toml_file_path}["build"] does not have key "target-dir"')
            warnings_reported = True            
            continue
        pattern = f'{PART2_VAL}/apps/rust/auto_generated/dev_{caller_proj_name}_(.*)/target'
        target_dir = configs['build']['target-dir']
        match = re.fullmatch(pattern, target_dir)
        if match == None:
            basic_logger.warning(f'\nWARN. {config_toml_file_path} target-dir |{target_dir}| does not match pattern')
            warnings_reported = True            
            continue
        production_target = f'{PART2_VAL}/apps/rust/auto_generated/{caller_proj_name}_{match.groups()[0]}/target'
        configs['build']['target-dir'] = production_target
        try:
            with open(config_toml_file_path, 'w') as file:
                toml.dump(configs, file)
        except BaseException as e:
            warnings_reported = True            
            basic_logger.warning(f'\nWARN. toml.dump failure on {config_toml_file_path}: {e}')
            continue
        # you now have to run either "maturin develop --release" (if pyo3 project) or "cargo build"
        # so you have to find the Cargo.toml file and find whether one of the dependencies is "pyo3"
        cargo_toml_file_path = path.parent.joinpath('Cargo.toml')
        if not cargo_toml_file_path.is_file(): 
            warnings_reported = True            
            basic_logger.warning(f'\nWARN. {cargo_toml_file_path} is not a file')
        try:
            cargo_configs = toml.load(cargo_toml_file_path)
        except BaseException as e:
            warnings_reported = True            
            basic_logger.warning(f'\nWARN. toml.load failure on {cargo_toml_file_path}: {e}')
            continue
        if 'dependencies' in cargo_configs and 'pyo3' in cargo_configs['dependencies']:
            basic_logger.info(f'running "maturin develop --release" in dir {path.parent}')
            # now run the maturin command in dir path.parent
            completed_process = subprocess.run('maturin develop --release', cwd=path.parent)
        else:
            basic_logger.info(f'running "cargo build" in dir {path.parent}')
            completed_process = subprocess.run('cargo build', cwd=path.parent)
        if completed_process.returncode == 0:
            basic_logger.info('... process seems to have completed ok')
        else:
            warnings_reported = True            
            basic_logger.warning(f'WARN. Non-zero return code from process: {completed_process.returncode}')
    # "unlink" (i.e. delete) certain files in the production location
    run_deploy_file_path = prod_proj_dir_path.joinpath('run_deploy.py')
    # if run_deploy_file_path.is_file():
    run_deploy_file_path.unlink()

    msg = 'Standard deploy concluded'
    if warnings_reported:
        msg += ' but some warnings reported: see warnings'
    basic_logger.info(f'{"="*50}\n{msg}\n: project {caller_proj_name} version {dev_version} is now in production\n{"="*50}')
    # if there is a custom_deploy.py file in the calling root directory, run that file
    proj_cust_deploy_file_path = dev_proj_dir_path.joinpath('custom_deploy.py')
    if proj_cust_deploy_file_path.is_file():
        basic_logger.info(f'about to run custom deploy file: {proj_cust_deploy_file_path}')
        """
NB 
1. for importlib.import_module to work the module string given must point to a module when added 
to one of the entries in sys.path. The same applies when using "import xxx".
2. if you add a pathlib.Path to sys.path this won't work! It must be a string, i.e. of the directory where
your module is to be found.
3. when you go "import xxx", this does indeed run (execute) that file!
4. it's probably a good idea to remove this added entry in sys.path once you've finished importing. 
        """
        sys.path.append(str(cwd))
        import custom_deploy # type: ignore
        sys.path.remove(str(cwd))
        custom_deploy.main()
    # suggest a change to the version number in the development location
    msg = 'DEPLOY finished OK'
    if warnings_reported:
        msg += ' but some warnings reported: see warnings'
        
def get_version(location, proj_dir_path, old_style=False):
    # 2024-04-20 there are now two possibilities for the version file: 
    # 1) [project root dir]/version.toml (PREFERRED, TAKE PRECEDENCE) and 2) [project root dir]/src/version.py (old style)
    if not old_style:
        proj_version_file_path = proj_dir_path.joinpath('version.toml')
        if not proj_version_file_path.is_file():
            basic_logger.warning(f'WARN. {proj_version_file_path} is not a file. Will try to see if version can be obtained from version_file.py... ')
            return get_version(location, proj_dir_path, True)
        try:
            with open(proj_version_file_path, 'r') as f:
                toml_data = toml.load(f) # is a dict
            min_lib_version = toml_data['version']
            version = packaging_version.Version(min_lib_version)
            return version
        except BaseException as e:
            return get_version(location, proj_dir_path, True)
    proj_version_file_path = proj_dir_path.joinpath('src', 'version_file.py')
    if not proj_version_file_path.is_file():
        basic_logger.error(f'FATAL. Couldn\'t find the project {location} version file at: |{proj_version_file_path}|')
        return
    # take all the lines in the file and disregard all which are empty or starting with "\s*#"...
    version_file_lines = proj_version_file_path.read_text().splitlines()
    version_file_lines[:] = [line for line in version_file_lines if line != '' and not re.match(r'\s*#.*', line)]    
    if len(version_file_lines) == 0:
        basic_logger.error(f'FATAL. Project {location} version file at: |{proj_version_file_path}| contains no non-comment lines')
        return
    if len(version_file_lines) > 1:
        basic_logger.error(f'FATAL. Project {location} version file at: |{proj_version_file_path}| contains too many non-comment lines. ' + 
              'Should contain one line, like this: "version=\'0.0.2\'"')
        return
    # if there is a production app already in use, check the version
    match = re.match(REQUIRED_VERSION_REGEX_STR, version_file_lines[0])
    if not match:
        basic_logger.error(f'FATAL. Project {location} version file at: |{proj_version_file_path}| line ' + 
              f'Does not match required regex |{REQUIRED_VERSION_REGEX_STR}|')
        return
    # NB match.groups() will be a one-tuple
    try:
        version_to_return = packaging_version.parse(match.groups()[0])
        basic_logger.info(f'lib - version_to_return {version_to_return}')
        return version_to_return
    except packaging_version.InvalidVersion:
        basic_logger.error(f'FATAL. Project {location} version file seems to contain invalid version. Check file contents. ' + 
            f'Should contain one non-comment line, matching regex |{REQUIRED_VERSION_REGEX_STR}|')
        return
    
def revert(dev_proj_dir_path, prod_proj_dir_path):
    # TODO 2025-12-28: do I want to implement a proper "revert" function???
    pass
#     # NB it is possible that the original deploy operation was the first one done, so no previous version will exist in the production location
#     print('revert...')
#     # delete the current production project dir
#     if not prod_proj_dir_path.is_dir():
#         print(f'FATAL. During revert: the production project path {prod_proj_dir_path} is not a directory')
#         return
#     # find the version of this file you are just about to delete
#     prod_version = get_version('production', prod_proj_dir_path)
#     if prod_version == None:
#         return
#     # find all directories matching "{project_name}_\d+\.\d+.\d+" in the production directory
#     caller_proj_name = dev_proj_dir_path.name
#     production_dir_path = prod_proj_dir_path.parent
#     # map_retired_version_to_path = {}
#     newest_retired_version = None
#     newest_retired_version_path = None
#     for f in production_dir_path.iterdir():
#         if f.is_dir():
#             match = re.match(fr'{caller_proj_name}_(\d+\.\d+\.\d+)', f.name)
#             if match:
#                 dir_version = packaging_version.parse(match.groups()[0])
#                 # map_retired_version_to_path[dir_version] = f
#                 if newest_retired_version == None or newest_retired_version < dir_version:
                    
#                     # the one thing that a genuine "retired version directory" must contain is a "src" subfolder
#                     if not f.joinpath('src').is_dir():
#                         print(f'WARNING. The directory {f} should be a retired project production directory. ' + 
#                             'But it is excluded from consideration as it does not contain a "src" subdirectory')
#                     else:
#                         newest_retired_version = dir_version
#                         newest_retired_version_path = f
                        
#     # at least one such "retired version" found...
#     if newest_retired_version == None:
#         print(f'FATAL. No retired production version of project {caller_proj_name} was found, so cannot revert.')
#         return
#     print(f'newest_retired_version {newest_retired_version} path {newest_retired_version_path}')
#     # check that the version file in this "highest version dir path"
#     retired_version = get_version('newest retired production project', newest_retired_version_path)
#     if retired_version == None: return
#     # check that the production version is higher than the retired version. If not, error and exit
#     if prod_version <= retired_version:
#         print(f'FATAL. The production version is {prod_version} and the retired version is {retired_version}. ' + 
#             'But to do a revert the production version must be higher than the retired version.')
#         return 
#     # only at this point, having ascertained that there is at least one qualifying "retired" directory 
#     # for the project in the production directory, can we actually delete the current, operational, production directory
#     try:
#         shutil.rmtree(prod_proj_dir_path)
#     except PermissionError as e:
#         print(f'FATAL. permission error during revert: {e}. The production application may be running...')
#         return
#     if prod_proj_dir_path.exists():
#         print(f'FATAL. Although the production directory at {prod_proj_dir_path} should have been deleted, for some reason it still exists.')
#         return
#     # we now need to rename the latest retired directory to simple "{project_name}" 
#     try:
#         newest_retired_version_path.replace(prod_proj_dir_path)
#     except PermissionError as e:
#         print(f'FATAL. permission error: {e}')
#         return
#     print(f'Standard revert concluded: project {caller_proj_name} version {retired_version} has now been returned to production')
#     # if there is a custom_deploy.py file in the calling root directory, run that file
#     proj_cust_deploy_file_path = dev_proj_dir_path.joinpath('custom_deploy.py')
#     if proj_cust_deploy_file_path.is_file():
#         print(f'about to run custom deploy file with REVERT=True: {proj_cust_deploy_file_path}')
#         sys.path.append(str(dev_proj_dir_path))
#         import custom_deploy
#         sys.path.remove(str(dev_proj_dir_path))
#         custom_deploy.main(revert=True)
#     # suggest a change to the version number in the development location
#     print(f'REVERT finished OK. You should now change the version number in the dev project\'s version file')


# 2025-12-28 the name, if called by running "import library_core.deploy", will not be "__main__"
main()


