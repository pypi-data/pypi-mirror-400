import torch
import os
from PIL import Image, ImageFile
from torchvision.transforms.functional import InterpolationMode
import torchvision.transforms as T
from transformers import AutoTokenizer

# 使用相对导入加载包内的模型定义
from .internvl.model.internvl_chat.modeling_unipercept import InternVLChatModel

ImageFile.LOAD_TRUNCATED_IMAGES = True

class UniPerceptRewardInferencer:
    IMAGENET_MEAN = (0.485, 0.456, 0.406)
    IMAGENET_STD = (0.229, 0.224, 0.225)
    
    # 默认的 Hugging Face 仓库 ID
    DEFAULT_HF_REPO = "Thunderbolt215215/UniPercept"

    def __init__(
        self, 
        model_path: str = None, 
        device: str = "cuda", 
        dtype: torch.dtype = torch.bfloat16
    ):
        """
        Args:
            model_path (str, optional): 本地模型路径或 HF Repo ID。
                                        如果不指定 (None)，默认从 Hugging Face 下载 Thunderbolt215215/UniPercept。
            device (str): 运行设备 ('cuda' or 'cpu').
            dtype (torch.dtype): 模型精度，默认为 torch.bfloat16。
        """
        self.device = device
        self.dtype = dtype
        
        # 逻辑：如果用户指定了路径则用用户的，否则用默认 HF 仓库
        self.model_path = model_path if model_path is not None else self.DEFAULT_HF_REPO
        
        print(f"Loading UniPercept model from: {self.model_path} ...")
        
        # 检查 Flash Attention (与参考脚本一致，通常建议开启)
        try:
            import flash_attn
            has_flash_attn = True
        except ImportError:
            has_flash_attn = False
            print("Warning: flash_attn not found, using standard attention.")

        # 加载模型 (参数与参考脚本完全对齐)
        self.model = InternVLChatModel.from_pretrained(
            self.model_path,
            torch_dtype=dtype,
            low_cpu_mem_usage=True,
            use_flash_attn=has_flash_attn, 
            trust_remote_code=True
        ).eval().to(self.device)

        # 加载 Tokenizer (参数与参考脚本完全对齐，尤其是 use_fast=False)
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path, 
            trust_remote_code=True, 
            use_fast=False
        )
        
        # 默认生成配置 (与参考脚本一致)
        self.gen_cfg = dict(max_new_tokens=512, do_sample=False)
        
        # 预构建 Transform
        self.transform = self._build_transform(input_size=448)

    def _build_transform(self, input_size):
        """
        构建图像预处理流程，与参考脚本 build_transform 完全一致
        """
        return T.Compose([
            T.Lambda(lambda img: img.convert("RGB") if img.mode != "RGB" else img),
            T.Resize((input_size, input_size), interpolation=InterpolationMode.BICUBIC),
            T.ToTensor(),
            T.Normalize(mean=self.IMAGENET_MEAN, std=self.IMAGENET_STD),
        ])

    def preprocess_image(self, image_path):
        """
        加载并预处理图像，与参考脚本 load_image 完全一致
        """
        image = Image.open(image_path).convert("RGB")
        pixel_values = self.transform(image).unsqueeze(0)
        return pixel_values.to(self.dtype).to(self.device)

    def reward(self, image_paths):
        """
        对图像列表进行多维度打分。
        逻辑严格对应参考脚本中的 run_dataset 函数里的推理部分。
        
        Args:
            image_paths (list): 图片路径列表。
            
        Returns:
            list[dict]: 返回一个列表，每个元素是对应图片的字典，包含三个维度的分数。
                        例如: [{'iaa': 5.2, 'iqa': 4.1, 'ista': 3.8}, ...]
        """
        # 定义三个任务对应的 Prompt 描述
        # 严格对应参考脚本逻辑：
        # desc = "aesthetics" if task_type == "iaa" else ("quality" if task_type == "iqa" else "structure and texture richness")
        tasks_map = {
            "iaa": "aesthetics",
            "iqa": "quality",
            "ista": "structure and texture richness"
        }

        results = []
        
        for img_path in image_paths:
            if not os.path.exists(img_path):
                print(f"Warning: File {img_path} not found.")
                results.append(None)
                continue

            try:
                # 1. 预处理图片 (对应 load_image)
                pixel_values = self.preprocess_image(img_path)
                
                # 2. 依次计算三个维度的分数
                img_scores = {}
                for key, desc in tasks_map.items():
                    # 调用模型原有的 score 方法
                    # 对应: score = model.score(device, tokenizer, pixel_values, gen_cfg, desc)
                    raw_score = self.model.score(
                        self.device, 
                        self.tokenizer, 
                        pixel_values, 
                        self.gen_cfg, 
                        desc
                    )
                    
                    # 提取数值 (与参考脚本一致，处理返回值)
                    val = raw_score
                    if isinstance(val, (list, tuple)):
                        val = val[0]
                    if hasattr(val, 'item'):
                        val = val.item()
                        
                    img_scores[key] = val
                
                results.append(img_scores)

            except Exception as e:
                print(f"Error processing {img_path}: {e}")
                results.append(None)
        
        return results