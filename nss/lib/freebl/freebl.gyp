# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
{
  'includes': [
    '../../coreconf/config.gypi'
  ],
  'targets': [
    {
      'target_name': 'intel-gcm-wrap_c_lib',
      'type': 'static_library',
      'sources': [
        'intel-gcm-wrap.c'
      ],
      'dependencies': [
        '<(DEPTH)/exports.gyp:nss_exports'
      ],
      'cflags': [
        '-mssse3'
      ],
      'cflags_mozilla': [
        '-mssse3'
      ]
    },
    {
      'target_name': 'freebl',
      'type': 'static_library',
      'sources': [
        'loader.c'
      ],
      'dependencies': [
        '<(DEPTH)/exports.gyp:nss_exports'
      ]
    },
    # For test builds, build a static freebl library so we can statically
    # link it into the test build binary. This way we don't have to
    # dlopen() the shared lib but can directly call freebl functions.
    {
      'target_name': 'freebl_static',
      'type': 'static_library',
      'includes': [
        'freebl_base.gypi',
      ],
      'dependencies': [
        '<(DEPTH)/exports.gyp:nss_exports',
      ],
      'conditions': [
        [ 'OS=="linux"', {
          'defines!': [
            'FREEBL_NO_DEPEND',
            'FREEBL_LOWHASH',
            'USE_HW_AES',
            'INTEL_GCM',
          ],
          'conditions': [
            [ 'target_arch=="x64"', {
              # The AES assembler code doesn't work in static test builds.
              # The linker complains about non-relocatable code, and I
              # currently don't know how to fix this properly.
              'sources!': [
                'intel-aes.s',
                'intel-gcm.s',
              ],
            }],
          ],
        }],
      ],
    },
    {
      'target_name': '<(freebl_name)',
      'type': 'shared_library',
      'includes': [
        'freebl_base.gypi',
      ],
      'dependencies': [
        '<(DEPTH)/exports.gyp:nss_exports',
      ],
      'conditions': [
        [ 'OS!="linux" and OS!="android"', {
          'conditions': [
            [ 'moz_fold_libs==0', {
              'dependencies': [
                '<(DEPTH)/lib/util/util.gyp:nssutil3',
              ],
            }, {
              'libraries': [
                '<(moz_folded_library_name)',
              ],
            }],
          ],
        }, 'target_arch=="x64"', {
          'dependencies': [
            'intel-gcm-wrap_c_lib',
          ],
        }],
        [ 'OS=="win" and cc_is_clang==1', {
          'dependencies': [
            'intel-gcm-wrap_c_lib',
          ],
        }],
        [ 'OS=="linux"', {
          'sources': [
            'nsslowhash.c',
            'stubs.c',
          ],
        }],
      ],
      'variables': {
       'conditions': [
         [ 'OS=="linux"', {
           'mapfile': 'freebl_hash_vector.def',
         }, {
           'mapfile': 'freebl.def',
         }],
       ]
      },
    },
  ],
  'conditions': [
    [ 'OS=="linux"', {
      # stub build
      'targets': [
        {
          'target_name': 'freebl3',
          'type': 'shared_library',
          'defines': [
            'FREEBL_NO_DEPEND',
          ],
          'sources': [
            'lowhash_vector.c'
          ],
          'dependencies': [
            '<(DEPTH)/exports.gyp:nss_exports'
          ],
          'variables': {
            'mapfile': 'freebl_hash.def'
          }
        },
      ],
    }],
  ],
  'target_defaults': {
    'include_dirs': [
      'mpi',
      'ecl'
    ],
    'defines': [
      'SHLIB_SUFFIX=\"<(dll_suffix)\"',
      'SHLIB_PREFIX=\"<(dll_prefix)\"',
      'SHLIB_VERSION=\"3\"',
      'SOFTOKEN_SHLIB_VERSION=\"3\"',
      'RIJNDAEL_INCLUDE_TABLES',
      'MP_API_COMPATIBLE'
    ],
    'conditions': [
      [ 'OS=="win" and target_arch=="ia32"', {
        'msvs_settings': {
          'VCCLCompilerTool': {
            #TODO: -Ox optimize flags
            'PreprocessorDefinitions': [
              'NSS_X86_OR_X64',
              'NSS_X86',
              'MP_ASSEMBLY_MULTIPLY',
              'MP_ASSEMBLY_SQUARE',
              'MP_ASSEMBLY_DIV_2DX1D',
              'MP_USE_UINT_DIGIT',
              'MP_NO_MP_WORD',
              'USE_HW_AES',
              'INTEL_GCM',
            ],
          },
        },
      }],
      [ 'OS=="win" and target_arch=="x64"', {
        'msvs_settings': {
          'VCCLCompilerTool': {
            #TODO: -Ox optimize flags
            'PreprocessorDefinitions': [
              'NSS_USE_64',
              'NSS_X86_OR_X64',
              'NSS_X64',
              'MP_IS_LITTLE_ENDIAN',
              'NSS_BEVAND_ARCFOUR',
              'MPI_AMD64',
              'MP_ASSEMBLY_MULTIPLY',
              'NSS_USE_COMBA',
              'USE_HW_AES',
              'INTEL_GCM',
            ],
          },
        },
      }],
      [ 'OS!="win"', {
        'conditions': [
          [ 'target_arch=="x64"', {
            'defines': [
              'NSS_USE_64',
              'NSS_X86_OR_X64',
              'NSS_X64',
              # The Makefile does version-tests on GCC, but we're not doing that here.
              'HAVE_INT128_SUPPORT',
            ],
          }, {
            'sources': [
              'ecl/uint128.c',
            ],
          }],
          [ 'target_arch=="ia32"', {
            'defines': [
              'NSS_X86_OR_X64',
              'NSS_X86',
            ],
          }],
        ],
      }],
      [ 'OS=="linux"', {
        'defines': [
          'FREEBL_LOWHASH',
          'FREEBL_NO_DEPEND',
        ],
      }],
      [ 'OS=="linux" or OS=="android"', {
        'conditions': [
          [ 'target_arch=="x64"', {
            'defines': [
              'MP_IS_LITTLE_ENDIAN',
              'NSS_BEVAND_ARCFOUR',
              'MPI_AMD64',
              'MP_ASSEMBLY_MULTIPLY',
              'NSS_USE_COMBA',
            ],
          }],
          [ 'target_arch=="x64"', {
            'defines': [
              'USE_HW_AES',
              'INTEL_GCM',
            ],
          }],
          [ 'target_arch=="ia32"', {
            'defines': [
              'MP_IS_LITTLE_ENDIAN',
              'MP_ASSEMBLY_MULTIPLY',
              'MP_ASSEMBLY_SQUARE',
              'MP_ASSEMBLY_DIV_2DX1D',
              'MP_USE_UINT_DIGIT',
            ],
          }],
          [ 'target_arch=="arm"', {
            'defines': [
              'MP_ASSEMBLY_MULTIPLY',
              'MP_ASSEMBLY_SQUARE',
              'MP_USE_UINT_DIGIT',
              'SHA_NO_LONG_LONG',
            ],
          }],
          [ 'target_arch=="arm64" or target_arch=="aarch64"', {
            'defines': [
              'NSS_USE_64',
            ],
          }],
        ],
      }],
    ],
  },
  'variables': {
    'module': 'nss',
  }
}
