## Copyright (C) 2025 Solaar Contributors
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with this program; if not, write to the Free Software Foundation, Inc.,
## 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# Classes, etc., for new-style Profiles, feature x8102

# The main class is a Profile, information stored on a device (usually in NVM) that modifies the behavior of the device
# Profiles can be generic or tuned to a device
# Profiles contain a number of tags and values, represented as a mapping from tags to Fields
# Fields have the data to change a particular kind of behavior of the device
# Fields also store whether they have been modified

# Devices have information on which tags they support.
# Devices have information on which keys are acceptable for the KeyMapping and FnKeyMapping fields.

# Profiles can be read from or written to YAML.
# Profiles can be read from or written to devices
# Fields can be read from or written to byte strings.

import binascii
import copy
import struct

from enum import Flag
from enum import IntEnum

import yaml

from . import exceptions
from . import special_keys
from .hidpp20_constants import SupportedFeature


class UsagePageIndex(IntEnum):
    Keyboard = 0x07
    GenericDesktop = 0x01
    Consumer = 0x0C

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_scalar("!UsagePageIndex", data.name)

    @classmethod
    def from_yaml(cls, loader, node):
        return UsagePageIndex[loader.construct_scalar(node)]


yaml.SafeLoader.add_constructor("!UsagePageIndex", UsagePageIndex.from_yaml)
yaml.Dumper.add_representer(UsagePageIndex, UsagePageIndex.to_yaml)


class Modifiers(Flag):
    LControl = 0x01
    LShift = 0x02
    LAlt = 0x04
    LCommand = 0x08
    RControl = 0x10
    RShift = 0x20
    RAlt = 0x40
    RCommand = 0x80


class Tag(IntEnum):
    ID = 1
    Version = 2
    Name = 3
    MultiHostAssignment = 6
    FnKeyMapping = 7
    KeyMapping = 8
    RollerMapping = 9
    Index = -1  # Solaar "tag" for device profile index


# WARNING: The generated YAML loads back with the interior class objects being dictionaries, not class objects
# So the result has to be post-processed, using yaml_post_process
# This can't be done during YAML loading because PyYAML inserts dictionary values after node creation.


# A Profile has attributes that represent profile fields.
# Each of these attributes has its own class
class Profile(yaml.YAMLObject):
    yaml_tag = "!Profile"
    yaml_loader = yaml.SafeLoader

    def __init__(self, id=None, name=""):
        if id:
            self.set_field(Tag.ID, id)
        if name:
            self.set_field(Tag.Name, Name(name))

    @property
    def name(self):
        return getattr(self, Tag.Name.name, None)

    def get_field(self, attribute):
        return getattr(self, attribute.name, None)

    def set_field(self, attribute, value):
        setattr(self, attribute.name, value)

    def del_field(self, attribute):
        delattr(self, attribute.name)

    def to_str(self):
        return str(self.fields)

    @classmethod
    def from_yaml(cls, loader, node):
        obj = cls()
        for name, value in loader.construct_mapping(node).items():
            setattr(obj, name, value)
        return obj

    def yaml_post_process(self):  # turn the interior dictionary entries into class objects
        for name, value in self.__dict__.items():
            print("YPP", name, value)
            if name in TagClasses:
                val = TagClasses[name](value)
                print("YPP", name, value, val)
                setattr(self, name, val)


class Field(yaml.YAMLObject):
    yaml_loader = yaml.SafeLoader
    modified = True

    def to_device(self, device, index):
        if self.modified:
            tag = struct.pack("!H", self.profile_tag)
            bytes = self.to_bytes()
            self.device.feature_request(SupportedFeature.MODULAR_PROFILE_MANAGEMENT, 0x80, index)
            seq = self.device.feature_request(SupportedFeature.MODULAR_PROFILE_MANAGEMENT, 0x90, tag)[0]
            offset = 0
            while offset < len(bytes):
                self.device.feature_request(
                    SupportedFeature.MODULAR_PROFILE_MANAGEMENT, 0xA0, seq, bytes[offset : offset + 15]
                )
                offset += 15
            crc = struct.pack("!L", binascii.crc32(tag + bytes))
            response = self.device.feature_request(SupportedFeature.MODULAR_PROFILE_MANAGEMENT, 0xB0, crc)
            if response[0]:
                print("Write RESPONSE", response[0])
            return response[0]


class ID(Field):
    yaml_tag = "!ProfileID"
    profile_tag = Tag.ID

    def __init__(self, id: int):
        self.id = id

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:int", str(data.id))

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(loader.construct_scalar(node))

    def to_bytes(self):
        return struct.pack("!H", self.id)

    @classmethod
    def from_bytes(cls, bytes):
        return struct.unpack("!H")[0]


class Index(Field):  # the device profile index that the profile is associated with
    yaml_tag = "!ProfileIndex"
    profile_tag = Tag.Index

    def __init__(self, index: int):
        self.index = index

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:int", str(data.index))

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(loader.construct_scalar(node))

    def to_bytes(self):
        return b""


