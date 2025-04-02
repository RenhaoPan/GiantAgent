from jmcomic import JmOptionPlugin
from jmcomic.jm_option import *
import os
from minio import Minio
from minio.error import S3Error

# 初始化MinIO客户端
minio_client = Minio(
    "8.133.196.106:9000",
    access_key="panrenhao",
    secret_key="panrenhao",
    secure=False  # 如果使用HTTPS则为True，否则为False
)
BUCKET_NAME = 'jmoss'
class Img2BathchPdfPlugin(JmOptionPlugin):
    plugin_key = 'img2batchpdf'

    def invoke(self,
               photo: JmPhotoDetail = None,
               album: JmAlbumDetail = None,
               downloader=None,
               pdf_dir=None,
               filename_rule='Pid',
               delete_original_file=False,
               **kwargs,
               ):
        if photo is None and album is None:
            jm_log('wrong_usage', 'img2pdf必须运行在after_photo或after_album时')

        try:
            import img2pdf
        except ImportError:
            self.warning_lib_not_install('img2pdf')
            return

        self.delete_original_file = delete_original_file

        # 处理生成的pdf文件的路径
        pdf_dir = self.ensure_make_pdf_dir(pdf_dir)

        # 处理pdf文件名
        filename = DirRule.apply_rule_directly(album, photo, filename_rule)

        # pdf路径
        pdf_filepath = os.path.join(pdf_dir, f'{filename}')

        # 调用 img2pdf 把 photo_dir 下的所有图片转为pdf
        img_path_ls, img_dir_ls = self.batch_write_img_2_pdf(pdf_filepath, album, photo, filename)
        self.log(f'Convert Successfully: JM{album or photo} → {pdf_filepath}')

        # 执行删除
        img_path_ls += img_dir_ls
        self.execute_deletion(img_path_ls)

    def batch_write_img_2_pdf(self, pdf_filepath, album: JmAlbumDetail, photo: JmPhotoDetail, filename):
        import img2pdf

        if album is None:
            img_dir_ls = [self.option.decide_image_save_dir(photo)]
        else:
            img_dir_ls = [self.option.decide_image_save_dir(photo) for photo in album]

        img_path_ls = []

        for img_dir in img_dir_ls:
            imgs = files_of_dir(img_dir)
            if not imgs:
                continue
            img_path_ls += imgs

        # 每次处理的图片数量
        batch_size = 20
        index = 1
        for i in range(0, len(img_path_ls), batch_size):
            batch_images = img_path_ls[i:i + batch_size]
            temp_pdf_path = f"{pdf_filepath}_{index}.pdf"
            index += 1

            with open(temp_pdf_path, 'wb') as f:
                f.write(img2pdf.convert(batch_images))


        return img_path_ls, img_dir_ls

    @staticmethod
    def ensure_make_pdf_dir(pdf_dir: str):
        pdf_dir = pdf_dir or os.getcwd()
        pdf_dir = fix_filepath(pdf_dir, True)
        mkdir_if_not_exists(pdf_dir)
        return pdf_dir


class LongImgBatchPlugin(JmOptionPlugin):
    plugin_key = 'long_img_batch'

    def invoke(self,
               photo: JmPhotoDetail = None,
               album: JmAlbumDetail = None,
               downloader=None,
               img_dir=None,
               filename_rule='Pid',
               batch_size=20,
               delete_original_file=False,
               **kwargs,
               ):
        if photo is None and album is None:
            jm_log('wrong_usage', 'long_img必须运行在after_photo或after_album时')

        try:
            from PIL import Image
        except ImportError:
            self.warning_lib_not_install('PIL')
            return

        self.delete_original_file = delete_original_file
        self.batch_size = batch_size
        # 处理文件夹配置
        img_dir = self.get_img_dir(img_dir)

        # 处理生成的长图文件的路径
        filename = DirRule.apply_rule_directly(album, photo, filename_rule)

        # 长图路径
        long_img_path = os.path.join(img_dir, f'{filename}')

        # 调用 PIL 把 photo_dir 下的所有图片合并为长图
        img_path_ls = self.batch_write_img_2_long_img(long_img_path, album, photo, filename)
        self.log(f'Convert Successfully: JM{album or photo} → {long_img_path}')

        # 执行删除
        self.execute_deletion(img_path_ls)

    def batch_write_img_2_long_img(self, long_img_path, album: JmAlbumDetail, photo: JmPhotoDetail, filename) -> List[str]:
        import itertools

        if album is None:
            img_dir_items = [self.option.decide_image_save_dir(photo)]
        else:
            img_dir_items = [self.option.decide_image_save_dir(photo) for photo in album]

        img_paths = itertools.chain(*map(files_of_dir, img_dir_items))
        img_paths = filter(lambda x: not x.startswith('.'), img_paths)  # 过滤系统文件

        # 每次处理的图片数量
        batch_size = self.batch_size
        index = 1
        temp_images = []
        temp_img_paths = []

        for img_path in img_paths:
            temp_img_paths.append(img_path)
            if len(temp_img_paths) == batch_size:
                temp_long_img_path = f"{long_img_path}_{index}.png"
                self.merge_images(temp_img_paths, temp_long_img_path, filename, index)
                index += 1
                temp_img_paths = []
        # 处理剩余的图片
        if temp_img_paths:
            temp_long_img_path = f"{long_img_path}_{index}.png"
            self.merge_images(temp_img_paths, temp_long_img_path, filename, index)

        return img_paths

    def merge_images(self, img_paths, output_path, filename, index):
        from PIL import Image
        images = self.open_images(img_paths)
        try:
            resample_method = Image.Resampling.LANCZOS
        except AttributeError:
            resample_method = Image.LANCZOS

        min_img_width = min(img.width for img in images)
        total_height = 0
        for i, img in enumerate(images):
            if img.width > min_img_width:
                images[i] = img.resize((min_img_width, int(img.height * min_img_width / img.width)),
                                       resample=resample_method)
            total_height += images[i].height

        long_img = Image.new('RGB', (min_img_width, total_height))
        y_offset = 0
        for img in images:
            long_img.paste(img, (0, y_offset))
            y_offset += img.height

        long_img.save(output_path)
        for img in images:
            img.close()

        # 上传到MinIO
        minio_client.fput_object(BUCKET_NAME, f"{filename}_{index}.png", output_path)

    def open_images(self, img_paths: List[str]):
        images = []
        for img_path in img_paths:
            try:
                img = Image.open(img_path)
                images.append(img)
            except IOError as e:
                self.log(f"Failed to open image {img_path}: {e}", 'error')
        return images

    @staticmethod
    def get_img_dir(img_dir: Optional[str]) -> str:
        img_dir = fix_filepath(img_dir or os.getcwd())
        bucket_name = os.path.basename(img_dir)
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
        return img_dir