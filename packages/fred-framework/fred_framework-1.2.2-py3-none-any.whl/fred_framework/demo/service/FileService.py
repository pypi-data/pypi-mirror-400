# coding: utf-8
"""
 * @Author：cyg
 * @Package：FileService
 * @Project：Default (Template) Project
 * @name：FileService
 * @Date：2025/5/26 15:38
 * @Filename：FileService
"""
import os
from datetime import datetime
from flask import abort, session
from flask_babelplus import gettext
from PIL import Image

from demo import demo
from fred_framework.common.Utils import Utils



class FileService:
	"""
	上传文件
	"""

	def upload_file(self, path: str) -> str:
		file_dict = Utils.upload_file(path)
		if file_dict['file_name'] != "":
			return file_dict['file_name']
		else:
			abort(400, file_dict['msg'])

	