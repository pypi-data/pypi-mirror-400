#
#      Licensed to the Apache Software Foundation (ASF) under one
#      or more contributor license agreements.  See the NOTICE file
#      distributed with this work for additional information
#      regarding copyright ownership.  The ASF licenses this file
#      to you under the Apache License, Version 2.0 (the
#      "License"); you may not use this file except in compliance
#      with the License.  You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#      Unless required by applicable law or agreed to in writing,
#      software distributed under the License is distributed on an
#      "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#      KIND, either express or implied.  See the License for the
#      specific language governing permissions and limitations
#      under the License.
#

"""
This module contains exceptions used throughout the API.
"""


class CmisException(Exception):
    """
    Common base class for all exceptions.
    """

    def __init__(self, status=None, url=None, details=None):
        Exception.__init__(self, f"Error {status} at {url} \n {details}")
        self.status = status
        self.url = url
        self.details = details


class InvalidArgumentException(CmisException):
    """InvalidArgumentException"""


class ObjectNotFoundException(CmisException):
    """ObjectNotFoundException"""


class NotSupportedException(CmisException):
    """NotSupportedException"""


class PermissionDeniedException(CmisException):
    """PermissionDeniedException"""


class RuntimeException(CmisException):
    """RuntimeException"""


class ConstraintException(CmisException):
    """ConstraintException"""


class ContentAlreadyExistsException(CmisException):
    """ContentAlreadyExistsException"""


class FilterNotValidException(CmisException):
    """FilterNotValidException"""


class NameConstraintViolationException(CmisException):
    """NameConstraintViolationException"""


class StorageException(CmisException):
    """StorageException"""


class StreamNotSupportedException(CmisException):
    """StreamNotSupportedException"""


class UpdateConflictException(CmisException):
    """UpdateConflictException"""


class VersioningException(CmisException):
    """VersioningException"""