class Name(Field):
    yaml_tag = "!ProfileName"
    profile_tag = Tag.Name

    def __init__(self, name: str):
        self.name = name

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data.name)

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(loader.construct_scalar(node))

    def to_bytes(self):
        return self.name[0:16].encode("utf-16")

    @classmethod
    def from_bytes(cls, bytes):
        return cls(bytes.decode("utf-16"))


class KeyMapping(Field):
    yaml_tag = "!KeyMapping"
    profile_tag = Tag.KeyMapping

    def __init__(self, keys=None):  # turn bare numbers and dicts into correct objects
        self.keys = {}
        if keys:
            for key, value in keys.items():
                if isinstance(value, Key):
                    print("INIT", type(key), key, type(value), value)
                    self.keys[key] = value
                else:
                    for map in [KeyOne, KeyTwo, KeyControl]:
                        found = map.from_dict(value)
                        if found is not None:
                            break
                    if found is None:
                        raise Exception("Can't initialize key from dictionary")
                    else:
                        key = special_keys.CONTROL[key]  # convert to required class
                        self.keys[key] = found

    def __deepcopy__(self, _memo):
        print("DEEPCOPY KM", type(self.keys), self.keys)
        keys = {k: copy.copy(m) for k, m in self.keys.items()}
        return KeyMapping(keys)

    def add_key(self, key, mapped):
        self.keys[special_keys.CID[int(key)]] = mapped

    @classmethod
    def to_yaml(cls, dumper, data):
        dump = {int(key): val for key, val in data.keys.items()}
        return dumper.represent_mapping("tag:yaml.org,2002:map", dump)

    @classmethod
    def from_yaml(cls, loader, node):
        keys = loader.construct_mapping(node)
        return cls(keys)

    def to_bytes(self):
        bytes = b"".join([struct.pack("!H", key) + val.to_bytes() for key, val in self.keys.items()])
        return bytes

    @classmethod
    def from_bytes(cls, bytes):
        mapping = cls()
        while bytes:
            key = struct.unpack("!H", bytes[:2])[0]
            for map in [KeyOne, KeyTwo, KeyControl]:
                found = map.from_bytes(bytes[2:])
                if found is not None:
                    break
            if found is None:
                raise Exception("Can't convert from bytes")
            else:
                bytes, mapped = found
                mapping.add_key(key, mapped)
        return mapping


class FnKeyMapping(KeyMapping):
    yaml_tag = "!ProfileFnKeyMapping"
    profile_tag = Tag.FnKeyMapping


def to_code(page, code):
    result = (
        special_keys.USB_HID_KEYCODES[int(code)]
        if page == UsagePageIndex["Keyboard"]
        else special_keys.HID_CONSUMERCODES[int(code)]
        if page == UsagePageIndex["Consumer"]
        else code
    )
    return result


class Key(yaml.YAMLObject):
    pass


class KeyOne(Key):
    yaml_tag = "!ProfileKeyOne"
    yaml_loader = yaml.SafeLoader
    tag = 0x01

    def __init__(self, modifiers, page, code):
        self.modifiers = modifiers if isinstance(modifiers, Modifiers) else Modifiers(int(modifiers))
        self.page = UsagePageIndex(int(page))
        self.code = to_code(page, code)

    @classmethod
    def from_dict(cls, dct):
        if len(dct) == 3:
            return cls(dct["modifiers"], dct["page"], dct["code"])

    @classmethod
    def to_yaml(cls, dumper, data):
        dump = {"modifiers": data.modifiers.value, "page": int(data.page), "code": int(data.code)}
        return dumper.represent_mapping("tag:yaml.org,2002:map", dump, flow_style=True)

    def to_bytes(self):
        return struct.pack("!BBBH", self.tag, self.modifiers.value, int(self.page), int(self.code))

    @classmethod
    def from_bytes(cls, bytes):
        if cls.tag == bytes[0]:
            modifiers, page, code = struct.unpack("!BBH", bytes[1:5])
            return bytes[5:], cls(modifiers, page, code)


class KeyTwo(Key):
    yaml_tag = "!ProfileKeyTwo"
    yaml_loader = yaml.SafeLoader
    tag = 0x02

    def __init__(self, modifiers, page, code, page2, code2):
        self.modifiers = modifiers if isinstance(modifiers, Modifiers) else Modifiers(int(modifiers))
        self.page = UsagePageIndex(int(page))
        self.code = to_code(page, code)
        self.page2 = UsagePageIndex(int(page2))
        self.code2 = to_code(page2, code2)

    @classmethod
    def from_dict(cls, dct):
        if len(dct) == 5:
            return cls(dct["modifiers"], dct["page"], dct["code"], dct["page2"], dct["code2"])

    @classmethod
    def to_yaml(cls, dumper, data):
        dump = {
            "modifiers": data.modifiers.value,
            "page": int(data.page),
            "code": int(data.code),
            "page2": int(data.page2),
            "code2": int(data.code2),
        }
        return dumper.represent_mapping("tag:yaml.org,2002:map", dump, flow_style=True)

    def to_bytes(self):
        return struct.pack(
            "!BBBHH", self.tag, self.modifiers.value, int(self.page) + (int(self.page2) << 4), int(self.code), int(self.code2)
        )

    @classmethod
    def from_bytes(cls, bytes):
        if cls.tag == bytes[0]:
            modifiers, pages, code1, code2 = struct.unpack("!BBHH", bytes[1:7])
            page1 = pages & 0xF
            page2 = pages >> 4
            return bytes[7:], cls(modifiers, page1, code1, page2, code2)


