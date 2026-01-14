OUTPUT_FORMAT("elf64-littleriscv", "elf64-littleriscv",
       "elf64-littleriscv")
OUTPUT_ARCH(riscv)
LD_FEATURE(SANE_EXPR)
ENTRY(_start)
PHDRS {
  attributes 0x70000003;
  text PT_LOAD;
  tdata PT_LOAD;
  tls PT_TLS;
  data PT_LOAD;
}
SECTIONS {
  .text __fw_text
  :
  {
    *(.start)
    *(.text.unlikely .text.*_unlikely .text.unlikely.*)
    *(.text.exit .text.exit.*)
    *(.text.startup .text.startup.*)
    *(.text.hot .text.hot.*)
    *(.text .stub .text.* .gnu.linkonce.t.*)
    *(.gnu.warning)
    . = ALIGN(4);
   } :text
  .tdata __fw_tls
  :
  {
    . = ALIGN(4);
    __ldm_tdata_init = .;
    *(.tdata.start)
    *(.tdata .tdata.* .gnu.linkonce.td.*)
    . = ALIGN(4);
    *(.tdata.end)
  } :tdata :tls
  .tbss
  :
  {
    *(.tbss.start)
    *(.tbss .tbss.* .gnu.linkonce.tb.* .tcommon)
    . = ALIGN(4);
    *(.tbss.end)
  } :tdata :tls
  .data __fw_data
  :
  {
    __ldm_data_start = .;
    *(.rodata .rodata.* .gnu.linkonce.r.*)
    *(.rodata1)
    *(.data.rel.ro.local* .gnu.linkonce.d.rel.ro.local.*) *(.data.rel.ro .data.rel.ro.* .gnu.linkonce.d.rel.ro.*)
    *(.srodata.cst16) *(.srodata.cst8) *(.srodata.cst4) *(.srodata.cst2) *(.srodata .srodata.*)
    *(.sdata .sdata.* .gnu.linkonce.s.*)
    *(.sdata2 .sdata2.* .gnu.linkonce.s2.*)
    *(.data .data.* .gnu.linkonce.d.*)
    *(.data1)
    . = ALIGN(4);
    __ldm_data_end = .;
  } :data
  .empty.ctors.dtors
  : AT(LOADADDR(.data) + (ADDR(.empty.ctors.dtors) - ADDR(.data)))
  {
    KEEP (*(.ctors .ctors.* .dtors .dtors.*))
  } :data
  .empty.init_array.fini_array
  : AT(LOADADDR(.empty.ctors.dtors) + (ADDR(.empty.init_array.fini_array) - ADDR(.empty.ctors.dtors)))
  {
    KEEP (*(.preinit_array))
    KEEP (*(SORT_BY_INIT_PRIORITY(.init_array.*)))
    KEEP (*(.init_array))
    KEEP (*(SORT_BY_INIT_PRIORITY(.fini_array.*)))
    KEEP (*(.fini_array))
  } :data
  .bss
  : AT(LOADADDR(.empty.init_array.fini_array) + (ADDR(.bss) - ADDR(.empty.init_array.fini_array)))
  {
    __ldm_bss_start = .;
    *(.sbss2 .sbss2.* .gnu.linkonce.sb2.*)
    *(.dynsbss)
    *(.sbss .sbss.* .gnu.linkonce.sb.*)
    *(.scommon)
    *(.dynbss)
    *(.bss .bss.* .gnu.linkonce.b.*)
    *(COMMON)
    . = ALIGN(4);
    __ldm_bss_end = .;
  } :data
  .segments 0 (INFO)
  :
  {
    LONG(ADDR(.text)) LONG(ADDR(.text)) LONG(__text_size)
    LONG(ADDR(.tdata)) LONG(__ldm_tdata_init)
       LONG(__tls_size - __min_stack - (__ldm_tdata_init - ADDR(.tdata)))
    LONG(ADDR(.data)) LONG(__ldm_data_start) LONG(__data_size - (__ldm_data_start - ADDR(.data)))
  }
  .riscv.attributes 0 : { *(.riscv.attributes) } :attributes
}
