# -*- coding: utf-8 -*-
#
#
# This file is a part of 'linuxacademy-dl' project.
#
# Copyright (c) 2016-2017, Vassim Shahir
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

from __future__ import unicode_literals, absolute_import, \
                    print_function, with_statement
from Crypto.Cipher import AES
from io import BytesIO
from .exceptions import HLSDecryptException


class HLSDecryptAES128(object):
    def __init__(self, chunk_stream, key, iv):
        self.chunk_stream = chunk_stream
        self.key = key
        self.iv = self.iv_from_int(
            int(iv, 16) if type(iv) in (type(u''), type(b'')) else iv
        )

    @property
    def chunk_stream(self):
        return self.__chunk_stream

    @chunk_stream.setter
    def chunk_stream(self, val):
        if hasattr(val, 'read'):
            self.__chunk_stream = val
        else:
            raise HLSDecryptException('chunk_stream must be a '
                                      'file like object')

    def iv_from_int(self, int_iv):
        return b''.join(chr((int_iv >> (i * 8)) & 0xFF)
                        for i in range(AES.block_size)[::-1])

    def decrypt(self):
        decrypted_chunk = BytesIO()
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)

        next_chunk = ''
        finished = False

        while not finished:
            chunk, next_chunk = next_chunk, \
                cipher.decrypt(self.chunk_stream.read(1024 * AES.block_size))
            if len(next_chunk) == 0:
                padding_length = ord(chunk[-1])
                chunk = chunk[:-padding_length]
                finished = True
            decrypted_chunk.write(bytes(chunk))
        decrypted_chunk.seek(0)
        return decrypted_chunk
