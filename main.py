import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re

# Определяем типы токенов
TOKEN_TYPES = [
    ('FLOAT', r'\d+(\.\d+)?([eE][+-]?\d+)?(?<![eE][eE])'),  # Числа с плавающей точкой
    ('IDEN', r'([A-Za-z_][A-Za-z0-9_]*)'),  # Идентификаторы
    ('ASSIGN', r':='),  # Знак присваивания
    ('ADD', r'\+'),  # Оператор сложения
    ('SUB', r'-'),  # Оператор вычитания
    ('MUL', r'\*'),  # Оператор умножения
    ('DIV', r'/'),  # Оператор деления
    ('LPAREN', r'\('),  # Левая круглая скобка
    ('RPAREN', r'\)'),  # Правая круглая скобка
    ('SEMICOLON', r';'),  # Точка с запятой
    ('WHITESPACE', r'\s+'),  # Пробелы (игнорируем)
    ('DOTDOT', r'\.\.'),  # Две точки подряд (ошибка)
]

# Объединяем регулярные выражения в одно
TOKEN_REGEX = '|'.join(f'(?P<{token_type}>{pattern})' for token_type, pattern in TOKEN_TYPES)
token_regex = re.compile(TOKEN_REGEX)


class SyntaxAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Оптимизация Бухтияров_М_А ИС-42")

        # Поля ввода
        self.text_input = tk.Text(root, height=30, width=50)
        self.text_input.grid(row=0, column=0, sticky="nswe", padx=(0, 5))

        # Кнопки для управления
        self.button_frame = tk.Frame(root)
        self.button_frame.grid(row=1, column=0, padx=10, pady=5)

        self.load_button = tk.Button(self.button_frame, text="Загрузить файл", command=self.load_from_file)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.analyze_button = tk.Button(self.button_frame, text="Анализировать", command=self.analyze)
        self.analyze_button.pack(side=tk.LEFT, padx=5)

        # Таблица токенов
        self.token_tree = ttk.Treeview(root, columns=("No", "Тип", "Значение"), show="headings")
        self.token_tree.heading("No", text="№")
        self.token_tree.heading("Тип", text="Тип")
        self.token_tree.heading("Значение", text="Значение")
        self.token_tree.grid(row=0, column=1, padx=5, sticky="nswe")

        # Дерево синтаксического анализа
        self.parse_tree = ttk.Treeview(root)
        self.parse_tree.heading("#0", text="Синтаксическое дерево")
        self.parse_tree.grid(row=0, column=2, padx=10, sticky="nswe")

        # Настройка стиля
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)

    def load_from_file(self):
        """Загрузка текста из файла."""
        file_path = filedialog.askopenfilename(
            title="Выберите текстовый файл",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    self.text_input.delete(1.0, tk.END)
                    self.text_input.insert(tk.END, content)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")

    def analyze(self):
        """Запуск анализа."""
        input_text = self.text_input.get("1.0", tk.END).strip()
        if not input_text:
            messagebox.showerror("Ошибка", "Пустой ввод")
            return

        try:
            # Лексический анализ
            tokens = self.lexer(input_text)
            if not tokens:
                return
            self.display_tokens(tokens)

            # Синтаксический анализ
            analyzer = SyntaxAnalyzer()
            parse_tree = analyzer.parse(tokens)
            self.display_parse_tree(parse_tree)

            # Вызов окна для отображения триад
            self.show_triads_window(parse_tree)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка анализа: {e}")

    def lexer(self, text):
        """Лексический анализатор."""
        tokens = []
        for match in token_regex.finditer(text):
            token_type = match.lastgroup
            token_value = match.group(token_type)

            if token_type == "WHITESPACE":
                continue  # Пропускаем пробелы

            if token_type == "DOTDOT":
                messagebox.showerror("Ошибка", "Две точки подряд ('..') недопустимы.")
                return []

            tokens.append((token_type, token_value))

        return tokens

    def display_tokens(self, tokens):
        self.token_tree.delete(*self.token_tree.get_children())
        for idx, (token_type, token_value) in enumerate(tokens, start=1):
            self.token_tree.insert("", "end", values=(idx, token_type, token_value))

    def display_parse_tree(self, tree, parent=""):
        """Отображение дерева синтаксического анализа."""
        self.parse_tree.delete(*self.parse_tree.get_children())

        def add_node(node, parent):
            if isinstance(node, tuple):
                label = node[0]
                item = self.parse_tree.insert(parent, "end", text=label)
                for child in node[1:]:
                    add_node(child, item)
            else:
                self.parse_tree.insert(parent, "end", text=str(node))

        for expr in tree:
            add_node(expr, parent)

    def show_triads_window(self, parse_tree):
        """Отображение окна с триадами в текстовом виде."""
        triad_window = tk.Toplevel(self.root)
        triad_window.title("Триады")

        tk.Label(triad_window, text="Изначальные триады").pack(pady=5)
        initial_text = tk.Text(triad_window, height=10, width=60)
        initial_text.pack(padx=10, pady=5)

        tk.Label(triad_window, text="Оптимизированные триады").pack(pady=5)
        optimized_text = tk.Text(triad_window, height=10, width=60)
        optimized_text.pack(padx=10, pady=5)

        # Генерация триад
        analyzer = SyntaxAnalyzer()
        initial_triads = analyzer.build_triads(parse_tree)
        optimized_triads = analyzer.optimize_triads(initial_triads)

        # Отображение триад
        self._fill_triads_text(initial_text, initial_triads)
        self._fill_triads_text(optimized_text, optimized_triads)

        triad_window.geometry("700x600")

    def _fill_triads_text(self, text_widget, triads):
        text_widget.delete("1.0", tk.END)
        for idx, triad in enumerate(triads, start=1):
            if len(triad) == 4:  # Проверяем, что триада корректная
                result, operator, arg1, arg2 = triad
                text_widget.insert(tk.END, f"{idx}. {operator} ({arg1}, {arg2})\n")
            else:
                idx = idx - 1


class SyntaxAnalyzer:
    def __init__(self):
        self.tokens = []
        self.current = 0

    def parse(self, tokens):
        self.tokens = tokens
        self.current = 0
        expressions = []
        while not self._at_end():
            expressions.append(self._S())
            if not self._at_end() and self.tokens[self.current][0] == "SEMICOLON":
                self.current += 1  # Просто пропускаем точку с запятой, не добавляя её в дерево
        return expressions

    def _S(self):
        if self._at_end():
            raise Exception("Ошибка ввода")

        if self.tokens[self.current][0] == "IDEN":
            iden = self.tokens[self.current][1]
            self.current += 1
            if not self._at_end() and self.tokens[self.current][0] == "ASSIGN":
                self.current += 1
                expr = self._E()
                return ("<S>", iden, ":=", expr)

            expr = self._E()
            return ("<S>", iden, expr)

        expr = self._E()
        return ("<S>", expr)

    def _E(self):
        left = self._T()
        while not self._at_end() and self.tokens[self.current][0] in {"ADD", "SUB"}:
            op = self.tokens[self.current][1]
            self.current += 1

            # Проверяем, что после оператора идет валидный фактор
            if self._at_end() or self.tokens[self.current][0] not in {"IDEN", "FLOAT", "LPAREN"}:
                raise Exception(
                    f"Ожидалось значение после оператора '{op}', но найдено '{self.tokens[self.current][1]}'")

            right = self._F()
            left = ("<E>", left, op, right)
        return left

    def _T(self):
        left = self._F()
        while not self._at_end() and self.tokens[self.current][0] in {"MUL", "DIV"}:
            op = self.tokens[self.current][1]
            self.current += 1

            if self._at_end() or self.tokens[self.current][0] not in {"IDEN", "FLOAT", "LPAREN"}:
                raise Exception(
                    f"Ожидалось значение после оператора '{op}', но найдено '{self.tokens[self.current][1]}'")
            right = self._F()
            left = ("<E>", left, op, right)
        return left

    def _F(self):
        if self._at_end():
            raise Exception("Ошибка ввода: выражение неожиданно закончилось")

        if self.tokens[self.current][0] == "LPAREN":
            self.current += 1
            if self._at_end():
                raise Exception("Ошибка: Ожидалось выражение после открывающей скобки")

            expr = self._E()

            if not self._at_end() and self.tokens[self.current][0] == "RPAREN":
                self.current += 1
                return ("<E>", "(", expr, ")")
            else:
                raise Exception("Ошибка: Ожидалась закрывающая скобка")

        elif self.tokens[self.current][0] in {"IDEN", "FLOAT"}:
            value = self.tokens[self.current][1]
            self.current += 1
            return ("<E>", value)

        # Если токен не распознан, бросаем исключение
        raise Exception(f"Ошибка: Нет открывающей скобки")

    def _at_end(self):
        return self.current >= len(self.tokens)

    def build_triads(self, parse_tree):
        triads = []
        temp_count = 1

        def process_node(node):
            nonlocal temp_count
            if isinstance(node, tuple):
                if len(node) == 4 and node[1] == "(" and node[3] == ")":
                    # Убираем скобки
                    return process_node(node[2])
                elif len(node) == 4:  # Бинарная операция
                    left = process_node(node[1])
                    operator = node[2]
                    right = process_node(node[3])
                    temp_result = f"^{temp_count}"
                    temp_count += 1
                    triads.append((temp_result, operator, left, right))
                    return temp_result
                elif len(node) == 3:  # Пропускаем `<S>` с тремя элементами
                    return process_node(node[2])
                elif len(node) == 2:  # Унарная операция
                    return process_node(node[1])
            elif isinstance(node, str):  # Литералы или идентификаторы
                return node
            return None

        # Обрабатываем каждый узел дерева
        for subtree in parse_tree:
            process_node(subtree)

        return triads

    def optimize_triads(self, triads):
        optimized = []
        while True:  # Будем повторять, пока не останется новых повторений
            new_optimized = []
            expression_map = {}  # Карта для отслеживания уже вычисленных выражений
            triad_references = {}  # Карта для замены ссылок на уникальные триады
            updated = False  # Флаг для отслеживания изменений

            # Первый проход: собираем выражения, применяем свертку и заменяем их ссылки
            for triad in triads:
                if len(triad) == 4:
                    temp_result, operator, left, right = triad

                    # Метод свертки: упрощение выражений
                    if operator in {"+", "-", "*", "/"}:
                        # Преобразования для констант
                        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                            # Если оба операнда - константы, вычисляем результат
                            if operator == "+":
                                folded_value = left + right
                            elif operator == "-":
                                folded_value = left - right
                            elif operator == "*":
                                folded_value = left * right
                            elif operator == "/":
                                folded_value = left / right if right != 0 else None  # Защита от деления на 0

                            if folded_value is not None:
                                # Заменяем триаду на результат вычисления
                                triad = (temp_result, "CONST", folded_value, None)
                                updated = True

                        # Преобразования для упрощения выражений
                        elif operator == "*" and (left == 1 or right == 1):
                            triad = (temp_result, "ASSIGN", left if right == 1 else right, None)
                            updated = True
                        elif operator == "*" and (left == 0 or right == 0):
                            triad = (temp_result, "CONST", 0, None)
                            updated = True
                        elif operator == "+" and (left == 0 or right == 0):
                            triad = (temp_result, "ASSIGN", left if right == 0 else right, None)
                            updated = True
                        elif operator == "-" and right == 0:
                            triad = (temp_result, "ASSIGN", left, None)
                            updated = True
                        elif operator == "/" and right == 1:
                            triad = (temp_result, "ASSIGN", left, None)
                            updated = True

                    # Проверяем, есть ли выражение в карте
                    expression_key = (operator, left, right)
                    if expression_key in expression_map:
                        # Если выражение уже встречено, заменяем ссылку на первую триаду
                        previous_result = expression_map[expression_key]
                        triad_references[temp_result] = previous_result  # Указываем, что эта триада дублируется
                        updated = True  # Отмечаем, что произошло изменение
                    else:
                        # Если выражение уникально, добавляем его в оптимизированный список
                        new_optimized.append(triad)
                        expression_map[expression_key] = temp_result  # Запоминаем результат этого выражения
                        triad_references[temp_result] = temp_result  # Указываем, что это оригинальная триада

                else:
                    # Если это не выражение с оператором, просто добавляем
                    new_optimized.append(triad)

            # Второй проход: заменяем ссылки на актуальные триады
            for i in range(len(new_optimized)):
                new_triad = []
                for element in new_optimized[i]:
                    # Если элемент является ссылкой на триаду, заменяем на оригинальную
                    if element in triad_references:
                        original_reference = triad_references[element]
                        if element != original_reference:
                            updated = True  # Отмечаем изменение, если ссылка была обновлена
                        new_triad.append(original_reference)
                    else:
                        new_triad.append(element)
                new_optimized[i] = tuple(new_triad)  # Обновляем триаду с замененными ссылками

            if not updated:
                # Если на этом этапе нет изменений, выходим из цикла
                break
            triads = new_optimized  # Продолжаем оптимизацию с обновленным списком триад

        return new_optimized


if __name__ == "__main__":
    root = tk.Tk()
    app = SyntaxAnalyzerApp(root)
    root.mainloop()
