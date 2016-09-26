# Htool - HyperText Object-Oriented Layer.
# Copyright (C) 2016 Dario Giovannetti <dev@dariogiovannetti.net>
#
# This file is part of Htool.
#
# Htool is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Htool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Htool.  If not, see <http://www.gnu.org/licenses/>.

# It shouldn't be necessary to expose the dom module
from . import docs, text
# Only expose the tags and misc classes directly
from .misc import *
from .tags import *
