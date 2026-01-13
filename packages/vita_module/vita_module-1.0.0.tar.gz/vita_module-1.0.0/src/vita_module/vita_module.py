import struct
import zlib
from dataclasses import dataclass
from typing import Self, BinaryIO

def c_str(data: bytes | bytearray) -> str:
    return data[:data.index(b"\x00")].decode()

class Struct:
    _format: str = ""
    _size: int = 0
    @classmethod
    def unpack(cls, data: bytes | bytearray) -> Self:
        fields = struct.unpack(cls._format, data[:cls._size])
        return cls(*fields)
    @classmethod
    def read_from(cls, reader: BinaryIO) -> Self:
        return cls.unpack(reader.read(cls._size))
    @classmethod
    def read_at(cls, reader, offset) -> Self:
        return cls.unpack(reader.read_at(offset, cls._size))

@dataclass
class SceModuleInfo(Struct):
    _format = "<hh27sbIIIIIIIIIIIIIII"
    _size = struct.calcsize(_format)
    attributes: int
    version: int
    module_name: bytes
    type: int
    gp_value: int
    exportsStart: int
    exportsEnd: int
    importsTop: int
    importsEnd: int
    module_nid: int
    tlsStart: int
    tlsFileSize: int
    tlsMemSize: int
    module_start: int
    module_stop: int
    exidx_top: int
    exidx_end: int
    extab_start: int
    extab_end: int

@dataclass
class SceModuleImports(Struct):
    _format = "<HHHHHHIIIIIIIIII"
    _size = struct.calcsize(_format)
    size: int
    version: int
    attribute: int
    num_functions: int
    num_vars: int
    num_tls_vars: int
    reserved1: int
    library_nid: int
    library_name: int
    reserved2: int
    func_nid_table: int
    func_entry_table: int
    var_nid_table: int
    var_entry_table: int
    tls_nid_table: int
    tls_entry_table: int


@dataclass
class SceModuleImports2(Struct):
    _format = "hhhhhIIIIII"
    _size = struct.calcsize(_format)
    size: int
    version: int
    attribute: int
    num_functions: int
    num_vars: int
    library_nid: int
    library_name: int
    func_nid_table: int
    func_entry_table: int
    var_nid_table: int
    var_entry_table: int


@dataclass
class SceModuleLibaryExports(Struct):
    _format = "BBHHHHHBBBBIIII"
    _size = 32
    size: int
    _pad: int
    version: int
    attr: int
    num_functions: int
    num_variables: int
    num_tls_vars: int
    hashinfo: int
    hashinfotls: int
    _pad2: int
    nidaltsets: int
    library_nid: int
    library_name: int
    nid_table: int
    addr_table: int


@dataclass
class ElfHeader(Struct):
    _format = "QQHHIIIIIHHHHHH"
    _size = 52
    e_ident_1: int
    e_ident_2: int
    e_type: int
    e_machine: int
    e_version: int
    e_entry: int
    e_phoff: int
    e_shoff: int
    e_flags: int
    e_ehsize: int
    e_phentsize: int
    e_phnum: int
    e_shentsize: int
    e_shnum: int
    e_shstrndx: int

@dataclass
class ElfPhdr(Struct):
    _format = "IIIIIIII"
    _size = 32
    p_type: int
    p_offset: int
    p_vaddr: int
    p_paddr: int
    p_filesz: int
    p_memsz: int
    p_flags: int
    p_align: int

@dataclass
class SegmentInfo(Struct):
    _format = "QQIIII"
    _size = 32
    offset: int
    size: int
    compressed: int
    field_14: int
    plaintext: int
    field_1C: int


class ModuleImportLibrary:
    info: SceModuleImports | SceModuleImports2
    nids: dict[int, int]
    name: str
    def __init__(self, info: SceModuleImports | SceModuleImports2, nids: dict[int, int], name: str):
        self.info = info
        self.nids = nids
        self.name = name

class ModuleExportLibrary:
    info: SceModuleLibaryExports
    nids: dict[int, int]
    name: str
    def __init__(self, info: SceModuleLibaryExports, nids: dict[int, int], name: str):
        self.info = info
        self.nids = nids
        self.name = name

