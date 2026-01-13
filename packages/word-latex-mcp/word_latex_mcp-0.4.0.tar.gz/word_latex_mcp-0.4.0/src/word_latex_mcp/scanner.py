"""
LaTeX 片段识别与定位模块
"""

import re
from typing import Iterator, Optional
from .models import LatexMatch, Region, BODY_REGIONS, ALL_REGIONS


class LatexPreProcessor:
    """Word 文本预处理器"""
    
    # Word 特殊字符映射
    CHAR_REPLACEMENTS = {
        '\r': '\n',         # 回车 -> 换行
        '\x0b': '\n',       # 垂直制表符（软回车）-> 换行
        '\x0c': '',         # 分页符 -> 移除
        '\x07': '',         # 表格单元格结束标记 -> 移除
        '\xa0': ' ',        # 不间断空格 -> 普通空格
        '\u2028': '\n',     # 行分隔符 -> 换行
        '\u2029': '\n',     # 段落分隔符 -> 换行
        '\u200b': '',       # 零宽空格 -> 移除
        '\u200c': '',       # 零宽非连接符 -> 移除
        '\u200d': '',       # 零宽连接符 -> 移除
        '\ufeff': '',       # BOM -> 移除
        # 智能引号
        '"': '"',           # 左双引号
        '"': '"',           # 右双引号
        ''': "'",           # 左单引号
        ''': "'",           # 右单引号
        '–': '-',           # En dash
        '—': '-',           # Em dash
        '…': '...',         # 省略号
    }
    
    @classmethod
    def preprocess(cls, text: str) -> str:
        """
        预处理 Word 文本，标准化特殊字符
        
        Args:
            text: 原始文本
            
        Returns:
            str: 标准化后的文本
        """
        result = text
        for old, new in cls.CHAR_REPLACEMENTS.items():
            result = result.replace(old, new)
        return result
    
    @classmethod
    def get_original_positions(cls, original: str, processed: str) -> dict[int, int]:
        """
        计算处理后位置到原始位置的映射
        
        这是为了在预处理后仍能定位到原文档中的正确位置
        """
        # 简单实现：假设字符一一对应（对于我们的替换规则基本成立）
        # 如果需要更精确的映射，可以扩展此方法
        return {}


