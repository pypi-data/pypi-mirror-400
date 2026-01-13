
/* clang-format off */
{%- for interface in interfaces %}
  {%- set registers = interface.regs %}
  {%- for reg in registers  %}
    {%- for offset in reg.offsets %}
      {%- set multireg_idx = loop.index0 %}
      {%- set reg_suffix = ('_' ~ multireg_idx|string) if reg.offsets|length > 1 %}
REG32({{ reg.name|upper ~ reg_suffix }}, {{ "0x{:x}u".format(offset) }})
      {%- for field in reg.fields %}
        {%- set field_name = ('_' ~ field.name|lower ~ reg_suffix) if reg.is_multifields %}
    FIELD({{ reg.name|upper ~ reg_suffix }}, {{ field.name }}, {{ "{}u, {}u".format(field.lsb, field.width) }})
      {%- endfor %}
    {%- endfor %}
  {%- endfor %}
{%- endfor %}
/* clang-format on */

#define R32_OFF(_r_) ((_r_) / sizeof(uint32_t))

#define R_LAST_REG (R_TIMEOUT_CTRL)
#define REGS_COUNT (R_LAST_REG + 1u)
#define REGS_SIZE  (REGS_COUNT * sizeof(uint32_t))
#define REG_NAME(_reg_) \
    ((((_reg_) <= REGS_COUNT) && REG_NAMES[_reg_]) ? REG_NAMES[_reg_] : "?")

#define REG_NAME_ENTRY(_reg_) [R_##_reg_] = stringify(_reg_)
static const char *REG_NAMES[REGS_COUNT] = {
    /* clang-format off */
{%- for interface in interfaces %}
  {%- set registers = interface.regs %}
  {%- for reg in registers  %}
    {%- for offset in reg.offsets %}
      {%- set multireg_idx = loop.index0 %}
      {%- set reg_suffix = ('_' ~ multireg_idx|string) if reg.offsets|length > 1 %}
    REG_NAME_ENTRY({{ reg.name ~ reg_suffix }}),
    {%- endfor %}
  {%- endfor %}
{%- endfor %}
    /* clang-format on */
};
#undef REG_NAME_ENTRY

struct {{name|upper}}State {
    SysBusDevice parent_obj;
    MemoryRegion mmio;

    uint32_t regs[REGS_COUNT];

    char *ot_id;
    uint32_t pclk;
    CharBackend chr;
};


static int {{name|lower}}_can_receive(void *opaque)
{
   {{name|upper}}State *s = opaque;

    return 0;
}

static uint64_t {{name|lower}}_read(void *opaque, hwaddr addr, unsigned size)
{
   {{name|upper}}State *s = opaque;
    (void)size;
    uint32_t val32;

    hwaddr reg = R32_OFF(addr);
    switch (reg) {
{%- for interface in interfaces %}
  {%- set registers = interface.regs %}
  {%- for reg in registers  %}
    {%- for offset in reg.offsets %}
      {%- set multireg_idx = loop.index0 %}
      {%- set reg_suffix = ('_' ~ multireg_idx|string) if reg.offsets|length > 1 %}
    case R_{{ reg.name|upper ~ reg_suffix }}:
    {%- endfor %}
  {%- endfor %}
{%- endfor %}
    default:
        qemu_log_mask(LOG_GUEST_ERROR, "%s: Bad offset 0x%" HWADDR_PRIx "\n",
                      __func__, addr);
        val32 = 0;
        break;
    }

    return (uint64_t)val32;
}

