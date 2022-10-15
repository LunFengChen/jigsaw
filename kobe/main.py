from PIL import Image
import os
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

from config import Config


class ImageMerge(object):
    def __init__(self):
        self.pic_dic = None
        self.means = None
        self.codes = None
        self.result_picture = None
        self._init_image_adjust()

    def _init_image_adjust(self):
        # 1. 目标生成图片读取
        picture = Image.open(Config.mo_pic_path)
        width, height = picture.size
        to_width = Config.corp_size[0] * Config.num
        to_height = ((to_width / width) * height // Config.corp_size[1]) * Config.corp_size[1]
        # 2. 生成调整后的图片
        self.picture = picture.resize((int(to_width), int(to_height)), Image.ANTIALIAS)

    def get_jigsaw(self):
        self.codes, self.means, self.pic_dic = self.mapping_table(Config.sub_pic_path)
        self.result_picture = self.merge(self.picture)

        self._draw(self.picture, self.result_picture)

    def _draw(self, pic, pic_obj):
        plt.figure(figsize=(15, 15))  # 画板大小
        plt.subplot(1, 2, 1), plt.title('原图')
        plt.imshow(pic)
        plt.axis('off')
        plt.subplot(1, 2, 2), plt.title('拼图')
        plt.imshow(pic_obj)
        plt.axis('off')
        plt.show()  # 展示对比图

    def pic_code(self, image: np.ndarray):
        width, height = image.shape
        avg = image.mean()
        one_hot = np.array([1 if image[i, j] > avg else 0 for i in range(width) for j in range(height)])
        return one_hot

    def rgb_mean(self, rgb_pic):
        """
        if picture is RGB channel, calculate average [R, G, B].
        """
        r_mean = np.mean(rgb_pic[:, :, 0])
        g_mean = np.mean(rgb_pic[:, :, 1])
        b_mean = np.mean(rgb_pic[:, :, 2])
        val = np.array([r_mean, g_mean, b_mean])
        return val

    def mapping_table(self, pic_folder):
        suffix = ['jpg', 'jpeg', 'JPG', 'JPEG', 'gif', 'GIF', 'png', 'PNG']
        if not os.path.isdir(pic_folder):
            raise OSError('Folder [{}] is not exist, please check.'.format(pic_folder))

        pic_list = os.listdir(pic_folder)
        item_num = len(pic_list)
        means, codes, pic_dic = {}, {}, {}
        for idx, pic in tqdm(enumerate(pic_list), desc='CODE'):
            if pic.split('.')[-1] in suffix:
                path = os.path.join(pic_folder, pic)
                try:
                    img = Image.open(path).convert('RGB').resize(Config.corp_size, Image.ANTIALIAS)
                    codes[idx] = self.pic_code(np.array(img.convert('L').resize((8, 8), Image.ANTIALIAS)))
                    means[idx] = self.rgb_mean(np.array(img))
                    pic_dic[idx] = np.array(img)
                except OSError as e:
                    print(e)
        return codes, means, pic_dic

    def structure_similarity(self, section, candidate):
        section = Image.fromarray(section).convert('L')
        one_hot = self.pic_code(np.array(section.resize((8, 8), Image.ANTIALIAS)))
        candidate = [(key_, np.equal(one_hot, self.codes[key_]).mean()) for key_, _ in candidate]
        most_similar = max(candidate, key=lambda item: item[1])
        return self.pic_dic[most_similar[0]]

    def color_similarity(self, pic_slice, top_n=Config.filter_size):
        slice_mean = self.rgb_mean(pic_slice)
        diff_list = [(key_, np.linalg.norm(slice_mean - value_)) for key_, value_ in self.means.items()]
        filter_ = sorted(diff_list, key=lambda item: item[1])[:top_n]
        return filter_

    def merge(self, picture):
        width, height = picture.size
        w_times, h_times = int(width / Config.corp_size[0]), int(height / Config.corp_size[1])
        picture = np.array(picture)

        for i in tqdm(range(w_times), desc='MERGE'):
            for j in range(h_times):
                section = picture[j * Config.corp_size[1]:(j + 1) * Config.corp_size[1],
                          i * Config.corp_size[0]:(i + 1) * Config.corp_size[0], :]
                candidate = self.color_similarity(section)
                most_similar = self.structure_similarity(section, candidate)
                picture[j * Config.corp_size[1]:(j + 1) * Config.corp_size[1],
                i * Config.corp_size[0]:(i + 1) * Config.corp_size[0], :] = most_similar

        picture = Image.fromarray(picture)
        picture.save(Config.save_path)
        return picture


if __name__ == '__main__':
    ImageMerge().get_jigsaw()
