import os
import json
import openai 

class OpenAIChatNode:
    """
    用于与OpenAI Chat API交互的ComfyUI节点
    使用官方OpenAI Python客户端
    """
    
    def __init__(self):
        self.client = None
        
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_url": ("STRING", {
                    "multiline": False,
                    "default": "https://api.openai.com/v1"
                }),
                "api_key": ("STRING", {
                    "multiline": False,
                    "default": ""
                }),
                "model": ("STRING", {
                    "multiline": False,
                    "default": "gpt-3.5-turbo"
                }),
                "system_prompt": ("STRING", {
                    "multiline": True,
                    "default": "You are a helpful assistant."
                }),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "Hello, how are you?"
                }),
                "temperature": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1
                }),
                "max_tokens": ("INT", {
                    "default": 1000,
                    "min": 1,
                    "max": 4096
                })
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "chat_completion"
    CATEGORY = "昂昂"

    def chat_completion(self, base_url: str, api_key: str, model: str, 
                       system_prompt: str, prompt: str, temperature: float = 0.7, 
                       max_tokens: int = 1000) -> tuple[str]:
        """
        使用OpenAI官方客户端调用Chat API获取回复
        """
        if not api_key:
            raise ValueError("API密钥不能为空")
            
        if not base_url:
            raise ValueError("Base URL不能为空")
            
        if not model:
            raise ValueError("模型名称不能为空")

        try:
            # 创建OpenAI客户端实例
            client = openai.OpenAI(
                api_key=api_key,
                base_url=base_url
            )

            messages = []
            # 添加系统提示（如果有）
            if system_prompt.strip():
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            # 添加用户提示
            messages.append({
                "role": "user",
                "content": prompt
            })

            # 使用官方客户端发送请求
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # 获取响应文本
            return (response.choices[0].message.content,)
            
        except openai.APITimeoutError:
            raise RuntimeError("请求超时，请检查网络连接或稍后重试")
        except openai.APIError as e:
            raise RuntimeError(f"API错误: {str(e)}")
        except openai.RateLimitError:
            raise RuntimeError("已达到API速率限制，请稍后重试")
        except openai.AuthenticationError:
            raise RuntimeError("API认证失败，请检查API密钥")
        except openai.BadRequestError as e:
            raise RuntimeError(f"请求参数错误: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"发生未知错误: {str(e)}")

class get_string:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_string": ("STRING", {"multiline": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string",)

    FUNCTION = "substr"

    # OUTPUT_NODE = False

    CATEGORY = "昂昂"

    def substr(self, input_string):
        out = input_string
        return (out,)

class LoadFileNode:
    """
    加载文件节点：读取指定路径的文件内容
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {
                    "multiline": False,
                    "default": "path/to/your/file"
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "load_file"
    CATEGORY = "昂昂"

    def load_file(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return (content,)

class ExtractJsonFieldNode:
    """
    提取JSON字段节点：从JSON内容中提取指定字段的值
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_content": ("STRING", {
                    "multiline": True,
                    "default": "{}"
                }),
                "field_name": ("STRING", {
                    "multiline": False,
                    "default": "field"
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "extract_field"
    CATEGORY = "昂昂"

    def extract_field(self, json_content, field_name):
        try:
            data = json.loads(json_content)
            if field_name not in data:
                raise KeyError(f"Field '{field_name}' not found in JSON")
            
            value = data[field_name]
            return (json.dumps(value, ensure_ascii=False),)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON content")

# 节点注册
NODE_CLASS_MAPPINGS = {
    "OpenAIChatNode": OpenAIChatNode,
    "inputString":get_string,
    "LoadFile": LoadFileNode,
    "ExtractJsonField": ExtractJsonFieldNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OpenAIChatNode": "OpenAI Chat",
    "inputString": "input String",
    "LoadFile": "Load File",
    "ExtractJsonField": "JSON Get Value"
} 
