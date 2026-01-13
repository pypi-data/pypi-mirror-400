class StateTemplates:
    @staticmethod
    def get_template(name: str) -> str:
        class_name = ''.join(word.capitalize() for word in name.split('_'))
        
        return f'''from aiogram.fsm.state import State, StatesGroup

class {class_name}(StatesGroup):
    """FSM states for {name}"""
    # Add your states here
    # Example:
    # start = State()
    # waiting_data = State()
    # confirm = State()
    pass
'''
