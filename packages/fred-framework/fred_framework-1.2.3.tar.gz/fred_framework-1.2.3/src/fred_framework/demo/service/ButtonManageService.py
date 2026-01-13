"""
 * @Author：cyg
 * @Package：ButtonManageService
 * @Project：Default (Template) Project
 * @name：ButtonManageService
 * @Date：2025/1/20 10:00
 * @Filename：ButtonManageService
"""
from flask import abort
from flask_babelplus import gettext
from sqlalchemy import and_

from model.model import AuthButton, AuthMenu, AuthApiRelation, db


class ButtonManageService:
    def button_list(self, args):
        """
        获取按钮列表
        优化：当选择一级菜单时，递归查询该菜单及其所有子菜单下的按钮
        """
        page = args.get('pageNum', 1)
        per_page = args.get('pageSize', 10)
        menu_id = args.get('menu_id')
        button_name = args.get('button_name', '').strip()

        # 如果指定了菜单ID，需要递归查找所有子菜单ID
        menu_ids = None
        if menu_id:
            menu_ids = self._get_menu_and_children_ids(menu_id)

        # 使用ORM模型查询按钮列表，优化查询避免N+1问题
        # 构建基础查询
        query = db.session.query(AuthButton, AuthMenu).join(AuthMenu, AuthButton.menu_id == AuthMenu.id)

        # 添加查询条件
        if menu_ids:
            # 使用 IN 查询，包含所有子菜单
            query = query.filter(AuthButton.menu_id.in_(menu_ids))

        if button_name:
            query = query.filter(AuthButton.button_name.like(f'%{button_name}%'))

        # 获取总数
        total = query.count()

        # 分页查询
        offset = (page - 1) * per_page
        results = query.offset(offset).limit(per_page).all()

        # 如果没有结果，直接返回空列表
        if not results:
            return {
                'records': [],
                'total': 0,
                'pageNum': page,
                'pageSize': per_page,
            }

        # 获取所有按钮ID，用于批量查询API关系
        button_ids = [result[0].id for result in results]

        # 批量查询所有API关系，避免N+1查询问题
        api_relations = {}
        if button_ids:
            relations = AuthApiRelation.query.filter(AuthApiRelation.auth_id.in_(button_ids)).all()
            for relation in relations:
                if relation.auth_id not in api_relations:
                    api_relations[relation.auth_id] = []
                api_relations[relation.auth_id].append({
                    'id': relation.id,
                    'api_url': relation.api_url or '',
                    'method': relation.method or 'GET'
                })

        # 处理查询结果
        button_list = []
        for button, menu in results:
            api_list = api_relations.get(button.id, [])

            button_dict = {
                'id': button.id,
                'button_name': button.button_name,
                'menu_id': button.menu_id,
                'menu_name': menu.name if menu else '未知菜单',
                'explain': button.explain or '',
                'api_list': api_list,
                # 保持向后兼容，显示第一个API信息
                'api_url': api_list[0]['api_url'] if api_list else ''
            }
            button_list.append(button_dict)

        result = {
            'records': button_list,
            'total': total,
            'pageNum': page,
            'pageSize': per_page,
        }
        return result

    def _get_menu_and_children_ids(self, menu_id):
        """
        递归获取菜单及其所有子菜单的ID列表
        """
        menu_ids = [menu_id]

        # 查询所有菜单
        all_menus = AuthMenu.query.all()

        def get_children_ids(parent_id):
            """递归获取子菜单ID"""
            children = []
            for menu in all_menus:
                if menu.parent_id == parent_id:
                    children.append(menu.id)
                    # 递归获取子菜单的子菜单
                    children.extend(get_children_ids(menu.id))
            return children

        # 获取所有子菜单ID
        children_ids = get_children_ids(menu_id)
        menu_ids.extend(children_ids)

        return menu_ids

    def add_button(self, data):
        """
        新增按钮
        """
        # 检查菜单是否存在
        menu = AuthMenu.query.get(data['menu_id'])
        if not menu:
            abort(400, gettext('菜单不存在'))

        # 检查按钮名称是否已存在
        existing_button = AuthButton.query.filter(
            and_(
                AuthButton.menu_id == data['menu_id'],
                AuthButton.button_name == data['button_name']
            )
        ).first()

        if existing_button:
            abort(400, gettext('该菜单下已存在相同名称的按钮'))

        # 创建新按钮
        button = AuthButton(
            menu_id=data['menu_id'],
            button_name=data['button_name'],
            explain=data.get('explain', ''),
            api_url='',  # 不再使用单个API字段
            method=''    # 不再使用单个method字段
        )

        db.session.add(button)
        db.session.flush()  # 获取button.id

        # 添加API关联关系
        api_list = data.get('api_list', [])

        # 向后兼容：如果没有api_list但有api_url，则创建一个API项
        if not api_list and data.get('api_url'):
            api_list = [{
                'api_url': data.get('api_url', ''),
                'method': data.get('method', 'GET')
            }]

        if api_list:
            for api_info in api_list:
                api_relation = AuthApiRelation(
                    auth_id=button.id,
                    api_url=api_info.get('api_url', ''),
                    method=api_info.get('method', 'GET'),
                    type=1  # 设置权限类型为1，表示按钮权限
                )
                db.session.add(api_relation)

        db.session.commit()

        return button.id

    def update_button(self, data):
        """
        更新按钮
        """
        button_id = data.get('id')
        button = AuthButton.query.get(button_id)

        if not button:
            abort(400, gettext('按钮不存在'))

        # 检查菜单是否存在
        menu = AuthMenu.query.get(data['menu_id'])
        if not menu:
            abort(400, gettext('菜单不存在'))

        # 检查按钮名称是否已存在（排除当前按钮）
        existing_button = AuthButton.query.filter(
            and_(
                AuthButton.menu_id == data['menu_id'],
                AuthButton.button_name == data['button_name'],
                AuthButton.id != button_id
            )
        ).first()

        if existing_button:
            abort(400, gettext('该菜单下已存在相同名称的按钮'))

        # 更新按钮信息
        button.menu_id = data['menu_id']
        button.button_name = data['button_name']
        button.explain = data.get('explain', '')

        # 删除原有的API关联关系
        AuthApiRelation.query.filter_by(auth_id=button_id).delete()

        # 添加新的API关联关系
        api_list = data.get('api_list', [])

        # 向后兼容：如果没有api_list但有api_url，则创建一个API项
        if not api_list and data.get('api_url'):
            api_list = [{
                'api_url': data.get('api_url', ''),
                'method': data.get('method', 'GET')
            }]

        if api_list:
            for api_info in api_list:
                api_relation = AuthApiRelation(
                    auth_id=button_id,
                    api_url=api_info.get('api_url', ''),
                    method=api_info.get('method', 'GET'),
                    type=1  # 设置权限类型为1，表示按钮权限
                )
                db.session.add(api_relation)

        db.session.commit()

        return button.id

    def delete_button(self, args):
        """
        删除按钮
        """
        button_id = args.get('id')
        button = AuthButton.query.get(button_id)

        if not button:
            abort(400, gettext('按钮不存在'))

        # 删除按钮关联的API关系
        AuthApiRelation.query.filter_by(auth_id=button_id).delete()

        # 删除按钮
        db.session.delete(button)
        db.session.commit()

        return True

    def get_menu_list(self, args=None):
        """
        获取菜单列表（用于下拉选择）- 只显示启用的菜单，返回树形结构
        参考 AuthMenuService 的 menu_list 方法实现
        """
        import json

        # 如果传入了参数，支持分页和搜索功能
        if args:
            page = args.get('pageNum', 1)
            per_page = args.get('pageSize', 10)
            title_kw = (args.get('title') or '').strip()
            deleted = args.get('deleted', 0)

            # 基础查询：一级菜单
            base_query = AuthMenu.query.filter(AuthMenu.parent_id == 0)
            # 删除状态过滤：默认仅未删除
            if deleted in (0, 1):
                base_query = base_query.filter(AuthMenu.deleted == deleted)

            # 如有标题关键字，需要查询匹配到的任意层级菜单，并回溯到其一级父菜单
            if title_kw:
                # 预取全部菜单（带删除状态约束）
                all_items_query = AuthMenu.query
                if deleted in (0, 1):
                    all_items_query = all_items_query.filter(AuthMenu.deleted == deleted)
                all_items = all_items_query.order_by(AuthMenu.sort.asc()).all()

                # 找出名字或 meta.title 命中的所有菜单
                needle = title_kw.lower()
                matched_items = []
                for item in all_items:
                    name_ok = (item.name or '').lower().find(needle) != -1
                    meta_title = ''
                    try:
                        meta_title = (json.loads(item.meta).get('title') if item.meta else '') or ''
                    except Exception:
                        meta_title = ''
                    meta_ok = meta_title.lower().find(needle) != -1
                    if name_ok or meta_ok:
                        matched_items.append(item)

                # 计算这些命中项对应的一级父菜单 id 集合
                root_ids = set()
                if matched_items:
                    id_to_item = {it.id: it for it in all_items}
                    for it in matched_items:
                        cur = it
                        while cur and cur.parent_id != 0:
                            cur = id_to_item.get(cur.parent_id)
                        if cur:
                            root_ids.add(cur.id)

                # 若无匹配，直接返回空集，避免返回所有一级菜单
                if not root_ids:
                    return {
                        'records': [],
                        'total': 0,
                        'pageNum': page,
                        'pageSize': per_page,
                    }

                # 在基础查询上限定到这些根 id
                base_query = base_query.filter(AuthMenu.id.in_(list(root_ids)))

            # 分页取根节点
            menu_page = base_query.order_by(AuthMenu.deleted.asc(), AuthMenu.sort.asc()).paginate(page=page, per_page=per_page)

            # 构建整棵树，再用分页根节点挑选对应子树返回
            all_menu_items = AuthMenu.query.all()
            tree_structure = self.build_menu_tree(all_menu_items)
            records = []
            for item in menu_page.items:
                for child in tree_structure:
                    if child['id'] == item.id:
                        records.append(child)
            return {
                'records': records,
                'total': menu_page.total,
                'pageNum': menu_page.page,
                'pageSize': menu_page.per_page,
            }
        else:
            # 原有逻辑：返回所有未删除且未隐藏的菜单树形结构
            menus = AuthMenu.query.filter(AuthMenu.deleted == 0).order_by(AuthMenu.sort.asc()).all()
            return self.build_menu_tree(menus)

    def build_menu_tree(self, menu_items, parent_id=0):
        """
        构建菜单树形结构
        只返回id和name字段
        """
        import json

        tree = []
        for item in menu_items:
            if item.parent_id == parent_id:
                children = self.build_menu_tree(menu_items, item.id)

                # 解析 meta 字段检查是否隐藏
                is_hide = False
                try:
                    meta = json.loads(item.meta) if item.meta else {}
                    is_hide = meta.get('isHide', False)
                except json.JSONDecodeError:
                    pass

                # 只显示未隐藏的菜单，且只返回id和name
                if not is_hide:
                    menu_dict = {
                        'id': item.id,
                        'name': item.name
                    }

                    if children:
                        menu_dict['children'] = children

                    tree.append(menu_dict)
        return tree

    def get_all_api_urls(self):
        """
        获取所有接口URL列表 - 使用文件扫描方式
        """
        from fred_framework.common.Utils import Utils
        return Utils.get_api_urls_from_files()

