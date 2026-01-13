from pathlib import Path
from pyboot.commons.utils.log import Logger
from pyboot.commons.utils.utils import iterkeys,convert_to_string
import os

_logger = Logger('dataflow.utils.file')

def get_file_with_profile(path: str | Path, profile: str = "dev") -> Path:
    """
    在文件名与扩展名之间插入 `-profile`；
    若无扩展名，则直接拼接 `-profile`。
    """
    p = Path(path)
    
    if profile is None or profile.strip() == '':
        return p
    
    suffix = p.suffix          # 含点号，如 '.yaml'
    name = p.stem              # 纯文件名，不含后缀
    new_name = f"{name}-{profile}{suffix}" if suffix else f"{name}-{profile}"
    return p.with_name(new_name)

def guess_content_type_by_file_name(file_name):
    """
    Get file type by filename.

    :type file_name: string
    :param file_name: None
    =======================
    :return:
        **Type Value**
    """
    mime_map = dict()
    mime_map["js"] = "application/javascript"
    mime_map["xlsx"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    mime_map["xltx"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.template"
    mime_map["potx"] = "application/vnd.openxmlformats-officedocument.presentationml.template"
    mime_map["ppsx"] = "application/vnd.openxmlformats-officedocument.presentationml.slideshow"
    mime_map["pptx"] = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    mime_map["sldx"] = "application/vnd.openxmlformats-officedocument.presentationml.slide"
    mime_map["docx"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    mime_map["dotx"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.template"
    mime_map["xlam"] = "application/vnd.ms-excel.addin.macroEnabled.12"
    mime_map["xlsb"] = "application/vnd.ms-excel.sheet.binary.macroEnabled.12"
    try:
        file_name = convert_to_string(file_name)
        name = os.path.basename(file_name.lower())
        suffix = name.split('.')[-1]
        if suffix in iterkeys(mime_map):
            mime_type = mime_map[suffix]
        else:
            import mimetypes

            mimetypes.init()
            mime_type = mimetypes.types_map.get("." + suffix, 'application/octet-stream')
    except Exception:
        mime_type = 'application/octet-stream'
    if not mime_type:
        mime_type = 'application/octet-stream'

    return mime_type

if __name__ == "__main__":
    print(get_file_with_profile('conf/application.yml'))