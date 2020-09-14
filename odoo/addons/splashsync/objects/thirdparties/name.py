# -*- coding: utf-8 -*-
#
#  This file is part of SplashSync Project.
#
#  Copyright (C) 2015-2019 Splash Sync  <www.splashsync.com>
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  For the full copyright and license information, please view the LICENSE
#  file that was distributed with this source code.

from splashpy import const, Framework
from splashpy.componants import FieldFactory


class Name:
    """
    Manage Encode/Decode Concatenated Name
    """

    varfullname = {"first": "", "last": "", "legal": ""}

    def buildNameFields(self):
        FieldFactory.create(const.__SPL_T_VARCHAR__, "legal", "Legal Name")
        FieldFactory.microData("http://schema.org/Organization", "legalName")
        FieldFactory.isRequired()
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_VARCHAR__, "last", "Last Name")
        FieldFactory.microData("http://schema.org/Person", "givenName")
        FieldFactory.association('first')
        # ==================================================================== #
        FieldFactory.create(const.__SPL_T_VARCHAR__, "first", "First Name")
        FieldFactory.microData("http://schema.org/Person", "familyName")

    def getNameFields(self, index, field_id):
        if field_id == "legal":
            self._out[field_id] = Name.decodefullname(self)[field_id]
            self._in.__delitem__(index)
        if field_id == "first":
            self._out[field_id] = Name.decodefullname(self)[field_id]
            self._in.__delitem__(index)
        if field_id == "last":
            self._out[field_id] = Name.decodefullname(self)[field_id]
            self._in.__delitem__(index)

    def setNameFields(self, field_id, field_data):
        if field_data is None:
            field_data = ""
        if field_id == "legal":
            Name.varfullname[field_id] = Name.decodefullname(self)[field_id]
            if Name.isactualdatadifferent(self, field_id, field_data):
                Name.varfullname[field_id] = str(field_data).strip()
            self._in.__delitem__(field_id)
        if field_id == "first":
            Name.varfullname[field_id] = Name.decodefullname(self)[field_id]
            if Name.isactualdatadifferent(self, field_id, field_data):
                Name.varfullname[field_id] = str(field_data).strip()
            self._in.__delitem__(field_id)
        if field_id == "last":
            Name.varfullname[field_id] = Name.decodefullname(self)[field_id]
            if Name.isactualdatadifferent(self, field_id, field_data):
                Name.varfullname[field_id] = str(field_data).strip()
            self._in.__delitem__(field_id)
        if all(x not in self._in for x in ["first", "last", "legal"]):
            setattr(self.object, "name", Name.encodefullname(Name.varfullname["first"], Name.varfullname["last"], Name.varfullname["legal"]))

    def decodefullname(self):
        elements = {"first": "", "last": "", "legal": ""}
        fullname = str(getattr(self.object, "name")).strip()
        if fullname is None:
            return
        if " - " not in fullname:
            elements["legal"] = fullname
        if " - " in fullname:
            elements["legal"] = fullname.split(" - ")[-1].strip()
            residual = fullname.split(" - ")[0].strip()
            if ", " not in residual:
                elements["first"] = residual.strip()
            else:
                elements["first"] = residual.split(", ")[0].strip()
                elements["last"] = residual.split(", ")[-1].strip()
        return elements

    @staticmethod
    def encodefullname(first, last, legal):
        if legal == "":
            legal = "Legal Name to Define"
        if (isinstance(first, str)) and (len(first) > 0):
            if (isinstance(last, str)) and (len(last) > 0):
                result = first + ", " + last + " - " + legal   # first, last - legal
            else:
                result = first + " - " + legal                 # first - legal
        else:
            result = legal                                     # legal
        return result

    def isactualdatadifferent(self, field_id, field_data):
        actualfield = Name.decodefullname(self)[field_id]
        return field_data != actualfield
