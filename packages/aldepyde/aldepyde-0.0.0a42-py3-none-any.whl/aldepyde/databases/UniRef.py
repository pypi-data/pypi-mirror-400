import zlib
import re
from aldepyde.databases._database import streamable_database
from aldepyde.data.distributions.standards import source_head, distribution_head
from aldepyde.utils import ProgressBar
import os
import json
from dataclasses import dataclass


@dataclass
class UniProtFastaRecord():
    header: str
    sequence: str

class uniref_parser(streamable_database):
    def __init__(self):
        super().__init__()

    # TODO single entry parsing
    # TODO store metadata upon request
    # TODO implement abstract methods



    @staticmethod
    def _stream_uniref_plain(path, chunk_size=8192, use_progress_bar=False, compressed=False):
        raw_stream, size = streamable_database.open_stream(path)
        pbar = ProgressBar(size//chunk_size) if use_progress_bar else None
        decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
        try:
            while True:
                if not compressed:
                    decomp_chunk = raw_stream.read(chunk_size)
                else:
                    comp_chunk = raw_stream.read(chunk_size)
                    decomp_chunk = decompressor.decompress(comp_chunk)
                    if comp_chunk == b"":
                        break
                if not decomp_chunk:
                    break
                if pbar is not None:
                    pbar.update()
                yield decomp_chunk
            final = decompressor.flush()
            if final:
                yield final
        finally:
            raw_stream.close()

    @staticmethod
    def _next_link(headers) -> str|None:
        link_statement = headers.get('Link')
        if link_statement is None:
            return None
        m = re.match(r'<([^>]+)>', link_statement)
        return m.group(1)

    @staticmethod
    def _stream_paginated_plain(url, chunk_size=8192, compressed=False):
        try:
            while True:
                raw_stream, size, headers = streamable_database.open_stream(url, provide_headers=True)
                decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)

                while True:
                    if not compressed:
                        decomp_chunk = raw_stream.read(chunk_size)
                    else:
                        comp_chunk = raw_stream.read(chunk_size)
                        decomp_chunk = decompressor.decompress(comp_chunk)
                    if not decomp_chunk:
                        break
                    yield decomp_chunk
                final = decompressor.flush()
                if final:
                    yield final
                url = uniref_parser._next_link(headers)
                # print(url)
                if url is None:
                    break
                raw_stream.close()
        finally:
            raw_stream.close()

    @staticmethod
    def stream_uniref_gz(filepath, chunk_size=8192, use_progress_bar=False):
        raw_stream, size = streamable_database.open_stream(filepath)
        pbar = ProgressBar(size//chunk_size) if use_progress_bar else None
        decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
        try:
            while True:
                comp_chunk = raw_stream.read(chunk_size)
                if not comp_chunk:
                    break
                if pbar is not None:
                    pbar.update()
                decomp_chunk = decompressor.decompress(comp_chunk)
                if decomp_chunk:
                    yield decomp_chunk
            final = decompressor.flush()
            if final:
                yield final
        finally:
            raw_stream.close()

    @staticmethod
    def download_paginated(url, destination, chunk_size=8192):
        with open(destination, 'wb') as fp:
            while True:
                raw_stream, size, headers = streamable_database.open_stream(url, provide_headers=True)
                while True:
                    chunk = raw_stream.read(chunk_size)
                    if not chunk:
                        break
                    fp.write(chunk)
                url = uniref_parser._next_link(headers)
                if url is None:
                    break
                raw_stream.close()

    @staticmethod
    def download_file(url, destination, chunk_size=8192, use_progress_bar=False):
        raw_stream, size = streamable_database.open_stream(url)
        pbar = ProgressBar(size // chunk_size) if use_progress_bar else None
        with open(destination, 'wb') as fp:
            while True:
                chunk = raw_stream.read(chunk_size)
                if not chunk:
                    break
                if pbar is not None:
                    pbar.update()
                fp.write(chunk)


    @staticmethod
    def _stitch_streamed_sequences(stream):
        buffer = b''
        one_record_re = re.compile(br'\A>.*(?:\n(?!>).*?)*(?=\n>|$)')
        for chunk in stream:
            buffer += chunk
            # Take out just one entry at a time. Don't be a hero and shatter the whole chunk
            while buffer.count(b'\n>') > 0:
                m = one_record_re.match(buffer)
                entry = m.group(0)
                buffer = buffer[len(entry) + 1:]
                spl = entry.split(b'\n')
                header = spl[0].decode('utf-8')
                sequence = b''.join(spl[1:]).decode('utf-8')
                yield UniProtFastaRecord(header=header, sequence=sequence)
        spl = buffer.split(b'\n')
        header = spl[0].decode('utf-8')
        sequence = b''.join(spl[1:]).decode('utf-8')
        yield UniProtFastaRecord(header=header, sequence=sequence)
        #         yield  b"".join(entry.split(b'\n')[1:])
        # yield b"".join(buffer.split(b'\n')[1:])

        #         sequences = [b">" + seq for seq in buffer.split(b">") if seq != b""]
        #         buffer = buffer[buffer.rfind(b">"):]
        #         ret_l = [b"".join(sequence.split(b'\n')[1:]).replace(b"\n", b"") for sequence in sequences[:-1]]
        #         for s in ret_l:
        #             yield s if not as_str else s.decode()
        # yield uniref_parser._final_sequence(buffer) if not as_str else uniref_parser._final_sequence(buffer).decode()

    @staticmethod
    def _final_sequence(buffer):
        lines = buffer.split(b'\n')
        return b"".join(lines[1:])

    @staticmethod
    def stream_file(filepath, chunk_size=8192, use_progress_bar=False, stitch=False):
        with open(filepath, 'rb') as fp:
            magic_start = fp.read(2)
        compressed = True if magic_start == b'\x1f\x8b' else False
        if not stitch:
            yield from uniref_parser._stream_uniref_plain(filepath, chunk_size=chunk_size,
                                                      use_progress_bar=use_progress_bar, compressed=compressed)
        else:
            yield from uniref_parser._stitch_streamed_sequences(uniref_parser._stream_uniref_plain(filepath, chunk_size=chunk_size,
                                                      use_progress_bar=use_progress_bar, compressed=compressed))

    @staticmethod
    def stream_query(url, chunk_size=8192, use_progress_bar=False, stitch=False):
        paginated = True if 'size' in url else False
        compressed = True if 'compressed' in url else False
        if not paginated:
            if not stitch:
                yield from uniref_parser._stream_uniref_plain(url, chunk_size=chunk_size, use_progress_bar=use_progress_bar, compressed=compressed)
            else:
                yield from uniref_parser._stitch_streamed_sequences(uniref_parser._stream_uniref_plain(
                    url,chunk_size=chunk_size, use_progress_bar=use_progress_bar, compressed=compressed))
        else:
            if not stitch:
                yield from uniref_parser._stream_paginated_plain(url, chunk_size=chunk_size, compressed=compressed)
            else:
                yield from uniref_parser._stitch_streamed_sequences(uniref_parser._stream_paginated_plain(
                    url,chunk_size=chunk_size, compressed=compressed))

    @staticmethod
    def download_query(url, destination, chunk_size=8192, use_progress_bar=False):
        paginated = True if 'size' in url else False
        if not paginated:
            uniref_parser.download_file(url, destination=destination,
                                        chunk_size=chunk_size, use_progress_bar=use_progress_bar)
        else:
            uniref_parser.download_paginated(url, destination=destination,
                                        chunk_size=chunk_size)

    @staticmethod
    def stream_uniref50(chunk_size=8192, use_progress_bar=False, stitch=False):
        if not stitch:
            yield from uniref_parser.stream_uniref_gz('https://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref50/uniref50.fasta.gz',
                                                  chunk_size=chunk_size, use_progress_bar=use_progress_bar)
        else:
            yield from uniref_parser._stitch_streamed_sequences(uniref_parser.stream_uniref_gz(
                'https://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref50/uniref50.fasta.gz',
                                                  chunk_size=chunk_size, use_progress_bar=use_progress_bar))

    @staticmethod
    def stream_uniref90(chunk_size=8192, use_progress_bar=False, stitch=False):
        if not stitch:
            yield from uniref_parser.stream_uniref_gz('https://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref90/uniref90.fasta.gz',
                                                  chunk_size=chunk_size, use_progress_bar=use_progress_bar)
        else:
            yield from uniref_parser._stitch_streamed_sequences(uniref_parser.stream_uniref_gz(
                'https://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref90/uniref90.fasta.gz',
                chunk_size=chunk_size, use_progress_bar=use_progress_bar))

    @staticmethod
    def stream_uniref100(chunk_size=8192, use_progress_bar=False, stitch=False):
        if not stitch:
            yield from uniref_parser.stream_uniref_gz('https://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref100/uniref100.fasta.gz',
                                                  chunk_size=chunk_size, use_progress_bar=use_progress_bar)
        else:
            yield from uniref_parser._stitch_streamed_sequences(uniref_parser.stream_uniref_gz(
                'https://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref100/uniref100.fasta.gz',
                chunk_size=chunk_size, use_progress_bar=use_progress_bar))

    @staticmethod
    def download_uniref50(destination='uniref50.fasta.gz', chunk_size=8192, use_progress_bar=False):
        uniref_parser.download_file('https://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref50/uniref50.fasta.gz', destination=destination,
                                    chunk_size=chunk_size, use_progress_bar=use_progress_bar)

    @staticmethod
    def download_uniref90(destination='uniref90.fasta.gz', chunk_size=8192, use_progress_bar=False):
        uniref_parser.download_file('https://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref90/uniref90.fasta.gz', destination=destination,
                                    chunk_size=chunk_size, use_progress_bar=use_progress_bar)
    @staticmethod
    def download_uniref100(destination='uniref100.fasta.gz', chunk_size=8192, use_progress_bar=False):
        uniref_parser.download_file('https://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref100/uniref100.fasta.gz', destination=destination,
                                    chunk_size=chunk_size, use_progress_bar=use_progress_bar)



            # yield from uniref_parser._stream_uniref_plain(filepath, chunk_size=chunk_size,
            #                                               use_progress_bar=use_progress_bar, stitch=stitch)

    @staticmethod
    def aa_frequency(path:str, json_dest:str|None = None, as_probs=False, chunk_size=8192, use_progress_bar=False) -> dict:
        is_filepath = True if os.path.isfile(path) else False
        if is_filepath:
            generator = uniref_parser.stream_file(path, chunk_size=chunk_size, use_progress_bar=use_progress_bar, stitch=True)
        else:
            generator = uniref_parser.stream_query(path, chunk_size=chunk_size, use_progress_bar=use_progress_bar, stitch=True)
        occurances = dict()
        for record in generator:
            for c in record.sequence:
                if c not in occurances:
                    occurances[c] = 0
                occurances[c] += 1
        if as_probs:
            total = sum(occurances.values())
            for key in occurances:
                occurances[key] = occurances[key] / total
        if json_dest is not None:
            json_dict = {
                distribution_head : occurances,
                source_head : path
            }
            with open(json_dest, 'w') as fp:
                json.dump(json_dict, fp, indent=3)
        return occurances