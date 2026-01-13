import itertools
import os
import re
from typing import Optional, Tuple
from xml.etree import ElementTree as et

from kk_scene_wrapper.utils import (
    animation_terms,
    body_extra_terms,
    body_terms,
    make_terms_regex,
    sfx_extra_terms,
    sfx_terms,
)


class SceneData:
    class Error(Exception):
        pass

    class ContentError(Error):
        pass

    class TimelineDoesNotExist(Error):
        pass

    class MemoryError(Error):
        pass

    class ValueError(Error):
        pass

    file_path: str
    timeline_regex: "re.Pattern"
    sfx_status: bool
    image_type: str

    _TIMELINE_PATTERN = re.compile(
        rb"timeline.{1,10}?sceneInfo(?P<flag>.*?)(?P<data><root\b[^>/]*?/>|<root\b[^>]*?>(?P<inner>.*?)</root>)",
        re.DOTALL,
    )
    _DURATION_PATTERN = re.compile(rb'duration="([\d\.]+)"')
    _ANIMATION_PATTERN = re.compile(rb'guideObjectPath="([^"]*)"')
    _SFX_TERMS = make_terms_regex(sfx_terms())
    _SFX_EXTRA_TERMS = make_terms_regex(itertools.chain(sfx_terms(), sfx_extra_terms()))
    _ANIMATION_TERMS = make_terms_regex(animation_terms())
    _BODY_TERMS = make_terms_regex(body_terms())
    _BODY_EXTRA_TERMS = make_terms_regex(
        itertools.chain(body_terms(), body_extra_terms())
    )
    _THREENODENAMING_PATTERN = re.compile(
        rb"org\.njaecha\.plugins\.treenodenaming\xe2\x80\x99(?P<workspace>.+?)(\xe2\x80\x99\x00|$)",
        re.DOTALL,
    )
    _PLUGINLIST_PATTERN = re.compile(
        rb"PluginListTool(?P<plugins>.+?)(?<=([^\w ]))PNG(?=[^\w ])",
        re.DOTALL,
    )
    _VMDPLAY_PATTERN = re.compile(
        rb"<VMDPlaySaveData(?P<data>.+?)</VMDPlaySaveData>",
        re.DOTALL,
    )

    # Timeline data starts with b'timeline[somebytes_I_dont_know]sceneInfo[bytes(length_flag + bit_length_of_data_lenght)][bytes(data_lenght)]'
    # right before the xml data, the known flags must be updated on every change.
    _timeline_length_flag: int = 216

    def __init__(self, file_path: str, timeline_regex: Optional[str] = None):
        self.file_path = file_path
        self.timeline_regex = (
            re.compile(timeline_regex) if timeline_regex else self._TIMELINE_PATTERN
        )
        if os.path.splitext(self.file_path)[1] != ".png":
            raise SceneData.ContentError("File is not a scene data file")

        try:
            with open(file_path, "rb") as filekk:
                self._content = filekk.read()
        except MemoryError:
            raise SceneData.MemoryError("File is to big, file.read() failed")

        if not self._is_scene_data():
            raise SceneData.ContentError("Not a scene data file")

        self._cached_timeline: Optional[bytes] = None

        (
            self.image_type,
            self.sfx_status,
            self._duration,
        ) = self._check_timeline()

    @property
    def content_str(self) -> str:
        try:
            return self._content.decode("utf-8", errors="ignore")
        except MemoryError:
            raise SceneData.MemoryError(
                "File content is too big, content.decode('utf-8', errors='ignore') failed"
            )

    @property
    def content(self) -> bytes:
        return self._content

    @property
    def duration(self) -> float:
        return self._duration

    @duration.setter
    def duration(self, value: float):
        raise NotImplementedError("Modification of the timeline is not supported (yet)")

        if not self.has_timeline():
            raise SceneData.ValueError("Scene data does not have a timeline")
        elif self.image_type == "static":
            raise SceneData.ValueError(
                "Scene data is Static and does not have a duration"
            )
        elif value <= 0:
            raise SceneData.ValueError("Duration must be greater than 0")
        elif value == self._duration:
            return
        else:
            # replace "duration={value}" by value in the timeline string
            modified_timeline = re.sub(
                self._DURATION_PATTERN,
                f'duration="{value}"'.encode("utf-8"),
                self.get_timeline_xml(),
            )
            self.replace_timeline(modified_timeline)
            self._duration = value
        return self

    def get_timeline_info(self) -> Tuple[str, bool, float]:
        return self.image_type, self.sfx_status, self.duration

    def get_timeline_xml(self, raise_exception: bool = False) -> Optional[bytes]:
        if self._cached_timeline:
            return self._cached_timeline
        elif match := self.timeline_regex.search(self._content):
            if match.group("inner") is not None:
                self._cached_timeline = match.group("data")
                return self._cached_timeline
            elif raise_exception:
                raise SceneData.TimelineDoesNotExist("Timeline data not found")

        return None

    def get_timeline_xml_tree(
        self, raise_exception: bool = False
    ) -> Optional[et.ElementTree]:
        xml_str = self.get_timeline_xml(raise_exception=raise_exception)
        return et.ElementTree(et.fromstring(xml_str)) if xml_str else None

    def get_treenodenaming(self, raise_exception: bool = False) -> Optional[bytes]:
        if match := self._THREENODENAMING_PATTERN.search(self._content):
            return match.group("workspace")
        elif raise_exception:
            raise SceneData.TimelineDoesNotExist("Treenodenaming data not found")
        else:
            return None

    def replace_timeline(self, new_timeline: str):
        """Replace the timeline data with a new one"""

        raise NotImplementedError("Modification of the timeline is not supported (yet)")

        length_flag, timeline_byte_legth = self._get_timeline_byte_vars(new_timeline)

        def replace(match):
            return (
                match.group(0)
                .replace(match.group("data"), new_timeline)
                .replace(match.group("flag"), length_flag + timeline_byte_legth)
            )

        self._content = re.sub(self.timeline_regex, replace, self._content)
        self._cached_timeline = new_timeline

    def has_timeline(self) -> bool:
        return self.image_type != "static"

    def save(self, overwrite: bool = False):
        filename, ext = os.path.splitext(self.file_path)
        if not overwrite and os.path.exists(self.file_path):
            filename = filename + "_new"

        file_path = os.path.join(os.path.dirname(self.file_path), f"{filename}{ext}")
        with open(file_path, "wb") as filekk:
            filekk.write(self._content)

        self.file_path = file_path

    def _get_timeline_byte_vars(self, timeline) -> Tuple[bytes, bytes]:
        """Return the length flag and the timeline byte length"""
        num_bytes = (len(timeline).bit_length() + 7) // 8
        length_flag = (
            self._timeline_length_flag + (num_bytes if num_bytes <= 3 else 3)
        ).to_bytes(1, byteorder="big")
        timeline_byte_length = len(timeline).to_bytes(num_bytes, byteorder="big")
        return length_flag, timeline_byte_length

    def _is_scene_data(self) -> bool:
        return (
            os.path.splitext(self.file_path)[1] == ".png" and b"KStudio" in self._content
        )

    def _count_anim_interpolables(
        self, node: et.Element, min_keyframes: int = 3, stop: int = 0
    ) -> int:
        """
        Count how many interpolables of type 'guideObjectPath' have a number of keyframes >= min_keyframes.
        """
        found: int = 0
        for child in node:
            if child.tag == "interpolableGroup":
                found += self._count_anim_interpolables(child, min_keyframes, stop)
            elif child.tag == "interpolable":
                if (
                    "body" in child.get("guideObjectPath", "")
                    or (path := child.get("guideObjectPath")) is not None
                    and "camera" not in path.lower()
                    and "camera" not in child.get("alias", "").lower()
                    and len(child) >= min_keyframes
                ):
                    found += 1
            if stop and found >= stop:
                break

        return found

    def _count_guideobject_interpolables(
        self, node: et.Element, min_keyframes: int = 3, stop: int = 0
    ) -> int:
        """
        Count how many interpolables of type 'id=guideObject' have a number of keyframes >= min_keyframes.
        """
        found: int = 0
        for child in node:
            if child.tag == "interpolableGroup":
                found += self._count_guideobject_interpolables(child, min_keyframes, stop)
            elif child.tag == "interpolable":
                if "guideObject" in child.get("id", "") and len(child) >= min_keyframes:
                    found += 1
            if stop and found >= stop:
                break

        return found

    def _count_terms(self, pattern: re.Pattern, workspace: bytes, max_count: int) -> int:
        count = 0
        for _ in re.finditer(pattern, workspace):
            count += 1
            if count >= max_count:
                break
        return count

    def _check_timeline(self) -> Tuple[str, bool, float]:
        """
        Returns:
            tuple (image_type, sfx_status, duration)
            image_type: "animation", "dynamic", "static", None
            sfx_status: bool
            duration: float
        """
        workspace = self.get_treenodenaming()
        if not workspace:
            workspace = self.content
            _body_terms = self._BODY_TERMS
            # If the scene does not use the treenodenaming plugin, check for 4+ letter sfx terms in the content
            excluded_portions = []
            for pluginlist_match in self._PLUGINLIST_PATTERN.finditer(workspace):
                excluded_portions.append(pluginlist_match.span())
            if vmdplay_match := self._VMDPLAY_PATTERN.search(workspace):
                excluded_portions.append(vmdplay_match.span())

            if excluded_portions:
                sfx_status = False
                # Check for SFX terms outside excluded portions
                for match in re.finditer(self._SFX_TERMS, workspace):
                    if not any(
                        start <= match.start() < end for start, end in excluded_portions
                    ):
                        sfx_status = True
                        break
            else:
                sfx_status = re.search(self._SFX_TERMS, workspace) is not None
        else:
            _body_terms = self._BODY_EXTRA_TERMS
            # If it uses the plugin, check for 2+ letter sfx terms in the workspace
            sfx_status = re.search(self._SFX_EXTRA_TERMS, workspace) is not None

        timeline_xml = self.get_timeline_xml()

        if not timeline_xml or b"Timeline" not in timeline_xml:
            return ("dynamic" if sfx_status else "static"), False, 0.0

        timeline = et.ElementTree(et.fromstring(timeline_xml)).getroot()
        duration = float(timeline.get("duration", 0.0))

        # Iterate over timeline and all its children until you find 3 or more children that fufill these 2 conditions:
        # - They each have the "guideObjectPath" attribute.
        # - They have 3 or more children/keyframes.
        # If the conditions are met return "animation" else return "dynamic"

        min_keyframes = 3
        if self._count_anim_interpolables(timeline, min_keyframes, 3) >= 3:
            return "animation", sfx_status, duration
        elif (
            self._count_terms(self._ANIMATION_TERMS, workspace, 2) >= 2
            or self._count_terms(_body_terms, workspace, 4) >= 4
        ) and self._count_guideobject_interpolables(timeline, min_keyframes, 6) >= 6:
            return "animation", sfx_status, duration
        else:
            # No guideObjectPath means no motion, except face motions and cameras
            return "dynamic", sfx_status, duration
