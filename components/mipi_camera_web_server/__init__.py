# components/mipi_camera_web_server/__init__.py

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.const import CONF_ID, CONF_PORT
from esphome.core import coroutine_with_priority

DEPENDENCIES = ["mipi_dsi_cam", "network"]
CODEOWNERS = ["@youkorr"]

CONF_CAMERA_ID = "camera_id"
CONF_ENABLE_JPEG = "enable_jpeg"
CONF_ENABLE_H264 = "enable_h264"

mipi_camera_web_server_ns = cg.esphome_ns.namespace("mipi_camera_web_server")
MipiCameraWebServer = mipi_camera_web_server_ns.class_("MipiCameraWebServer", cg.Component)

# Namespace caméra
mipi_dsi_cam_ns = cg.esphome_ns.namespace("mipi_dsi_cam")
MipiDsiCam = mipi_dsi_cam_ns.class_("MipiDsiCam")

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(MipiCameraWebServer),
        cv.Required(CONF_CAMERA_ID): cv.use_id(MipiDsiCam),
        cv.Optional(CONF_PORT, default=81): cv.port,
        cv.Optional(CONF_ENABLE_JPEG, default=True): cv.boolean,
        cv.Optional(CONF_ENABLE_H264, default=False): cv.boolean,
    }
).extend(cv.COMPONENT_SCHEMA)


@coroutine_with_priority(60.0)
async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    # Lier la caméra
    camera = await cg.get_variable(config[CONF_CAMERA_ID])
    cg.add(var.set_camera(camera))
    cg.add(var.set_port(config[CONF_PORT]))

    # Options de format
    if config[CONF_ENABLE_JPEG]:
        cg.add(var.enable_jpeg_stream(True))
    if config[CONF_ENABLE_H264]:
        cg.add(var.enable_h264_stream(True))

    # Librairies réseau (ESP32-P4)
    cg.add_library("ESP Async WebServer", None)
    cg.add_library("AsyncTCP", None)

    # Build flags et PSRAM
    cg.add_build_flag("-DBOARD_HAS_PSRAM")
    cg.add_build_flag("-DUSE_ESP32_VARIANT_ESP32P4")
    cg.add_build_flag("-DCONFIG_CAMERA_CORE0=1")

    # Définir les macros de stream
    if config[CONF_ENABLE_JPEG]:
        cg.add_define("USE_JPEG_STREAMING")
    if config[CONF_ENABLE_H264]:
        cg.add_define("USE_H264_STREAMING")

    # Log compile info
    cg.add(cg.RawExpression(f'''
        ESP_LOGI("compile", "MIPI Camera Web Server:");
        ESP_LOGI("compile", "  Port: {config[CONF_PORT]}");
        ESP_LOGI("compile", "  JPEG streaming: {'enabled' if config[CONF_ENABLE_JPEG] else 'disabled'}");
        ESP_LOGI("compile", "  H.264 streaming: {'enabled' if config[CONF_ENABLE_H264] else 'disabled'}");
    '''))

