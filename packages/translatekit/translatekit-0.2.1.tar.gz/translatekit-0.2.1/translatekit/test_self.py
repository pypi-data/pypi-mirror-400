import zipfile
import xml.etree.ElementTree as ET
import os
import re
from copy import deepcopy
from typing import List, Tuple, Dict, Any

# 假设translate函数已经存在
from test import *

class WordDocumentTranslator:
    def __init__(self, translate_func):
        """
        初始化翻译器
        
        Args:
            translate_func: 翻译函数，输入文本列表，输出翻译后的文本列表
        """
        self.translate = translate_func
        self.namespaces = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
            'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
        }
        
        # 注册命名空间以便正确解析XML
        for prefix, uri in self.namespaces.items():
            ET.register_namespace(prefix, uri)
    
    def _get_run_properties(self, run_element):
        """
        获取run的格式属性
        
        Args:
            run_element: run的XML元素
            
        Returns:
            格式属性的字符串表示
        """
        properties = {}
        
        # 获取run的属性元素
        r_pr = run_element.find('w:rPr', self.namespaces)
        if r_pr is not None:
            # 提取各种格式属性
            for child in r_pr:
                tag = child.tag.split('}')[-1]  # 去掉命名空间
                if tag == 'rFonts':
                    properties['font'] = child.attrib.get('w:ascii', '')
                elif tag == 'sz':
                    properties['size'] = child.attrib.get('w:val', '')
                elif tag == 'color':
                    properties['color'] = child.attrib.get('w:val', '')
                elif tag == 'b':
                    properties['bold'] = True
                elif tag == 'i':
                    properties['italic'] = True
                elif tag == 'u':
                    properties['underline'] = True
        
        return str(properties)
    
    def _should_merge_runs(self, run1_props, run2_props):
        """
        判断两个run是否应该合并
        
        Args:
            run1_props: 第一个run的属性
            run2_props: 第二个run的属性
            
        Returns:
            bool: 是否应该合并
        """
        # 如果属性完全相同，则合并
        return run1_props == run2_props
    
    def extract_text_from_docx(self, docx_path: str) -> Tuple[Dict[str, Any], List[str]]:
        """
        从docx文件中提取文本和文档结构
        
        Returns:
            Tuple[文档结构信息, 文本列表]
        """
        document_structure = {
            'paragraphs': [],
            'text_elements': []
        }
        all_text_elements = []
        
        with zipfile.ZipFile(docx_path, 'r') as docx_zip:
            # 读取主要的document.xml文件
            with docx_zip.open('word/document.xml') as doc_file:
                doc_tree = ET.parse(doc_file)
                doc_root = doc_tree.getroot()
                
                # 提取段落和文本
                paragraph_index = 0
                for paragraph in doc_root.findall('.//w:p', self.namespaces):
                    paragraph_info = {
                        'index': paragraph_index,
                        'runs': [],
                        'merged_run_groups': []  # 存储合并的run组信息
                    }
                    
                    # 获取段落中的所有run
                    runs = paragraph.findall('.//w:r', self.namespaces)
                    
                    # 合并相似的run
                    merged_runs = []
                    current_run_group = []
                    current_props = None
                    
                    for i, run in enumerate(runs):
                        run_props = self._get_run_properties(run)
                        
                        # 获取run中的文本
                        text_elems = run.findall('.//w:t', self.namespaces)
                        run_text = ''.join([elem.text if elem.text else "" for elem in text_elems])
                        
                        # 跳过空run
                        if not run_text.strip():
                            continue
                        
                        # 如果是第一个run或与当前组属性相同，则添加到当前组
                        if current_props is None or self._should_merge_runs(current_props, run_props):
                            current_run_group.append((run, run_text, run_props, i))
                            current_props = run_props
                        else:
                            # 开始新的组
                            if current_run_group:
                                merged_runs.append(current_run_group)
                            current_run_group = [(run, run_text, run_props, i)]
                            current_props = run_props
                    
                    # 添加最后一组
                    if current_run_group:
                        merged_runs.append(current_run_group)
                    
                    # 处理合并后的run组
                    run_index = 0
                    for run_group in merged_runs:
                        # 如果组中只有一个run，保持原样
                        if len(run_group) == 1:
                            run, run_text, run_props, original_index = run_group[0]
                            run_info = {
                                'paragraph_index': paragraph_index,
                                'run_index': run_index,
                                'text_elements': [],
                                'is_merged': False,
                                'original_run': run,
                                'original_indices': [original_index]
                            }
                            
                            text_index = 0
                            for text_elem in run.findall('.//w:t', self.namespaces):
                                text_content = text_elem.text if text_elem.text else ""
                                
                                # 保存文本元素信息
                                text_info = {
                                    'paragraph_index': paragraph_index,
                                    'run_index': run_index,
                                    'text_index': text_index,
                                    'original_text': text_content,
                                    'xml_element': deepcopy(text_elem),  # 保存元素的引用
                                    'original_run': run,
                                    'is_merged': False,
                                    'original_indices': [original_index]
                                }
                                
                                run_info['text_elements'].append(text_info)
                                all_text_elements.append(text_info)
                                
                                text_index += 1
                            
                            paragraph_info['runs'].append(run_info)
                            run_index += 1
                        else:
                            # 合并多个run
                            merged_text = ''.join([text for _, text, _, _ in run_group])
                            first_run = run_group[0][0]  # 使用第一个run作为代表
                            original_indices = [idx for _, _, _, idx in run_group]
                            
                            run_info = {
                                'paragraph_index': paragraph_index,
                                'run_index': run_index,
                                'text_elements': [],
                                'is_merged': True,
                                'merged_runs': run_group,  # 保存所有被合并的run
                                'original_run': first_run,
                                'original_indices': original_indices,
                                'merged_text': merged_text
                            }
                            
                            # 记录合并组信息
                            paragraph_info['merged_run_groups'].append({
                                'group_index': run_index,
                                'original_indices': original_indices,
                                'merged_text': merged_text
                            })
                            
                            # 创建一个虚拟的文本元素用于合并的文本
                            text_info = {
                                'paragraph_index': paragraph_index,
                                'run_index': run_index,
                                'text_index': 0,
                                'original_text': merged_text,
                                'xml_element': None,  # 将在后续处理中创建
                                'is_merged': True,
                                'merged_runs': run_group,
                                'original_indices': original_indices
                            }
                            
                            run_info['text_elements'].append(text_info)
                            all_text_elements.append(text_info)
                            
                            paragraph_info['runs'].append(run_info)
                            run_index += 1
                    
                    document_structure['paragraphs'].append(paragraph_info)
                    paragraph_index += 1
        
        # 提取纯文本列表用于翻译
        text_list = [elem['original_text'] for elem in all_text_elements]
        
        return document_structure, text_list, all_text_elements
    
    def create_translated_docx(self, original_docx_path: str, output_docx_path: str, 
                             document_structure: Dict[str, Any], 
                             all_text_elements: List[Dict[str, Any]], 
                             translated_texts: List[str]) -> None:
        """
        创建翻译后的docx文件
        
        Args:
            original_docx_path: 原始文档路径
            output_docx_path: 输出文档路径
            document_structure: 文档结构信息
            all_text_elements: 所有文本元素信息
            translated_texts: 翻译后的文本列表
        """
        # 创建临时工作目录
        temp_dir = "temp_docx_extract"
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # 解压原始docx文件
            with zipfile.ZipFile(original_docx_path, 'r') as original_zip:
                original_zip.extractall(temp_dir)
            
            # 更新document.xml中的文本内容
            doc_xml_path = os.path.join(temp_dir, 'word/document.xml')
            doc_tree = ET.parse(doc_xml_path)
            doc_root = doc_tree.getroot()
            
            # 构建文本元素映射以便快速查找
            text_elem_map = {}
            for text_elem_info in all_text_elements:
                key = (text_elem_info['paragraph_index'], 
                       text_elem_info['run_index'], 
                       text_elem_info['text_index'])
                text_elem_map[key] = text_elem_info
            
            # 首先处理所有合并的run组
            paragraph_index = 0
            for paragraph in doc_root.findall('.//w:p', self.namespaces):
                # 获取当前段落的合并组信息
                current_para_info = None
                for para_info in document_structure['paragraphs']:
                    if para_info['index'] == paragraph_index:
                        current_para_info = para_info
                        break
                
                if current_para_info and current_para_info['merged_run_groups']:
                    # 获取段落中的所有run
                    all_runs_in_para = paragraph.findall('.//w:r', self.namespaces)
                    
                    # 处理每个合并组
                    for merge_group in current_para_info['merged_run_groups']:
                        original_indices = merge_group['original_indices']
                        
                        if len(original_indices) > 1:
                            # 找到第一个run
                            if original_indices[0] < len(all_runs_in_para):
                                first_run = all_runs_in_para[original_indices[0]]
                                
                                # 找到对应的翻译文本
                                group_key = (paragraph_index, merge_group['group_index'], 0)
                                if group_key in text_elem_map:
                                    elem_info = text_elem_map[group_key]
                                    translated_index = all_text_elements.index(elem_info)
                                    if translated_index < len(translated_texts):
                                        # 更新第一个run的文本
                                        text_elems = first_run.findall('.//w:t', self.namespaces)
                                        if text_elems:
                                            # 更新第一个文本元素
                                            text_elems[0].text = translated_texts[translated_index]
                                            # 删除其他文本元素
                                            for text_elem in text_elems[1:]:
                                                first_run.remove(text_elem)
                                        else:
                                            # 如果没有文本元素，创建一个
                                            text_elem = ET.SubElement(first_run, f'{{{self.namespaces["w"]}}}t')
                                            text_elem.text = translated_texts[translated_index]
                                
                                # 删除其他run
                                for i in range(1, len(original_indices)):
                                    if original_indices[i] < len(all_runs_in_para):
                                        run_to_remove = all_runs_in_para[original_indices[i]]
                                        if run_to_remove in paragraph:
                                            paragraph.remove(run_to_remove)
                
                paragraph_index += 1
            
            # 然后处理普通（未合并）的run
            paragraph_index = 0
            for paragraph in doc_root.findall('.//w:p', self.namespaces):
                run_index = 0
                for run in paragraph.findall('.//w:r', self.namespaces):
                    text_index = 0
                    for text_elem in run.findall('.//w:t', self.namespaces):
                        key = (paragraph_index, run_index, text_index)
                        if key in text_elem_map:
                            elem_info = text_elem_map[key]
                            # 跳过已处理的合并run
                            if not elem_info.get('is_merged', False):
                                translated_index = all_text_elements.index(elem_info)
                                if translated_index < len(translated_texts):
                                    text_elem.text = translated_texts[translated_index]
                        text_index += 1
                    run_index += 1
                paragraph_index += 1
            
            # 保存修改后的document.xml
            doc_tree.write(doc_xml_path, encoding='UTF-8', xml_declaration=True)
            
            # 重新打包为docx文件
            with zipfile.ZipFile(output_docx_path, 'w', zipfile.ZIP_DEFLATED) as new_zip:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        new_zip.write(file_path, arcname)
                        
        finally:
            # 清理临时文件
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def translate_document(self, input_path: str, output_path: str = None) -> str:
        """
        翻译整个Word文档
        
        Args:
            input_path: 输入文档路径
            output_path: 输出文档路径（可选）
            
        Returns:
            输出文档路径
        """
        if output_path is None:
            base_name = os.path.splitext(input_path)[0]
            output_path = f"{base_name}_translated.docx"
        
        print(f"开始翻译文档: {input_path}")
        
        # 1. 提取文本和文档结构
        print("正在解析文档结构...")
        document_structure, text_list, all_text_elements = self.extract_text_from_docx(input_path)
        
        print(f"找到 {len(text_list)} 个文本片段")
        
        # 2. 过滤空文本和只包含空白字符的文本
        non_empty_texts = []
        text_indices = []
        
        for i, text in enumerate(text_list):
            if text and text.strip():
                non_empty_texts.append(text)
                text_indices.append(i)
        
        print(f"需要翻译的文本片段: {len(non_empty_texts)}")
        
        # 3. 批量翻译文本
        print("正在翻译文本...")
        print(non_empty_texts)
        translated_non_empty = self.translate(non_empty_texts)
        print(translated_non_empty)
        
        # 4. 重建完整的翻译文本列表（包括空文本）
        full_translated_texts = [""] * len(text_list)
        for idx, trans_text in zip(text_indices, translated_non_empty):
            full_translated_texts[idx] = trans_text
        
        # 5. 创建翻译后的文档
        print("正在生成翻译后的文档...")
        self.create_translated_docx(
            input_path, 
            output_path, 
            document_structure, 
            all_text_elements, 
            full_translated_texts
        )
        
        print(f"翻译完成! 输出文件: {output_path}")
        return output_path

def main():
    """
    主函数 - 使用示例
    """
    # 创建翻译器实例
    translators = BaiduTranslator(config=config)
    translate=translators.translate
    translator = WordDocumentTranslator(translate)
    
    # 指定输入文件路径
    input_file = "24.docx"  # 请替换为您的实际文件路径
    
    if not os.path.exists(input_file):
        print(f"错误: 输入文件 '{input_file}' 不存在")
        return
    
    # 执行翻译
    try:
        output_file = translator.translate_document(input_file)
        print(f"成功生成翻译文档: {output_file}")
    except Exception as e:
        print(f"翻译过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print(translators.get_performance_metrics())

if __name__ == "__main__":
    main()