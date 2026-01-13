### USAGE ##############################################################
___
```python
from kk_scene_wrapper import SceneData

path = "/path/to/scene-file"
sd = SceneData(path)

timeline_binary = sd.get_timeline_xml()
timeline = sd.get_timeline_xml_tree()
(
  image_type: Optional[str],# "animation", "dynamic", "static", None
  sfx_status: bool,         # True if sfx found
  duration: int
) = sd.get_timeline_info()
```
