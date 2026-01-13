from setuptools import setup, find_packages

# relative links to absolute
with open("./README.md", "r") as f:
    readme = f.read()
# readme = readme.replace('src="./img_phy_sim/raytracing_example.png"', 'src="https://github.com/xXAI-botXx/Image-Physics-Simulation/raw/main/img_phy_sim/raytracing_example.png"')  # click on your picture and click copy lin address to graphic

setup(
    name='runtime_guard',
    version='0.4',
    packages=find_packages(),
    install_requires=[],
    author="Tobia Ippolito",
    description = 'A ressource monitor without any dependencies.',
    long_description = readme,
    long_description_content_type="text/markdown",
    include_package_data=True,  # Ensures files from MANIFEST.in are included
    download_url = 'https://github.com/xXAI-botXx/Runtime-Guard/archive/v_03.tar.gz',
    url="https://github.com/xXAI-botXx/Runtime-Guard",
    project_urls={
        "Documentation": "https://xXAI-botXx.github.io/Runtime-Guard/",
        "Source": "https://github.com/xXAI-botXx/Runtime-Guard"
    },
    keywords = ['Training', 'Monitoring', 'DeepLearning'],
    classifiers=[
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',      # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13'
    ],
    license="MIT",
)

