from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from pymongo import MongoClient
from collections import OrderedDict


Builder.load_string('''
<DataTable>:
    id: main_win
    RecycleView:
        viewclass: 'CustLabel'
        id: table_floor
        RecycleGridLayout:
            id: table_floor_layout
            default_size: (None, 250)
            default_size_hint: (1, None)
            size_hint_y: None
            height: self.minimum_height
            spacing: 5
<CustLabel@Label>:
    bcolor: (1,1,1,1)
    canvas.before:
        Color:
            rgba: root.bcolor
        Rectangle:
            pos: self.pos
            size: self.size
''')

class DataTable(BoxLayout):

    def __init__(self, table='', **kwargs):
        super().__init__(**kwargs)

        self.client = MongoClient()
        self.db = self.client.silverpos

        products = table

        col_titles = [k for k in products.keys()]
        row_len = len(products[col_titles[0]])
        self.columns = len(col_titles)
        #print(row_len)
        table_data = []
        for t in col_titles:
            table_data.append({'text':str(t), 'size_hint_y':None, 'height':50, 'bcolor':(.06,.45,.45,1)})
        for i in range(row_len):
            for t in col_titles:
                table_data.append({'text':str(products[t][i]),'size_hint_y':None,'height':30,'bcolor':(.06,.25,.25,1)})
        self.ids.table_floor_layout.cols = self.columns
        self.ids.table_floor.data = table_data


class DataTableApp(App):
    def build(self):
        return DataTable()


if __name__ == "__main__":
    da = DataTableApp()
    da.run()