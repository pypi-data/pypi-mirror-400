import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pycmd.environ import Environment

ARGS = globals().get('ARGS', {})

env = Environment()

print("=== PyCMD Demo ===")
print()

print("=== Custom Arguments Demo ===")
print(f"Received custom arguments: {ARGS}")

if 'target' in ARGS:
    print(f"Build target: {ARGS['target']}")
    env['BUILD_TARGET'] = ARGS['target']

if 'config' in ARGS:
    print(f"Build config: {ARGS['config']}")
    env['BUILD_CONFIG'] = ARGS['config']

if 'optimize' in ARGS:
    print(f"Optimization level: {ARGS['optimize']}")
    env['OPTIMIZE'] = ARGS['optimize']

if 'debug' in ARGS:
    print(f"Debug mode: {ARGS['debug']}")
    env['DEBUG'] = ARGS['debug']

if 'positional' in ARGS:
    print(f"Positional arguments: {ARGS['positional']}")

print()

output = env.Execute('echo Hello from Command.py')
print(f"Command output: {output.strip()}")

env.Command(
    target='output.txt',
    source=['input.txt'],
    action='echo "Building output" > output.txt'
)

env['CC'] = 'gcc'
env['CFLAGS'] = '-O2 -Wall'

if env.get('BUILD_CONFIG') == 'debug':
    env.Append(CFLAGS='-g')
    print("Added debug flags")

if env.get('BUILD_TARGET') == 'release':
    env.Append(CFLAGS='-O3')
    print("Added release optimization flags")

print(f"CC: {env['CC']}")
print(f"CFLAGS: {env['CFLAGS']}")

print()
print("=== Environment Variables ===")
for key in ['BUILD_TARGET', 'BUILD_CONFIG', 'OPTIMIZE', 'DEBUG']:
    value = env.get(key)
    if value:
        print(f"{key}: {value}")

print()
print("=== Program Demo ===")

build_program = env.Program('build', [
    {'command': 'echo Step 1: Preparing build environment', 'description': 'Prepare environment'},
    {'command': 'echo Step 2: Compiling source files', 'description': 'Compile sources'},
    {'command': 'echo Step 3: Linking objects', 'description': 'Link objects'},
    {'command': 'echo Step 4: Build complete', 'description': 'Finalize build'}
])

build_program.execute()

test_program = env.Program('test')
test_program.add_command('echo Running unit tests...', 'Unit tests')
test_program.add_command('echo Running integration tests...', 'Integration tests')
test_program.add_command('echo All tests passed!', 'Test summary')
test_program.execute()

deploy_commands = [
    'echo Packaging application...',
    'echo Uploading to server...',
    'echo Deployment complete!'
]
deploy_program = env.Program('deploy', deploy_commands)
deploy_program.execute()

print()
print("=== Program with Preaction and Postaction Demo ===")

def setup_environment(env):
    print("    Custom preaction: Setting up build environment...")
    env['BUILD_DIR'] = 'build'
    env['OUTPUT_DIR'] = 'output'
    return True

def cleanup_environment(env):
    print("    Custom postaction: Cleaning up temporary files...")
    print(f"    Build directory was: {env.get('BUILD_DIR')}")
    return True

advanced_program = env.Program('advanced-build')

advanced_program.add_preaction('echo Checking dependencies...', 'Check dependencies')
advanced_program.add_preaction(setup_environment, 'Setup environment')

advanced_program.add_command('echo Compiling main.c...', 'Compile main.c')
advanced_program.add_command('echo Compiling utils.c...', 'Compile utils.c')
advanced_program.add_command('echo Linking executable...', 'Link executable')

advanced_program.add_postaction(cleanup_environment, 'Cleanup')
advanced_program.add_postaction('echo Build artifacts created successfully!', 'Final message')

advanced_program.execute()

print()
print("=== Chained Program Demo ===")

release_program = env.Program('release-pipeline')
release_program.add_preaction('echo Starting release pipeline...', 'Start pipeline')
release_program.add_preaction('echo Validating version...', 'Validate version')

release_program.add_commands([
    {'command': 'echo Building for production...', 'description': 'Production build'},
    {'command': 'echo Running tests...', 'description': 'Test'},
    {'command': 'echo Creating release package...', 'description': 'Package'}
])

release_program.add_postaction('echo Uploading to release server...', 'Upload')
release_program.add_postaction('echo Sending notification...', 'Notify')
release_program.add_postaction('echo Release complete!', 'Complete')

release_program.execute()