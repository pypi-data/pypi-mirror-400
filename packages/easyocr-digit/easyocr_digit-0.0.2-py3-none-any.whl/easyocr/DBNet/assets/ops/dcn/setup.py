from setuptools import setup
from torch.utils.cpp_extension import BuildExtension
from torch.utils.cpp_extension import CppExtension

modules = [
        CppExtension('deform_conv_cpu', [
            'src/deform_conv_cpu.cpp',
            'src/deform_conv_cpu_kernel.cpp',
        ]),
        CppExtension('deform_pool_cpu', [
            'src/deform_pool_cpu.cpp', 
            'src/deform_pool_cpu_kernel.cpp'
        ])
]


setup(
    name='deform_conv',
    ext_modules=modules,
    cmdclass={'build_ext': BuildExtension})