class LatexScanner:
    """LaTeX 公式扫描器 - 增强版 v0.4.0"""

    # ========== 核心 LaTeX 命令特征（用于识别无分隔符公式） ==========
    # 常见 LaTeX 数学命令
    LATEX_COMMANDS = [
        # 分数、根号
        r'\\frac', r'\\dfrac', r'\\tfrac', r'\\sqrt', r'\\root',
        # 积分、求和、极限、乘积
        r'\\int', r'\\oint', r'\\iint', r'\\iiint', r'\\sum', r'\\prod',
        r'\\lim', r'\\limsup', r'\\liminf',
        # 矩阵环境
        r'\\begin\{[a-z]*matrix\}', r'\\begin\{array\}', r'\\begin\{cases\}',
        r'\\begin\{align', r'\\begin\{equation', r'\\begin\{gather',
        # 上下标带花括号（明确的数学表达式）
        r'[a-zA-Z]_\{[^}]+\}', r'[a-zA-Z]\^\{[^}]+\}',
        # 希腊字母
        r'\\alpha', r'\\beta', r'\\gamma', r'\\delta', r'\\epsilon',
        r'\\theta', r'\\lambda', r'\\mu', r'\\pi', r'\\sigma', r'\\omega',
        r'\\Gamma', r'\\Delta', r'\\Theta', r'\\Lambda', r'\\Sigma', r'\\Omega',
        # 数学运算符
        r'\\cdot', r'\\times', r'\\div', r'\\pm', r'\\mp',
        r'\\leq', r'\\geq', r'\\neq', r'\\approx', r'\\equiv',
        r'\\subset', r'\\supset', r'\\in', r'\\notin',
        # 箭头
        r'\\to', r'\\rightarrow', r'\\leftarrow', r'\\Rightarrow', r'\\Leftarrow',
        # 数学字体
        r'\\mathbf', r'\\mathit', r'\\mathrm', r'\\mathcal', r'\\mathbb',
        r'\\vec', r'\\hat', r'\\bar', r'\\tilde', r'\\dot',
        # 括号
        r'\\left[(\[{|]', r'\\right[)\]}|]',
        # 函数
        r'\\sin', r'\\cos', r'\\tan', r'\\log', r'\\ln', r'\\exp',
        # 其他常用
        r'\\partial', r'\\nabla', r'\\infty', r'\\forall', r'\\exists',
    ]

    # 用于检测文本是否包含 LaTeX 命令的正则
    LATEX_COMMAND_PATTERN = re.compile('|'.join(LATEX_COMMANDS))

    # ========== 标准分隔符模式 ==========
    # 预编译正则表达式 - 升级版
    # 策略：同时匹配转义字符和LaTeX模式
    # 1. escaped: 匹配 \\. (消耗掉转义符和被转义的字符，如 \$ 或 \\)
    # 2. display: 匹配 $$...$$
    # 3. inline: 匹配 $...$

    LATEX_PATTERN_MULTILINE = re.compile(
        r'(?P<escaped>\\.)|'
        r'(?P<display>\$\$(?P<d_content>.*?)\$\$)|'
        r'(?P<inline>\$(?P<i_content>.*?)\$)',
        re.DOTALL
    )

    # 单行模式（不允许行内公式跨行）
    LATEX_PATTERN_SINGLELINE = re.compile(
        r'(?P<escaped>\\.)|'
        r'(?P<display>\$\$(?P<d_content>.*?)\$\$)|'
        r'(?P<inline>\$(?P<i_content>[^\n\r\x0b]*?)\$)',
        re.DOTALL
    )

    # ========== 扩展格式模式 ==========
    # LaTeX 标准定界符: \[...\] 显示公式
    LATEX_BRACKET_DISPLAY = re.compile(
        r'\\\[(?P<content>[\s\S]*?)\\\]'
    )

    # LaTeX 标准定界符: \(...\) 行内公式
    LATEX_PAREN_INLINE = re.compile(
        r'\\\((?P<content>[\s\S]*?)\\\)'
    )

    # Markdown 代码块: ```latex ... ``` 或更宽松的变体
    MARKDOWN_LATEX_BLOCK = re.compile(
        r'```latex\s*\n?(?P<content>[\s\S]*?)```',
        re.IGNORECASE
    )

    # 纯 latex 标签块：行首 "latex" 后跟公式行（常见于 Word/Markdown 转换）
    # 格式：独立行 "latex" 后面跟着以 LaTeX 命令或数学表达式开头的行
    PLAIN_LATEX_TAG = re.compile(
        r'^[ \t]*latex[ \t]*$',
        re.MULTILINE | re.IGNORECASE
    )

    # 行独立 LaTeX：整行都是 LaTeX 公式
    # 支持多种开头模式：
    # - 以圆括号开头: (a + b)^n = ...
    # - 以字母+下标开头: x_{n} = ...
    # - 以函数形式开头: f(x) = ..., f'(x_0) = ...
    # - 以 LaTeX 命令开头: \frac{...}, \int_{...}
    # - 以大写字母开头的方程: E(X) = ..., S^2 = ...
    STANDALONE_LATEX_LINE = re.compile(
        r'^[ \t]*(?P<content>'
        r'(?:\([a-zA-Z]|'                  # (a + b) 开头
        r'[a-zA-Z]\'?\s*\(|'               # f(x), f'(x) 开头
        r'[a-zA-Z]_\{|'                    # x_{n} 开头
        r'[a-zA-Z]\^[{0-9]|'               # x^2, x^{n} 开头
        r'[A-Z]\s*\(|'                     # E(X), S(x) 开头
        r'\\[a-zA-Z]+)'                    # \frac, \int 等 LaTeX 命令开头
        r'[^\n]*'                           # 后续内容
        r')[ \t]*$',
        re.MULTILINE
    )

    # 金额模式：$后面紧跟数字（可能有小数点和逗号）
    MONEY_PATTERN = re.compile(r'^[\d,]+\.?\d*$')

    # ========== 伪公式模式（应跳过） ==========
    # 扩展金额模式：包含货币符号、百分比等
    EXTENDED_MONEY_PATTERNS = [
        re.compile(r'^[\d,]+\.?\d*%?$'),           # 数字或百分比
        re.compile(r'^[A-Z]{2,3}\s*[\d,]+\.?\d*$'), # 货币代码 + 数字 (USD 100)
        re.compile(r'^[\d,]+\.?\d*\s*[A-Z]{2,3}$'), # 数字 + 货币代码 (100 USD)
    ]

    # 代码/路径变量模式（仅匹配明显的代码变量，不匹配短变量）
    CODE_VAR_PATTERNS = [
        re.compile(r'^[A-Z_][A-Z0-9_]{2,}$'),     # 全大写变量 3+ 字符 (PATH, HOME)
        re.compile(r'^[a-z_][a-z0-9_]{3,}$'),     # 全小写变量 4+ 字符 (name, variable)
        re.compile(r'^\w+\.\w+$'),                 # 文件名 (file.txt)
        re.compile(r'^/[\w/]+$'),                  # Unix 路径
        re.compile(r'^[a-zA-Z]:\\[\w\\]+$'),       # Windows 路径
    ]

    # ========== LaTeX 环境模式 ==========
    # 显示公式环境（带编号和不带编号）
    # 支持: equation, equation*, align, align*, gather, gather*,
    #       multline, multline*, displaymath, eqnarray, eqnarray*
    LATEX_DISPLAY_ENVS = re.compile(
        r'\\begin\{(?P<env>equation|align|gather|multline|displaymath|eqnarray)\*?\}'
        r'(?P<content>[\s\S]*?)'
        r'\\end\{(?P=env)\*?\}',
        re.IGNORECASE
    )

    # 行内公式环境: \begin{math}...\end{math}
    LATEX_INLINE_ENV = re.compile(
        r'\\begin\{math\}(?P<content>[\s\S]*?)\\end\{math\}',
        re.IGNORECASE
    )

    # ```math 代码块（GitHub 风格）
    MARKDOWN_MATH_BLOCK = re.compile(
        r'```math\s*\n?(?P<content>[\s\S]*?)```',
        re.IGNORECASE
    )

    # 子方程组环境: \begin{subequations}...\end{subequations}
    LATEX_SUBEQUATIONS = re.compile(
        r'\\begin\{subequations\}(?P<content>[\s\S]*?)\\end\{subequations\}',
        re.IGNORECASE
    )
    
    def __init__(
        self,
        skip_money_patterns: bool = True,
        policy_manager: Optional["PolicyManager"] = None,
        enable_extended_formats: bool = True
    ):
        r"""
        初始化扫描器

        Args:
            skip_money_patterns: 是否跳过疑似金额的模式如 $100$
            policy_manager: 策略管理器（可选）
            enable_extended_formats: 是否启用扩展格式识别（```latex, \\[...\\], 行独立等）
        """
        self.skip_money_patterns = skip_money_patterns
        self.policy_manager = policy_manager
        self.enable_extended_formats = enable_extended_formats

        # 根据配置选择正则
        if policy_manager and not policy_manager.config.allow_multiline_inline:
            self.latex_pattern = self.LATEX_PATTERN_SINGLELINE
        else:
            self.latex_pattern = self.LATEX_PATTERN_MULTILINE
    
    def _is_money_pattern(self, latex_code: str) -> bool:
        """判断是否为金额模式"""
        if not self.skip_money_patterns:
            return False
        return bool(self.MONEY_PATTERN.match(latex_code.strip()))

    def _is_pseudo_formula(self, latex_code: str) -> bool:
        """
        判断是否为伪公式（应跳过的非数学内容）

        检测类型:
        - 代码变量和路径（仅当不含 LaTeX 命令时）

        注意：金额检测由 _is_money_pattern 负责，受 skip_money_patterns 控制
        """
        content = latex_code.strip()

        # 空内容
        if not content:
            return True

        # 代码变量模式（仅当不包含 LaTeX 命令且无数学符号时）
        if not self._contains_latex_commands(content):
            # 检查是否有明确的数学符号（如 ^, _, =, +, - 等）
            has_math_symbols = any(c in content for c in '^_=+*/\\{}[]')
            if not has_math_symbols:
                for pattern in self.CODE_VAR_PATTERNS:
                    if pattern.match(content):
                        return True

        return False
    
    def _extract_context(self, text: str, start: int, end: int, context_len: int = 20) -> str:
        """提取上下文摘要"""
        ctx_start = max(0, start - context_len)
        ctx_end = min(len(text), end + context_len)
        
        prefix = "..." if ctx_start > 0 else ""
        suffix = "..." if ctx_end < len(text) else ""
        
        return prefix + text[ctx_start:ctx_end] + suffix
    
    def _check_length_limits(self, latex_code: str, is_display: bool) -> bool:
        """检查是否超过长度限制"""
        if not self.policy_manager:
            return True  # 无配置时不限制
        
        config = self.policy_manager.config
        max_len = config.max_display_length if is_display else config.max_inline_length
        return len(latex_code) <= max_len
    
    def _check_line_count(self, latex_code: str) -> bool:
        """检查跨行数是否在限制内"""
        if not self.policy_manager:
            return True
        
        config = self.policy_manager.config
        line_count = latex_code.count('\n') + latex_code.count('\r') + latex_code.count('\x0b') + 1
        return line_count <= config.max_line_count
    
    def scan_text(
        self, 
        text: str, 
        region: Region,
        base_offset: int = 0,
        paragraph_index: int = -1,
        region_index: int = -1,
        preprocess: bool = True
    ) -> Iterator[LatexMatch]:
        """
        扫描文本中的 LaTeX 片段
        
        Args:
            text: 要扫描的文本
            region: 所属区域
            base_offset: 基础偏移量（用于计算在文档中的绝对位置）
            paragraph_index: 段落索引
            region_index: 区域内索引
            preprocess: 是否预处理文本
            
        Yields:
            LatexMatch: 匹配的 LaTeX 片段信息
        """
        # 预处理文本（标准化 Word 特殊字符）
        # 注意：我们在原始文本上匹配，但可能需要在预处理后的文本上识别
        # 为了保持位置准确性，我们使用原始文本匹配
        working_text = text
        
        for match in self.latex_pattern.finditer(working_text):
            # 如果匹配的是转义字符，跳过
            if match.group('escaped'):
                continue
            
            # 判断是 $$ 还是 $
            if match.group('display'):
                # $$...$$ 显示公式
                latex_code = match.group('d_content')
                is_display = True
            elif match.group('inline'):
                # $...$ 行内公式
                latex_code = match.group('i_content')
                is_display = False
            else:
                continue
            
            # 跳过金额模式
            if self._is_money_pattern(latex_code):
                continue

            # 跳过伪公式（代码变量、路径等）
            if self._is_pseudo_formula(latex_code):
                continue

            # 检查长度限制
            if not self._check_length_limits(latex_code, is_display):
                continue
            
            # 检查跨行数限制
            if not self._check_line_count(latex_code):
                continue
            
            full_match = match.group(0)
            start_pos = base_offset + match.start()
            end_pos = base_offset + match.end()
            context = self._extract_context(working_text, match.start(), match.end())
            
            yield LatexMatch(
                latex_code=latex_code,
                full_match=full_match,
                start_pos=start_pos,
                end_pos=end_pos,
                region=region,
                is_display=is_display,
                paragraph_index=paragraph_index,
                context=context,
                region_index=region_index,
            )

        # 扩展格式扫描（如果启用）
        if self.enable_extended_formats:
            yield from self._scan_extended_formats(
                working_text, region, base_offset, paragraph_index, region_index
            )

    def _scan_extended_formats(
        self,
        text: str,
        region: Region,
        base_offset: int = 0,
        paragraph_index: int = -1,
        region_index: int = -1
    ) -> Iterator[LatexMatch]:
        r"""
        扫描扩展 LaTeX 格式

        支持格式：
        1. ```latex ... ``` Markdown 代码块
        2. \\[...\\] LaTeX 显示公式
        3. \\(...\\) LaTeX 行内公式
        4. 行独立 LaTeX 公式（检测含有 LaTeX 命令的独立行）

        Args:
            text: 要扫描的文本
            region: 所属区域
            base_offset: 基础偏移量
            paragraph_index: 段落索引
            region_index: 区域内索引

        Yields:
            LatexMatch: 匹配的 LaTeX 片段信息
        """
        # 记录已匹配的位置范围，避免重复
        matched_ranges = set()

        # 1. Markdown 代码块: ```latex ... ```
        for match in self.MARKDOWN_LATEX_BLOCK.finditer(text):
            content = match.group('content').strip()
            if not content:
                continue

            # 处理代码块中的多个公式（按行或 % 注释分割）
            formulas = self._extract_formulas_from_block(content)

            for formula in formulas:
                if not self._is_valid_latex(formula):
                    continue

                if not self._check_length_limits(formula, is_display=True):
                    continue

                full_match = match.group(0)
                start_pos = base_offset + match.start()
                end_pos = base_offset + match.end()
                context = self._extract_context(text, match.start(), match.end())

                # 记录已匹配范围
                matched_ranges.add((match.start(), match.end()))

                yield LatexMatch(
                    latex_code=formula,
                    full_match=full_match,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    region=region,
                    is_display=True,  # 代码块通常是显示公式
                    paragraph_index=paragraph_index,
                    context=context,
                    region_index=region_index,
                )

        # 1b. Markdown ```math 代码块（GitHub 风格）
        for match in self.MARKDOWN_MATH_BLOCK.finditer(text):
            if self._overlaps_ranges(match.start(), match.end(), matched_ranges):
                continue

            content = match.group('content').strip()
            if not content:
                continue

            formulas = self._extract_formulas_from_block(content)
            for formula in formulas:
                if not self._is_valid_latex(formula):
                    continue
                if not self._check_length_limits(formula, is_display=True):
                    continue

                full_match = match.group(0)
                start_pos = base_offset + match.start()
                end_pos = base_offset + match.end()
                context = self._extract_context(text, match.start(), match.end())
                matched_ranges.add((match.start(), match.end()))

                yield LatexMatch(
                    latex_code=formula,
                    full_match=full_match,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    region=region,
                    is_display=True,
                    paragraph_index=paragraph_index,
                    context=context,
                    region_index=region_index,
                )

        # 1c. LaTeX 显示公式环境: equation, align, gather 等
        for match in self.LATEX_DISPLAY_ENVS.finditer(text):
            if self._overlaps_ranges(match.start(), match.end(), matched_ranges):
                continue

            content = match.group('content').strip()
            env_name = match.group('env')
            if not content:
                continue

            # 对于 align/gather 等环境，内容本身可能包含多行对齐
            # 保留完整内容，让转换器处理
            if not self._check_length_limits(content, is_display=True):
                continue

            full_match = match.group(0)
            start_pos = base_offset + match.start()
            end_pos = base_offset + match.end()
            context = self._extract_context(text, match.start(), match.end())
            matched_ranges.add((match.start(), match.end()))

            yield LatexMatch(
                latex_code=content,
                full_match=full_match,
                start_pos=start_pos,
                end_pos=end_pos,
                region=region,
                is_display=True,
                paragraph_index=paragraph_index,
                context=context,
                region_index=region_index,
            )

        # 1d. LaTeX 行内公式环境: \begin{math}...\end{math}
        for match in self.LATEX_INLINE_ENV.finditer(text):
            if self._overlaps_ranges(match.start(), match.end(), matched_ranges):
                continue

            content = match.group('content').strip()
            if not content or not self._is_valid_latex(content):
                continue

            if not self._check_length_limits(content, is_display=False):
                continue

            full_match = match.group(0)
            start_pos = base_offset + match.start()
            end_pos = base_offset + match.end()
            context = self._extract_context(text, match.start(), match.end())
            matched_ranges.add((match.start(), match.end()))

            yield LatexMatch(
                latex_code=content,
                full_match=full_match,
                start_pos=start_pos,
                end_pos=end_pos,
                region=region,
                is_display=False,  # 行内公式
                paragraph_index=paragraph_index,
                context=context,
                region_index=region_index,
            )

        # 2. LaTeX 显示公式: \[...\]
        for match in self.LATEX_BRACKET_DISPLAY.finditer(text):
            # 检查是否与已匹配范围重叠
            if self._overlaps_ranges(match.start(), match.end(), matched_ranges):
                continue

            content = match.group('content').strip()
            if not content or not self._is_valid_latex(content):
                continue

            if not self._check_length_limits(content, is_display=True):
                continue

            full_match = match.group(0)
            start_pos = base_offset + match.start()
            end_pos = base_offset + match.end()
            context = self._extract_context(text, match.start(), match.end())

            matched_ranges.add((match.start(), match.end()))

            yield LatexMatch(
                latex_code=content,
                full_match=full_match,
                start_pos=start_pos,
                end_pos=end_pos,
                region=region,
                is_display=True,
                paragraph_index=paragraph_index,
                context=context,
                region_index=region_index,
            )

        # 3. LaTeX 行内公式: \(...\)
        for match in self.LATEX_PAREN_INLINE.finditer(text):
            if self._overlaps_ranges(match.start(), match.end(), matched_ranges):
                continue

            content = match.group('content').strip()
            if not content or not self._is_valid_latex(content):
                continue

            if not self._check_length_limits(content, is_display=False):
                continue

            full_match = match.group(0)
            start_pos = base_offset + match.start()
            end_pos = base_offset + match.end()
            context = self._extract_context(text, match.start(), match.end())

            matched_ranges.add((match.start(), match.end()))

            yield LatexMatch(
                latex_code=content,
                full_match=full_match,
                start_pos=start_pos,
                end_pos=end_pos,
                region=region,
                is_display=False,
                paragraph_index=paragraph_index,
                context=context,
                region_index=region_index,
            )

        # 4. 行独立 LaTeX：检测独立的公式行（无分隔符但含 LaTeX 命令）
        for match in self.STANDALONE_LATEX_LINE.finditer(text):
            if self._overlaps_ranges(match.start(), match.end(), matched_ranges):
                continue

            content = match.group('content').strip()

            # 跳过注释行（以 % 开头）
            if content.startswith('%'):
                continue

            # 必须包含 LaTeX 命令才认为是公式
            if not self._contains_latex_commands(content):
                continue

            # 额外验证：排除普通文本行
            if not self._is_standalone_formula(content):
                continue

            if not self._check_length_limits(content, is_display=True):
                continue

            full_match = match.group(0)
            start_pos = base_offset + match.start()
            end_pos = base_offset + match.end()
            context = self._extract_context(text, match.start(), match.end())

            # 添加到已匹配范围，避免后续重复匹配
            matched_ranges.add((match.start(), match.end()))

            yield LatexMatch(
                latex_code=content,
                full_match=full_match,
                start_pos=start_pos,
                end_pos=end_pos,
                region=region,
                is_display=True,  # 独立行通常是显示公式
                paragraph_index=paragraph_index,
                context=context,
                region_index=region_index,
            )

        # 5. 纯 latex 标签格式：独立的 "latex" 行后跟公式行
        # 这种格式常见于从 Word 或其他编辑器粘贴的内容
        yield from self._scan_plain_latex_tag_format(
            text, region, base_offset, paragraph_index, region_index, matched_ranges
        )

    def _scan_plain_latex_tag_format(
        self,
        text: str,
        region: Region,
        base_offset: int,
        paragraph_index: int,
        region_index: int,
        matched_ranges: set
    ) -> Iterator[LatexMatch]:
        """
        扫描纯 latex 标签格式

        格式示例：
            1. 基础公式
            latex
            % 注释
            x = \\frac{...}{...}
            % 另一个注释
            y = \\sum_{...}
            2. 下一节
        """
        # 查找所有 "latex" 标签行
        for tag_match in self.PLAIN_LATEX_TAG.finditer(text):
            tag_end = tag_match.end()

            # 找到标签后的内容（直到下一个非公式行）
            remaining_text = text[tag_end:]
            lines = remaining_text.split('\n')

            formula_lines = []
            total_consumed = 0

            for line in lines:
                stripped = line.strip()

                # 空行跳过（但不终止）
                if not stripped:
                    total_consumed += len(line) + 1  # +1 for \n
                    continue

                # 注释行跳过
                if stripped.startswith('%'):
                    total_consumed += len(line) + 1
                    continue

                # 检查是否是公式行（包含 LaTeX 命令）
                if self._contains_latex_commands(stripped):
                    formula_lines.append(stripped)
                    total_consumed += len(line) + 1
                # 检查是否是简单数学表达式
                elif self._looks_like_equation(stripped):
                    formula_lines.append(stripped)
                    total_consumed += len(line) + 1
                else:
                    # 遇到非公式行，终止
                    break

            # 生成匹配结果
            for formula in formula_lines:
                if not formula:
                    continue

                # 检查是否与已匹配范围重叠（简化：只用公式内容检查）
                # 由于位置计算复杂，这里用内容匹配
                if not self._check_length_limits(formula, is_display=True):
                    continue

                # 计算近似位置
                formula_pos = text.find(formula, tag_end)
                if formula_pos == -1:
                    continue

                if self._overlaps_ranges(formula_pos, formula_pos + len(formula), matched_ranges):
                    continue

                start_pos = base_offset + formula_pos
                end_pos = base_offset + formula_pos + len(formula)
                context = self._extract_context(text, formula_pos, formula_pos + len(formula))

                yield LatexMatch(
                    latex_code=formula,
                    full_match=formula,  # 无分隔符，full_match 就是公式本身
                    start_pos=start_pos,
                    end_pos=end_pos,
                    region=region,
                    is_display=True,
                    paragraph_index=paragraph_index,
                    context=context,
                    region_index=region_index,
                )

    def _looks_like_equation(self, content: str) -> bool:
        """检查内容是否看起来像方程（无 LaTeX 命令的简单数学表达式）"""
        # 必须包含等号或某些数学运算符
        if '=' not in content and not any(op in content for op in ['+', '-', '*', '/', '^', '_']):
            return False

        # 必须以字母或括号开头
        if not content or not (content[0].isalpha() or content[0] in '({'):
            return False

        # 不能是纯中文或纯数字
        has_letter = any(c.isalpha() and ord(c) < 128 for c in content)
        has_math_symbol = any(c in '=+-*/^_{}[]()' for c in content)

        return has_letter and has_math_symbol

    def _extract_formulas_from_block(self, block_content: str) -> list[str]:
        """
        从代码块中提取公式列表

        支持：
        - 整块作为一个公式
        - 按 % 注释行分割的多个公式
        """
        # 移除 % 开头的注释行
        lines = block_content.split('\n')
        formula_lines = []
        current_formula = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith('%'):
                # 遇到注释行，保存当前公式并开始新公式
                if current_formula:
                    formula = '\n'.join(current_formula).strip()
                    if formula:
                        formula_lines.append(formula)
                    current_formula = []
            else:
                current_formula.append(line)

        # 保存最后一个公式
        if current_formula:
            formula = '\n'.join(current_formula).strip()
            if formula:
                formula_lines.append(formula)

        # 如果只有一个公式或没有注释分割，返回整块
        if len(formula_lines) <= 1:
            cleaned = '\n'.join(l for l in lines if not l.strip().startswith('%'))
            cleaned = cleaned.strip()
            return [cleaned] if cleaned else []

        return formula_lines

    def _is_valid_latex(self, content: str) -> bool:
        """检查内容是否是有效的 LaTeX 公式"""
        if not content or len(content) < 2:
            return False

        # 必须包含 LaTeX 命令或数学表达式特征
        return self._contains_latex_commands(content) or self._has_math_features(content)

    def _contains_latex_commands(self, content: str) -> bool:
        """检查是否包含 LaTeX 命令"""
        return bool(self.LATEX_COMMAND_PATTERN.search(content))

    def _has_math_features(self, content: str) -> bool:
        """检查是否有数学表达式特征（无 LaTeX 命令时的备用检测）"""
        # 包含上下标、分数线等数学特征
        math_features = [
            r'[_^]',           # 上下标
            r'[+\-*/=]',       # 运算符
            r'\{[^}]+\}',      # 花括号
            r'\([^)]+\)',      # 圆括号内有内容
        ]
        for pattern in math_features:
            if re.search(pattern, content):
                return True
        return False

    def _is_standalone_formula(self, content: str) -> bool:
        """
        判断是否是独立的公式行

        排除普通文本，只接受明确的数学公式
        """
        # 必须以特定模式开头
        formula_starters = [
            r'^[a-zA-Z]\'?\s*\(',      # f(x), f'(x)
            r'^[a-zA-Z]_\{',           # x_{...}
            r'^\\[a-zA-Z]+',           # \frac, \int, etc.
            r'^\([a-zA-Z]',            # (a + b)
            r'^[a-zA-Z]\s*=',          # x =
            r'^\{',                     # { 开头
        ]

        for pattern in formula_starters:
            if re.match(pattern, content):
                return True

        # 或者包含多个 LaTeX 命令（更可能是公式）
        cmd_count = len(self.LATEX_COMMAND_PATTERN.findall(content))
        return cmd_count >= 2

    def _overlaps_ranges(self, start: int, end: int, ranges: set) -> bool:
        """检查位置范围是否与已有范围重叠"""
        for r_start, r_end in ranges:
            if not (end <= r_start or start >= r_end):
                return True
        return False

    def scan_word_range(self, word_range, region: Region, region_index: int = -1) -> list[LatexMatch]:
        """
        扫描 Word Range 对象
        
        Args:
            word_range: Word Range COM 对象
            region: 所属区域
            region_index: 区域内索引
            
        Returns:
            list[LatexMatch]: 匹配列表
        """
        try:
            text = word_range.Text
            base_offset = word_range.Start
            matches = list(self.scan_text(text, region, base_offset, region_index=region_index))
            return matches
        except Exception:
            # COM 对象访问失败时返回空列表
            return []
    
    def scan_paragraphs(self, doc, region: Region = Region.BODY) -> list[LatexMatch]:
        """
        扫描文档正文段落
        
        Args:
            doc: Word Document COM 对象
            region: 区域类型
            
        Returns:
            list[LatexMatch]: 匹配列表
        """
        matches = []
        try:
            for i, para in enumerate(doc.Paragraphs):
                para_matches = list(self.scan_text(
                    para.Range.Text,
                    region,
                    base_offset=para.Range.Start,
                    paragraph_index=i
                ))
                matches.extend(para_matches)
        except Exception:
            pass
        return matches
    
    def scan_tables(self, doc, region: Region = Region.BODY) -> list[LatexMatch]:
        """
        扫描文档表格
        
        Args:
            doc: Word Document COM 对象
            region: 区域类型
            
        Returns:
            list[LatexMatch]: 匹配列表
        """
        matches = []
        try:
            for table_idx, table in enumerate(doc.Tables):
                for row in table.Rows:
                    for cell in row.Cells:
                        cell_matches = self.scan_word_range(
                            cell.Range, 
                            region, 
                            region_index=table_idx
                        )
                        matches.extend(cell_matches)
        except Exception:
            pass
        return matches
    
    def scan_headers_footers(self, doc) -> list[LatexMatch]:
        """
        扫描页眉页脚
        
        Args:
            doc: Word Document COM 对象
            
        Returns:
            list[LatexMatch]: 匹配列表
        """
        matches = []
        try:
            for sec_idx, section in enumerate(doc.Sections):
                # 页眉
                for header in section.Headers:
                    header_matches = self.scan_word_range(
                        header.Range,
                        Region.HEADER,
                        region_index=sec_idx
                    )
                    matches.extend(header_matches)
                
                # 页脚
                for footer in section.Footers:
                    footer_matches = self.scan_word_range(
                        footer.Range,
                        Region.FOOTER,
                        region_index=sec_idx
                    )
                    matches.extend(footer_matches)
        except Exception:
            pass
        return matches
    
    def scan_footnotes(self, doc) -> list[LatexMatch]:
        """
        扫描脚注
        
        Args:
            doc: Word Document COM 对象
            
        Returns:
            list[LatexMatch]: 匹配列表
        """
        matches = []
        try:
            for i, footnote in enumerate(doc.Footnotes):
                fn_matches = self.scan_word_range(
                    footnote.Range,
                    Region.FOOTNOTE,
                    region_index=i
                )
                matches.extend(fn_matches)
        except Exception:
            pass
        return matches
    
    def scan_endnotes(self, doc) -> list[LatexMatch]:
        """
        扫描尾注
        
        Args:
            doc: Word Document COM 对象
            
        Returns:
            list[LatexMatch]: 匹配列表
        """
        matches = []
        try:
            for i, endnote in enumerate(doc.Endnotes):
                en_matches = self.scan_word_range(
                    endnote.Range,
                    Region.ENDNOTE,
                    region_index=i
                )
                matches.extend(en_matches)
        except Exception:
            pass
        return matches
    
    def scan_comments(self, doc) -> list[LatexMatch]:
        """
        扫描批注
        
        Args:
            doc: Word Document COM 对象
            
        Returns:
            list[LatexMatch]: 匹配列表
        """
        matches = []
        try:
            for i, comment in enumerate(doc.Comments):
                comment_matches = self.scan_word_range(
                    comment.Range,
                    Region.COMMENT,
                    region_index=i
                )
                matches.extend(comment_matches)
        except Exception:
            pass
        return matches
    
    def scan_textboxes(self, doc) -> list[LatexMatch]:
        """
        扫描文本框和形状
        
        Args:
            doc: Word Document COM 对象
            
        Returns:
            list[LatexMatch]: 匹配列表
        """
        matches = []
        try:
            # 浮动形状
            for i, shape in enumerate(doc.Shapes):
                if shape.TextFrame.HasText:
                    tb_matches = self.scan_word_range(
                        shape.TextFrame.TextRange,
                        Region.TEXTBOX,
                        region_index=i
                    )
                    matches.extend(tb_matches)
        except Exception:
            pass
        
        try:
            # 内联形状
            for i, shape in enumerate(doc.InlineShapes):
                if hasattr(shape, 'TextFrame') and shape.TextFrame.HasText:
                    tb_matches = self.scan_word_range(
                        shape.TextFrame.TextRange,
                        Region.TEXTBOX,
                        region_index=i
                    )
                    matches.extend(tb_matches)
        except Exception:
            pass
        
        return matches
    
    def scan_body(self, doc) -> list[LatexMatch]:
        """
        扫描正文区域（段落 + 表格）
        
        Args:
            doc: Word Document COM 对象
            
        Returns:
            list[LatexMatch]: 匹配列表
        """
        matches = []
        matches.extend(self.scan_paragraphs(doc))
        # matches.extend(self.scan_tables(doc))  # Paragraphs 已经包含表格内容，避免重复扫描
        return matches
    
    def scan_other_regions(self, doc) -> list[LatexMatch]:
        """
        扫描非正文区域
        
        Args:
            doc: Word Document COM 对象
            
        Returns:
            list[LatexMatch]: 匹配列表
        """
        matches = []
        matches.extend(self.scan_headers_footers(doc))
        matches.extend(self.scan_footnotes(doc))
        matches.extend(self.scan_endnotes(doc))
        matches.extend(self.scan_comments(doc))
        matches.extend(self.scan_textboxes(doc))
        return matches
    
    def scan_all(self, doc) -> list[LatexMatch]:
        """
        扫描全部区域
        
        Args:
            doc: Word Document COM 对象
            
        Returns:
            list[LatexMatch]: 匹配列表
        """
        matches = []
        matches.extend(self.scan_body(doc))
        matches.extend(self.scan_other_regions(doc))
        return matches
    
    def scan_regions(self, doc, regions: set[Region]) -> list[LatexMatch]:
        """
        扫描指定区域
        
        Args:
            doc: Word Document COM 对象
            regions: 要扫描的区域集合
            
        Returns:
            list[LatexMatch]: 匹配列表
        """
        matches = []
        
        if Region.BODY in regions:
            matches.extend(self.scan_body(doc))
        if Region.HEADER in regions or Region.FOOTER in regions:
            matches.extend(self.scan_headers_footers(doc))
        if Region.FOOTNOTE in regions:
            matches.extend(self.scan_footnotes(doc))
        if Region.ENDNOTE in regions:
            matches.extend(self.scan_endnotes(doc))
        if Region.COMMENT in regions:
            matches.extend(self.scan_comments(doc))
        if Region.TEXTBOX in regions:
            matches.extend(self.scan_textboxes(doc))
        
        return matches