class KeyControl(Key):
    yaml_tag = "!ProfileKeyControl"
    yaml_loader = yaml.SafeLoader
    tag = 0x05

    def __init__(self, control):
        self.control = special_keys.CONTROL[int(control)]

    @classmethod
    def from_dict(cls, dct):
        if len(dct) == 1:
            return cls(dct["control"])

    @classmethod
    def to_yaml(cls, dumper, data):
        dump = {"control": int(data.control)}
        return dumper.represent_mapping("tag:yaml.org,2002:map", dump, flow_style=True)

    def to_bytes(self):
        return struct.pack("!BH", self.tag, int(self.control))

    @classmethod
    def from_bytes(cls, bytes):
        if cls.tag == bytes[0]:
            control = struct.unpack("!H", bytes[1:3])[0]
            return bytes[3:], cls(control)


class DeviceProfiles:
    def __init__(self, device):  # This doesn't get the profiles themselves, just the other information
        self.device = device
        response = self.device.feature_request(SupportedFeature.MODULAR_PROFILE_MANAGEMENT)
        self.default_editable = response[0] & 0x01
        self.host_profile = response[0] & 0x02
        self.always_active_protocol = response[0] & 0x04
        self.max_profiles = int(response[1])
        self.editable = response[2] & 0x01
        self.resetable = response[2] & 0x02
        self.disablable = response[2] & 0x04
        self.enableable = response[2] & 0x08
        self.triggerable = response[2] & 0x10
        self.get_power_on = response[2] & 0x20
        self.set_power_on = response[2] & 0x40
        self.get_enabled = response[2] & 0x80
        self.tags = self.supported_tags()
        self.profiles = self.profile_ids()

    def get_list(self, function, initial_bytes, size):
        lst = []
        offset = 0
        done = False
        packing = "B" if size == 1 else "!H" if size == 2 else None
        try:
            while not done:
                bytes = struct.pack(packing, offset)
                print("REQUEST", self.device.name, function, offset, initial_bytes, bytes)
                response = self.device.feature_request(
                    SupportedFeature.MODULAR_PROFILE_MANAGEMENT, function, initial_bytes, bytes
                )
                print("REQUEST", self.device.name, function, offset, initial_bytes, bytes, response)
                for off in range(0, 16, size):
                    e = struct.unpack(packing, response[off : off + size])[0]
                    if e:
                        lst.append(e)
                    else:
                        done = True
                        break
                offset += 16
        except exceptions.FeatureCallError:
            pass
        return lst

    def supported_tags(self):
        tags = self.get_list(0x10, b"", 2)
        print("Tags", self.device.name, tags)
        return tags

    def profile_ids(self):
        ids = self.get_list(0x40, b"", 1)
        profiles = {id: None for id in ids}
        print("Profile IDS", self.device.name, profiles)
        return profiles

    def read_profile(self, index):
        tags = self.get_list(0x50, struct.pack("B", index), 2)
        tags = [Tag(tag) for tag in tags]
        print("RProfile tags", self.device.name, index, tags)
        prof = Profile()
        for tag in tags:
            args = struct.pack("!BHB", index, tag, 0)
            result = self.device.feature_request(SupportedFeature.MODULAR_PROFILE_MANAGEMENT, 0x60, args)
            id, length = struct.unpack("!BH", result[0:3])
            bytes = b""
            while len(bytes) < length:
                result = self.device.feature_request(SupportedFeature.MODULAR_PROFILE_MANAGEMENT, 0x70, id)
                id += 1
                bytes = bytes + result[1:16]
            bytes = bytes[0:length]
            value = TagClasses[tag.name].from_bytes(bytes) if tag.name in TagClasses else bytes
            setattr(prof, tag.name, value)
        prof.Index = Index(index)
        return prof

    def get_profile_ids(self):
        print("GPI", self.device.name, list(self.profiles.keys()))
        for id in self.profiles.keys():
            yield id

    def get_profile(self, id, cached=True):
        if self.profiles[id] is None or not cached:
            prof = self.read_profile(id)
            self.profiles[id] = prof
        return self.profiles[id]


TagClasses = {
    Tag.ID.name: ID,
    Tag.Name.name: Name,
    Tag.FnKeyMapping.name: FnKeyMapping,
    Tag.KeyMapping.name: KeyMapping,
    Tag.Index.name: Index,
}


def load_profiles_from_yaml(filename):
    with open(filename) as file:
        profiles = yaml.safe_load(file)
    if profiles is None:
        profiles = []
    for prof in profiles:
        prof.yaml_post_process()
    print("LPFY", type(profiles), profiles)
    return profiles


def save_profiles_to_yaml(filename, profiles):
    print("SPTY", filename, type(profiles), profiles)
    with open(filename, "w") as file:
        yaml.dump(profiles, file, default_flow_style=None, width=150)
    return True