class VitaModule:
    BASE = 0x81000000
    
    elf_header: ElfHeader
    segments: list[tuple[int,bytearray]]
    text_seg: bytearray
    module_info: SceModuleInfo
    module_name: str
    exports: dict[int, ModuleExportLibrary]
    imports: dict[int, ModuleImportLibrary]
    
    def _read_elf(self, reader: BinaryIO):
        reader.seek(0)
        elf_offset = 0
        is_self = reader.read(4) == b"SCE\0"
        if is_self:
            reader.seek(32 + 4*8, 0)
            elf_offset = int.from_bytes(reader.read(8), "little")
            phdr_offset = int.from_bytes(reader.read(8), "little")
            _ = reader.read(8)
            segment_info_offset = int.from_bytes(reader.read(8), "little")

        reader.seek(elf_offset)
        elf = ElfHeader.read_from(reader)
        if not is_self:
            phdr_offset = elf.e_phoff
        
        self.elf_header = elf
        self.segments = []
        
        reader.seek(phdr_offset)
        phdrs: list[ElfPhdr] = []
        for i in range(elf.e_phnum):
            phdr = ElfPhdr.read_from(reader)
            phdrs.append(phdr)
        
        if is_self:
            segment_infos: list[SegmentInfo] = []
            reader.seek(segment_info_offset)
            for i in range(elf.e_phnum):
                segment_info = SegmentInfo.read_from(reader)
                segment_infos.append(segment_info)
            
            for i in range(elf.e_phnum):
                phdr = phdrs[i]
                if phdr.p_type != 1:
                    continue
                segment_info = segment_infos[i]
                if segment_info.plaintext != 2:
                    raise ValueError("encrypted self")
                reader.seek(segment_info.offset)
                data = reader.read(segment_info.size)
                if segment_info.compressed == 2:
                    data = zlib.decompressobj().decompress(data)
                data_array = bytearray(data)
                self.segments.append((phdr.p_vaddr, data_array))
        else:
            for i in range(elf.e_phnum):
                phdr = phdrs[i]
                if phdr.p_type != 1:
                    continue
                reader.seek(phdr.p_offset)
                data = reader.read(phdr.p_filesz)
                data_array = bytearray(data)
                self.segments.append((phdr.p_vaddr, data_array))
        self.text_seg = self.segments[0][1]
    
    def _read_module_info(self):
        entry: int = self.elf_header.e_entry
        segment_num: int = (entry >> 30) & 0x3
        info_offset: int = entry & 0x3fffffff
        self.module_info = SceModuleInfo.read_at(self, VitaModule.BASE + info_offset)
        self.module_name = c_str(self.module_info.module_name)
        
    def _read_imports(self):
        imports_size = self.module_info.importsEnd - self.module_info.importsTop
        imports_data = self.read_at(VitaModule.BASE + self.module_info.importsTop, imports_size)
        offset = 0
        self.imports = {}
        while offset < imports_size:
            size = int.from_bytes(imports_data[offset:][:2], "little")
            if size == SceModuleImports._size:
                imp = SceModuleImports.unpack(imports_data[offset:])
            elif size == SceModuleImports2._size:
                imp = SceModuleImports2.unpack(imports_data[offset:])
            else:
                raise ValueError("unknown import size")
            
            nids = {}
            if imp.func_nid_table != 0:
                for i in range(imp.num_functions):
                    nid = self.read_uint32( imp.func_nid_table + i*4)
                    entry = self.read_uint32(imp.func_entry_table + i*4)
                    nids[nid] = entry

            lib_name = self.read_cstring(imp.library_name)
            module_import = ModuleImportLibrary(imp, nids, lib_name)
            self.imports[imp.library_nid] = module_import
            offset += imp.size
    
    def _read_exports(self):
        exports_size = self.module_info.exportsEnd - self.module_info.exportsStart
        exports_data = self.read_at(VitaModule.BASE + self.module_info.exportsStart, exports_size)
        offset = 0
        self.exports = {}
        while offset < exports_size:
            lib = SceModuleLibaryExports.unpack(exports_data[offset:])
            if lib.library_nid == 0 and lib.library_name == 0:
                lib_name = "unnamed"
            else:
                lib_name = self.read_cstring(lib.library_name)

            nids: dict[int,int] = {}
            for i in range(lib.num_functions):
                nid = self.read_uint32(lib.nid_table + i*4)
                entry = self.read_uint32(lib.addr_table + i*4)
                nids[nid] = entry
            self.exports[lib.library_nid] = ModuleExportLibrary(lib, nids, lib_name)
            offset += lib.size
    
    @classmethod
    def read_from(cls, reader: BinaryIO) -> "VitaModule":
        module = cls()
        module._read_elf(reader)
        module._read_module_info()
        module._read_imports()
        module._read_exports()
        return module
    
    def read_at(self, offset: int, size: int) -> bytearray:
        for vaddr, data in self.segments:
            if vaddr <= offset < vaddr + len(data):
                local_offset = offset - vaddr
                return data[local_offset:local_offset+size]
        raise ValueError(f"Offset {offset:X} not in any segment")
    
    def read_uint32(self, offset: int) -> int:
        data = self.read_at(offset, 4)
        return int.from_bytes(data, "little") & 0xFFFFFFFF
    
    def read_cstring(self, offset: int, max_len=256, strict=True) -> str:
        data = self.read_at(offset, max_len)
        end = data.find(b"\0")
        if end == -1:
            raise ValueError("no null terminator")
        return data[:end].decode("utf-8", "strict" if strict else "replace")
    
    def get_export_address(self, library_nid: int, function_nid: int) -> int | None:
        if library_nid not in self.exports:
            return None
        lib_export = self.exports[library_nid]
        if function_nid not in lib_export.nids:
            return None
        return lib_export.nids[function_nid]

    def find(self, needle: bytes) -> int:
        for vaddr, data in self.segments:
            offset = data.find(needle)
            if offset == -1:
                continue
            return vaddr+offset
        return -1
