class ProgressBar:
    __slots__ = ('_length', '_template', '_template_styled', '_boundaryChar', '_fillChar', '_emptyChar', '_cached_bar')

    def __init__(self, length: int = 20, *, template: str = '%b%f%e%b %p%', template_styled: str = '%b%f%e%b <blue>%p</blue>%', boundary_char: str = '|', fill_char: str = '█', empty_char: str = '░'):
        '''
        进度条

        - Args
            - length: 进度条长度
            - template: 进度条模板；支持的占位符有：
                - %b: 边界字符
                - %f: 进度条主体
                - %e: 已完成部分
                - %p: 百分比
            - template_styled: 样式化进度条模板，支持的占位符同上
            - boundary_char: 边界字符
            - fill_char: 已完成部分字符
            - empty_char: 未完成部分字符
        '''

        self._length = length
        '''  进度条长度 '''
        self._template = template
        '''  进度条模板 '''
        self._template_styled = template_styled
        '''  样式化进度条模板 '''
        self._boundaryChar = boundary_char
        '''  边界字符 '''
        self._fillChar = fill_char
        '''  已完成部分字符 '''
        self._emptyChar = empty_char
        '''  未完成部分字符 '''

        self._cached_bar: list[tuple[str, str]] = []
        ''' 进度条缓存 '''

        self._cache()

    def _cache(self):
        ''' 预生成进度条缓存 '''

        self._cached_bar.clear()
        for i in range(self.length + 1):
            empty = self.length - i
            self._cached_bar.append((
                self.template.replace('%b', self.boundary_char).replace('%f', self.fill_char * i).replace('%e', self.empty_char * empty),
                self.template_styled.replace('%b', self.boundary_char).replace('%f', self.fill_char * i).replace('%e', self.empty_char * empty)
            ))

    def __call__(self, value: float) -> tuple[str, str]:
        '''
        生成进度条

        - Args
            - value: 进度，范围[0, 1]

        - Returns
            未样式化进度条和样式化进度条
        '''

        bar, bar_styled = self._cached_bar[int(self.length * value)]
        value = '{:.2f}'.format(value * 100)
        return (bar.replace('%p', value), bar_styled.replace('%p', value))

    @property
    def length(self) -> int:
        ''' 进度条长度 '''

        return self._length

    @length.setter
    def length(self, value: int):
        self._length = value
        self._cache()

    @property
    def template(self) -> str:
        ''' 进度条模板 '''

        return self._template

    @template.setter
    def template(self, value: str):
        self._template = value
        self._cache()

    @property
    def template_styled(self) -> str:
        ''' 样式化进度条模板 '''

        return self._template_styled

    @template_styled.setter
    def template_styled(self, value: str):
        self._template_styled = value
        self._cache()

    @property
    def boundary_char(self) -> str:
        ''' 边界字符 '''

        return self._boundaryChar

    @boundary_char.setter
    def boundary_char(self, value: str):
        self._boundaryChar = value
        self._cache()

    @property
    def fill_char(self) -> str:
        ''' 已完成部分字符 '''

        return self._fillChar

    @fill_char.setter
    def fill_char(self, value: str):
        self._fillChar = value
        self._cache()

    @property
    def empty_char(self) -> str:
        ''' 未完成部分字符 '''

        return self._emptyChar

    @empty_char.setter
    def empty_char(self, value: str):
        self._emptyChar = value
        self._cache()
