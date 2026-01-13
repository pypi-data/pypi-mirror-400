from setuptools import setup, find_packages

setup(
    name="unipercept-reward",
    version="1.0.2",
    author="Shuo Cao",
    description="UniPercept: Towards Unified Perceptual-Level Image Understanding",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/thunderbolt215/UniPercept",
    
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    
    # 核心依赖列表（已移除 flash_attn）
    install_requires=[
        "transformers==4.49.0",
        "accelerate>=1.10.1",
        "datasets>=4.0.0",
        "bitsandbytes>=0.47.0",
        "peft==0.17.1",
        "trl>=0.17.0",
        "deepspeed>=0.15.4",
        "qwen-vl-utils",
        "timm",
        "einops",
        "decord",
        "av",
        "pillow",
        "numpy",
        "pandas",
        "scipy",
        "latex2sympy2_extended",
        "math-verify",
        "liger_kernel",
        "wandb",
        "tensorboardX",
        "matplotlib",
        "rich",
        "tqdm",
        "pycocotools",
        "python-Levenshtein",
        "deep-translator",
        "openai",
        "httpx[socks]",
        "beautifulsoup4",
        "torch==2.8.0",
        "torchvision==0.23.0",
    ],
    
    # 可选依赖：用户可以通过 [flash] 选项安装
    extras_require={
        "flash": ["flash_attn>=2.8.3"],
    },
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)