# coding: utf-8
"""
 * @Author：cyg
 * @Package：FileController
 * @Project：Default (Template) Project
 * @name：FileController
 * @Date：2025/5/21 16:35
 * @Filename：FileController
"""
from flask.views import MethodView
from demo import demo
from demo.controller import admin_required
from demo.schema.UploadImg import UploadImg, FileUploadResponseSchema
from demo.service.FileService import FileService


@demo.route("/file/upload/img")
class FileImgController(MethodView):
	@admin_required
	@demo.arguments(UploadImg, location='files')
	@demo.response(200, FileUploadResponseSchema)
	def post(self, args):
		"""
		上传图片
		"""
		file_name = FileService().upload_file("demo/avatar")
		return {"fileUrl": file_name}

