from dashboard import *


class TaskHandlerButtonAdvanced(TaskHandlerButton):
    class StateButton(ipywidgets.Button):
        def __init__(self,task,name,color1="lightblue", color2="red"):
            # super().__init__(layout=ipywidgets.Layout(width='auto', height='30px'))
            super().__init__(description=name,layout=ipywidgets.Layout(height='30px'))

            self.task=task

            self.style.button_color = 'gray'
            self.state_color = color1
            self.non_state_color = color2
            self.on_click(self.called)

        @property
        def state(self):
            return self.style.button_color == self.state_color

        def change_state(self):
            if self.state:
                self.style.button_color = self.non_state_color
            else:
                self.style.button_color = self.state_color

        def called(self, things=None):
            if not self.state:
                self.task.start()
            else:
                self.task.stop()

            # TODO: change_state default, sync_state with running
            self.change_state()

        @loop()
        async def sync_state(self, func):
            if func() != self.state:
                self.change_state()

    def create_buttons(self, widgets):
        self.box = ipywidgets.Box([self.StateButton(self,self.name), *widgets])

