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

from __future__ import unicode_literals, print_function, with_statement
from . import __title__
from ._session import session
from concurrent.futures import ThreadPoolExecutor
from requests_futures.sessions import FuturesSession

import os
import subprocess
import multiprocessing
import tempfile
import logging

logger = logging.getLogger(__title__)


class DownloadEngine(object):

    POOL_SIZE = multiprocessing.cpu_count() * 2

    def __init__(self, use_ffmpeg=True, skip_existing=True):
        self.use_ffmpeg = use_ffmpeg
        self.skip_existing = skip_existing
        self.session = FuturesSession(
            executor=ThreadPoolExecutor(max_workers=self.POOL_SIZE),
            session=session
        )

    def ts_download(self, ts_chunk_urls, save_as):
        try:
            contents = [self.session.get(url) for url in ts_chunk_urls]

            ts_accumulator = tempfile.NamedTemporaryFile() \
                if self.use_ffmpeg \
                else open(save_as, "wb")

            for content in contents:
                itm = content.result()
                ts_accumulator.write(itm.content)

            if self.use_ffmpeg:
                self.ffmpeg_process(ts_accumulator.name, save_as)

        except OSError as exc:
            logger.critical('Failed to download: %s', exc)

        finally:
            ts_accumulator.close()

    def __call__(self, ts_chunk_urls, save_to, file_name):
        try:
            os.makedirs(save_to)
        except:
            pass

        final_path = os.path.join(save_to, file_name)

        if self.skip_existing and os.path.exists(final_path):
            logger.info("Skipping already existing file {}".format(final_path))
        else:
            logger.info("Downloading {}".format(final_path))
            self.ts_download(ts_chunk_urls, final_path)
            logger.info("Downloaded {}".format(final_path))

    def ffmpeg_process(self, input_file_name, output_file_name):
        command = [
            'ffmpeg',
            '-i', input_file_name,
            '-y',
            '-bsf:a', 'aac_adtstoasc',
            '-vcodec', 'copy',
            '-c', 'copy',
            '-crf', '50',
            '-f', 'mp4', output_file_name
        ]
        logger.debug("Executin FFMPEG Command {}".format(' '.join(command)))
        subprocess.call(command)
