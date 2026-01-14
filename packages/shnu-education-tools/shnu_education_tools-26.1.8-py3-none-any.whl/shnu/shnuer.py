import pandas as pd
from functools import reduce
from pathlib import Path
import datetime
import configparser
import sys


# ======================
# 1. 配置管理
# ======================
class ConfigManager:
    def __init__(self, config_path="config.ini"):
        self.config_path = Path(config_path)
        self.config = configparser.ConfigParser()

    def load(self):
        if not self.config_path.exists():
            self._create_sample()
            print(f"⚠️ 未找到配置文件，已生成示例：{self.config_path.resolve()}")
            print("👉 请修改 config.ini 后重新运行程序")
            sys.exit(0)

        self.config.read(self.config_path, encoding="utf-8")

        try:
            self.names_xlsx = self.config["paths"]["names_xlsx"]
            self.homework_dir = self.config["paths"]["homework_dir"]
        except KeyError as e:
            raise KeyError(f"config.ini 中缺少必要配置项：{e}")

        return self

    def _create_sample(self):
        self.config["paths"] = {
            "names_xlsx": "2024数学类（周二上午）.xlsx",
            "homework_dir": "平时成绩",
        }
        with open(self.config_path, "w", encoding="utf-8") as f:
            self.config.write(f)
            os.startfile('config.ini')


# ======================
# 2. 作业扫描
# ======================
class HomeworkScanner:
    def __init__(self, homework_dir):
        self.root = Path(homework_dir)

        if not self.root.exists():
            raise FileNotFoundError(f"作业目录不存在：{self.root.resolve()}")

    def scan(self):
        homeworks = [p for p in self.root.iterdir() if p.is_dir()]
        dicts = map(self._dir_to_string, homeworks)
        return {k.name: v for d in dicts for k, v in d.items()}

    def _dir_to_string(self, root, level=0):
        """
        将目录结构映射为 {root_path: 目录结构字符串}
        """
        root = Path(root)
        lines = []
        indent = "    " * level
        lines.append(f"{indent}{root.name}/")

        for item in sorted(root.iterdir(), key=lambda x: (x.is_file(), x.name)):
            if item.is_dir():
                sub_dict = self._dir_to_string(item, level + 1)
                lines.append(sub_dict[item])
            else:
                lines.append(f"{'    ' * (level + 1)}{item.name}")

        return {root: "\n".join(lines)}


# ======================
# 3. 成绩计算
# ======================
class ScoreCalculator:
    def __init__(self, names_xlsx, homeworks_dict):
        self.names_xlsx = Path(names_xlsx)
        self.homeworks_dict = homeworks_dict

        if not self.names_xlsx.exists():
            raise FileNotFoundError(f"学生名单不存在：{self.names_xlsx.resolve()}")

    def load_students(self):
        df = pd.read_excel(
            self.names_xlsx,
            header=[1],
            skiprows=[0]  # 上师大特有格式
        )

        data = df[['学号', '姓名', '行政班']].copy()
        data['学号'] = data['学号'].astype(str).str.strip()
        data['姓名'] = data['姓名'].str.strip()

        self.data = data
        return self

    def calculate(self):
        # 每次作业是否提交
        for k, v in self.homeworks_dict.items():
            self.data[k] = self.data['学号'].apply(lambda x: x in v)

        # 提交次数
        self.data['交作业次数'] = reduce(
            lambda x, y: x + self.data[y],
            self.homeworks_dict.keys(),
            0
        )

        # 提交率
        self.data['提交率(%)'] = round(
            self.data['交作业次数'] / len(self.homeworks_dict),
            2
        )

        # 平时成绩
        self.data['平时成绩'] = self.data['提交率(%)'].apply(
            lambda x: round(min(x, 1), 2) * 100
        )

        return self

    def export(self):
        output_file = self.names_xlsx.with_name(
            f"{self.names_xlsx.stem}-平时成绩-{datetime.date.today()}.xlsx"
        )
        self.data.to_excel(output_file, index=False)
        print(f"✅ 平时成绩已生成：{output_file.resolve()}")


# ======================
# 4. 主程序
# ======================
def main():
    # 1. 读取配置
    config = ConfigManager().load()

    # 2. 扫描作业
    scanner = HomeworkScanner(config.homework_dir)
    homeworks_dict = scanner.scan()

    # 3. 计算成绩
    calculator = (
        ScoreCalculator(config.names_xlsx, homeworks_dict)
        .load_students()
        .calculate()
    )
    calculator.export()


if __name__ == "__main__":
    main()
