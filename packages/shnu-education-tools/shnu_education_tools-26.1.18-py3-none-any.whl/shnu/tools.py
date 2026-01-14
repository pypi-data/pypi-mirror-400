import os, datetime
from pathlib import Path
from shutil import copyfile
from functools import reduce
import pandas as pd

class Assistant:

    def __init__(self,name_list='人工智能.xlsx',
                 homework_dir ='./期末试卷',
                 sorted=False,
                 sorted_homework_dir=None):
        '''

        :param name_list: 教务处导出的学生名单
        :param homework_dir: 学生提交作业的跟目录。该目录下有 n个子目录，每个子目录名对应提交作业的时间
        :param sorted: 将学生的作业安装学号分拣出来，排序到另一个目录
        :param sorted_homework_dir: 学生作业排序输出根目录
        '''
        self.homework_dir = homework_dir
        self.name_list = name_list
        self.sorted = sorted
        self.sorted_homework_dir= sorted_homework_dir
    def get_name_list(self):
        return self.name_list
    def get_homework_dir(self):
        return self.homework_dir
    def get_sorted(self):
        return self.sorted
    def get_sorted_homework_dir(self):
        return self.sorted_homework_dir


    @staticmethod
    def directory_to_str(directory_path, sep='\n'):
        '''

        :param directory_path: 目录名
        :param sep: 分隔符
        :return: 字符串，内容为子目录下面的所有子目录和文件
        '''
        directory = Path(directory_path)
        print(f'Please wait for browsing {directory_path}..... ')
        # 获取目录下的所有子目录和文件（包括子目录的子目录）
        all_items = map(str, list(directory.rglob('*')))
        return sep.join(all_items)

    @staticmethod
    def find_student_files(homework_dir):
        '''

        :param homework_dir: 学生提交作业目录
        :return: 返回学生作业文件
        '''
        # 创建 Path 对象
        homework_dir = Path(homework_dir)
        # 使用 rglob() 方法获取所有符合条件的文件路径
        student_files = list(homework_dir.rglob('*.*'))  # *.rar
        # 返回结果
        return list(student_files)
    def homework_check(self):
        '''

        :return:返回3个DataFrame；0：统计学生作业的Dataframe:
                                1：作业提交次数为零的Dataframe:
                                2：作业次数大于0的DataFrame
        '''
        name_list = self.get_name_list()
        homework_dir = self.get_homework_dir()

        output_file = Path(name_list).stem + '-' + Path(homework_dir).stem + f'-{datetime.date.today()}.xlsx'
        # 注意：从教务导出的文件并不是Excel文件（其实是Html文件，Python解析会出错），需要使用Excel文件打开，将其存储为.xlsx 格式
        df = pd.read_excel(name_list, header=[1], skiprows=[0])
        # 上师大特有格式
        df['学号'] = df['学号'].astype(str).str.strip()
        df['姓名'] = df['姓名'].str.strip()
        self.data = df[['学号', '姓名', '行政班']]
        homework_dict = {i.name: Assistant.directory_to_str(i) for i in Path(homework_dir).iterdir() if i.is_dir()}
        # 检查作业 超一流精简代码
        for i in homework_dict:
            self.data[i] = self.data['姓名'].apply(lambda x: x.strip() in homework_dict[i])
        self.data['提交次数'] = reduce(lambda x, y: x + self.data[y], homework_dict.keys(), 0)
        self.data['提交率(%)'] = self.data['提交次数'] / len(homework_dict) * 100

        if self.sorted:
            if self.get_sorted_homework_dir() is None:
               self.sorted_homework_dir = self.get_homework_dir() + '_排序'
            self.data['学号-姓名'] = self.data.index.map(lambda x: Path(
                self.sorted_homework_dir) / f"{x + 1:02d}-{(df['学号'].str.strip() + '-' + df['姓名'].str.strip())[x]}")

            self.data['学号-姓名'].apply(lambda x: Path(x).mkdir(parents=True, exist_ok=True))

            dd = self.data.set_index('学号')['学号-姓名'].to_dict()

            student_files_list = Assistant.find_student_files(homework_dir)

            for file_path in student_files_list:
             for key, value in dd.items():
                if key in str(file_path):
                    copyfile(file_path, value / file_path.name)
            #print(f'文件分拣完毕得到{output_file}文件！！')
        # 作业记录到Excel 文件中
            self.data.drop(columns=['学号-姓名'], inplace=True)
        #self.data.to_excel(output_file, index=None)
        Assistant.result=self.data
        self.data0 = self.data[self.data['提交次数']==0]
        self.data1 = self.data[self.data['提交次数']>0]
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            self.data.to_excel(writer, sheet_name='交作业全部信息', index=False)
            self.data0.to_excel(writer, sheet_name='未交作业-同学', index=False)
            self.data1.to_excel(writer, sheet_name='交过作业-同学', index=False)
        os.startfile(output_file)
        return self.data,self.data0,self.data1

def work(ini_file='shnu.ini'):
        import configparser
        # 创建一个ConfigParser对象
        config = configparser.ConfigParser()
        try:
            # 读取INI文件
            config.read(ini_file,encoding='utf-8')  # 替换为你的INI文件路径
            # 获取配置项的值
            name_list = config.get('shnu','name_list').strip().replace('\n', '')
            homework_dir = config.get('shnu','homework_dir').strip().replace('\n', '')
            #sorted=eval(config.get('shnu','sorted').strip().replace('\n', ''))
            sorted_homework_dir = config.get('shnu','sorted_homework_dir').strip().replace('\n', '')
            ast = Assistant(name_list=name_list,homework_dir=homework_dir,sorted=True, sorted_homework_dir=sorted_homework_dir)
            result = ast.homework_check()
            print('*'*33)
            print(result[0])
            print('*' * 33)
            print(result[1])
            print('*' * 33)
            print(result[2])
        except:
            contents='''[shnu]
            name_list=人工智能.xlsx
            homework_dir =./期末试卷
            sorted_homework_dir=./期末试卷-ok
            '''
            open('shnu.ini','w',encoding='utf-8').write(contents)
            os.startfile('shnu.ini')

if __name__ == '__main__':
    work()



