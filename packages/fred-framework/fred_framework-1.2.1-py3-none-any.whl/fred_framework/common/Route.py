# coding: utf-8
"""
 * @Author：cyg
 * @Package：Route
 * @Project：Default (Template) Project
 * @name：Route
 * @Date：2025/6/1 11:25
 * @Filename：Route
"""

import os

from flask import send_from_directory, render_template, abort
from jinja2 import ChoiceLoader, FileSystemLoader


class Route:
    
    @staticmethod
    def _get_project_root():
        """
        获取项目根目录（使用当前工作目录）
        
        :return: 项目根目录路径
        """
        return os.getcwd()
    
    def __init__(self, app):
        self.app = app
    
    def set_routes(self):
        # 1. 蓝图路由配置
        sys_blueprints = ['api-docs', 'swagger_ui']
        i = 0
        project_root = self._get_project_root()
        jinja_loader_arr = [self.app.jinja_loader]
        home_modules = self.app.config.get('HOME_MODULES', None)
        for blueprint_name in self.app.blueprints:
            if blueprint_name in sys_blueprints:
                continue
            jinja_loader_arr.append(FileSystemLoader(f'{blueprint_name}/templates'))
            is_home = False
            web_path = os.path.join(project_root, f'{blueprint_name}/templates/{blueprint_name}')
            index_path = os.path.join(project_root, f'{blueprint_name}/templates/{blueprint_name}/index.html')
            if not os.path.exists(web_path) or not os.path.exists(index_path):
                continue
            if not home_modules and i == 0:
                is_home = True
            elif home_modules == blueprint_name:
                is_home = True
            if is_home:
                self.register_static_route(blueprint_name, is_home)
            self.register_static_route(blueprint_name, False)
            i += 1
        self.app.jinja_loader = ChoiceLoader(jinja_loader_arr)

    def register_static_route(self, blueprint_name, is_home):
        assets_path_pre = "/" if is_home else f"/{blueprint_name}"

        # 动态生成唯一 endpoint 名称
        if is_home:
            index_endpoint = f"{blueprint_name}_home_index"
        else:
            index_endpoint = f"{blueprint_name}_index"

        @self.app.route(f"{assets_path_pre}", endpoint=f"{index_endpoint}_root")
        def module_index_root():
            return render_template(f"{blueprint_name}/index.html")

        # 统一处理所有路径请求（包括静态资源文件和 SPA 页面路由）
        @self.app.route(f"{assets_path_pre}/<path:path>", endpoint=index_endpoint)
        def module_index_path(path):
            project_root = self._get_project_root()
            
            # 1. 自动探测资源文件逻辑
            # 搜索优先级：1. 蓝图模板目录 (前端打包目录)  2. 项目根目录 (处理 map/, uploads/, assets/ 等)
            search_dirs = [
                os.path.join(project_root, f'{blueprint_name}/templates/{blueprint_name}'),
                project_root
            ]
            
            for base_dir in search_dirs:
                file_path = os.path.normpath(os.path.join(base_dir, path))
                if os.path.isfile(file_path):
                    return send_from_directory(os.path.dirname(file_path), os.path.basename(file_path))

            # 2. SPA 路由支持：如果请求没有文件后缀，或者明确请求 index.html
            file_ext = os.path.splitext(path)[1]
            if not file_ext or path == 'index.html' or path.endswith('/'):
                return render_template(f"{blueprint_name}/index.html")
            
            # 3. 如果有后缀但文件确实不存在，返回 404
            abort(404)
