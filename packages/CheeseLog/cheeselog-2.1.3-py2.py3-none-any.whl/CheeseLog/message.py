class Message:
    __slots__ = ('key', 'weight', 'message_template', 'timer_template', 'message_template_styled')

    def __init__(self, key: str, weight: int = 10, message_template: str | None = None, timer_template: str | None = None, message_template_styled: str | None = None):
        '''
        - Args
            - weight: 权重，更高的权重意味着更高的日志级别
            - message_template: 日志消息模板，未设置时默认为`CheeseLogger`实例的`message_template`
            - timer_template: 日期模板，未设置时默认为`CheeseLogger`实例的`timer_template`
            - message_template_styled: 带样式的日志消息模板，未设置时默认为`CheeseLogger`实例的`message_template_styled`
        '''

        self.key: str = key
        self.weight: int = weight
        ''' 权重，更高的权重意味着更高的日志级别 '''
        self.message_template: str | None = message_template
        ''' 日志消息模板，未设置时默认为`CheeseLogger`实例的`message_template` '''
        self.timer_template: str | None = timer_template
        ''' 日期模板，未设置时默认为`CheeseLogger`实例的`timer_template` '''
        self.message_template_styled: str | None = message_template_styled
        ''' 带样式的日志消息模板，未设置时默认为`CheeseLogger`实例的`message_template_styled` '''
