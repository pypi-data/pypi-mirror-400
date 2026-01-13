# coding: utf-8
from marshmallow import Schema, fields

"""
 * @Author：PyCharm - yougangchen
 * @Package：UploadImg
 * @Project：fred-frame
 * @name：UploadImg
 * @Date：2025/5/27 16:31 - 星期二
 * @Filename：UploadImg
 
"""


class UploadImg(Schema):
	"""
        @desc : 上传文件
    """
	file = fields.Raw(metadata={'type': 'file'}, required=True)


class FileUploadResponseSchema(Schema):
	"""
	文件上传响应Schema
	"""
	fileUrl = fields.Str(metadata={'description': '文件URL'})


class AnnotationUploadResponseSchema(Schema):
	"""
	标注文件上传响应Schema
	"""
	fileUrl = fields.Str(metadata={'description': '文件URL'})
	fileName = fields.Str(metadata={'description': '文件名'})
	filePath = fields.Str(metadata={'description': '文件路径'})
