#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation
# All rights reserved.
#
# Distributed under the terms of the MIT License
#-------------------------------------------------------------------------

from io import BytesIO
from pyfindvs.msbuildcompiler.options import GlobalOptionsBase, ItemOptionsBase

import pkgutil
import os.path
import xml.etree.ElementTree as ET

class Template:
    _NS = 'http://schemas.microsoft.com/developer/msbuild/2003'
    _NSD = {'n': _NS}

    def __init__(self, template='vcxproj.template'):
        self.template = template
        ET.register_namespace('', self._NS)
        self.root = ET.ElementTree()
        if os.path.isfile(template):
            self.root.parse(template)
        else:
            self.root.parse(BytesIO(pkgutil.get_data('pyfindvs.msbuildcompiler', template)))

    def merge_options(self, *options):
        for opts in options:
            if isinstance(opts, GlobalOptionsBase):
                configuration, platform = getattr(opts, 'Configuration', None), getattr(opts, 'Platform', None)
                if configuration and platform:
                    pc = self.root.find("n:ItemGroup[@Label='ProjectConfigurations']/n:ProjectConfiguration", self._NSD)
                    pc.set('Include', '{}|{}'.format(configuration, platform))
                    pc.find("n:Configuration", self._NSD).text = configuration
                    pc.find("n:Platform", self._NSD).text = platform

                go = self.root.find("n:PropertyGroup[@Label='{}']".format(opts._PropertyGroup), self._NSD)
                for prop_name in dir(opts):
                    if prop_name[0] not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                        continue
                    value = getattr(opts, prop_name)
                    e = go.find("n:" + prop_name, self._NSD)
                    if e:
                        if value:
                            e.text = value
                        else:
                            go.remove(e)
                    else:
                        if value:
                            ET.SubElement(go, prop_name).text = value
            elif isinstance(opts, ItemOptionsBase):
                idg_tag = opts._ItemDefinitionGroup
                idg = self.root.find('n:ItemDefinitionGroup/n:{}'.format(idg_tag), self._NSD)
                for prop_name in dir(opts):
                    if prop_name[0] not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                        continue
                    value = getattr(opts, prop_name)
                    if not value:
                        continue
                    ET.SubElement(idg, prop_name).text = value
            else:
                raise TypeError("unsupported options '{}'".format(type(opts)))

    def add_items(self, item_type, items):
        ig = self.root.find("n:ItemGroup[@Label='Sources']", self._NSD)
        for item in items:
            if isinstance(item, str):
                ET.SubElement(ig, item_type).set('Include', item)
            elif isinstance(item, dict):
                e = ET.SubElement(ig, item_type)
                for k, v in item.items():
                    if k == 'Include':
                        e.set(k, v)
                    else:
                        ET.SubElement(e, k).text = v
            else:
                raise TypeError('unsupported type for item: {!r}'.format(type(item)))

    def save(self, file):
        self.root.write(file, encoding='utf-8', xml_declaration=True)

    def __str__(self):
        raw_f = BytesIO()
        self.save(raw_f)
        return raw_f.getvalue().decode('utf-8')

    def __repr__(self):
        return '<{} from {}>'.format(type(self).__name__, self.template)
