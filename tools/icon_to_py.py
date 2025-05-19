import base64

def icon_to_py(icon_path, output_path):
    with open(icon_path, 'rb') as f:
        icon_data = base64.b64encode(f.read()).decode('utf-8')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f'''# -*- coding: utf-8 -*-

# 이 파일은 자동 생성된 파일입니다. 직접 수정하지 마세요.
# 아이콘 데이터를 base64로 인코딩하여 저장합니다.

ICON_DATA = b"{icon_data}"

def get_icon():
    from PyQt5.QtGui import QIcon, QPixmap, QImage
    from PyQt5.QtCore import QBuffer, QIODevice, QByteArray
    import base64
    
    # base64 데이터를 QByteArray로 변환
    icon_bytes = base64.b64decode(ICON_DATA)
    byte_array = QByteArray(icon_bytes)
    
    # QBuffer를 통해 QIcon 생성
    buffer = QBuffer(byte_array)
    buffer.open(QIODevice.ReadOnly)
    icon = QIcon()
    icon.addPixmap(QPixmap.fromImage(QImage.fromData(buffer.readAll())))
    buffer.close()
    
    return icon
''')

if __name__ == '__main__':
    import os
    icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'image', 'hshell.ico')
    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'gui', 'icon_data.py')
    icon_to_py(icon_path, output_path)
    print(f"아이콘 데이터가 {output_path}에 저장되었습니다.") 