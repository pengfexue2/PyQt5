import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QApplication, QLineEdit, QPushButton, QGridLayout)
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import Qt, QRegExp

# QWidget是Cal的父类
class Calculator(QWidget):
    """
    计算器的基本页面的基本界面, 完成基本的计算
    """
    # __init__创建实例时传入的参数，参考链接 https://www.cnblogs.com/illusion1010/p/9527034.html
    def __init__(self):
        #super() 函数是用于调用父类(超类)的一个方法
        #参考链接 https://www.runoob.com/python/python-func-super.html
        super(Calculator, self).__init__()
        #这里先定义ui()函数，下面会具体定义
        self.ui()

        self.char_stack = []  # 操作符号的栈
        self.num_stack = []  # 操作数的栈
        self.nums = [chr(i) for i in range(48, 58)]  # 用于判断按钮的值是不是数字 chr(48)-chr(57)对应数字0-9
        self.operators = ['+', '-', '*', '/','x^y']  # 用于判断按钮的值是不是操作符

        self.empty_flag = True  # 这个flag的含义是来判断计算器是不是第一次启动，在显示屏幕中无数据
        self.after_operator = False  # 看了计算器的计算，比如1+2在输入+后，1还显示在屏幕上，输入了2之后，1就被替换了， 这个flag的作用就是这样的

        self.char_top = ''  # 保留栈顶的操作符号
        self.num_top = 0  # 保留栈顶的数值
        self.res = 0  # 保留计算结果，看计算器计算一次后，在继续按等号，还会重复最近一次的计算1+2,得到3之后，在按等号就是3+2， 以此类推.

        # >先计算, 为什么同样的符号改成了后计算, 是为了方便做一项操作,
        # 就是在你计算一个表达式之后，在继续按住等号, 以及会执行最后一次的符号运算
        self.priority_map = {
            '++': '>', '+-': '>', '-+': '>', '--': '>',
            '+*': '<', '+/': '<', '-*': '<', '-/': '<',
            '**': '>', '//': '>', '*+': '>', '/+': '>',
            '*-': '>', '/-': '>', '*/': '>', '/*': '>'
        }

    # 这个函数主要适用于初始化界面
    def ui(self):
        # QRegExp是Qt的正则表达式，此处禁用键盘，即把任意非空内容都过滤掉
        reg = QRegExp("^$")  # 把键盘禁用了, 仅可以按钮的输入
        validator = QRegExpValidator(reg, self)

        # 这个line_edit即计算器显示区，是一个文本编辑区
        self.line_edit = QLineEdit('0', self)
        self.line_edit.setAlignment(Qt.AlignRight)
        self.line_edit.setValidator(validator)
        # 将该区域设置为只读
        self.line_edit.setReadOnly(True)

        # 使用girdlayout进行界面布局
        grid = QGridLayout()
        self.setLayout(grid)
        # 计算器界面上各个按钮显示的名字
        btn_names = [
            'C', 'x^y', 'x^2', '/',
            '7', '8', '9', '*',
            '4', '5', '6', '-',
            '1', '2', '3', '+',
            '0', '', '.', '='
        ]
        # 先在界面上将定义好的显示区添加，设置尺寸
        grid.addWidget(self.line_edit, 0, 0, 1, 4)
        # i代表行数，j代表列数，将布局中的每个按键坐标位置和按键名称匹配
        positions = [(i, j) for i in range(1, 6) for j in range(4)]
        for pos, name in zip(positions, btn_names):
            if name == '':
                continue
            btn = QPushButton(name)
            # 在布局的时候，直接把每个按钮连接到点击事件上
            btn.clicked.connect(self.show_msg)
            if name == '0':
                tmp_pos = (pos[0], pos[1] + 1)
                grid.addWidget(btn, *pos, 1, 2)
            else:
                grid.addWidget(btn, *pos)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setWindowTitle('Calculator')
        # 设置计算器界面在桌面显示位置
        self.move(300, 150)
        self.show()

    def clear_line_edit(self):
        self.line_edit.clear()
        self.line_edit.setText('0')
        self.res = 0
        # 清空，就相当于刚打开计算器一样
        self.empty_flag = True

    def deal_num_btn(self, sender_text):
        # 这个after_operatpr就是判断是不是在输入了操作符号后，有输入数字
        # 比如 1+ 这时候在输入2， 这种情况, 这时候，应该把1清理掉，去显示2
        if self.after_operator:
            self.line_edit.clear()
            self.after_operator = False
        _str = self.line_edit.text()
        # 对line_edit是否有数据，有数据就继续往里面追加，没有就是重新开始
        if _str == '0' or _str == 'Error' or self.empty_flag:
            _str = ''
        self.line_edit.setText(_str + sender_text)
        # 加入了数据，empty_falg就改变了
        self.empty_flag = False

    def deal_operator_btn(self, sender_text):
        # 操作符号 +, -, *, /
        self.empty_flag = False
        _str = self.line_edit.text()

        # 比如刚打开计算器 你直接输入了一个 +
        if _str == '0' or _str == 'Error':
            # 就是需要上一次的计算结果, 需要把上一次的计算结果送入数字栈，操作符送入符号栈
            self.num_stack.append(self.res)
            self.char_stack.append(sender_text)
        else:
            # 在你输入操作符号之前，可能输入了数字或者一个操作符
            # 如果输入的是一个操作符那么，num_stack和char_stack的长度是一样的，可以来判断
            # 1++ 第二个加号并没有进入数字栈，所以可以看出, 他俩的长度是一样的
            self.num_top = float(_str) if _str.count('.') != 0 \
                else int(_str)
            self.num_stack.append(self.num_top)
            self.char_top = sender_text
            num_stack_len, char_stack_len = len(self.num_stack), len(self.char_stack)
            if (num_stack_len == char_stack_len) and num_stack_len != 0:
                # 在这里处理类似 输入 1+- 这种情况就是 1-后一个字符替换前面的
                self.char_stack[-1] = sender_text
            else:
                # 是正常的输入，1+2+此时，2入数字栈
                # 1+2*..... 类似输入
                if len(self.char_stack) == 0:
                    self.char_stack.append(self.char_top)
                else:
                    # 考虑符号的优先级, 1+2*这个时候只需要*入栈即可， 1*2+就要去计算1*2了
                    operator_cmp_key = self.char_stack[-1] + sender_text
                    if self.priority_map[operator_cmp_key] == '>':
                        print(self.num_stack, self.char_stack)
                        self.calculate(sender_text)
                    self.char_stack.append(sender_text)
                # 你输入一个操作符号, 那么接下里输入的时候，需要把前的line_edit 内容清空
                self.after_operator = True

    def deal_point_btn(self):
        _str = self.line_edit.text()
        self.empty_flag = False
        # 计算line_edit中有多少小数点
        point_count = self.line_edit.text().count('.')
        if point_count == 0:
            _str += '.'
        self.line_edit.setText(_str)

    def deal_square_btn(self):
        _str = self.line_edit.text()
        self.empty_flag = False
        square = int(_str)**2
        print(square)
        self.line_edit.setText(str(square))

    def deal_equal_btn(self):
        _str = self.line_edit.text()
        self.empty_flag = True
        try:
            # 在等号前 处理的数字 可能是上一次的计算结果，也可能是输入的数据的最后一个指，所以不能直接保存在num_top中， 考虑如果是上一次的计算结果是，直接保存在num_top会是什么结果
            tmp_num = float(_str) if _str.count('.') != 0 \
                else int(_str)
            self.num_stack.append(tmp_num)
            if len(self.num_stack) == 1:
                # 你刚做完一个计算， 结果还保留在屏幕上，这时候再按=，
                # 例如 1+2， 此时屏幕显示3，你再按=就是计算3+2， 再按就是5+2
                # 需要上一次的结果, 所以要在数字栈中加入num_top, 符号栈中加入char_top
                self.char_stack.append(self.char_top)
                self.num_stack.append(self.num_top)
            else:
                # line_edit的值不是上一次的计算结果，我们就把他保存在num_top中。
                self.num_top = tmp_num
        except Exception as e:
            # 可能出现异常的原因是 我忘了，可能抓不到异常，如果发现请告诉我
            self.num_stack.append(self.num_top)
            print('Error: {}'.format(e.args))
        self.calculate()
        self.num_stack.clear()
        self.char_stack.clear()

    def show_msg(self):
        # 看ui函数，每个按钮都连接了show_msg的点击事件
        sender = self.sender()
        sender_text = sender.text()
        # "C"键触发清零事件
        if sender_text == 'C':
            self.clear_line_edit()
        # 数字键触发输入数字事件
        elif sender_text in self.nums:
            self.deal_num_btn(sender_text)
        # 小数点键会触发小数点键
        elif sender_text == '.':
            self.deal_point_btn()
        # 运算符按钮会触发运算符事件
        elif sender_text in self.operators:
            self.deal_operator_btn(sender_text)
        # =会触发计算结果事件
        elif sender_text == '=':
            self.deal_equal_btn()
        elif sender_text == 'x^2':
            self.deal_square_btn()

    def auxiliary_calculate(self, first_num, second_num, operator: str):
        # 辅助计算
        if operator == '/':
            if second_num == 0:
                _str = 'Error'
                self.res = 0
                self.line_edit.setText(_str)
                return None
            else:
                return first_num / second_num
        elif operator == '*':
            return first_num * second_num
        elif operator == '+':
            return first_num + second_num
        elif operator == '-':
            return first_num - second_num
        elif operator =="x^y":
            return first_num ** second_num

    def calculate(self, operator='='):
        # 这里就很好理解了
        if operator == '=':
            # 要最后的结果
            print(self.num_stack)
            print(self.char_stack)
            error_falg = False
            while len(self.char_stack) >= 1:
                n1 = self.num_stack.pop()
                n2 = self.num_stack.pop()
                op = self.char_stack.pop()
                result = self.auxiliary_calculate(n2, n1, op)
                if result is None:
                    self.num_stack.clear()
                    self.char_stack.clear()
                    error_falg = True
                    break
                else:
                    self.num_stack.append(result)
            if not error_falg:
                self.res = self.num_stack.pop()
                if self.res == int(self.res):
                    self.res = int(self.res)
                self.line_edit.setText(str(self.res))
            else:
                self.line_edit.setText('Error')
        else:
            op = self.char_stack.pop()
            while len(self.char_stack) >= 0 and (self.priority_map[op + operator] == '>'):
                n1 = self.num_stack.pop()
                n2 = self.num_stack.pop()
                result = self.auxiliary_calculate(n2, n1, op)
                if result is None:
                    self.num_stack.clear()
                    self.char_stack.clear()
                    break
                self.num_stack.append(self.auxiliary_calculate(n2, n1, op))
                try:
                    op = self.char_stack.pop()
                except Exception as e:
                    break
            self.res = self.num_stack[-1]
            if self.res == int(self.res):
                self.res = int(self.res)
            self.line_edit.setText(str(self.res))

# 该代码实际要执行的命令
if __name__ == '__main__':
    # 所有的PyQt5应用必须创建一个应用（Application）对象。sys.argv参数是一个来自命令行的参数列表
    app = QApplication(sys.argv)
    # cal就是我们要建立的计算器，它是Calculator类的一个实例
    cal = Calculator()
    # 计算器退出相关的
    sys.exit(app.exec_())






