project('robotpy-urcl', ['cpp'],
        default_options: ['warning_level=1', 'cpp_std=c++20',
                          'b_colorout=auto', 'optimization=2', 'b_pie=true'])

subdir('semiwrap')

urcl_sources += files(
    'urcl/wrapper.cpp',
)

#
# Static link
#

cpp = meson.get_compiler('cpp')
libs_path = meson.current_source_dir() + '/lib/lib'

urcl_deps += [
    cpp.find_library('URCLDriver', dirs: libs_path),
    cpp.find_library('URCL', dirs: libs_path),
]

subdir('semiwrap/modules')