static void {{name|lower}}_write(void *opaque, hwaddr addr, uint64_t val64,
                          unsigned size)
{
    {{name|upper}}State *s = opaque;
    (void)size;
    uint32_t val32 = val64;

    hwaddr reg = R32_OFF(addr);

    uint32_t pc = ibex_get_current_pc();

    switch (reg) {
{%- for interface in interfaces %}
  {%- set registers = interface.regs %}
  {%- for reg in registers  %}
    {%- for offset in reg.offsets %}
      {%- set multireg_idx = loop.index0 %}
      {%- set reg_suffix = ('_' ~ multireg_idx|string) if reg.offsets|length > 1 %}
    case R_{{ reg.name|upper ~ reg_suffix }}:
    {%- endfor %}
  {%- endfor %}
{%- endfor %}
    default:
        qemu_log_mask(LOG_GUEST_ERROR, "%s: Bad offset 0x%" HWADDR_PRIx "\n",
                      __func__, addr);
        break;
    }
}

static const MemoryRegionOps {{name|lower}}_ops = {
    .read = {{name|lower}}_read,
    .write = {{name|lower}}_write,
    .endianness = DEVICE_NATIVE_ENDIAN,
    .impl.min_access_size = 4,
    .impl.max_access_size = 4,
};


static Property {{name|lower}}_properties[] = {
    DEFINE_PROP_STRING("ot_id", Ot{{name|upper}}State, ot_id),
    DEFINE_PROP_CHR("chardev", Ot{{name|upper}}State, chr),
    DEFINE_PROP_UINT32("pclk", Ot{{name|upper}}State, pclk, 0u),
    DEFINE_PROP_END_OF_LIST(),
};

static int {{name|lower}}_be_change(void *opaque)
{
    {{name|upper}}State *s = opaque;

    qemu_chr_fe_set_handlers(&s->chr, {{name|lower}}_can_receive, {{name|lower}}_receive,
                             NULL, {{name|lower}}_be_change, s, NULL, true);

    if (s->watch_tag > 0) {
        g_source_remove(s->watch_tag);
        // NOLINTNEXTLINE(clang-analyzer-optin.core.EnumCastOutOfRange)
        s->watch_tag = qemu_chr_fe_add_watch(&s->chr, G_IO_OUT | G_IO_HUP,
                                             {{name|lower}}_watch_cb, s);
    }

    return 0;
}

static void {{name|lower}}_reset(DeviceState *dev)
{
    {{name|upper}}State *s = {{name|upper}}(dev);

    memset(&s->regs[0], 0, sizeof(s->regs));

    {{name|lower}}_update_irqs(s);
    ibex_irq_set(&s->alert, 0);
}

static void {{name|lower}}_realize(DeviceState *dev, Error **errp)
{
    {{name|upper}}State *s = {{name|upper}}(dev);
    (void)errp;

    g_assert(s->ot_id);

    qemu_chr_fe_set_handlers(&s->chr, {{name|lower}}_can_receive, {{name|lower}}_receive,
                             NULL, {{name|lower}}_be_change, s, NULL, true);
}

static void {{name|lower}}_init(Object *obj)
{
    {{name|upper}}State *s = {{name|upper}}(obj);


    memory_region_init_io(&s->mmio, obj, &{{name|lower}}_ops, s, TYPE_{{name|upper}},
                          REGS_SIZE);
    sysbus_init_mmio(SYS_BUS_DEVICE(obj), &s->mmio);
}

static void {{name|lower}}_class_init(ObjectClass *klass, void *data)
{
    DeviceClass *dc = DEVICE_CLASS(klass);
    (void)data;

    dc->realize = {{name|lower}}_realize;
    device_class_set_legacy_reset(dc, {{name|lower}}_reset);
    device_class_set_props(dc, {{name|lower}}_properties);
    set_bit(DEVICE_CATEGORY_INPUT, dc->categories);
}

static const TypeInfo {{name|lower}}_info = {
    .name = TYPE_{{name|upper}},
    .parent = TYPE_SYS_BUS_DEVICE,
    .instance_size = sizeof({{name|upper}}State),
    .instance_init = {{name|lower}}_init,
    .class_init = {{name|lower}}_class_init,
};

static void {{name|lower}}_register_types(void)
{
    type_register_static(&{{name|lower}}_info);
}

type_init({{name|lower}}_register_types);
