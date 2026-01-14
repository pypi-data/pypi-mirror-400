"""
代码生成模块
基于论文分析生成实现代码
"""

from pathlib import Path
from typing import Dict, Any, Optional
import json
import yaml


class CodeGenerator:
    """代码生成器"""
    
    def __init__(self, code_dir: Optional[str] = None, config_path: str = "config.yaml"):

        """
        初始化代码生成器
        
        Args:
            code_dir: 代码存储目录（如果为None，则从配置文件读取）
            config_path: 配置文件路径
        """
        self.paper_workspace_dir = None

        if code_dir is None:
            # 从配置文件读取
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                pr = config.get("paper_reading", {}) if isinstance(config, dict) else {}
                self.paper_workspace_dir = pr.get("paper_workspace_dir") or pr.get("output_root")
                code_dir = pr.get("code_dir", "data/code")
            else:
                code_dir = "data/code"

        self.paper_workspace_dir = Path(self.paper_workspace_dir) if self.paper_workspace_dir else None
        if self.paper_workspace_dir:
            self.paper_workspace_dir.mkdir(parents=True, exist_ok=True)

        self.code_dir = Path(code_dir)
        self.code_dir.mkdir(parents=True, exist_ok=True)

    
    def create_project_structure(
        self,
        paper_title: str,
        implementation_guide: str,
        language: str = "python",
        paper_id: Optional[str] = None
    ) -> Path:
        """
        创建项目结构
        
        Args:
            paper_title: 论文标题
            implementation_guide: 实现指南
            language: 编程语言
            paper_id: 论文唯一标识，如果提供则使用作为目录名
        
        Returns:
            项目根目录路径
        """
        if self.paper_workspace_dir:
            # 新结构：data/papers/<paper_id>/code
            if paper_id:
                project_dir = self.paper_workspace_dir / paper_id / "code"
            else:
                safe_title = "".join(c for c in paper_title if c.isalnum() or c in (" ", "-", "_", ".")).strip()
                safe_title = safe_title.replace(" ", "_")[:50]
                project_dir = self.paper_workspace_dir / safe_title / "code"
        else:
            # 旧结构（兼容）
            if paper_id:
                project_dir = self.code_dir / paper_id
            else:
                safe_title = "".join(c for c in paper_title if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_title = safe_title.replace(' ', '_')[:50]
                project_dir = self.code_dir / safe_title

        
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建基础文件
        if language == "python":
            self._create_python_project(project_dir, paper_title, implementation_guide)
        elif language == "cpp":
            self._create_cpp_project(project_dir, paper_title, implementation_guide)
        
        return project_dir
    
    def _create_python_project(
        self,
        project_dir: Path,
        paper_title: str,
        implementation_guide: str
    ):
        """创建 Python 项目结构"""
        # README
        readme_content = f"""# {paper_title} - 实现

## 项目说明

基于论文实现的代码项目。

## 实现指南

{implementation_guide}

## 使用说明

\`\`\`bash
pip install -r requirements.txt
python main.py
\`\`\`

## 项目结构

- `main.py`: 主程序入口
- `algorithm.py`: 核心算法实现
- `utils.py`: 工具函数
- `config.py`: 配置文件
- `tests/`: 测试代码
"""
        (project_dir / "README.md").write_text(readme_content, encoding='utf-8')
        
        # requirements.txt
        (project_dir / "requirements.txt").write_text("numpy>=1.24.0\nmatplotlib>=3.7.0\n", encoding='utf-8')
        
        # 主程序模板
        main_content = """\"\"\"
主程序入口
\"\"\"

from algorithm import CoreAlgorithm
from config import Config


def main():
    \"\"\"主函数\"\"\"
    config = Config()
    algorithm = CoreAlgorithm(config)
    
    # 运行算法
    result = algorithm.run()
    print(f"结果: {result}")


if __name__ == "__main__":
    main()
"""
        (project_dir / "main.py").write_text(main_content, encoding='utf-8')
        
        # 算法模板
        algorithm_content = """\"\"\"
核心算法实现
根据论文中的方法实现
\"\"\"


class CoreAlgorithm:
    \"\"\"核心算法类\"\"\"
    
    def __init__(self, config):
        \"\"\"
        初始化算法
        
        Args:
            config: 配置对象
        \"\"\"
        self.config = config
    
    def run(self):
        \"\"\"
        运行算法
        
        Returns:
            算法结果
        \"\"\"
        # TODO: 实现论文中的核心算法
        pass
    
    def step1(self):
        \"\"\"步骤1\"\"\"
        pass
    
    def step2(self):
        \"\"\"步骤2\"\"\"
        pass
"""
        (project_dir / "algorithm.py").write_text(algorithm_content, encoding='utf-8')
        
        # 配置文件
        config_content = """\"\"\"
配置文件
\"\"\"


class Config:
    \"\"\"配置类\"\"\"
    
    def __init__(self):
        \"\"\"初始化配置\"\"\"
        # TODO: 根据论文设置参数
        self.param1 = 1.0
        self.param2 = 0.5
"""
        (project_dir / "config.py").write_text(config_content, encoding='utf-8')
        
        # 工具文件
        utils_content = """\"\"\"
工具函数
\"\"\"

import numpy as np


def helper_function(x):
    \"\"\"
    辅助函数
    
    Args:
        x: 输入
    
    Returns:
        输出
    \"\"\"
    return x
"""
        (project_dir / "utils.py").write_text(utils_content, encoding='utf-8')
        
        # 测试目录
        test_dir = project_dir / "tests"
        test_dir.mkdir(exist_ok=True)
        
        test_content = """\"\"\"
测试代码
\"\"\"

import unittest
from algorithm import CoreAlgorithm
from config import Config


class TestAlgorithm(unittest.TestCase):
    \"\"\"算法测试类\"\"\"
    
    def setUp(self):
        \"\"\"测试准备\"\"\"
        self.config = Config()
        self.algorithm = CoreAlgorithm(self.config)
    
    def test_run(self):
        \"\"\"测试运行\"\"\"
        result = self.algorithm.run()
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
"""
        (test_dir / "test_algorithm.py").write_text(test_content, encoding='utf-8')
    
    def _create_cpp_project(
        self,
        project_dir: Path,
        paper_title: str,
        implementation_guide: str
    ):
        """创建 C++ 项目结构"""
        # 类似 Python 项目，创建 C++ 项目结构
        readme_content = f"""# {paper_title} - C++ 实现

## 项目说明

基于论文的 C++ 实现。

## 编译

\`\`\`bash
mkdir build && cd build
cmake ..
make
\`\`\`

## 运行

\`\`\`bash
./main
\`\`\`
"""
        (project_dir / "README.md").write_text(readme_content, encoding='utf-8')
        
        # CMakeLists.txt
        cmake_content = """cmake_minimum_required(VERSION 3.10)
project(PaperImplementation)

set(CMAKE_CXX_STANDARD 17)

add_executable(main main.cpp algorithm.cpp)
"""
        (project_dir / "CMakeLists.txt").write_text(cmake_content, encoding='utf-8')
        
        # main.cpp
        main_cpp = """#include <iostream>
#include "algorithm.h"

int main() {
    CoreAlgorithm algorithm;
    algorithm.run();
    return 0;
}
"""
        (project_dir / "main.cpp").write_text(main_cpp, encoding='utf-8')
        
        # algorithm.h
        algorithm_h = """#ifndef ALGORITHM_H
#define ALGORITHM_H

class CoreAlgorithm {
public:
    void run();
private:
    void step1();
    void step2();
};

#endif
"""
        (project_dir / "algorithm.h").write_text(algorithm_h, encoding='utf-8')
        
        # algorithm.cpp
        algorithm_cpp = """#include "algorithm.h"
#include <iostream>

void CoreAlgorithm::run() {
    // TODO: 实现核心算法
    step1();
    step2();
}

void CoreAlgorithm::step1() {
    // TODO: 实现步骤1
}

void CoreAlgorithm::step2() {
    // TODO: 实现步骤2
}
"""
        (project_dir / "algorithm.cpp").write_text(algorithm_cpp, encoding='utf-8')
    
    def save_implementation_guide(
        self,
        paper_title: str,
        guide: str,
        paper_id: Optional[str] = None
    ) -> Path:
        """
        保存实现指南
        
        Args:
            paper_title: 论文标题
            guide: 实现指南内容
            paper_id: 论文唯一标识，如果提供则保存到论文独立目录
        
        Returns:
            文件路径
        """
        if self.paper_workspace_dir:
            if paper_id:
                paper_dir = self.paper_workspace_dir / paper_id / "code"
            else:
                safe_title = "".join(c for c in paper_title if c.isalnum() or c in (" ", "-", "_", ".")).strip()
                safe_title = safe_title.replace(" ", "_")[:50]
                paper_dir = self.paper_workspace_dir / safe_title / "code"
            paper_dir.mkdir(parents=True, exist_ok=True)
            guide_path = paper_dir / "implementation_guide.md"
        else:
            if paper_id:
                paper_dir = self.code_dir / paper_id
                paper_dir.mkdir(parents=True, exist_ok=True)
                guide_path = paper_dir / "implementation_guide.md"
            else:
                safe_title = "".join(c for c in paper_title if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_title = safe_title.replace(' ', '_')[:50]
                guide_path = self.code_dir / f"{safe_title}_implementation_guide.md"

        
        guide_path.write_text(guide, encoding='utf-8')
        
        return guide_path
