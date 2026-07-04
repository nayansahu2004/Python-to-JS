javascript
// Compiled using the command: node main.js
// Input data as a JSON object
const systemInfo = {
    'os': {
        'system': 'Windows',
        'arch': 'AMD64',
        'release': '11',
        'version': '10.0.26200',
        'kernel': '11',
        'distro': null,
        'wsl': false,
        'rosetta2_translated': false,
        'target_triple': ''
    },
    'package_managers': ['winget'],
    'cpu': {
        'brand': 'AMD Ryzen 5 5600H with Radeon Graphics',
        'cores_logical': 12,
        'cores_physical': 6,
        'simd': []
    },
    'toolchain': {
        'compilers': {
            'gcc': '',
            'g++': '',
            'clang': '',
            'msvc_cl': ''
        },
        'build_tools': {
            'cmake': '',
            'ninja': '',
            'make': ''
        },
        'linkers': {
            'ld_lld': ''
        }
    }
};

// No direct equivalent to Python's variable types
// Since JavaScript is dynamically typed, variables are inferred at runtime

let a = 10;
let b = 20;

// Printing to the console
globalThis.console.log(a + b);
