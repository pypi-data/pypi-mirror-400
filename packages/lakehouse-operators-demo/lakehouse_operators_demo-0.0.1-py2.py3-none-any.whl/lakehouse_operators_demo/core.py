
# -*- coding: utf8 -*-
import fasttext
import os
from typing import Dict

class FastTextLanguageDetector:
    """
    FastText语言检测器
    使用模型: lid.176.bin
    """
    
    def __init__(self, model_path: str = "lid.176.bin"):
        """
        初始化检测器
        
        Args:
            model_path: fastText模型文件路径
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"模型文件 '{model_path}' 不存在，请先下载\n"
                "下载命令: wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"
            )
        
        self.model = fasttext.load_model(model_path)
    
    def process(self, input_dict: Dict) -> Dict:
        """
        处理单条数据，在输入字典基础上新增语言检测结果
        
        Args:
            input_dict: 输入字典，必须包含文本字段
            
        Returns:
            新增语言检测结果的字典
        """
        # 浅层拷贝
        output_dict = input_dict.copy()
        
        # 获取文本内容
        text_field = "text"
        text = output_dict.get(text_field, "")
        
        if not text:
            # 如果没有文本，返回空结果
            output_dict["detected_language"] = None
            output_dict["detection_confidence"] = 0.0
            return output_dict
        
        # 进行语言检测
        labels, scores = self.model.predict(text, k=1)
        
        # 提取结果
        lang_code = labels[0].replace("__label__", "")
        confidence = float(scores[0])
        
        # 添加到输出字典
        output_dict["detected_language"] = lang_code
        output_dict["detection_confidence"] = confidence
        
        return output_dict


# 使用示例
def main():
    # 初始化检测器
    detector = FastTextLanguageDetector("lid.176.bin")
    
    # 测试数据
    test_data = {
        "id": 1,
        "text": "Hello, this is a test for language detection.",
        "timestamp": "2024-01-01"
    }
    
    # 处理数据
    result = detector.process(test_data)
    
    print("输入字典:", test_data)
    print("输出字典:", result)
    print(f"检测到语言: {result['detected_language']}")
    print(f"置信度: {result['detection_confidence']:.4f}")
    
    # 更多测试
    samples = [
        {"id": 2, "text": "今天天气真好，适合出门散步。"},
        {"id": 3, "text": "Bonjour, comment allez-vous?"},
        {"id": 4, "text": "Hola, ¿cómo estás?"},
    ]
    
    print("\n更多测试:")
    for sample in samples:
        result = detector.process(sample)
        print(f"ID {sample['id']}: {result['detected_language']} (置信度: {result['detection_confidence']:.4f})")


if __name__ == "__main__":
    main()